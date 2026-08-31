"""
Normalizer family member html/v1. Classification spec §14.

Deliberately does not attempt true main-content region detection (the
spec allows using one "where the document declares one"); this is the
boilerplate-stripping fallback path, applied uniformly. Stated here
rather than left to be discovered, per the spec's own instinct in §23:
a normalizer that claimed to solve content detection perfectly would be
the more impressive docstring and the less true one. Expect some false
positives on revision detection (a dynamic block this misses) and some
false negatives (a real content change inside a stripped region, if any
ever were) -- both bounded by how much of the page nav/header/footer/aside
actually contain.
"""
import re

_STRIP_ENTIRE = re.compile(
    r'<(script|style|noscript|iframe|nav|header|footer|aside)\b[^>]*>.*?</\1>',
    re.IGNORECASE | re.DOTALL,
)
_COMMENTS = re.compile(r'<!--.*?-->', re.DOTALL)
_TAGS = re.compile(r'<[^>]+>')
_WS = re.compile(r'\s+')


def normalize_html(raw_bytes_or_str):
    text = raw_bytes_or_str
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")

    # Remove boilerplate regions and their content entirely. Loop because
    # nested/adjacent matches of the same tag can leave residue on one pass.
    prev = None
    while prev != text:
        prev = text
        text = _STRIP_ENTIRE.sub(" ", text)

    text = _COMMENTS.sub(" ", text)
    text = _TAGS.sub(" ", text)  # strip remaining tags, keep inner text
    text = _WS.sub(" ", text).strip()
    text = text.lower()
    return text
