#!/usr/bin/env python3
"""
Prepare an isolated re-grade test kit for one already-published issue.

Built for the specific experiment discussed against the v4.2/v2.9 change
request: re-grade TI-20260817-001's claims from scratch, one source at a
time with no cross-source context, and compare the result against the
grades that actually shipped. That comparison is the cheapest real test
of two things at once -- whether claim_writer.py's arithmetic reproduces
a human-judged grade, and whether isolated per-source reading is even
practical to carry out.

What this script does NOT do: it does not grade anything. Grading is a
judgment call over each isolated source document, and that is exactly
the part a fresh model context needs to do blind. This script only
does the mechanical prep: fetch each cited source fresh, save each one
to its own isolated file so nothing sees more than one source at a
time, extract the claim text and existing citation mapping from the
published article, and emit one blank draft template per claim for a
grader to fill in -- with the published grade held back in a separate
answer key so filling in the template isn't just transcribing what's
already known.

Needs real internet access -- run this on your machine, not in a
sandboxed session. Mirrors capture_evidence.py's fetch logic exactly,
but writes isolated per-source files instead of one shared manifest,
because the point here is that nothing reading source A can see
source B's file at all.

Usage:
  python3 scripts/prepare_regrade_test.py --serial TI-20260817-001

Writes to data/regrade_test/{serial}/:
  sources/{REF}.txt          normalized text of that source, alone
  sources/{REF}.meta.json    url, source_id, fetch info, hash-vs-manifest comparison
  claims/{claim_id}.draft.json   blank template: text, source(s), null judgment fields
  ANSWER_KEY.json            claim_id -> published tag/grade -- for the comparison step only
  README.md                 the isolation protocol, plain language, for whoever grades these
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from html_normalize import normalize_html  # noqa: E402

UA = "Mozilla/5.0 (compatible; KnightsWhoSayNi-RegradeTest/1.0; +https://dcollette4456.github.io/)"
FETCH_TIMEOUT = 15
MAX_BODY_BYTES = 8 * 1024 * 1024

CLAIM_BLOCK_RE = re.compile(
    r'\{\{<\s*claim\s+([^>]*?)>\}\}(.*?)\{\{<\s*/claim\s*>\}\}',
    re.DOTALL,
)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
CITE_RE = re.compile(r'\{\{<\s*cite\s+(\d+)\s*>\}\}')


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            body = resp.read(MAX_BODY_BYTES)
            return {"ok": True, "http_status": resp.status,
                    "content_type": resp.headers.get("Content-Type", "").split(";")[0].strip() or None,
                    "body": body}
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read(MAX_BODY_BYTES)
        except Exception:
            pass
        return {"ok": True, "http_status": e.code, "content_type": None, "body": body}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def find_article(serial):
    ledger = json.loads((ROOT / "data" / "serials.json").read_text(encoding="utf-8"))
    entry = next((e for e in ledger["serials"] if e["serial"] == serial), None)
    if entry is None:
        sys.exit(f"error: {serial} not found in data/serials.json")
    slug = entry["path"].strip("/").split("/")[-1]
    matches = list((ROOT / "content" / "issues").glob(f"*{slug}*.md"))
    if not matches:
        sys.exit(f"error: no content file matching slug {slug!r} for {serial}")
    return matches[0]


def parse_claims(article_text):
    """Returns a list of {claim_id, tag, corroborated, cite_refs (ints), text}."""
    claims = []
    for attrs_str, body in CLAIM_BLOCK_RE.findall(article_text):
        attrs = dict(ATTR_RE.findall(attrs_str))
        cite_refs = sorted({int(n) for n in CITE_RE.findall(body)})
        text = CITE_RE.sub("", body).strip()
        text = re.sub(r"\s+", " ", text)
        claims.append({
            "claim_id": attrs.get("claim", f"C{len(claims) + 1:03d}"),
            "tag": attrs.get("tag"),
            "corroborated": attrs.get("corroborated"),
            "cite_refs": cite_refs,
            "text": text,
        })
    return claims


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--serial", required=True)
    p.add_argument("--out", default=None, help="Output directory. Default data/regrade_test/{serial}/")
    args = p.parse_args()

    serial = args.serial
    out_dir = Path(args.out) if args.out else ROOT / "data" / "regrade_test" / serial
    sources_dir = out_dir / "sources"
    claims_dir = out_dir / "claims"
    sources_dir.mkdir(parents=True, exist_ok=True)
    claims_dir.mkdir(parents=True, exist_ok=True)

    citations = json.loads((ROOT / "data" / "citations" / f"{serial}.json").read_text(encoding="utf-8"))
    manifest_path = ROOT / "data" / "evidence" / f"{serial}.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    manifest_by_ref = {e["ref"]: e for e in manifest["entries"]} if manifest else {}

    article_path = find_article(serial)
    article_text = article_path.read_text(encoding="utf-8")
    claims = parse_claims(article_text)
    if not claims:
        sys.exit(f"error: found zero {{{{< claim >}}}} blocks in {article_path}. "
                 f"Does this issue use the newer <div class=\"claim\"> markup instead? "
                 f"This script only parses the shortcode style.")

    # fetch each cited source exactly once, save it isolated
    ref_meta = {}
    for i, cite in enumerate(citations, start=1):
        ref = f"REF-{i:03d}"
        print(f"[{i}/{len(citations)}] fetching {cite['url']}", file=sys.stderr)
        result = fetch(cite["url"])
        meta = {
            "ref": ref,
            "url": cite["url"],
            "canonical_name": cite["canonical_name"],
            "type": cite["type"],
            "origin": cite.get("origin"),
            "fetched": now_iso(),
        }
        if manifest_by_ref.get(ref):
            meta["source_id"] = manifest_by_ref[ref]["source_id"]

        if not result["ok"]:
            meta["fetch_error"] = result["error"]
            (sources_dir / f"{ref}.meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            print(f"    FAILED: {result['error']}", file=sys.stderr)
            ref_meta[i] = meta
            continue

        body = result["body"]
        normalized = normalize_html(body)
        sha_raw = hashlib.sha256(body).hexdigest()
        sha_norm = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        meta.update({
            "http_status": result["http_status"],
            "content_type": result["content_type"],
            "sha256_raw": sha_raw,
            "sha256_normalized": sha_norm,
        })

        prior = manifest_by_ref.get(ref)
        if prior and prior.get("sha256_normalized"):
            meta["hash_vs_original_manifest"] = "match" if prior["sha256_normalized"] == sha_norm else "CHANGED_SINCE_ORIGINAL_CAPTURE"
        else:
            meta["hash_vs_original_manifest"] = "no_prior_manifest_entry"

        (sources_dir / f"{ref}.txt").write_text(normalized, encoding="utf-8")
        (sources_dir / f"{ref}.meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        ref_meta[i] = meta
        print(f"    ok, {meta['hash_vs_original_manifest']}", file=sys.stderr)

    # emit blank claim drafts + the separate answer key
    answer_key = {}
    for c in claims:
        refs = [f"REF-{n:03d}" for n in c["cite_refs"]]
        source_ids = sorted({ref_meta[n].get("source_id") for n in c["cite_refs"] if ref_meta.get(n, {}).get("source_id")})

        draft = {
            "_instructions": (
                "Read ONLY the file(s) named in _read_only_these_files. Do not open any other "
                "file in sources/, do not open the published article, do not open other claim "
                "drafts in this directory. Answer every null field honestly from that document "
                "alone. Leave a field null if the document does not support an answer, rather "
                "than guessing."
            ),
            "_read_only_these_files": [f"sources/{r}.txt" for r in refs],
            "serial": serial,
            "claim_id_from_published_article": c["claim_id"],
            "text": c["text"],
            "source_id": source_ids[0] if len(source_ids) == 1 else source_ids,
            "source_type": None,
            "gates": {
                "origin_identified": None, "primary_reachable": None, "document_retrieved": None,
                "gated": None, "own_observation": None, "named_primary": None, "relay_depth": None,
                "self_interested_only": None, "aggregate": None,
                "artifact_test": None, "method_test": None, "hedge_test": None,
            },
            "evidentiary_status": None,
            "polarity": None,
            "volatility": None,
            "scope": None,
            "document_sha256_normalized": None,
            "origin_named": None,
            "time": {"observed_period": None, "source_published": None, "fetched": None},
            "grader": {"model": None, "spec_version": None, "schema_version": 4,
                       "normalizer": "html/v1", "run": None, "passes": 1, "agreement": "single_pass"},
            "segmentation": {"atomic_assertions": None, "merged": None, "merge_basis": None, "assertions": []},
            "hunt_value": {"behavioral": None, "behavioral_basis": None, "huntable": None,
                           "telemetry_classes": [], "collection_point_basis": None,
                           "collection_point_source": None, "indicator_bearing": None},
            "sectors": {"confirmed": [], "contextual": [], "justified_by": None},
            "actors": {"subject": [], "referenced": [], "names_used_by_source": [], "justified_by": None},
            "entities": {"clusters": [], "families": [], "tools": [], "campaigns": [], "vulnerabilities": [], "justified_by": None},
            "provenance": {"pool": None, "source_published": None, "window": None, "capture_is_retrospective": False},
        }
        (claims_dir / f"{c['claim_id']}.draft.json").write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")

        answer_key[c["claim_id"]] = {"published_tag": c["tag"], "published_corroborated": c.get("corroborated")}

    (out_dir / "ANSWER_KEY.json").write_text(json.dumps(answer_key, indent=2) + "\n", encoding="utf-8")

    readme = f"""# Re-grade test kit: {serial}

Do not open ANSWER_KEY.json until every claim draft in claims/ is filled in.
It holds the grade this issue actually published, and seeing it first
defeats the point of the test.

## Protocol

For each file in claims/*.draft.json:

1. Open ONLY the source file(s) listed in that draft's `_read_only_these_files`.
   Do not open any other file in sources/. Do not open the published article
   at {article_path.relative_to(ROOT)}. Do not open another claim's draft file.
2. Answer every `null` field in the draft honestly, from that document alone.
   Leave a field `null` rather than guessing if the document doesn't support
   an answer.
3. Save the file. Move to the next claim only after this one is done, and
   only open its own listed source file(s) -- not ones already read for a
   prior claim, even if it's the same file. Re-read it fresh each time
   rather than relying on memory of it from an earlier claim.

## After every draft is filled in

Hand the completed claims/*.draft.json files back. They'll be run through
scripts/claim_writer.py and the computed grades compared against
ANSWER_KEY.json. Where they diverge, that's the actual, useful result --
not a problem to explain away.

## What's in sources/

One `{{{{REF}}}}.txt` (normalized text) and one `{{{{REF}}}}.meta.json` per
cited source, fetched fresh just now. The meta file's `hash_vs_original_manifest`
field says whether this page has changed since it was originally cited --
`CHANGED_SINCE_ORIGINAL_CAPTURE` means the document you're reading now is not
exactly what was cited then, which is itself worth noting if it affects an answer.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"\nwrote {len(claims)} claim draft(s) to {claims_dir.relative_to(ROOT)}")
    print(f"wrote {len(citations)} source file(s) to {sources_dir.relative_to(ROOT)}")
    print(f"answer key (do not open yet): {(out_dir / 'ANSWER_KEY.json').relative_to(ROOT)}")
    print(f"protocol: {(out_dir / 'README.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
