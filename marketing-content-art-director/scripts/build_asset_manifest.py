#!/usr/bin/env python3
"""Build an asset manifest from a campaign brief."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


CHANNELS = {
    "meta": [("feed", "4:5"), ("story-reel", "9:16"), ("proof-carousel", "1:1")],
    "tiktok": [("native-hook", "9:16"), ("proof-cutdown", "9:16")],
    "google": [("modular-square", "1:1"), ("landscape", "1.91:1"), ("portrait", "4:5")],
    "linkedin": [("single-image", "1:1"), ("document-carousel", "1:1"), ("link-visual", "1.91:1")],
    "pinterest": [("discovery-pin", "2:3"), ("idea-video", "9:16")],
    "web": [("desktop-hero", "wide"), ("mobile-hero", "9:16"), ("proof-image", "4:3")],
}


def normalize_channels(record: dict, override: list[str] | None) -> list[str]:
    values = override or record.get("channels") or ["meta", "tiktok", "web"]
    expanded = [item for group in values for item in str(group).split(",") if item]
    unknown = [item for item in expanded if item not in CHANNELS]
    if unknown:
        raise ValueError(f"Unknown channel(s): {', '.join(unknown)}")
    return list(dict.fromkeys(expanded))


def build_manifest(record: dict, channels: list[str]) -> list[dict]:
    campaign = str(record.get("campaign_id") or record.get("project") or "campaign").lower().replace(" ", "-")
    lanes = record.get("selected_lanes") or ["clear", "signature", "departure"]
    rows = []
    counter = 1
    for lane in lanes:
        for channel in channels:
            for asset_type, ratio in CHANNELS[channel]:
                rows.append(
                    {
                        "asset_id": f"ASSET-{counter:03d}",
                        "campaign": campaign,
                        "lane": lane,
                        "channel": channel,
                        "asset_type": asset_type,
                        "ratio": ratio,
                        "funnel_stage": "TBD",
                        "hypothesis": "TBD",
                        "hook": "TBD",
                        "proof": "TBD",
                        "cta": "TBD",
                        "owner": "TBD",
                        "status": "planned",
                        "filename": f"{campaign}-{lane}-{channel}-{asset_type}-{ratio.replace(':', 'x')}-v01",
                    }
                )
                counter += 1
    return rows


def to_csv(rows: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()) if rows else [])
    if rows:
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a channel asset manifest.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--channels", nargs="+")
    parser.add_argument("--format", choices=("csv", "json"), default="csv")
    parser.add_argument("--output")
    args = parser.parse_args()
    record = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = build_manifest(record, normalize_channels(record, args.channels))
    content = json.dumps(rows, indent=2, ensure_ascii=True) + "\n" if args.format == "json" else to_csv(rows)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()

