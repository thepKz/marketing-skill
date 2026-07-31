#!/usr/bin/env python3
"""Decide which frames one product photograph can actually produce, and what a reshoot buys.

The promise attached to image models is that one photograph becomes a whole listing. It is half
true, and the half that is false is expensive: a front-on photograph cannot become a back-of-pack
shot, a single unit cannot become a bundle, and one colourway cannot become a range. Those are not
prompt problems. The information is not in the file. A model asked for them returns something
plausible, and a plausible ingredient panel is a fabricated claim.

So this script separates the frames a source can produce from the frames it cannot, using two
checks that are arithmetic rather than judgement:

Presence. Each slot in `data/product-compositions.csv` names, in `needs_present`, the one thing a
single front-on photograph does not contain - a back exposure, a person wearing it, both states of a
before-and-after. Declare what you have with `--have`. Anything still missing is reported as
missing, not as a prompt to write harder.

Pixels. Each slot has a delivery size, taken from `data/frame-ratios.csv`, and a target product fill
taken from Google Merchant Center's documented band of no less than 75 and no more than 90 percent
for a main product image. Given the source dimensions and how tall the product stands in it, the
resample factor follows. Above 1.0 the frame is being upscaled, and Google's own guidance is "Don't
scale up an image or submit a thumbnail" - so above 1.0 the slot fails rather than warns. `--accept-
upscale` will let a factor through, and it downgrades the verdict to `review` with the factor named,
because someone should see the number they agreed to.

The four verdicts are the ones the rest of this skill uses. `passed`, `failed`, `skipped` when an
input was never supplied, and `review` when the arithmetic ran and does not settle the question.
`review` exists so that the gates that do fail mean something. A checker that returns a verdict on
everything gets ignored on everything.

What the script will not do: judge whether the frame is any good, decide whether a lifestyle scene
is honest, or check the output. Those are `references/product-composition-set.md`, `creative-
evaluation.md` and a pair of eyes at full size and at thumbnail size.

Everything is stdlib. No key, no network, no image provider.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
SLOTS_TABLE = DATA / "product-compositions.csv"
RATIOS_TABLE = DATA / "frame-ratios.csv"

# Google Merchant Center, https://support.google.com/merchants/answer/6324350, fetched 2026-07-31:
# "Don't scale up an image or submit a thumbnail." A factor of exactly 1.0 is the source at its own
# size, so the ceiling is 1.0 and not something slightly above it as a convenience.
UPSCALE_CEILING = 1.0

# The five derivations that leave the product's own pixels alone. Everything not in this set needs a
# view, a person or a state the source does not contain, which is why no amount of source resolution
# rescues it. Named here as well as in the table's generator because it is the line the script
# reasons across, and a reader of this file should not have to open another one to find it.
PRESERVING = {"reframe", "relight", "outpaint", "background-swap", "scene-rebuild"}

SETS = {
    "marketplace": ("Every slot a listing page can hold, main image first",
                    lambda row: row["marketplace_main_image"] in {"allowed", "additional-only"}),
    "social": ("Feed, story and banner placements",
               lambda row: row["marketplace_main_image"] == "disallowed"),
    "one-photo": ("Only what a single photograph can produce with no further exposures",
                  lambda row: row["needs_present"] == "-"),
    "full": ("Every slot in the table", lambda row: True),
}


class CompositionSet:
    """The slot table joined to the delivery sizes, with the arithmetic on top."""

    def __init__(self, slots: list[dict], ratios: dict[str, dict]) -> None:
        self.slots = slots
        self.ratios = ratios
        self.by_slot = {row["slot_id"]: row for row in slots}

    @classmethod
    def load(cls) -> "CompositionSet":
        slots = list(csv.DictReader(io.StringIO(SLOTS_TABLE.read_text(encoding="utf-8"))))
        ratios = {row["ratio_id"]: row for row
                  in csv.DictReader(io.StringIO(RATIOS_TABLE.read_text(encoding="utf-8")))}
        missing = sorted({row["ratio"] for row in slots} - set(ratios))
        if missing:
            raise ValueError(f"slots name ratios that do not exist: {', '.join(missing)}")
        return cls(slots, ratios)

    def delivery(self, slot: dict) -> tuple[int, int]:
        ratio = self.ratios[slot["ratio"]]
        return int(ratio["w"]), int(ratio["h"])

    def largest_crop(self, source: tuple[int, int], slot: dict) -> tuple[float, float]:
        """The biggest frame at the slot's ratio that fits inside the source, in source pixels."""
        width, height = source
        target_w, target_h = self.delivery(slot)
        aspect = target_w / target_h
        if width / height >= aspect:
            return height * aspect, float(height)
        return float(width), width / aspect

    def factor(self, slot: dict, source: tuple[int, int] | None,
               product_px: int | None) -> dict | None:
        """The resample factor this slot demands, and which of the two constraints set it.

        Two separate things can force an upscale and they are not the same thing. The frame can be
        too small for the delivery size, and the product can be too small inside the frame for the
        fill the slot wants. Reporting only the larger of the two would hide which one to fix, and
        they have different fixes: move the camera closer, or shoot at a higher resolution.

        The product-fill arithmetic has to know how much of the product the slot shows, or it gets
        the macro backwards. A slot that crops into the product has fewer source pixels to work with,
        not the same number: a macro showing 15 percent of a 2600 px product is drawing on 390 px and
        has to fill a 1080 px frame from them, which is 2.769x. Treating `product_px` as available in
        full is what made this script pass that slot at 0.415x, and it is the one verdict a shop
        owner would have caught by eye.
        """
        if source is None:
            return None
        crop_w, crop_h = self.largest_crop(source, slot)
        target_w, target_h = self.delivery(slot)
        frame_factor = target_h / crop_h
        parts = [{"constraint": "frame",
                  "factor": round(frame_factor, 3),
                  "why": f"the largest {slot['ratio']} crop inside the source is "
                         f"{int(crop_w)}x{int(crop_h)} and the delivery size is {target_w}x{target_h}"}]
        if product_px is not None:
            shows = int(slot["shows_pct_of_product"])
            available = product_px * shows / 100
            wanted = int(row_fill(slot) / 100 * target_h)
            product_factor = wanted / available
            seen = (f"the product stands {product_px} px tall in the source"
                    if shows == 100 else
                    f"this slot shows {shows} percent of the product, which is {int(available)} px "
                    f"of the {product_px} px it stands in the source")
            parts.append({"constraint": "product-fill",
                          "factor": round(product_factor, 3),
                          "why": f"{seen} and this slot wants that filling {row_fill(slot)} percent "
                                 f"of {target_h} px, so {wanted} px"})
        worst = max(parts, key=lambda part: part["factor"])
        return {"factor": worst["factor"], "set_by": worst["constraint"], "parts": parts}

    def judge(self, slot: dict, have: set[str], source: tuple[int, int] | None,
              product_px: int | None, accept_upscale: float | None) -> dict:
        result = {"slot": slot["slot_id"],
                  "name_en": slot["name_en"],
                  "ratio": slot["ratio"],
                  "delivery": "x".join(str(n) for n in self.delivery(slot)),
                  "derivation": slot["derivation"],
                  "iptc_digital_source_type": slot["iptc_digital_source_type"],
                  "marketplace_main_image": slot["marketplace_main_image"]}

        needed = slot["needs_present"]
        if needed != "-" and needed not in have:
            # This is the branch the whole script exists for. The frame is not hard to produce, it
            # is impossible to produce honestly, and no amount of prompting changes that.
            result.update({"status": "failed",
                           "why": f"the source does not contain {needed.replace('-', ' ')}, and "
                                  f"{slot['derivation']} would invent it",
                           "unlocked_by": needed,
                           "lock": slot["lock"]})
            return result

        measured = self.factor(slot, source, product_px)
        if measured is None:
            result.update({"status": "skipped",
                           "why": "no source dimensions were given, so the pixel arithmetic cannot "
                                  "run. Nothing here says the slot is fine"})
            return result

        result["resample"] = measured
        if measured["factor"] <= UPSCALE_CEILING:
            if slot["condition_is"] == "judgement":
                # The pixels are sufficient and the pixels are not the condition. This slot rebuilds
                # a scene around a cutout, and whether that reads as a photograph depends on an edge
                # being cuttable and a light direction being matchable. Returning `passed` here would
                # be the script answering a question it did not ask.
                result.update({"status": "review",
                               "why": f"the pixels are sufficient at {measured['factor']}x, and the "
                                      f"pixels are not what decides this slot. Look at the source "
                                      f"and settle: {slot['needs_from_source'].lower()}",
                               "unsettled": slot["needs_from_source"],
                               "lock": slot["lock"]})
                return result
            result.update({"status": "passed",
                           "why": f"the source carries this frame at {measured['factor']}x, so no "
                                  f"pixels are being invented inside the product",
                           "lock": slot["lock"]})
            return result
        if accept_upscale is not None and measured["factor"] <= accept_upscale:
            result.update({"status": "review",
                           "why": f"the frame needs {measured['factor']}x, which is an upscale you "
                                  f"accepted up to {accept_upscale}x. Set by the "
                                  f"{measured['set_by']} constraint. Inspect the locked detail at "
                                  f"full size before this ships: {slot['lock']}"})
            return result
        result.update({"status": "failed",
                       "why": f"the frame needs {measured['factor']}x, set by the "
                              f"{measured['set_by']} constraint. Google Merchant Center documents "
                              f"not scaling an image up, and a resampler cannot add the label "
                              f"detail this slot locks",
                       "lock": slot["lock"]})
        return result

    def report(self, slot_ids: list[str], have: set[str], source: tuple[int, int] | None,
               product_px: int | None, accept_upscale: float | None) -> dict:
        judged = [self.judge(self.by_slot[slot_id], have, source, product_px, accept_upscale)
                  for slot_id in slot_ids]
        counts = {status: sum(1 for j in judged if j["status"] == status)
                  for status in ("passed", "failed", "skipped", "review")}
        return {"asked_for": slot_ids,
                "source": "x".join(str(n) for n in source) if source else None,
                "product_height_px": product_px,
                "declared_present": sorted(have),
                "upscale_ceiling": UPSCALE_CEILING,
                "accepted_upscale": accept_upscale,
                "slots": judged,
                "counts": counts,
                "reshoot_value": self.reshoot_value(judged),
                "declare_in_metadata": self.metadata(judged),
                "verdict": self.settle(judged, counts, source, product_px)}

    def reshoot_value(self, judged: list[dict]) -> list[dict]:
        """What one more exposure would unlock, so the reshoot argument is a count.

        A shop owner deciding whether to photograph the back of the box is not helped by being told
        that additional images improve conversion. They are helped by being told that this one
        exposure turns two failing slots into producible ones, and which two.
        """
        blocked: dict[str, list[str]] = {}
        for entry in judged:
            if entry["status"] == "failed" and "unlocked_by" in entry:
                blocked.setdefault(entry["unlocked_by"], []).append(entry["slot"])
        return [{"one_more_exposure": needed, "unlocks": sorted(slots), "count": len(slots)}
                for needed, slots in sorted(blocked.items(), key=lambda kv: (-len(kv[1]), kv[0]))]

    def metadata(self, judged: list[dict]) -> list[dict]:
        """The IPTC codes the producible frames have to carry.

        Google Merchant Center requires generated images to keep their IPTC DigitalSourceType tag,
        and a background swap or an outpaint is a generated image even though the product in it is
        a real photograph. The code differs per slot, so it is listed per slot rather than once.
        """
        codes: dict[str, list[str]] = {}
        for entry in judged:
            if entry["status"] in {"passed", "review"}:
                codes.setdefault(entry["iptc_digital_source_type"], []).append(entry["slot"])
        return [{"qcode": code,
                 "uri": f"http://cv.iptc.org/newscodes/digitalsourcetype/{code}",
                 "applies_to": sorted(slots)}
                for code, slots in sorted(codes.items())]

    def settle(self, judged: list[dict], counts: dict[str, int],
               source: tuple[int, int] | None, product_px: int | None) -> dict:
        producible = [j["slot"] for j in judged if j["status"] == "passed"]
        if source is None:
            return {"status": "skipped",
                    "why": "no source dimensions were supplied. Every slot is unjudged, which is "
                           "not the same as every slot being fine",
                    "next": "measure the source file and pass --source WxH"}
        if product_px is None:
            note = ("--product-px was not given, so only the frame constraint was checked. A frame "
                    "that fits can still hold the product too small for the slot's fill")
        else:
            note = None
        if counts["failed"]:
            missing = sorted({j["unlocked_by"] for j in judged if j.get("unlocked_by")})
            return {"status": "failed",
                    "why": f"{counts['failed']} of {len(judged)} slots cannot be produced from this "
                           f"source. {len(producible)} can",
                    "producible": producible,
                    "missing_exposures": missing,
                    "next": "run the producible slots now and decide the reshoot on the "
                            "reshoot_value count, not on how the set looks half-finished",
                    "note": note}
        if counts["review"]:
            # The two review causes need different words because they need different actions. An
            # accepted upscale is settled by looking at the delivered frame; an unsettled condition is
            # settled by looking at the source. Collapsing them into "inspect the output" sends the
            # user to the wrong file.
            unsettled = sorted({j["slot"] for j in judged if j.get("unsettled")})
            upscaled = [j["slot"] for j in judged
                        if j["status"] == "review" and j["slot"] not in unsettled]
            reasons = []
            if upscaled:
                reasons.append(f"{len(upscaled)} only pass because an upscale was accepted "
                               f"({', '.join(upscaled)})")
            if unsettled:
                reasons.append(f"{len(unsettled)} have enough pixels but turn on something the "
                               f"arithmetic does not measure ({', '.join(unsettled)})")
            return {"status": "review",
                    "why": f"{counts['review']} of {len(judged)} slots are unsettled: "
                           + "; ".join(reasons),
                    "producible": producible,
                    "next": "inspect the locked detail at full size on the upscaled frames, and look "
                            "at the source itself for the rest",
                    "note": note}
        if counts["skipped"]:
            return {"status": "skipped",
                    "why": f"{counts['skipped']} slots could not be judged",
                    "producible": producible,
                    "note": note}
        return {"status": "passed",
                "why": f"all {len(judged)} slots are producible from this source without inventing "
                       f"product detail",
                "producible": producible,
                "next": "generate, then check every frame against its own lock column",
                "note": note}


def row_fill(slot: dict) -> int:
    return int(slot["product_fill_pct"])


def parse_source(text: str) -> tuple[int, int]:
    lowered = text.lower().replace("×", "x")
    if "x" not in lowered:
        raise argparse.ArgumentTypeError(f"--source wants WxH, for example 3000x4000, not {text!r}")
    width, _, height = lowered.partition("x")
    try:
        pair = (int(width), int(height))
    except ValueError:
        raise argparse.ArgumentTypeError(f"--source wants two whole numbers, not {text!r}") from None
    if pair[0] <= 0 or pair[1] <= 0:
        raise argparse.ArgumentTypeError("--source dimensions must both be positive")
    return pair


def as_text(report: dict, unit: CompositionSet) -> str:
    lines = ["PRODUCT COMPOSITION SET", ""]
    lines.append(f"source              {report['source'] or 'not given'}")
    if report["product_height_px"]:
        lines.append(f"product height      {report['product_height_px']} px in the source")
    if report["declared_present"]:
        lines.append(f"also photographed   {', '.join(report['declared_present'])}")
    counts = report["counts"]
    lines.append(f"slots               {len(report['asked_for'])} asked for: "
                 + ", ".join(f"{n} {name}" for name, n in counts.items() if n))
    lines.append("")

    for entry in report["slots"]:
        lines.append(f"[{entry['status'].upper()}] {entry['slot']} - {entry['name_en']}")
        lines.append(f"    {entry['ratio']} at {entry['delivery']}, by {entry['derivation']}")
        lines.append(f"    {entry['why']}")
        if "resample" in entry:
            for part in entry["resample"]["parts"]:
                lines.append(f"    {part['constraint']:13} {part['factor']}x  {part['why']}")
        if entry.get("lock"):
            lines.append(f"    lock: {entry['lock']}")
        lines.append("")

    if report["reshoot_value"]:
        lines.append("WHAT ONE MORE EXPOSURE BUYS")
        for item in report["reshoot_value"]:
            lines.append(f"    {item['one_more_exposure']:32} unlocks {item['count']}: "
                         f"{', '.join(item['unlocks'])}")
        lines.append("")

    if report["declare_in_metadata"]:
        lines.append("DECLARE IN IPTC DigitalSourceType")
        for item in report["declare_in_metadata"]:
            lines.append(f"    {item['qcode']:38} {', '.join(item['applies_to'])}")
        lines.append("")

    verdict = report["verdict"]
    lines.append(f"VERDICT  {verdict['status'].upper()}")
    lines.append(f"    {verdict['why']}")
    for key in ("missing_exposures", "next", "note"):
        value = verdict.get(key)
        if value:
            if isinstance(value, list):
                value = ", ".join(value)
            lines.append(f"    {key}: {value}")
    return "\n".join(lines) + "\n"


def build_parser(unit: CompositionSet | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decide which product frames one photograph can produce, and what a reshoot buys.")
    parser.add_argument("--source", type=parse_source, metavar="WxH",
                        help="pixel dimensions of the source photograph, for example 3000x4000")
    parser.add_argument("--product-px", type=int, metavar="N",
                        help="how tall the product stands in the source, in pixels")
    parser.add_argument("--slots", nargs="+", metavar="SLOT", help="slot ids from the table")
    parser.add_argument("--set", choices=sorted(SETS), help="a named group of slots")
    parser.add_argument("--have", nargs="+", default=[], metavar="THING",
                        help="what the source set also contains, from the needs_present vocabulary")
    parser.add_argument("--accept-upscale", type=float, metavar="FACTOR",
                        help="allow a resample up to this factor, reported as review not passed")
    parser.add_argument("--list-slots", action="store_true", help="print the table and exit")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output", metavar="PATH")
    return parser


def list_slots(unit: CompositionSet) -> str:
    lines = [f"{len(unit.slots)} slots in data/product-compositions.csv", ""]
    width = max(len(row["slot_id"]) for row in unit.slots)
    for row in unit.slots:
        lines.append(f"{row['slot_id']:{width}}  {row['obtainable_from_one_photo']:11} "
                     f"{row['derivation']:16} {row['ratio']:13} {row['needs_present']}")
    lines.append("")
    lines.append("--set groups:")
    for name, (why, predicate) in sorted(SETS.items()):
        members = [row["slot_id"] for row in unit.slots if predicate(row)]
        lines.append(f"  {name:12} {len(members):2}  {why}")
    lines.append("")
    lines.append("--have vocabulary, from the needs_present column:")
    for value in sorted({row["needs_present"] for row in unit.slots} - {"-"}):
        members = [row["slot_id"] for row in unit.slots if row["needs_present"] == value]
        lines.append(f"  {value:32} unlocks {', '.join(members)}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    unit = CompositionSet.load()
    parser = build_parser(unit)
    args = parser.parse_args(argv)

    if args.list_slots:
        emit(list_slots(unit), args.output)
        return 0

    if args.slots and args.set:
        parser.error("give --slots or --set, not both")
    if args.slots:
        unknown = [slot for slot in args.slots if slot not in unit.by_slot]
        if unknown:
            parser.error(f"no such slot: {', '.join(unknown)}. Run --list-slots")
        slot_ids = list(dict.fromkeys(args.slots))
    else:
        predicate = SETS[args.set or "marketplace"][1]
        slot_ids = [row["slot_id"] for row in unit.slots if predicate(row)]

    vocabulary = {row["needs_present"] for row in unit.slots} - {"-"}
    unknown_have = [thing for thing in args.have if thing not in vocabulary]
    if unknown_have:
        parser.error(f"--have does not know {', '.join(unknown_have)}. "
                     f"Choose from: {', '.join(sorted(vocabulary))}")
    if args.product_px is not None and args.product_px <= 0:
        parser.error("--product-px must be positive")
    if args.product_px is not None and args.source is None:
        parser.error("--product-px is a measurement inside the source, so it needs --source too")
    if args.product_px is not None and args.product_px > args.source[1]:
        parser.error(f"--product-px {args.product_px} is taller than the source itself "
                     f"({args.source[1]} px)")
    if args.accept_upscale is not None and args.accept_upscale < UPSCALE_CEILING:
        parser.error(f"--accept-upscale below {UPSCALE_CEILING} would refuse frames the source "
                     f"already carries")

    report = unit.report(slot_ids, set(args.have), args.source, args.product_px,
                         args.accept_upscale)
    if args.format == "json":
        emit_json(report, args.output)
    else:
        emit(as_text(report, unit), args.output)

    status = report["verdict"]["status"]
    return {"passed": 0, "failed": 2, "review": 3, "skipped": 3}[status]


if __name__ == "__main__":
    sys.exit(main())
