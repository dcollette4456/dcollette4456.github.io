#!/usr/bin/env python3
"""
Turn a draft's existing {{< claim >}} tags into the task list an isolated
grading pass consumes: one entry per claim-source pair, source resolved
to a source_id via data/citations/{serial}.json and the registry.

This is classification spec §30 stage 3, assertion reduction, and it is
scoped narrowly on purpose. It does NOT invent claim boundaries. A
{{< claim tag="..." claim="Cxxx" >}}...{{< /claim >}} block is what this
script segments; deciding where those boundaries belong -- which
sentences are one assertion, which are two -- is the judgment §2's
composite-claim rule is about, and mechanizing it would be the amendment
A failure mode with extra steps: a script confidently declaring assertion
boundaries it did not actually reason about. If the draft handed to
Claude Code has no claim tags yet, that tagging is a authoring judgment
to make first (by hand, or by Claude Code reading the draft), not
something this script guesses at.

What this script does mechanize, because it's arithmetic rather than
judgment: a claim tag citing more than one source is split into lettered
sub-claims, one source each, in ascending REF order (classification spec
§2's composite-claim rule, same logic prepare_regrade_test.py already
uses for the regrade pipeline). A claim's own body text becomes the
descriptor handed to its isolated grading call. That body text is the
draft author's prose, not a hand-vetted neutral pointer -- there is no
mechanical way to strip characterization out of prose without risking
stripping the assertion along with it -- so gate_evaluation.topic_framing_present
is written true for every segment by default rather than asserting a
neutrality this script did not verify. A person or Claude Code reviewing
the segment list before grading runs can override it per segment where
the text genuinely is a bare pointer.

Usage:
  python3 scripts/segment_draft.py <draft.md> --serial TI-YYYYMMDD-NNN

Requires data/citations/{serial}.json to exist already (run
extract_citations_from_draft.py first) and data/sources/registry.json to
have a source_id for each cited domain (run build_registry.py after
extraction, before this).

Writes data/claim_segments/{serial}.json:
  [{sub_id, claim_id, tag, corroborated, ref, url, source_id, source_type,
    assertion_text, gate_evaluation_stub}, ...]

data/claim_segments/ is gitignored. It's a task list for the grading pass,
not an evidentiary record -- the retained artifact is the claim draft
each segment turns into once grading actually happens (classification
spec §15A), same reasoning that keeps the visual queue out of the repo.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from citations import canonical_domain  # noqa: E402
from prepare_regrade_test import CLAIM_BLOCK_RE, ATTR_RE, CITE_RE, split_claims  # noqa: E402

CITE_STRIP_RE = re.compile(r'\{\{<\s*cite\s+\d+\s*>\}\}')
SHORTCODE_STRIP_RE = re.compile(r'\{\{[<%].*?[%>]\}\}', re.DOTALL)
TAG_STRIP_RE = re.compile(r'<[^>]+>')


def parse_claims_with_body(article_text):
    """Like prepare_regrade_test.parse_claims, but keeps the claim body
    text (needed here as the descriptor; the regrade tool didn't need it
    because it used hand-vetted descriptors instead)."""
    claims = []
    for attrs_str, body in CLAIM_BLOCK_RE.findall(article_text):
        attrs = dict(ATTR_RE.findall(attrs_str))
        cite_refs = sorted({int(n) for n in CITE_RE.findall(body)})
        claims.append({
            "claim_id": attrs.get("claim", f"C{len(claims) + 1:03d}"),
            "tag": attrs.get("tag"),
            "corroborated": attrs.get("corroborated"),
            "cite_refs": cite_refs,
            "body": body,
        })
    return claims


def clean_body_text(body):
    text = CITE_STRIP_RE.sub("", body)
    text = SHORTCODE_STRIP_RE.sub("", text)
    text = TAG_STRIP_RE.sub("", text)
    return re.sub(r'\s+', ' ', text).strip()


def load_citations_ordered(serial):
    path = ROOT / "data" / "citations" / f"{serial}.json"
    if not path.exists():
        sys.exit(f"error: {path.relative_to(ROOT)} does not exist. Run "
                  f"extract_citations_from_draft.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry_by_domain_and_name():
    """Keyed by (canonical_domain, canonical_name), matching the key
    build_registry.py itself uses. Domain alone is not a unique key into
    the registry -- cisa.gov, for one real example already in this
    registry, carries both "CISA Cybersecurity Advisories" and the "CISA
    Known Exploited Vulnerabilities (KEV) Catalog" as separate registered
    sources. A citation's own canonical_name (already an admission
    judgment made in data/citations/{serial}.json by this point) is what
    disambiguates which one a given citation resolves to."""
    path = ROOT / "data" / "sources" / "registry.json"
    if not path.exists():
        return {}
    return {(e["canonical_domain"], e["canonical_name"]): e
            for e in json.loads(path.read_text(encoding="utf-8"))}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("draft", help="Path to the draft article")
    p.add_argument("--serial", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    text = Path(args.draft).read_text(encoding="utf-8")
    claims = parse_claims_with_body(text)
    if not claims:
        sys.exit("error: no {{< claim >}} blocks found. Segmentation (which assertion is which) "
                  "is a judgment call this script does not make -- tag the draft's claims first.")

    citations = load_citations_ordered(args.serial)
    # REF-NNN assignment is list order, 1-indexed, per citations.py's own
    # docstring -- same rule capture_evidence.py uses when it writes the
    # evidence manifest, so REF numbers here will match REF numbers there.
    ref_to_citation = {i: c for i, c in enumerate(citations, start=1)}
    registry_by_domain_and_name = load_registry_by_domain_and_name()

    split = split_claims(claims)
    segments = []
    unresolved = []
    for c in split:
        ref_n = c["ref_n"]
        citation = ref_to_citation.get(ref_n)
        if citation is None:
            unresolved.append(c["sub_id"])
            continue
        domain = canonical_domain(citation["url"])
        registry_entry = registry_by_domain_and_name.get((domain, citation["canonical_name"]))
        source_id = registry_entry["source_id"] if registry_entry else None
        if source_id is None:
            unresolved.append(c["sub_id"])
        segments.append({
            "sub_id": c["sub_id"],
            "claim_id": c["claim_id"],
            "tag": c["tag"],
            "corroborated": c["corroborated"],
            "ref": f"REF-{ref_n:03d}" if ref_n else None,
            "url": citation["url"],
            "source_id": source_id,
            # Admission fact (classification spec §21), not a grading
            # judgment -- carried through from citations.json rather than
            # left for the isolated grader to re-derive from the document.
            "source_type": citation["type"],
            "assertion_text": clean_body_text(c["body"]),
            "gate_evaluation_stub": {
                "isolation": "single_source_single_claim",
                "sources_in_context": [f"REF-{ref_n:03d}"] if ref_n else [],
                "assertions_graded_in_this_call": 1,
                "topic_framing_present": True,
            },
        })

    out_path = ROOT / "data" / "claim_segments" / f"{args.serial}.json"
    if args.dry_run:
        print(json.dumps(segments, indent=2, ensure_ascii=False))
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {out_path.relative_to(ROOT)} ({len(segments)} segment(s))")

    if unresolved:
        print(f"\n{len(unresolved)} segment(s) could not resolve a source_id -- either the cited REF "
              f"number has no matching citations entry, or that domain has no registry entry yet "
              f"(run build_registry.py after extraction): {', '.join(unresolved)}", file=sys.stderr)


if __name__ == "__main__":
    main()
