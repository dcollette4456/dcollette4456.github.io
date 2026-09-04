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
the part a fresh model context needs to do blind. This script does the
mechanical prep: fetch each cited source fresh, save each one to its
own isolated file, split any claim citing more than one source into
lettered sub-claims (one source per grading call -- a merged claim's
gate vector isn't known to be identical across its sources until it's
been checked, so it can't be graded as one unit), and package each
sub-claim into a self-contained handoff/ folder: a filled-in grading
prompt, the classification spec, the draft template, and that one
source's files. Nothing else goes in the folder.

The published grade goes to a separate ANSWER_KEY.json, not into any
handoff folder -- a grader that can see the answer while filling in
gate questions is transcribing the test, not running it.

Needs real internet access -- run this on your machine, not in a
sandboxed session.

Usage:
  python3 scripts/prepare_regrade_test.py --serial TI-20260817-001 \\
      --spec-file /path/to/Classification_System_v4-1_Spec.md

Writes to data/regrade_test/{serial}/:
  sources/{REF}.txt            normalized text of that source, alone
  sources/{REF}.meta.json      url, source_id, fetch info, hash-vs-manifest comparison
  ANSWER_KEY.json              claim_id -> published tag -- for the comparison step only, not for handoff
  handoff/{claim_id}/          one self-contained folder per grading call:
    prompt.md                    the grading prompt, filled in
    Classification_System_v4-1_Spec.md   copied in if --spec-file was given
    {claim_id}.draft.json         the template to fill in
    {REF}.txt, {REF}.meta.json    that sub-claim's one source, and only that one
"""
import argparse
import hashlib
import json
import re
import shutil
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

# Descriptors are hand-vetted per issue: each one has to name the subject
# of an assertion without stating what the source concluded about it, and
# that judgment call can't be automated. This table is TI-20260817-001's,
# checked against the article and the raw sources before use. A claim with
# no entry here gets text: null and a loud warning instead of a guess.
DESCRIPTORS = {
    "TI-20260817-001": {
        "C001": "the QuickFox client's trojanized Electron build and the loader staging behavior that followed",
        "C002a": "what the vendor states about its own attribution confidence for this campaign",
        "C002b": "this outlet's reporting on the campaign's attribution, and whether it added independent analysis beyond the vendor report",
        "C003": "FDMTP observed in customer environments and the polling behavior of the domains it contacted",
        "C004": "exploitation of the N-central authentication bypass and the post-access activity observed",
        "C005": "the catalog entry for this vulnerability and its date",
        "C006a": "what this outlet reports about the actor attribution and the newly observed encryptor, and where it says this information originated",
        "C006b": "what this outlet reports about the actor attribution and the newly observed encryptor, and where it says this information originated",
    },
}

PROMPT_TEMPLATE = """# Grading prompt: {serial} re-grade test, claim {claim_id}

You are grading one claim against one source document, under the published
rule in the classification specification provided with this message.

## What you have

- The classification specification (`{spec_filename}`). This is the rule.
  Apply it as written.
- One claim draft file, `{claim_id}.draft.json`, with most fields set to null.
- One source document, `{ref}.txt`, and its metadata, `{ref}.meta.json`.

The claim under grading is: **{descriptor}**

That descriptor exists only to tell you which assertion in the source
document you are grading. It is not evidence, it is not a finding, and it
carries no conclusion you should adopt. Everything you answer comes from
the source document.

## What you do

Fill in every null field in the draft, honestly, from the source document
alone. Apply the gates in the order the specification states, first match
wins. Where the document does not support an answer, leave the field null.
A null is a correct answer when the document is silent. A guess is not.

Copy `sha256_normalized` from `{ref}.meta.json` into the draft's
`document_sha256_normalized` field, and copy `fetched` into `time.fetched`.
Fill `grader.model` with your own model identifier and `grader.run` with
the current UTC timestamp -- both are you identifying yourself, not a
judgment call.

Work the gates before you form any view of what the source is worth. If you
find yourself deciding the grade first and then answering the gate
questions to reach it, stop and start the gates over.

Return the completed draft as JSON, plus a short note stating which gate
produced the grade cap and why. Do not compute the grade digit, the gate
vector, the fingerprint, or the assertion license. Those are computed
downstream from your answers and a hand-computed one can drift from the
published arithmetic. Do not include the `_instructions` or
`_read_only_these_files` fields in your returned JSON; they are scaffolding
for this exercise, not part of the ledger record.

## What you must not do

- Do not search the web, and do not use anything you already know about
  this actor, campaign, vendor, or vulnerability from outside the provided
  document. If a fact is not in the document, it is not available to you.
  Your training data has read years of reporting on most of these subjects
  and none of it is evidence here.
- Do not ask for other source documents, other claim drafts, the published
  article, or any answer key. If any of those appear, say so and stop
  rather than reading them.
- Do not reason about what the other claims in this issue might say, or
  about whether your answer is consistent with them. Consistency across
  claims is not your problem and is not a property this grade is allowed
  to depend on.
- Do not adjust an answer because the resulting grade seems too high, too
  low, or surprising. A surprising grade is a result.

## One thing to check and record

`{ref}.meta.json` carries a `hash_vs_original_manifest` field. If it reads
`CHANGED_SINCE_ORIGINAL_CAPTURE`, the document in front of you is not
exactly the one originally cited. Grade what you have, and state in your
note that the document changed and whether the change touched anything
your answers depended on.

## Record your conditions

Add this block to the draft before returning it:

```json
"gate_evaluation": {{
  "isolation": "single_source_single_claim",
  "sources_in_context": ["{ref}"],
  "assertions_graded_in_this_call": 1,
  "topic_framing_present": false,
  "specification_version_read": "4.1"
}}
```

Set `topic_framing_present` to true, honestly, if anything in this prompt
or in the descriptor told you what the source concluded rather than what
it is about.
"""


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
    """Returns a list of {claim_id, tag, corroborated, cite_refs (ints)}."""
    claims = []
    for attrs_str, body in CLAIM_BLOCK_RE.findall(article_text):
        attrs = dict(ATTR_RE.findall(attrs_str))
        cite_refs = sorted({int(n) for n in CITE_RE.findall(body)})
        claims.append({
            "claim_id": attrs.get("claim", f"C{len(claims) + 1:03d}"),
            "tag": attrs.get("tag"),
            "corroborated": attrs.get("corroborated"),
            "cite_refs": cite_refs,
        })
    return claims


def split_claims(claims):
    """A claim citing N sources becomes N lettered sub-claims, one source
    each, in ascending REF order -- 'a' is always the lowest REF number."""
    out = []
    for c in claims:
        if len(c["cite_refs"]) <= 1:
            out.append({**c, "sub_id": c["claim_id"], "ref_n": c["cite_refs"][0] if c["cite_refs"] else None})
            continue
        for letter, ref_n in zip("abcdefgh", c["cite_refs"]):
            out.append({**c, "sub_id": f"{c['claim_id']}{letter}", "ref_n": ref_n})
    return out


def make_draft(serial, sub_id, ref, source_id, descriptor):
    return {
        "_instructions": (
            "Read ONLY the file(s) named in _read_only_these_files. Do not open any other "
            "file, do not open the published article, do not open other claim drafts. "
            "Answer every null field honestly from that document alone. Leave a field null "
            "if the document does not support an answer, rather than guessing."
        ),
        "_read_only_these_files": [f"{ref}.txt", f"{ref}.meta.json"],
        "serial": serial,
        "claim_id_from_published_article": sub_id,
        "text": descriptor,
        "source_id": source_id,
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--serial", required=True)
    p.add_argument("--out", default=None, help="Output directory. Default data/regrade_test/{serial}/")
    p.add_argument("--spec-file", default=None, help="Path to the classification spec markdown to copy into each handoff folder.")
    args = p.parse_args()

    serial = args.serial
    out_dir = Path(args.out) if args.out else ROOT / "data" / "regrade_test" / serial
    sources_dir = out_dir / "sources"
    handoff_dir = out_dir / "handoff"
    sources_dir.mkdir(parents=True, exist_ok=True)
    handoff_dir.mkdir(parents=True, exist_ok=True)

    spec_path = Path(args.spec_file) if args.spec_file else None
    if spec_path and not spec_path.exists():
        sys.exit(f"error: --spec-file {spec_path} does not exist")
    if not spec_path:
        print("WARNING: no --spec-file given. Handoff folders will not include the classification "
              "spec; you'll need to add it to each one by hand before sending.", file=sys.stderr)

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

    sub_claims = split_claims(claims)
    descriptors = DESCRIPTORS.get(serial, {})
    answer_key = {}
    missing_descriptors = []

    for sc in sub_claims:
        ref = f"REF-{sc['ref_n']:03d}" if sc["ref_n"] else None
        source_id = ref_meta.get(sc["ref_n"], {}).get("source_id") if sc["ref_n"] else None
        descriptor = descriptors.get(sc["sub_id"])
        if descriptor is None:
            missing_descriptors.append(sc["sub_id"])
            descriptor = None

        bundle_dir = handoff_dir / sc["sub_id"]
        bundle_dir.mkdir(parents=True, exist_ok=True)

        draft = make_draft(serial, sc["sub_id"], ref, source_id, descriptor)
        (bundle_dir / f"{sc['sub_id']}.draft.json").write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")

        if ref and (sources_dir / f"{ref}.txt").exists():
            shutil.copy(sources_dir / f"{ref}.txt", bundle_dir / f"{ref}.txt")
        if ref and (sources_dir / f"{ref}.meta.json").exists():
            shutil.copy(sources_dir / f"{ref}.meta.json", bundle_dir / f"{ref}.meta.json")

        spec_filename = spec_path.name if spec_path else "Classification_System_v4-1_Spec.md"
        if spec_path:
            shutil.copy(spec_path, bundle_dir / spec_path.name)

        prompt = PROMPT_TEMPLATE.format(
            serial=serial, claim_id=sc["sub_id"], ref=ref,
            descriptor=descriptor or "MISSING DESCRIPTOR -- fill in before sending, see script output",
            spec_filename=spec_filename,
        )
        (bundle_dir / "prompt.md").write_text(prompt, encoding="utf-8")

        answer_key[sc["sub_id"]] = {
            "parent_claim": sc["claim_id"],
            "published_tag": sc["tag"],
            "published_corroborated": sc.get("corroborated"),
            "ref": ref,
            "source_id": source_id,
        }

    (out_dir / "ANSWER_KEY.json").write_text(json.dumps(answer_key, indent=2) + "\n", encoding="utf-8")

    print(f"\nwrote {len(sub_claims)} handoff bundle(s) to {handoff_dir.relative_to(ROOT)}")
    for sc in sub_claims:
        print(f"  handoff/{sc['sub_id']}/  (source REF-{sc['ref_n']:03d})" if sc["ref_n"] else f"  handoff/{sc['sub_id']}/  (NO SOURCE)")
    print(f"answer key (do not open yet): {(out_dir / 'ANSWER_KEY.json').relative_to(ROOT)}")
    if missing_descriptors:
        print(f"\nWARNING: no vetted descriptor for {missing_descriptors} -- "
              f"those prompt.md files say so in place of a descriptor. Add entries to the "
              f"DESCRIPTORS table in this script and re-run before sending.", file=sys.stderr)
    print("\nEach handoff/{sub_claim}/ folder is self-contained: upload its contents to a "
          "brand-new conversation, one folder per conversation, none of them the same "
          "conversation as any other folder or as the one that wrote the article.")


if __name__ == "__main__":
    main()
