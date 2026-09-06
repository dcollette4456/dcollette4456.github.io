#!/usr/bin/env python3
"""
Extract a data/citations/{serial}.json file from a draft article.

First mechanical step of the draft-to-ledger pipeline (see
docs/specs/Automation_Pipeline_Scope.md). A draft handed to Claude Code
already has its sources cited -- this script pulls url, name, and REF
order out of the draft's own References section rather than requiring
anyone to retype them, so evidence capture and grading have something
to run against.

Two citation formats are read, because both already exist in this repo:

  1. Hugo shortcode: {{< src title="[REF-NNN] Title" url="..." ... >}}
     (e.g. content/issues/prc-trusted-channel-compromise.md)
  2. Raw HTML list: <li id="ref-NNN">...<a href="URL">...</a>...</li>
     (e.g. content/issues/sonicwall-lenovo-id-authentication-bypass.md)

What this script does NOT do: assign `type` (classification spec §3) or
write `type_basis` for a domain the registry has never seen before.
Classification spec §21 (v4.2 amendment E) made `type` author-supplied
on purpose -- it is a judgment call about what the publisher is, made by
reading the publisher's self-description, and this script has not read
anything. Where a cited domain already exists in data/sources/registry.json,
its established type and type_basis are reused (the judgment was already
made once; asking again would just add a chance to disagree with the
existing record). Where a domain is new, the entry is written with
type/type_basis left as the string "NEEDS_TYPE" and the script's summary
lists every one, so whoever runs this (a person, or Claude Code in the
authoring session) reads the publisher's own self-description and fills
those two fields in before evidence capture runs. This is the same
admission judgment classification spec §21 has always required; this
script only removes the retyping.

Usage:
  python3 scripts/extract_citations_from_draft.py <draft.md> --serial TI-YYYYMMDD-NNN
  python3 scripts/extract_citations_from_draft.py <draft.md> --serial TI-YYYYMMDD-NNN --dry-run
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from citations import canonical_domain  # noqa: E402

SRC_SHORTCODE_RE = re.compile(
    r'\{\{<\s*src\s+([^>]*?)\s*>\}\}', re.DOTALL
)
ATTR_RE = re.compile(r'(\w+)="((?:[^"\\]|\\.)*)"')
REF_IN_TITLE_RE = re.compile(r'\[REF-(\d+)\]\s*(.*)')

LI_REF_RE = re.compile(
    r'<li\s+id="ref-(\d+)"[^>]*>(.*?)</li>', re.DOTALL | re.IGNORECASE
)
HREF_RE = re.compile(r'<a\s+href="(https?://[^"]+)"[^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
TAG_STRIP_RE = re.compile(r'<[^>]+>')


def parse_shortcode_attrs(attr_text):
    return {m.group(1): m.group(2) for m in ATTR_RE.finditer(attr_text)}


def extract_shortcode_refs(text):
    """{{< src title="[REF-NNN] Name" byline="..." url="..." >}}"""
    out = []
    for m in SRC_SHORTCODE_RE.finditer(text):
        attrs = parse_shortcode_attrs(m.group(1))
        url = attrs.get("url")
        title = attrs.get("title", "")
        if not url:
            continue
        ref_match = REF_IN_TITLE_RE.match(title)
        if ref_match:
            ref_num = int(ref_match.group(1))
            name_hint = ref_match.group(2).strip()
        else:
            ref_num = None
            name_hint = title.strip()
        out.append({"ref_num": ref_num, "url": url, "name_hint": name_hint})
    return out


def extract_html_refs(text):
    """<li id="ref-NNN">...<a href="URL">domain</a>...</li>"""
    out = []
    for m in LI_REF_RE.finditer(text):
        ref_num = int(m.group(1))
        body = m.group(2)
        href_match = HREF_RE.search(body)
        if not href_match:
            continue
        url = href_match.group(1)
        # Name hint: the text before the <a> tag, stripped of markup, e.g.
        # 'SonicWall PSIRT. "SNWLID-2026-0016." 1 September 2026. '
        before_link = body[:href_match.start()]
        name_hint = TAG_STRIP_RE.sub("", before_link).strip(' .')
        name_hint = re.sub(r'^\[REF-\d+\]\s*', '', name_hint).strip(' .') or None
        out.append({"ref_num": ref_num, "url": url, "name_hint": name_hint})
    return out


def guess_canonical_name(name_hint, domain):
    """A byline like 'SonicWall PSIRT. "SNWLID-2026-0016." 1 September 2026'
    is not a publisher name -- it's the whole citation. Take the leading
    clause up to the first period as the best guess; fall back to the
    bare domain if that leaves nothing usable. This is a guess, not an
    admission judgment -- it only picks the string that goes in
    canonical_name, never the type."""
    if name_hint:
        first_clause = name_hint.split(".")[0].strip()
        if first_clause and len(first_clause) < 80:
            return first_clause
    return domain


def build_citations(refs, registry_by_domain):
    """refs: list of {ref_num, url, name_hint}. Returns (citations_list,
    needs_type_list), ordered ascending by ref_num where the draft gave
    one explicitly.

    This order is not cosmetic: citations.py's load order IS the REF
    numbering downstream (capture_evidence.py assigns REF-{i:03d} from
    array position), and the draft's own {{< cite N >}} markers and
    src-shortcode [REF-NNN] titles reference those same explicit numbers.
    Writing this file in raw document-appearance order rather than
    ascending ref_num silently reassigns every REF number the moment they
    don't already match -- caught by testing this against a real article
    whose References section isn't itself in REF order. A ref with no
    parsed number (the HTML <li id="ref-NNN"> form always has one; a
    malformed shortcode might not) sorts after every numbered one, in the
    order it was found.

    registry_by_domain is domain -> list of registry entries (a domain can
    carry more than one registered source, e.g. cisa.gov hosts both "CISA
    Cybersecurity Advisories" and the "CISA Known Exploited Vulnerabilities
    (KEV) Catalog" as separate registered sources). A single candidate on
    the domain resolves the way it always did. Multiple candidates cannot
    be resolved by domain alone -- silently picking one would misattribute
    the citation to the wrong existing source's type and history -- so the
    guessed name is matched case-insensitively against the candidates'
    canonical_name, and where that still doesn't land on exactly one match,
    the citation is left NEEDS_TYPE with the candidates listed, the same
    admission judgment this script already asks a human to make for a
    genuinely new domain."""
    ordered = sorted(enumerate(refs), key=lambda pair: (pair[1]["ref_num"] is None, pair[1]["ref_num"] or 0, pair[0]))
    citations = []
    needs_type = []
    seen_urls = set()
    for _, r in ordered:
        url = r["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        domain = canonical_domain(url)
        candidates = registry_by_domain.get(domain, [])
        registry_entry = None
        ambiguous_candidates = None
        if len(candidates) == 1:
            registry_entry = candidates[0]
        elif len(candidates) > 1:
            guessed = guess_canonical_name(r["name_hint"], domain).lower()
            matches = [c for c in candidates if c["canonical_name"].lower() == guessed]
            if len(matches) == 1:
                registry_entry = matches[0]
            else:
                ambiguous_candidates = [c["canonical_name"] for c in candidates]

        if registry_entry:
            entry = {
                "url": url,
                "canonical_name": registry_entry["canonical_name"],
                "type": registry_entry["type"],
            }
            basis = registry_entry.get("admission", {}).get("type_basis")
            if basis:
                entry["type_basis"] = basis
            if registry_entry.get("origin"):
                entry["origin"] = registry_entry["origin"]
        else:
            name = guess_canonical_name(r["name_hint"], domain)
            entry = {
                "url": url,
                "canonical_name": name,
                "type": "NEEDS_TYPE",
            }
            needs_type_entry = {"url": url, "domain": domain, "canonical_name": name}
            if ambiguous_candidates:
                needs_type_entry["ambiguous_with_existing"] = ambiguous_candidates
            needs_type.append(needs_type_entry)
        citations.append(entry)
    return citations, needs_type


def load_registry_by_domain():
    """domain -> list of registry entries. A list, not a single entry,
    because a domain is not a unique key into the registry -- see
    build_citations()'s docstring for why (cisa.gov is the real example
    already in this registry)."""
    registry_path = ROOT / "data" / "sources" / "registry.json"
    if not registry_path.exists():
        return {}
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    by_domain = {}
    for e in registry:
        by_domain.setdefault(e["canonical_domain"], []).append(e)
    return by_domain


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("draft", help="Path to the draft article (markdown or HTML)")
    p.add_argument("--serial", required=True, help="TI-YYYYMMDD-NNN, from scripts/allocate_serial.py")
    p.add_argument("--dry-run", action="store_true", help="Print what would be written; don't write the file")
    args = p.parse_args()

    draft_path = Path(args.draft)
    text = draft_path.read_text(encoding="utf-8")

    refs = extract_shortcode_refs(text) + extract_html_refs(text)
    if not refs:
        print("No citations found. Expected {{< src ... url=\"...\" >}} shortcodes or "
              "<li id=\"ref-NNN\">...<a href=\"URL\">...</a></li> references.", file=sys.stderr)
        sys.exit(1)

    registry_by_domain = load_registry_by_domain()
    citations, needs_type = build_citations(refs, registry_by_domain)

    out_path = ROOT / "data" / "citations" / f"{args.serial}.json"
    if args.dry_run:
        print(json.dumps(citations, indent=2, ensure_ascii=False))
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(citations, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {out_path.relative_to(ROOT)} ({len(citations)} citation(s))")

    if needs_type:
        print(f"\n{len(needs_type)} citation(s) are for domains not already in the registry and need a "
              f"type + type_basis before evidence capture / grading runs. Classification spec §21: read "
              f"what the publisher says about itself and assign from {{GOV, VND, MED, ACA, TEC, IND, NPO, "
              f"AGG, SOC, ADV, ANL}} -- do not guess from the domain name alone.", file=sys.stderr)
        for n in needs_type:
            print(f"  NEEDS_TYPE  {n['domain']:40s} {n['canonical_name']!r:40s} {n['url']}", file=sys.stderr)
            if n.get("ambiguous_with_existing"):
                print(f"      this domain already has {len(n['ambiguous_with_existing'])} other registered "
                      f"source(s) and the guessed name didn't match any of them: {n['ambiguous_with_existing']}. "
                      f"Confirm by hand whether this is one of those sources (fix canonical_name to match "
                      f"exactly) or a genuinely new source at this domain.", file=sys.stderr)


if __name__ == "__main__":
    main()
