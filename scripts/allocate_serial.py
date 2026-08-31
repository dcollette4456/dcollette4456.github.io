#!/usr/bin/env python3
"""
Allocate the next serial for a given date and append it to data/serials.json.

This is the fix for the serial collision described in CLAUDECODEBRIEF §4:
two issues authored in parallel each hand-constructed a serial and had no
way to see the other. Authors call this instead of writing a serial by
hand. Per classification spec §15, sequence assignment happens at commit
time, which is when this command should be run -- not earlier, while a
draft is still being written, since another issue could be assigned the
same date-sequence in between.

Usage:
  python3 scripts/allocate_serial.py --date 2026-09-01 \
      --title "Some Issue Title" \
      --path /issues/some-slug/ \
      [--prefix TI] [--issue-number 41] \
      [--classification-version 4.1] [--article-spec-version 2.8] \
      [--authoring hand] [--status assigned]

Prints the allocated serial to stdout and nothing else, so it is safe to
capture with $(...) in another script.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEDGER = ROOT / "data" / "serials.json"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", required=True, help="YYYYMMDD or YYYY-MM-DD, the publication date this serial is keyed on")
    p.add_argument("--prefix", default="TI", choices=["TI", "IW"], help="Product line prefix. Default TI.")
    p.add_argument("--title", required=True)
    p.add_argument("--path", required=True, help="Site-relative path, e.g. /issues/some-slug/")
    p.add_argument("--issue-number", type=int, default=None)
    p.add_argument("--classification-version", default=None)
    p.add_argument("--article-spec-version", default=None)
    p.add_argument("--authoring", default="hand", choices=["hand", "pipeline"])
    p.add_argument("--status", default="assigned", choices=["assigned", "draft", "published", "withdrawn"])
    args = p.parse_args()

    date_digits = args.date.replace("-", "")
    if len(date_digits) != 8 or not date_digits.isdigit():
        p.error(f"--date must be YYYYMMDD or YYYY-MM-DD, got {args.date!r}")

    with open(LEDGER, encoding="utf-8") as f:
        ledger = json.load(f)

    existing_for_date = [
        e for e in ledger["serials"]
        if e["serial"].startswith(f"{args.prefix}-{date_digits}-")
    ]
    next_seq = len(existing_for_date) + 1
    serial = f"{args.prefix}-{date_digits}-{next_seq:03d}"

    if any(e["serial"] == serial for e in ledger["serials"]):
        print(f"error: {serial} already exists in the ledger; refusing to allocate a duplicate", file=sys.stderr)
        sys.exit(1)

    entry = {
        "serial": serial,
        "assigned": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "title": args.title,
        "path": args.path,
        "authoring": args.authoring,
        "status": args.status,
    }
    if args.issue_number is not None:
        entry["issue_number"] = args.issue_number
    if args.classification_version:
        entry["classification_version"] = args.classification_version
    if args.article_spec_version:
        entry["article_spec_version"] = args.article_spec_version

    ledger["serials"].append(entry)

    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
        f.write("\n")

    print(serial)


if __name__ == "__main__":
    main()
