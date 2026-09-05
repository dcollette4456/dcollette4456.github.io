#!/usr/bin/env python3
"""
Rebuild data/sources/registry.json from every data/citations/{serial}.json
file. Per CLAUDECODEBRIEF §9: register + admission first, evidence capture
is a separate pass (scripts/capture_evidence.py).

Replaces the old scripts/build_registry_backfill.py, which carried a
hardcoded, hand-appended CITATIONS list -- adding an issue now means
adding one data/citations/{serial}.json file instead of editing a
growing script.

source_id is stable across runs: an already-registered (domain, name)
pair keeps the SRC-#### it was first assigned, in its original
admission order (so the impersonation check's registered-domains
history doesn't get reshuffled), by reading the registry.json already
on disk before rebuilding. Only genuinely new (domain, name) pairs get
a new SRC-#### appended at the end. Re-running with no new citations
reproduces the existing file unchanged (aside from `cited_in` picking
up any newly-added serials for an existing source). A source dropped
from every citations file is never deleted -- it stays in the registry
with whatever cited_in it last had, since registry history is a record,
not a cache.

`origin` is set only where the citation file says so -- see the
"never invent a value" rule in data/schema/citations-1.json and
CLAUDECODEBRIEF §9.

compute_registry() is the pure part (no I/O, no clock call baked in
implicitly -- `now` is a parameter) so scripts/validate_data.py can call
it and diff the result against what's on disk, to catch a citations
file that was edited without re-running this script.

Run with: python3 scripts/build_registry.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from citations import load_all_citations, impersonation_check, canonical_domain  # noqa: E402


def compute_registry(existing, citations, now):
    """existing: the registry list currently on disk (or []).
    citations: the (url, name, type, origin, serial, type_basis) tuples from
    load_all_citations(). now: an ISO timestamp string, used only for
    admission records on brand-new entries.
    Returns (registry_list, held_for_review, dropped_names)."""
    existing_by_key = {(e["canonical_domain"], e["canonical_name"]): e for e in existing}

    grouped = {}
    order_of_first_appearance = []
    for url, name, type_, origin, serial, type_basis in citations:
        key = (canonical_domain(url), name)
        if key not in grouped:
            grouped[key] = {
                "canonical_name": name,
                "canonical_domain": key[0],
                "type": type_,
                "origin": origin,
                "first_seen_url": url,
                "type_basis": type_basis,
                "cited_in": [],
            }
            order_of_first_appearance.append(key)
        entry = grouped[key]
        if serial not in entry["cited_in"]:
            entry["cited_in"].append(serial)

    existing_order = sorted(
        existing_by_key.keys(),
        key=lambda k: int(existing_by_key[k]["source_id"].split("-")[1]),
    )
    new_keys = [k for k in order_of_first_appearance if k not in existing_by_key]
    full_order = existing_order + new_keys

    dropped_names = [existing_by_key[k]["canonical_name"] for k in existing_by_key if k not in grouped]

    next_id = max((int(e["source_id"].split("-")[1]) for e in existing_by_key.values()), default=0) + 1

    registered_domains = []
    registry = []
    held_for_review = []

    for key in full_order:
        g = grouped.get(key)
        if g is None:
            registry.append(existing_by_key[key])
            registered_domains.append(key[0])
            continue

        if key in existing_by_key:
            source_id = existing_by_key[key]["source_id"]
        else:
            source_id = f"SRC-{next_id:04d}"
            next_id += 1

        near_matches = impersonation_check(g["canonical_domain"], registered_domains)
        registered_domains.append(g["canonical_domain"])

        if key in existing_by_key:
            entry = dict(existing_by_key[key])
            entry["cited_in"] = sorted(g["cited_in"])
            entry["backfill"] = dict(entry.get("backfill", {}))
            entry["backfill"]["from_issues"] = sorted(g["cited_in"])
            registry.append(entry)
            continue

        review_flag = "held_impersonation" if near_matches else "first_citation"
        impersonation_note = (
            f"near-match against {', '.join(near_matches)}: held for review"
            if near_matches else
            "no near-match against registry canonical domains"
        )
        if near_matches:
            held_for_review.append((source_id, g["canonical_name"], near_matches))

        entry = {
            "source_id": source_id,
            "canonical_name": g["canonical_name"],
            "canonical_domain": g["canonical_domain"],
            "type": g["type"],
            "language": "en",
            "synthetic": False,
            "cited_in": sorted(g["cited_in"]),
            "admission": {
                "first_seen_url": g["first_seen_url"],
                "admitted": now,
                "assigned_type": g["type"],
                "type_basis": g["type_basis"] or (
                    "no self-description recorded at citation; type assigned by the citing "
                    "author from the publisher's name and domain, not yet verified against a "
                    "fetched about/masthead page"
                ),
                "domain_age_days": None,
                "impersonation_check": impersonation_note,
                "review_flag": review_flag,
                "reviewed": False,
            },
            "live": {
                "unique_claims": 0,
                "citations": 0,
                "distribution": {},
                "record_status": "insufficient",
            },
            "backfill": {
                "unique_claims": 0,
                "citations": 0,
                "distribution": {},
                "record_status": "insufficient",
                "from_issues": sorted(g["cited_in"]),
            },
        }
        if g["origin"]:
            entry["origin"] = g["origin"]
        registry.append(entry)

    return registry, held_for_review, dropped_names


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    out_path = ROOT / "data" / "sources" / "registry.json"
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else []

    registry, held_for_review, dropped_names = compute_registry(existing, load_all_citations(), now)

    if dropped_names:
        print(f"NOTE: {len(dropped_names)} previously-registered source(s) have no citation file "
              f"referencing them anymore (left in place, not removed): {dropped_names}", file=sys.stderr)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")

    existing_count = len({(e["canonical_domain"], e["canonical_name"]) for e in existing})
    new_count = len(registry) - existing_count
    print(f"wrote {len(registry)} registry entries to {out_path.relative_to(ROOT)} "
          f"({new_count} new, {existing_count} carried over)")
    if held_for_review:
        print(f"\n{len(held_for_review)} entries HELD for impersonation review (publication block):")
        for source_id, name, matches in held_for_review:
            print(f"  - {source_id} {name!r} near-matches: {matches}")
    else:
        print("no entries held for impersonation review")


if __name__ == "__main__":
    main()
