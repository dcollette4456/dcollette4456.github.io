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
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from jsonschema_mini import validate, SchemaError
from frontmatter_mini import read_front_matter_scalars
from citations import load_all_citations
from build_registry import compute_registry

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


def validate_citations():
    schema_path = DATA / "schema" / "citations-1.json"
    citations_dir = DATA / "citations"
    if not citations_dir.exists():
        return
    schema = load_json(schema_path)

    for path in sorted(citations_dir.glob("*.json")):
        rel = str(path.relative_to(ROOT))
        serial = path.stem
        if not re.match(r"^(TI|IW)-(RETRO-[0-9]{3}|[0-9]{8}-[0-9]{3})$", serial):
            fail(rel, "$", f"filename {serial!r} is not a valid issue serial", "data/schema/citations-1.json")
            continue

        entries = load_json(path)
        try:
            validate(entries, schema)
        except SchemaError as e:
            fail(rel, e.path, e.message, "data/schema/citations-1.json")
            continue

        check_empty_strings(entries, rel)

        seen_urls = {}
        for i, c in enumerate(entries):
            url = c["url"]
            if url in seen_urls:
                fail(rel, f"$[{i}].url", f"duplicate URL within one citations file (also at index {seen_urls[url]})",
                     "scripts/capture_evidence.py assigns one REF number per citation position")
            seen_urls[url] = i


def check_registry_matches_citations(existing_registry):
    """Catches the drift this whole file-split exists to prevent: a
    citations file edited (or added) without re-running
    scripts/build_registry.py and committing the result. Recomputes the
    registry from the same inputs build_registry.py would use and
    compares keys/cited_in against what's actually on disk."""
    rel = str((DATA / "sources" / "registry.json").relative_to(ROOT))
    if not isinstance(existing_registry, list):
        return

    computed, _held, _dropped = compute_registry(existing_registry, load_all_citations(), now="1970-01-01T00:00:00Z")
    existing_by_key = {(e["canonical_domain"], e["canonical_name"]): e for e in existing_registry}
    computed_by_key = {(e["canonical_domain"], e["canonical_name"]): e for e in computed}

    missing = sorted(k[1] for k in computed_by_key.keys() - existing_by_key.keys())
    if missing:
        fail(rel, "$", f"{len(missing)} source(s) from data/citations/ are missing from the registry -- "
             f"run `python3 scripts/build_registry.py` and commit the result: {missing}",
             "scripts/build_registry.py")

    for key, existing_entry in existing_by_key.items():
        computed_entry = computed_by_key.get(key)
        if computed_entry is None:
            continue  # no citations file references this source anymore; registry correctly kept it
        if existing_entry.get("cited_in") != computed_entry.get("cited_in"):
            fail(rel, f"[{existing_entry.get('source_id')}].cited_in",
                 f"stale for {existing_entry['canonical_name']!r} -- "
                 f"run `python3 scripts/build_registry.py` and commit the result",
                 "scripts/build_registry.py")


def validate_registry():
    schema_path = DATA / "schema" / "registry-2.json"
    registry_path = DATA / "sources" / "registry.json"
    rel = str(registry_path.relative_to(ROOT))

    schema = load_json(schema_path)
    registry = load_json(registry_path)

    if not isinstance(registry, list):
        fail(rel, "$", "registry must be a JSON array of source entries", "CLAUDECODEBRIEF §5")
        return None

    seen_ids = {}
    domains_by_id = {}
    for i, entry in enumerate(registry):
        path = f"$[{i}]"
        try:
            validate(entry, schema)
        except SchemaError as e:
            fail(rel, f"{path}.{e.path.lstrip('$.')}" if e.path != "$" else path, e.message,
                 "CLAUDECODEBRIEF §5 / schema/registry-2.json")
            continue

        check_empty_strings(entry, rel, path)

        sid = entry["source_id"]
        if sid in seen_ids:
            fail(rel, f"{path}.source_id", f"duplicate source_id {sid!r} (also at index {seen_ids[sid]})",
                 "classification spec §12: source_id is stable and never re-keyed")
        seen_ids[sid] = i
        domains_by_id[sid] = entry["canonical_domain"]

        # brief §8 item 8: a registry entry with no admission record
        if "admission" not in entry:
            fail(rel, path, "registry entry has no admission record", "CLAUDECODEBRIEF §8 item 8 / classification spec §21")

    return {e["canonical_domain"]: e["source_id"] for e in registry if "canonical_domain" in e}


def check_published_issue_sources_are_registered(registry_by_domain):
    if registry_by_domain is None:
        return

    for md_path in sorted(CONTENT_ISSUES.glob("*.md")):
        rel = str(md_path.relative_to(ROOT))
        text = md_path.read_text(encoding="utf-8")
        fm = read_front_matter_scalars(text)
        if fm.get("draft") is True:
            continue

        m = re.search(r'\n## References\n(.*?)(\n## |\Z)', text, re.DOTALL)
        if not m:
            continue
        refs_block = m.group(1)
        # References are cited either as full https:// URLs or, in a couple
        # of markdown-list issues, as a bare domain-led path (MLA-ish
        # citation style with no scheme). Catch both.
        urls = re.findall(r'https?://[^\s")>\]]+', refs_block)
        bare = re.findall(
            r'(?<![\w/.-])(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|io|ai|dev|media|news|co\.uk|co\.kr|or\.kr)/[^\s,."<>)]*',
            refs_block,
        )
        for url in urls:
            domain = re.sub(r'^www\.', '', urlparse(url).netloc.lower())
            if domain not in registry_by_domain:
                fail(rel, "References", f"cited domain {domain!r} ({url}) has no registry entry",
                     "CLAUDECODEBRIEF §9 / classification spec §21")
        for raw in bare:
            domain = re.sub(r'^www\.', '', raw.split("/")[0].lower())
            if domain not in registry_by_domain:
                fail(rel, "References", f"cited domain {domain!r} ({raw}) has no registry entry",
                     "CLAUDECODEBRIEF §9 / classification spec §21")


def validate_ledgers(registry_source_ids):
    schema = load_json(DATA / "schema" / "ledger-5.json")
    ledger_dir = DATA / "ledger"
    known_claim_ids = {}  # serial -> set of claim_id

    for ledger_path in sorted(ledger_dir.glob("*.json")):
        rel = str(ledger_path.relative_to(ROOT))
        claims = load_json(ledger_path)

        try:
            validate(claims, schema)
        except SchemaError as e:
            fail(rel, e.path, e.message, "classification spec §15 / schema/ledger-5.json")
            continue

        check_empty_strings(claims, rel)

        seen_ids = set()
        for i, claim in enumerate(claims):
            path = f"$[{i}]"
            cid = claim.get("claim_id")
            if cid in seen_ids:
                fail(rel, f"{path}.claim_id", f"duplicate claim_id {cid!r} within one ledger file",
                     "classification spec §2 / §6 duplicate block")
            seen_ids.add(cid)

            # brief §8 item 7, extended from manifests to ledger claims
            sid = claim.get("source_id")
            if registry_source_ids is not None and sid not in registry_source_ids:
                fail(rel, f"{path}.source_id", f"{sid!r} has no registry entry",
                     "CLAUDECODEBRIEF §8 item 7 / classification spec §21")

            # brief §8 item 9: archive: not_attempted is a block; unavailable is legal
            archive = claim.get("archive")
            if archive and archive.get("status") == "not_attempted":
                fail(rel, f"{path}.archive.status", "archive status is 'not_attempted'; the pipeline must always try",
                     "CLAUDECODEBRIEF §8 item 9 / classification spec §14")

            # brief §8 item 5: a relay claim (grade 4 or 5) with no relay_depth
            if claim.get("grade") in (4, 5) and claim.get("relay_depth") is None:
                fail(rel, f"{path}.relay_depth", "relay-grade claim (4 or 5) carries no relay_depth",
                     "CLAUDECODEBRIEF §8 item 5 / classification spec §5")

            # brief §8 item 10: a negative-polarity claim published with no stated scope
            if claim.get("polarity") == "negative" and not claim.get("scope") and claim.get("grade") != 6:
                fail(rel, f"{path}", "negative-polarity claim has no stated scope but was not graded 6",
                     "CLAUDECODEBRIEF §8 item 10 / classification spec §29")

        known_claim_ids[ledger_path.stem] = seen_ids

    return known_claim_ids


def check_data_claim_attributes_resolve(known_claim_ids):
    """brief §8 item 3: a data-claim attribute resolving to no ledger entry."""
    for md_path in sorted(CONTENT_ISSUES.glob("*.md")):
        rel = str(md_path.relative_to(ROOT))
        text = md_path.read_text(encoding="utf-8")
        fm = read_front_matter_scalars(text)
        serial = fm.get("serial") or fm.get("reportSerial")

        for m in re.finditer(r'data-claim="([^"]+)"', text):
            ref = m.group(1)
            claim_id = ref.split("|")[0] if "|" in ref else ref
            issue_serial = claim_id.rsplit("-C", 1)[0] if "-C" in claim_id else serial
            ids = known_claim_ids.get(issue_serial, set())
            if claim_id not in ids:
                fail(rel, "data-claim", f"{ref!r} resolves to no ledger entry (no /data/ledger/{issue_serial}.json claim {claim_id})",
                     "CLAUDECODEBRIEF §8 item 3 / classification spec §15")


def validate_manifests(registry_source_ids):
    schema = load_json(DATA / "schema" / "manifest-1.json")
    evidence_dir = DATA / "evidence"
    if not evidence_dir.is_dir():
        return

    for manifest_path in sorted(evidence_dir.glob("*.manifest.json")):
        rel = str(manifest_path.relative_to(ROOT))
        manifest = load_json(manifest_path)

        try:
            validate(manifest, schema)
        except SchemaError as e:
            fail(rel, e.path, e.message, "CLAUDECODEBRIEF §7.2 / schema/manifest-1.json")
            continue

        check_empty_strings(manifest, rel)

        recomputed = manifest_recompute_hash(manifest["entries"])
        if recomputed != manifest["manifest_sha256"]:
            fail(rel, "$.manifest_sha256", "does not match a recomputed hash of $.entries",
                 "CLAUDECODEBRIEF §7.2")

        for i, entry in enumerate(manifest["entries"]):
            path = f"$.entries[{i}]"
            sid = entry.get("source_id")
            if registry_source_ids is not None and sid not in registry_source_ids:
                fail(rel, f"{path}.source_id", f"{sid!r} has no registry entry",
                     "CLAUDECODEBRIEF §8 item 7 / classification spec §21")

            archive = entry.get("archive")
            if archive and archive.get("status") == "not_attempted":
                fail(rel, f"{path}.archive.status", "archive status is 'not_attempted'; the pipeline must always try",
                     "CLAUDECODEBRIEF §8 item 9 / classification spec §14")


def manifest_recompute_hash(entries):
    import hashlib
    canonical = json.dumps(entries, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main():
    ledger_by_serial = validate_serials_ledger()
    check_published_issues_have_serials(ledger_by_serial)

    validate_citations()
    check_registry_matches_citations(load_json(DATA / "sources" / "registry.json"))

    registry_by_domain = validate_registry()
    check_published_issue_sources_are_registered(registry_by_domain)

    registry = load_json(DATA / "sources" / "registry.json")
    registry_source_ids = {e["source_id"] for e in registry} if isinstance(registry, list) else None
    known_claim_ids = validate_ledgers(registry_source_ids)
    check_data_claim_attributes_resolve(known_claim_ids)

    validate_manifests(registry_source_ids)

    if errors:
        print(f"data validation FAILED with {len(errors)} error(s):\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    print("data validation passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
