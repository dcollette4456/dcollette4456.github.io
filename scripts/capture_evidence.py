#!/usr/bin/env python3
"""
Evidence capture, step 4 of CLAUDECODEBRIEF ledger-and-evidence.md.

Incremental: for each URL cited in data/citations/{serial}.json, if
data/evidence/{serial}.manifest.json already has a captured entry for
that exact URL, it is left untouched -- not re-fetched, not re-hashed,
not re-timestamped. Only URLs with no prior entry are fetched. This
matters for two reasons: a full re-fetch of ~100 URLs on every run is
slow and hammers the same handful of servers repeatedly for no reason,
and worse, re-fetching a URL weeks after it was first cited can hash a
*different* version of the page than the one actually cited, silently
overwriting the original attestation with today's, dated as if it were
still the original capture. Once a URL has an entry, that entry is the
record, unless you deliberately ask to refresh it with --refresh.

Attestation (the two hashes) always happens for a newly-fetched URL.
Preservation (the archive copy) is attempted but its failure never
blocks an entry -- per brief §7.1, always do attestation, attempt
preservation, never let a failure of the second block the first.
Archive.org is rate-limited and fails often; --retry-archive re-attempts
*only* the archive submission for entries that don't have a captured
copy yet, without re-fetching or re-hashing content that's already
attested.

capture_is_retrospective stays a manifest-level flag, set true on every
write, same as before: this product has no live-capture-at-publication
pipeline yet, so any entry it writes was fetched after the fact,
whether that happened the same run as another entry in the file or not.
Per brief §9: "A document fetched today is not the document as it was
when cited... A manifest that implies capture at publication time
would be a false claim about the product's own process."

Usage:
  python3 scripts/capture_evidence.py                  # only new URLs
  python3 scripts/capture_evidence.py --only TI-...     # scope to one issue
  python3 scripts/capture_evidence.py --refresh URL...  # force re-fetch specific URLs
  python3 scripts/capture_evidence.py --retry-archive   # retry failed archive.org submissions only
  python3 scripts/capture_evidence.py --dry-run         # report what would happen, no network, no writes

Network-heavy and slow the first time an issue's URLs are captured;
near-instant on repeat runs once everything already has an entry.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from citations import load_all_citations, canonical_domain  # noqa: E402
from html_normalize import normalize_html  # noqa: E402

UA = "Mozilla/5.0 (compatible; KnightsWhoSayNi-EvidenceCapture/1.0; +https://dcollette4456.github.io/)"
FETCH_TIMEOUT = 15
ARCHIVE_TIMEOUT = 25
ARCHIVE_DELAY_SECONDS = 2
MAX_BODY_BYTES = 8 * 1024 * 1024


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            body = resp.read(MAX_BODY_BYTES)
            return {
                "ok": True,
                "http_status": resp.status,
                "content_type": resp.headers.get("Content-Type", "").split(";")[0].strip() or None,
                "body": body,
            }
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read(MAX_BODY_BYTES)
        except Exception:
            pass
        return {"ok": True, "http_status": e.code, "content_type": None, "body": body}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def submit_archive(url):
    save_url = f"https://web.archive.org/save/{url}"
    req = urllib.request.Request(save_url, headers={"User-Agent": UA})
    attempted = now_iso()
    try:
        with urllib.request.urlopen(req, timeout=ARCHIVE_TIMEOUT) as resp:
            loc = resp.headers.get("Content-Location")
            if loc:
                return {"status": "captured", "provider": "web.archive.org",
                        "url": f"https://web.archive.org{loc}", "attempted": attempted}
            final_url = resp.geturl()
            if "web.archive.org/web/" in final_url:
                return {"status": "captured", "provider": "web.archive.org",
                        "url": final_url, "attempted": attempted}
            return {"status": "failed", "provider": "web.archive.org", "attempted": attempted,
                    "note": "no snapshot location returned"}
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {"status": "failed", "provider": "web.archive.org", "attempted": attempted,
                    "note": "rate limited (429)"}
        return {"status": "failed", "provider": "web.archive.org", "attempted": attempted,
                "note": f"HTTP {e.code}"}
    except Exception as e:
        return {"status": "failed", "provider": "web.archive.org", "attempted": attempted,
                "note": f"{type(e).__name__}: {e}"}


def manifest_hash(entries):
    canonical = json.dumps(entries, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_fresh_entry(source_id, ref, url, fetch_cache, archive_cache):
    """Fetch (if not already in this run's cache), hash, and attempt
    archive submission for a URL with no prior manifest entry."""
    if url not in fetch_cache:
        print(f"    fetching {url}", file=sys.stderr)
        fetch_cache[url] = fetch(url)
    result = fetch_cache[url]

    entry = {
        "source_id": source_id,
        "ref": ref,
        "url": url,
        "format_family": "html",
        "preservation": "archive_only",
    }

    if not result["ok"]:
        entry["notes"] = f"fetch failed: {result['error']}"
        entry["preservation"] = "none"
        if url not in archive_cache:
            time.sleep(ARCHIVE_DELAY_SECONDS)
            print(f"    submitting to archive.org (local fetch failed)", file=sys.stderr)
            archive_cache[url] = submit_archive(url)
        entry["archive"] = archive_cache[url]
        return entry

    body = result["body"]
    sha_raw = hashlib.sha256(body).hexdigest()
    normalized = normalize_html(body)
    sha_norm = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    entry.update({
        "fetched": now_iso(),
        "http_status": result["http_status"],
        "content_type": result["content_type"],
        "content_length": len(body),
        "sha256_raw": sha_raw,
        "sha256_normalized": sha_norm,
        "normalizer": "html/v1",
        "extractor": None,
        "version_identity": {"kind": "normalized_hash", "value": sha_norm},
    })

    if url not in archive_cache:
        time.sleep(ARCHIVE_DELAY_SECONDS)
        print(f"    submitting to archive.org", file=sys.stderr)
        archive_cache[url] = submit_archive(url)
    entry["archive"] = archive_cache[url]
    if archive_cache[url]["status"] != "captured":
        entry["preservation"] = "none"
    if not (result["http_status"] and 200 <= result["http_status"] < 300):
        entry["notes"] = f"http_status {result['http_status']}; local fetch was not 2xx, archive.org was still tried"

    return entry


def retry_archive_only(prior_entry, archive_cache):
    """Re-attempt archive.org for an entry that already has content
    attested but no successful archive copy. Never re-fetches content."""
    url = prior_entry["url"]
    if url not in archive_cache:
        time.sleep(ARCHIVE_DELAY_SECONDS)
        print(f"    retrying archive.org for {url}", file=sys.stderr)
        archive_cache[url] = submit_archive(url)
    entry = dict(prior_entry)
    entry["archive"] = archive_cache[url]
    if archive_cache[url]["status"] == "captured":
        entry["preservation"] = "archive_only"
    return entry


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only", default=None, help="Scope to one issue serial instead of every citations file.")
    p.add_argument("--refresh", nargs="*", default=[], metavar="URL",
                   help="Force re-fetch and re-hash these specific URLs even if already captured.")
    p.add_argument("--retry-archive", action="store_true",
                   help="Re-attempt archive.org submission for entries with no successful archive copy yet, without re-fetching content.")
    p.add_argument("--dry-run", action="store_true", help="Report what would be fetched/retried; no network calls, no writes.")
    args = p.parse_args()
    refresh_set = set(args.refresh)

    registry_path = ROOT / "data" / "sources" / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source_id_by_key = {(e["canonical_domain"], e["canonical_name"]): e["source_id"] for e in registry}

    by_issue = {}
    for url, name, type_, origin, serial in load_all_citations():
        if args.only and serial != args.only:
            continue
        by_issue.setdefault(serial, []).append((url, name))

    fetch_cache = {}
    archive_cache = {}
    evidence_dir = ROOT / "data" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    new_fetches = 0
    archive_retries = 0
    issues_written = 0
    issues_skipped = 0

    for serial, cites in sorted(by_issue.items()):
        manifest_path = evidence_dir / f"{serial}.manifest.json"
        existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
        existing_by_url = {e["url"]: e for e in existing["entries"]} if existing else {}

        entries = []
        changed = False

        for i, (url, name) in enumerate(cites, start=1):
            ref = f"REF-{i:03d}"
            domain = canonical_domain(url)
            source_id = source_id_by_key.get((domain, name))
            if source_id is None:
                print(f"WARNING: no registry source_id for ({domain!r}, {name!r}); skipping {url}. "
                      f"Run scripts/build_registry.py first.", file=sys.stderr)
                continue

            prior = existing_by_url.get(url)
            needs_fetch = prior is None or url in refresh_set
            needs_archive_retry = (
                not needs_fetch and args.retry_archive and prior is not None
                and prior.get("archive", {}).get("status") != "captured"
                and "sha256_raw" in prior  # only retry archive for content we actually attested
            )

            if not needs_fetch and not needs_archive_retry:
                entry = dict(prior)
                entry["ref"] = ref
                entry["source_id"] = source_id
                entries.append(entry)
                continue

            changed = True
            if args.dry_run:
                action = "fetch (new)" if prior is None else ("refresh" if url in refresh_set else "retry-archive")
                print(f"[dry-run] {serial} {ref}: would {action} {url}")
                entry = dict(prior) if prior else {"source_id": source_id, "ref": ref, "url": url}
                entries.append(entry)
                continue

            if needs_fetch:
                new_fetches += 1
                print(f"[{new_fetches}] {serial} {ref}: fetching {url}", file=sys.stderr)
                entry = build_fresh_entry(source_id, ref, url, fetch_cache, archive_cache)
            else:
                archive_retries += 1
                entry = retry_archive_only(prior, archive_cache)
                entry["ref"] = ref
                entry["source_id"] = source_id
            entries.append(entry)

        if not changed:
            issues_skipped += 1
            print(f"{serial}: no new or changed citations, left untouched ({len(entries)} entries)")
            continue

        if args.dry_run:
            continue

        manifest = {
            "schema_version": 1,
            "serial": serial,
            "generated": now_iso(),
            "capture_is_retrospective": True,
            "entries": entries,
        }
        manifest["manifest_sha256"] = manifest_hash(entries)
        manifest["timestamp"] = existing["timestamp"] if existing else {"status": "not_yet_anchored"}

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        issues_written += 1
        print(f"wrote {manifest_path.relative_to(ROOT)} ({len(entries)} entries, hash {manifest['manifest_sha256'][:12]}...)")

    if args.dry_run:
        print(f"\n[dry-run] done. no network calls made, no files written.")
        return

    captured = sum(1 for r in archive_cache.values() if r["status"] == "captured")
    failed = sum(1 for r in archive_cache.values() if r["status"] != "captured")
    fetch_failed = sum(1 for r in fetch_cache.values() if not r["ok"])
    print(f"\ndone. {issues_written} manifest(s) written, {issues_skipped} unchanged and left alone. "
          f"{len(fetch_cache)} new URL(s) fetched ({fetch_failed} fetch failures), "
          f"{archive_retries} archive-only retries, {captured} archived, {failed} archive attempts failed.")


if __name__ == "__main__":
    main()
