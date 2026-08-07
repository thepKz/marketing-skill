#!/usr/bin/env python3
"""Check a compiled image prompt against what each model family actually documents.

The prompt-listicle genre treats every provider as the same machine with different
adjectives. The documentation does not. A negative-prompt block is an architectural
feature that exists where classifier-free guidance is exposed and is structurally
absent elsewhere; a token window is a place where text is silently deleted rather
than de-weighted; in-image text is a documented limitation on one provider, a
required syntax on another, and a published character budget on exactly one.

Every capability flag below names the row in `data/prompt-grammar.csv` that backs
it. That is the point of the file: a flag with no fact_id is a capability somebody
remembered, and a test refuses to let one exist. Where a provider publishes
nothing, the flag is None and the gate returns `review` rather than inventing a
number to compare against.

Usage:
    python check_prompt_grammar.py --prompt-file out/prompt.txt --provider flux
    python check_prompt_grammar.py --prompt "a market stall, the words \\"Bun Bo Hue\\"" \\
        --provider imagen --in-image-text
    python check_prompt_grammar.py --provider midjourney --recurring-person --needs-reproducible
    python check_prompt_grammar.py --list-families
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "prompt-grammar.csv"

# A prompt in this skill is compiled by scripts/compile_prompt.py, so these are the
# headings it actually emits, not a guess at what a negative block might look like.
NEGATIVE_MARKERS = ("NEGATIVE PROMPT", "DO NOT", "NEGATIVE CONSTRAINTS")

# Subword tokenizers land near 1.3 tokens per word and near one token per four
# characters for ordinary English; both routes are computed and the larger is kept,
# because undercounting here lets a prompt through the gate and loses its tail
# silently, which is the failure the gate exists for. It stays an estimate: the true
# count needs the provider's tokenizer, and only the open-weight families ship one.
TOKENS_PER_WORD = 1.3
CHARS_PER_TOKEN = 4.0


class Family:
    """One model family and the documented facts that constrain a prompt to it.

    `negative_prompt` is one of "field", "none", "legacy-only". `token_window` is the
    number of tokens after which text is documented to disappear, or None where no
    limit is published - which is not the same as no limit existing.
    """

    def __init__(self, name, aliases, negative_prompt, negative_fact, token_window,
                 window_fact, text_char_limit, text_phrase_limit, text_fact,
                 text_syntax, consistency, consistency_fact, seed, seed_fact,
                 deprecated, lifecycle_fact, prompt_char_limit=None,
                 char_limit_fact=None):
        self.name = name
        self.aliases = aliases
        self.negative_prompt = negative_prompt
        self.negative_fact = negative_fact
        self.token_window = token_window
        self.window_fact = window_fact
        self.text_char_limit = text_char_limit
        self.text_phrase_limit = text_phrase_limit
        self.text_fact = text_fact
        self.text_syntax = text_syntax
        self.consistency = consistency
        self.consistency_fact = consistency_fact
        self.seed = seed
        self.seed_fact = seed_fact
        self.deprecated = deprecated
        self.lifecycle_fact = lifecycle_fact
        # An encoder window and an API character limit are different failures. Overrun the
        # first and the tail is dropped silently; overrun the second and the request is
        # rejected outright. Collapsing them into one number would report a rejected
        # request as a truncated prompt.
        self.prompt_char_limit = prompt_char_limit
        self.char_limit_fact = char_limit_fact

    def facts(self):
        return [f for f in (self.negative_fact, self.window_fact, self.text_fact,
                            self.consistency_fact, self.seed_fact,
                            self.lifecycle_fact, self.char_limit_fact) if f]


FAMILIES = (
    Family("gpt-image", ("openai", "gpt-image-2", "gpt-image-1", "dalle", "dall-e"),
           "none", "openai-no-negative", None, "openai-no-structure-guidance",
           None, None, "openai-text-limitation", "double-quotes-recommended",
           "reference-image-documented-as-unreliable", "openai-consistency-limitation",
           "none", "openai-no-seed", False, "dalle-api-removed",
           prompt_char_limit=32000, char_limit_fact="openai-prompt-length"),
    Family("gemini-image", ("nano-banana", "nano-banana-2", "nano-banana-2-lite",
                            "nano-banana-pro", "gemini"),
           "none", "gemini-semantic-negative", None, "gemini-step-by-step",
           None, None, "gemini-text-then-image", "double-quotes-recommended",
           "reference-image-with-a-documented-ceiling", "gemini-reference-counts",
           "none", "gemini-no-seed", False, None),
    Family("imagen", ("vertex", "imagen-3", "imagen-4"),
           "legacy-only", "vertex-negative-legacy", None, "imagen-128-token-myth",
           25, 3, "imagen-text-25-chars", "double-quotes-recommended",
           "reference-image", "consistency-is-conditioning",
           "excludes-watermark", "imagen-seed-deterministic",
           True, "vertex-docs-frozen"),
    Family("midjourney", ("mj", "midjourney-v8"),
           "flag-only", "midjourney-prompt-length", None, "midjourney-prompt-length",
           None, None, "midjourney-text-quotes", "double-quotes-required",
           "none-on-current-version", "midjourney-cref-dead",
           "similar-not-identical", "seed-not-reproducible-mj",
           False, "mj-legal-pages-moved"),
    Family("flux", ("flux-2", "bfl"),
           "none", "flux2-no-negative", None, None,
           None, None, "flux-text-guidance", "double-quotes-recommended",
           "reference-image", "consistency-is-conditioning",
           None, None, False, None),
    Family("stable-diffusion-3", ("sd3", "sd3.5", "stability"),
           "field", "stability-turbo-negative", 256, "sd3-t5-256",
           None, None, "sd3-drop-t5-text", "double-quotes-recommended",
           "reference-image", "consistency-is-conditioning",
           None, None, False, None),
    Family("stable-diffusion-legacy", ("sd15", "sdxl", "sd-xl"),
           "field", "stability-turbo-negative", 77, "clip-77-silent",
           None, None, None, "double-quotes-recommended",
           "reference-image", "consistency-is-conditioning",
           None, None, False, None),
    Family("ideogram", (),
           "field", "ideogram-negative", None, None,
           None, None, None, "double-quotes-recommended",
           "reference-image", "consistency-is-conditioning",
           None, None, False, None),
    Family("firefly", ("adobe", "adobe-firefly"),
           "endpoint-dependent", "firefly-negative-scope", None, None,
           None, None, "firefly-text-effects-indemnity", "double-quotes-recommended",
           "reference-image", "consistency-is-conditioning",
           None, None, False, None),
)


def load_facts() -> dict:
    with DATA.open(encoding="utf-8", newline="") as fh:
        return {row["fact_id"]: row for row in csv.DictReader(fh)}


def resolve(provider: str) -> Family:
    key = provider.strip().lower()
    for family in FAMILIES:
        if key == family.name or key in family.aliases:
            return family
    known = ", ".join(f.name for f in FAMILIES)
    raise ValueError(f"unknown provider {provider!r}; families are {known}")


def estimate_tokens(text: str) -> int:
    """Pessimistic token estimate. See the two constants for why it is not exact."""
    words = len(re.findall(r"\S+", text)) * TOKENS_PER_WORD
    chars = len(text) / CHARS_PER_TOKEN
    return int(max(words, chars)) + 1


def quoted_strings(text: str) -> list:
    return re.findall(r'"([^"]+)"', text)


def looks_like_text_request(text: str) -> bool:
    return bool(re.search(r"(?i)\b(the words?|text reading|written|headline|caption|"
                          r"typograph\w*|lettering)\b", text)) or bool(quoted_strings(text))


def gate(name, status, detail, fact_id=None):
    entry = {"gate": name, "status": status, "detail": detail}
    if fact_id:
        entry["fact_id"] = fact_id
    return entry


def check_negative_block(text: str, family: Family, facts: dict) -> dict:
    present = [m for m in NEGATIVE_MARKERS if m in text.upper()]
    if not present:
        return gate("negative-prompt-field", "skipped",
                    "The prompt carries no negative block, so nothing to route.")
    fact = facts[family.negative_fact]
    if family.negative_prompt == "none":
        return gate("negative-prompt-field", "failed",
                    f"{family.name} has no negative-prompt field, so the "
                    f"{present[0]} block is not a separate channel - it is sent as part of the "
                    f"prompt, which means the model reads the words you were excluding. Rewrite "
                    f"each exclusion as a positive description of what should be there instead. "
                    f"{fact['claim']}",
                    family.negative_fact)
    if family.negative_prompt == "legacy-only":
        return gate("negative-prompt-field", "review",
                    f"{family.name} accepts the field on some model strings and not others, and "
                    f"the unsupported case is silent rather than an error. Name the exact model "
                    f"string before sending it. {fact['claim']}",
                    family.negative_fact)
    if family.negative_prompt == "endpoint-dependent":
        return gate("negative-prompt-field", "review",
                    f"{family.name} routes this by endpoint version rather than by product name. "
                    f"{fact['claim']}",
                    family.negative_fact)
    if family.negative_prompt == "flag-only":
        return gate("negative-prompt-field", "review",
                    f"{family.name} has no negative-prompt field; exclusions go through its own "
                    f"parameter syntax, which has to be checked live because parameters have been "
                    f"removed between versions. {facts['midjourney-cref-dead']['claim']}",
                    "midjourney-cref-dead")
    return gate("negative-prompt-field", "passed",
                f"{family.name} exposes a negative-prompt field. Write nouns and attributes in it, "
                f"never negated sentences, and never contradict the positive prompt.",
                family.negative_fact)


def check_window(text: str, family: Family, facts: dict) -> dict:
    tokens = estimate_tokens(text)
    if family.token_window is None:
        fact = facts.get(family.window_fact)
        detail = (f"About {tokens} tokens. No prompt length limit is published for {family.name}, "
                  f"so this is neither pass nor fail: front-loading the prompt is a precaution "
                  f"here, not a documented requirement.")
        if fact:
            detail += f" {fact['claim']}"
        return gate("prompt-window", "review", detail, family.window_fact)
    fact = facts[family.window_fact]
    if tokens > family.token_window:
        return gate("prompt-window", "failed",
                    f"About {tokens} tokens against a documented window of "
                    f"{family.token_window}. The overflow is not weighted less, it is absent, and "
                    f"nothing tells you so at request time. Cut it or move the load-bearing clauses "
                    f"to the front. {fact['claim']}",
                    family.window_fact)
    headroom = family.token_window - tokens
    return gate("prompt-window", "passed",
                f"About {tokens} tokens inside a {family.token_window}-token window, "
                f"{headroom} spare on a pessimistic count.",
                family.window_fact)


def check_char_limit(text: str, family: Family, facts: dict) -> dict:
    if family.prompt_char_limit is None:
        return gate("prompt-character-limit", "skipped",
                    f"No API character limit is published for {family.name}.")
    fact = facts[family.char_limit_fact]
    length = len(text)
    if length > family.prompt_char_limit:
        return gate("prompt-character-limit", "failed",
                    f"{length} characters against a documented maximum of "
                    f"{family.prompt_char_limit}. This one is a rejected request rather than a "
                    f"quiet truncation. {fact['claim']}",
                    family.char_limit_fact)
    return gate("prompt-character-limit", "passed",
                f"{length} characters against a documented maximum of "
                f"{family.prompt_char_limit}, which is a validation ceiling and not a budget to "
                f"fill.",
                family.char_limit_fact)


def check_in_image_text(text: str, family: Family, facts: dict, asked: bool) -> dict:
    strings = quoted_strings(text)
    if not asked and not looks_like_text_request(text):
        return gate("in-image-text", "skipped",
                    "No rendered text requested, so no budget to check. Set copy in layout and "
                    "this gate stays out of the way.")
    if not strings:
        detail = ("Text is requested in prose but no exact string is quoted, so the spelling is "
                  "the model's decision rather than yours.")
        if family.text_syntax == "double-quotes-required":
            fact = facts[family.text_fact]
            return gate("in-image-text", "failed",
                        f"{detail} On {family.name} this is not a style preference: {fact['claim']}",
                        family.text_fact)
        return gate("in-image-text", "review", detail, family.text_fact)

    over = [s for s in strings if family.text_char_limit and len(s) > family.text_char_limit]
    if over:
        fact = facts[family.text_fact]
        longest = max(over, key=len)
        return gate("in-image-text", "failed",
                    f"{len(over)} of {len(strings)} quoted strings exceed the documented "
                    f"{family.text_char_limit}-character budget, the longest at {len(longest)}. "
                    f"Shorten the headline to fit or set it in layout instead. {fact['claim']}",
                    family.text_fact)
    if family.text_phrase_limit and len(strings) > family.text_phrase_limit:
        return gate("in-image-text", "failed",
                    f"{len(strings)} quoted phrases against a documented limit of "
                    f"{family.text_phrase_limit}. This is a layout job, not a generation job.",
                    family.text_fact)
    if family.text_char_limit:
        return gate("in-image-text", "passed",
                    f"{len(strings)} quoted string(s), longest "
                    f"{max(len(s) for s in strings)} characters, inside the documented "
                    f"{family.text_char_limit}-character budget. Inspect every character anyway.",
                    family.text_fact)
    fact = facts.get(family.text_fact)
    detail = (f"{len(strings)} quoted string(s) and no published character budget for "
              f"{family.name}, so there is nothing to measure against. Quote the exact string with "
              f"its capitalization, spell unusual names letter-by-letter, and inspect the output "
              f"character by character before it ships.")
    if fact:
        detail += f" {fact['claim']}"
    return gate("in-image-text", "review", detail, family.text_fact)


def check_consistency(family: Family, facts: dict, recurring: bool) -> dict:
    if not recurring:
        return gate("character-consistency", "skipped",
                    "No recurring person in this run.")
    fact = facts[family.consistency_fact]
    if family.consistency == "reference-image-documented-as-unreliable":
        return gate("character-consistency", "review",
                    f"{family.name} lists recurring-character drift in its own Limitations "
                    f"section, which makes this the vendor saying the mechanism is unreliable "
                    f"rather than a rumour. {fact['claim']} Budget the retries, and check the face "
                    f"against the reference on every render rather than at the end.",
                    family.consistency_fact)
    if family.consistency == "reference-image-with-a-documented-ceiling":
        return gate("character-consistency", "review",
                    f"{family.name} publishes numbers for this, which nothing else here does. "
                    f"{fact['claim']} Count the recurring people in the shot against that ceiling "
                    f"before promising a group scene.",
                    family.consistency_fact)
    if family.consistency == "none-on-current-version":
        return gate("character-consistency", "failed",
                    f"{family.name} documents no working character-reference parameter on its "
                    f"current default version, so a recurring person cannot be held here by any "
                    f"documented mechanism. {fact['claim']}",
                    family.consistency_fact)
    return gate("character-consistency", "review",
                f"{family.name} documents consistency as reference-image conditioning and states "
                f"it is not guaranteed. Supply the reference and the locked parameter sheet from "
                f"plan_virtual_person.py, and check the result rather than assuming it. "
                f"{fact['claim']}",
                family.consistency_fact)


def check_seed(family: Family, facts: dict, needs: bool) -> dict:
    if not needs:
        return gate("seed-reproducibility", "skipped",
                    "Reproducibility not requested for this run.")
    if family.seed is None:
        return gate("seed-reproducibility", "review",
                    f"No seed behaviour is published for {family.name}. Keep the prompt and the "
                    f"output file, because an unpublished parameter is not a plan.")
    fact = facts[family.seed_fact]
    if family.seed == "none":
        return gate("seed-reproducibility", "failed",
                    f"{family.name} documents no seed parameter, so an identical regeneration "
                    f"cannot be promised. Archive the file. {fact['claim']}",
                    family.seed_fact)
    if family.seed == "similar-not-identical":
        return gate("seed-reproducibility", "failed",
                    f"{family.name} documents seeds as similar but not identical, which is the "
                    f"opposite of what the parameter is usually sold as. {fact['claim']}",
                    family.seed_fact)
    return gate("seed-reproducibility", "review",
                f"Reproducible, but at a cost: {fact['claim']}. Decide which of the two you keep "
                f"at pipeline design time, not per run.",
                family.seed_fact)


def check_lifecycle(family: Family, facts: dict) -> dict:
    if not family.deprecated:
        return gate("lifecycle", "passed",
                    f"{family.name} is not documented as deprecated.")
    fact = facts[family.lifecycle_fact]
    return gate("lifecycle", "review",
                f"{family.name} carries a published expiry date. {fact['claim']} Confirm the "
                f"endpoint still answers before quoting the capability to anybody.",
                family.lifecycle_fact)


def build(prompt: str, provider: str, in_image_text: bool = False,
          recurring_person: bool = False, needs_reproducible: bool = False) -> dict:
    facts = load_facts()
    family = resolve(provider)
    missing = [f for f in family.facts() if f not in facts]
    if missing:
        raise ValueError(f"{family.name} cites fact ids absent from prompt-grammar.csv: {missing}")

    gates = [
        check_negative_block(prompt, family, facts),
        check_window(prompt, family, facts),
        check_char_limit(prompt, family, facts),
        check_in_image_text(prompt, family, facts, in_image_text),
        check_consistency(family, facts, recurring_person),
        check_seed(family, facts, needs_reproducible),
        check_lifecycle(family, facts),
    ]
    failed = [g for g in gates if g["status"] == "failed"]
    review = [g for g in gates if g["status"] == "review"]
    if failed:
        status = "failed"
        summary = (f"{len(failed)} gate(s) contradict what {family.name} documents. Every one of "
                   f"them is a request the provider will accept and quietly not honour.")
    elif review:
        status = "review"
        summary = (f"Nothing contradicts the documentation, but {len(review)} gate(s) depend on "
                   f"something the provider does not publish. Decide those by testing, not by "
                   f"citing.")
    else:
        status = "passed"
        summary = f"The prompt is consistent with everything {family.name} documents."

    return {
        "provider": provider,
        "family": family.name,
        "estimated_tokens": estimate_tokens(prompt),
        "gates": gates,
        "verdict": {"status": status, "summary": summary},
    }


def as_text(report: dict) -> str:
    lines = [f"PROMPT GRAMMAR CHECK: {report['provider']} -> family {report['family']}",
             f"Estimated tokens: {report['estimated_tokens']} (pessimistic subword estimate)",
             ""]
    for g in report["gates"]:
        tag = f"[{g['status']}]"
        lines.append(f"{tag:<10} {g['gate']}")
        lines.append(f"           {g['detail']}")
        if g.get("fact_id"):
            lines.append(f"           source: prompt-grammar.csv {g['fact_id']}")
        lines.append("")
    lines.append(f"VERDICT {report['verdict']['status']}: {report['verdict']['summary']}")
    return "\n".join(lines)


def list_families() -> str:
    facts = load_facts()
    lines = [f"{'FAMILY':<25} {'NEGATIVE FIELD':<19} {'WINDOW':<12} "
             f"{'TEXT BUDGET':<13} SEED"]
    for f in FAMILIES:
        window = str(f.token_window) if f.token_window else (
            f"{f.prompt_char_limit} chars" if f.prompt_char_limit else "unpublished")
        budget = f"{f.text_char_limit} chars" if f.text_char_limit else "unpublished"
        seed = f.seed or "unpublished"
        lines.append(f"{f.name:<25} {f.negative_prompt:<19} {window:<12} {budget:<13} {seed}")
    cited = sorted({fid for f in FAMILIES for fid in f.facts()})
    lines.append("")
    lines.append(f"{len(cited)} of {len(facts)} rows in prompt-grammar.csv are cited by a gate. "
                 f"The rest are corrections and policy rows read by prompt-grammar.md.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--provider")
    parser.add_argument("--in-image-text", action="store_true",
                        help="the asset needs rendered text, even if the prompt does not say so")
    parser.add_argument("--recurring-person", action="store_true")
    parser.add_argument("--needs-reproducible", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output")
    parser.add_argument("--list-families", action="store_true")
    args = parser.parse_args()

    if args.list_families:
        print(list_families())
        return 0
    if not args.provider:
        parser.error("--provider is required")
    if args.prompt_file:
        prompt = pathlib.Path(args.prompt_file).read_text(encoding="utf-8")
    elif args.prompt:
        prompt = args.prompt
    elif args.recurring_person or args.needs_reproducible:
        # Asking only about mechanisms is a legitimate question, and answering it does
        # not need a prompt.
        prompt = ""
    else:
        parser.error("supply --prompt or --prompt-file, or ask about a mechanism with "
                     "--recurring-person / --needs-reproducible")

    try:
        report = build(prompt, args.provider, args.in_image_text, args.recurring_person,
                       args.needs_reproducible)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    content = json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" \
        else as_text(report)
    if args.output:
        pathlib.Path(args.output).write_text(content + "\n", encoding="utf-8")
    else:
        print(content)
    return {"passed": 0, "failed": 2, "review": 3, "skipped": 3}[report["verdict"]["status"]]


if __name__ == "__main__":
    from _emit import run_gate
    run_gate(main)
