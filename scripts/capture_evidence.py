#!/usr/bin/env python3
"""
Evidence capture, step 4 of CLAUDECODEBRIEF ledger-and-evidence.md.

Fetches every URL cited across the published issues' References sections
exactly once (cached by URL, since a handful of URLs are cited from more
than one issue), hashes the raw response and a normalized extraction,
attempts archive.org submission, and writes one evidence manifest per
issue to /data/evidence/{serial}.manifest.json.

Attestation (the two hashes) always happens. Preservation (the archive
copy) is attempted but its failure never blocks an entry -- per brief
§7.1, always do attestation, attempt preservation, never let a failure
of the second block the first.

This is a retrospective capture: every issue here was published before
this script existed, so `fetched` is today's date, not the issue's
original publication date, and every manifest sets
capture_is_retrospective: true and says so. Per brief §9: "A document
fetched today is not the document as it was when cited... A manifest
that implies capture at publication time would be a false claim about
the product's own process."

Run with: python3 scripts/capture_evidence.py
Network-heavy and slow by design (deliberate delay between archive.org
submissions to avoid hammering a free service). Safe to re-run: each
run recomputes manifests from a fresh fetch, it does not append.
"""
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from build_registry_backfill import CITATIONS, canonical_domain  # noqa: E402
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


def main():
    registry_path = ROOT / "data" / "sources" / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source_id_by_key = {(e["canonical_domain"], e["canonical_name"]): e["source_id"] for e in registry}

    # group citations by issue, preserving first-appearance order for REF numbering
    by_issue = {}
    for url, name, type_, origin, serial in CITATIONS:
        by_issue.setdefault(serial, []).append((url, name))

    fetch_cache = {}
    archive_cache = {}

    evidence_dir = ROOT / "data" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    total_urls = len({u for u, _n in [(c[0], c[1]) for c in CITATIONS]})
    done = 0

    for serial, cites in by_issue.items():
        entries = []
        for i, (url, name) in enumerate(cites, start=1):
            ref = f"REF-{i:03d}"
            domain = canonical_domain(url)
            source_id = source_id_by_key.get((domain, name))
            if source_id is None:
                print(f"WARNING: no registry source_id for ({domain!r}, {name!r}); skipping {url}", file=sys.stderr)
                continue

            if url not in fetch_cache:
                done += 1
                print(f"[{done}] fetching {url}", file=sys.stderr)
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
                entries.append(entry)
                continue

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

            if result["http_status"] and 200 <= result["http_status"] < 300:
                if url not in archive_cache:
                    time.sleep(ARCHIVE_DELAY_SECONDS)
                    print(f"    submitting to archive.org", file=sys.stderr)
                    archive_cache[url] = submit_archive(url)
                entry["archive"] = archive_cache[url]
                if archive_cache[url]["status"] != "captured":
                    entry["preservation"] = "none"
            else:
                entry["archive"] = {"status": "not_attempted", "attempted": now_iso()}
                entry["notes"] = f"http_status {result['http_status']}; archive submission skipped for a non-2xx fetch"
                entry["preservation"] = "none"

            entries.append(entry)

        manifest = {
            "schema_version": 1,
            "serial": serial,
            "generated": now_iso(),
            "capture_is_retrospective": True,
            "entries": entries,
        }
        manifest["manifest_sha256"] = manifest_hash(entries)
        manifest["timestamp"] = {"status": "not_yet_anchored"}

        out_path = evidence_dir / f"{serial}.manifest.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {out_path.relative_to(ROOT)} ({len(entries)} entries, hash {manifest['manifest_sha256'][:12]}...)")

    captured = sum(1 for r in archive_cache.values() if r["status"] == "captured")
    failed = sum(1 for r in archive_cache.values() if r["status"] != "captured")
    fetch_failed = sum(1 for r in fetch_cache.values() if not r["ok"])
    print(f"\ndone. {len(fetch_cache)} unique URLs fetched ({fetch_failed} fetch failures), "
          f"{captured} archived, {failed} archive attempts failed.")


if __name__ == "__main__":
    main()
