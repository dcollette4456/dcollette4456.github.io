"""
Shared helpers for reading data/citations/{serial}.json and for the
domain-normalization / impersonation-check logic the source registry
builder and the (retired) one-time backfill both need.

Adding an issue now means adding one data/citations/{serial}.json file;
nothing here hand-appends to a growing list. scripts/build_registry.py
and scripts/capture_evidence.py both import load_all_citations() so the
two stay looking at exactly the same input.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
CITATIONS_DIR = ROOT / "data" / "citations"


def canonical_domain(url):
    netloc = urlparse(url).netloc.lower()
    return re.sub(r"^www\.", "", netloc)


def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]


def impersonation_check(domain, existing_domains):
    """Near-match: small edit distance, or same registrable name differing
    only by TLD or a hyphen. Classification spec §21."""
    hits = []
    stem = re.sub(r"\.(com|net|org|io|ai|dev|co|media|news)$", "", domain)
    for other in existing_domains:
        if other == domain:
            continue
        other_stem = re.sub(r"\.(com|net|org|io|ai|dev|co|media|news)$", "", other)
        dist = levenshtein(domain, other)
        if dist <= 2 or stem.replace("-", "") == other_stem.replace("-", ""):
            hits.append(other)
    return hits


def load_all_citations(citations_dir=None):
    """Returns a list of (url, canonical_name, type, origin, serial) tuples,
    the same shape the old hardcoded CITATIONS list carried, read from every
    data/citations/*.json file. Files are read in sorted (serial) order for
    determinism; within a file, citation order is preserved exactly as
    written, since that order is what assigns REF numbers per issue.
    """
    d = Path(citations_dir) if citations_dir else CITATIONS_DIR
    out = []
    for path in sorted(d.glob("*.json")):
        serial = path.stem
        entries = json.loads(path.read_text(encoding="utf-8"))
        for e in entries:
            out.append((e["url"], e["canonical_name"], e["type"], e.get("origin"), serial))
    return out


def load_citations_for_issue(serial, citations_dir=None):
    """Returns the raw list of citation dicts for one issue, in file order."""
    d = Path(citations_dir) if citations_dir else CITATIONS_DIR
    path = d / f"{serial}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
