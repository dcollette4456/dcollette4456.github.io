#!/usr/bin/env python3
"""
Build-time validator for the /data/ data layer. Per CLAUDECODEBRIEF §8.

Run with: python3 scripts/validate_data.py

Exits non-zero and prints every failure (file, path, and the spec
section it enforces) on any violation. Intended to run in CI before the
Hugo build, so a broken ledger or a duplicate serial fails the deploy
rather than shipping silently.

Currently checked (brief §8, items 1-2):
  1. data/serials.json validates against data/schema/serials-1.json
  2. No duplicate serial in the ledger
  3. Every published issue's front-matter serial resolves in the ledger
  4. Every ledger entry with status "published" has a matching content file
  5. No empty-string ("") value anywhere in a /data/*.json file -- absent
     is legal, empty is not (brief §8 item 4, classification spec §6)

Other numbered checks in brief §8 (claim/manifest/registry validation)
land as their own schemas and data files exist; this script is written
to grow, not to be replaced.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jsonschema_mini import validate, SchemaError
from frontmatter_mini import read_front_matter_scalars

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
CONTENT_ISSUES = ROOT / "content" / "issues"

errors = []


def fail(file, path, message, spec_ref):
    errors.append(f"{file}  [{path}]  {message}  ({spec_ref})")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_empty_strings(obj, file, path="$"):
    """brief §8 item 4: absent is legal, empty is not."""
    if isinstance(obj, str):
        if obj == "":
            fail(file, path, "empty string value", "CLAUDECODEBRIEF §8 item 4 / classification spec §6")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            check_empty_strings(v, file, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_empty_strings(v, file, f"{path}[{i}]")


def validate_serials_ledger():
    schema_path = DATA / "schema" / "serials-1.json"
    ledger_path = DATA / "serials.json"
    rel = str(ledger_path.relative_to(ROOT))

    schema = load_json(schema_path)
    ledger = load_json(ledger_path)

    try:
        validate(ledger, schema)
    except SchemaError as e:
        fail(rel, e.path, e.message, "CLAUDECODEBRIEF §4 / schema/serials-1.json")
        return None  # can't reason about a ledger that doesn't even match its shape

    check_empty_strings(ledger, rel)

    entries = ledger["serials"]

    # duplicate serial check
    seen = {}
    for i, entry in enumerate(entries):
        s = entry["serial"]
        if s in seen and "collision" not in entry and "collision" not in entries[seen[s]]:
            fail(rel, f"$.serials[{i}].serial", f"duplicate serial {s!r} (also at index {seen[s]}) with no collision recorded",
                 "CLAUDECODEBRIEF §4 item 2 / classification spec §15")
        seen.setdefault(s, i)

    # published entries must have a matching content file at their path
    for i, entry in enumerate(entries):
        if entry["status"] != "published":
            continue
        slug = entry["path"].strip("/").split("/")[-1]
        matches = list(CONTENT_ISSUES.glob(f"*{slug}*.md"))
        if not matches:
            fail(rel, f"$.serials[{i}]", f"status is 'published' but no content file found for path {entry['path']!r}",
                 "CLAUDECODEBRIEF §4 item 2")

    return {e["serial"]: e for e in entries}


def check_published_issues_have_serials(ledger_by_serial):
    if ledger_by_serial is None:
        return
    for md_path in sorted(CONTENT_ISSUES.glob("*.md")):
        rel = str(md_path.relative_to(ROOT))
        text = md_path.read_text(encoding="utf-8")
        fm = read_front_matter_scalars(text)

        if fm.get("draft") is True:
            continue  # unpublished, no serial owed

        serial = fm.get("serial") or fm.get("reportSerial")
        if not serial:
            fail(rel, "front matter", "published issue carries no 'serial' field",
                 "CLAUDECODEBRIEF §4 item 2")
            continue

        if serial not in ledger_by_serial:
            fail(rel, "front matter.serial", f"serial {serial!r} is not present in data/serials.json",
                 "CLAUDECODEBRIEF §4 item 2")


def main():
    ledger_by_serial = validate_serials_ledger()
    check_published_issues_have_serials(ledger_by_serial)

    if errors:
        print(f"data validation FAILED with {len(errors)} error(s):\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print("data validation passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
