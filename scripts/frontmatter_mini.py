"""
Minimal YAML front-matter scalar reader.

Pulls top-level `key: value` scalars out of a Hugo content file's front
matter. Does not parse nested structures (lists, maps) -- callers that
need those should not use this. Good enough for what the data-layer
validator needs to check: serial, draft, classification_version, title.
"""
import re


def read_front_matter_scalars(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    scalars = {}
    for line in block.splitlines():
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$', line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw == "" or raw.startswith("|") or raw.startswith(">"):
            continue  # block scalar or nested block follows; not a top-level scalar
        if (raw.startswith('"') and raw.endswith('"') and len(raw) >= 2) or \
           (raw.startswith("'") and raw.endswith("'") and len(raw) >= 2):
            raw = raw[1:-1]
        if raw in ("true", "false"):
            scalars[key] = (raw == "true")
            continue
        scalars[key] = raw
    return scalars
