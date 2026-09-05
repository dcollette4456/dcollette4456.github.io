#!/usr/bin/env python3
"""
Build the prompt for one classification spec §30 stage-14 reconciliation
pass: a fresh instance holding the ledger and the article, and nothing
else, checking whether any tagged sentence asserts more than its ledger
claim.

This script does not dispatch anything -- it only builds deterministic
prompt text. Reconciliation itself has to run as an actual fresh model
call with no memory of the authoring conversation (classification spec
v4.2 amendment F: "the instance that wrote the prose cannot check the
prose"), and only the caller -- a Claude Code session with its own Agent
tool, not a Python script -- can start one of those. What this script
mechanizes is the part that IS deterministic: finding the right article
and ledger for a serial, and assembling the same prompt every time so
three passes are actually independent readings of identical input rather
than three slightly different framings of the question.

Per §30's reconciliation agreement rule: three passes, each answering the
same question independently; any pass reporting drift fails the
sentence, not majority. Run this three times (same serial, same
ledger, same article -- nothing here varies by pass number, the
independence comes from running it in three separate fresh contexts) and
union the flagged claim_ids across all three results.

Usage:
  python3 scripts/build_reconciliation_prompt.py --serial TI-YYYYMMDD-NNN
  python3 scripts/build_reconciliation_prompt.py --article path/to/draft.md --ledger path/to/ledger.json
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from prepare_regrade_test import find_article  # noqa: E402

PROMPT_TEMPLATE = """# Reconciliation pass: {serial}

You are checking one article against its own ledger, under classification
spec §30 stage 14 and §15. You hold the ledger and the article and nothing
else -- no memory of writing either one, no training knowledge about
whether the underlying events are true, no access to the original sources.
That is the whole point: the instance that wrote this prose cannot check
whether it drifted from the ledger it was supposed to be written against,
so you are a different reading of the same two documents.

## What you have

- The ledger: {ledger_path}
- The article: {article_path}

Read both in full before answering anything.

## What you check

The article body contains claim tags, `{{{{< claim tag="..." claim="Cxxx" >}}}}
...sentence(s)...{{{{< /claim >}}}}`. The `claim="Cxxx"` attribute names
which ledger entry (`claim_id` ending in that Cxxx, e.g. `{serial}-C001`)
the tagged sentence is supposed to be describing.

For every tagged block, compare the sentence(s) inside it against that
ledger entry's fields -- grade, evidentiary_status, polarity, volatility,
assertion_license, and the claim `text` itself. Ask one question per
tagged block: **does this sentence assert anything the ledger claim does
not support?**

Concretely, flag a block where the prose:
- States something as certain that the ledger's assertion_license only
  permits as hedged or attributed (a grade 2+ claim written without its
  required hedge; a grade 4 claim's primary not named where the license
  requires it)
- Generalizes past what the ledger's claim text actually says (three
  customer sites become "customers"; one vendor's non-attribution becomes
  a flat attribution)
- Claims corroboration the ledger's claim does not carry (`corroboration`
  absent or count 1, but the prose reads as though two sources confirmed
  it)
- States a volatility-sensitive fact (something described as currently
  active, live, or ongoing) where the ledger marks the claim `perishable`
  and does not carry a current-as-of date in the prose
- Asserts a negative ("no evidence of X") where the ledger claim is not a
  properly gated negative/absence claim under classification spec §29

Do NOT flag a block for:
- Voice or style (that's a different check, not this one)
- A sentence that is faithful to the ledger claim but not verbatim --
  reconciliation checks assertions, not word-for-word matching
- Anything outside a `{{{{< claim >}}}}` tag -- untagged prose (framing,
  transitions, hunt-value commentary) is not what this pass checks

## What you return

A JSON object:

```json
{{
  "pass_reads_ok": ["{serial}-C001", "{serial}-C003"],
  "pass_flags_drift": [
    {{"claim_id": "{serial}-C002", "ledger_text": "...", "article_sentence": "...",
      "why": "one sentence stating specifically what the article claims that the ledger does not support"}}
  ]
}}
```

List every claim_id you checked in one list or the other -- there is no
third bucket. If you are genuinely unsure whether a block drifts, say so
in `why` and flag it in `pass_flags_drift` anyway: per §30, any pass
reporting drift fails the sentence, and an uncertain pass that stays
silent is indistinguishable from a pass that checked and found nothing.

Do not fix the drift, do not suggest a rewrite, do not read anything else
in the repository. Report what you found and stop.
"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--serial", default=None)
    p.add_argument("--article", default=None, help="Explicit article path, overrides --serial lookup")
    p.add_argument("--ledger", default=None, help="Explicit ledger path, overrides --serial lookup")
    args = p.parse_args()

    if args.article and args.ledger:
        article_path = Path(args.article)
        ledger_path = Path(args.ledger)
        serial = args.serial or ledger_path.stem
    elif args.serial:
        article_path = find_article(args.serial)
        ledger_path = ROOT / "data" / "ledger" / f"{args.serial}.json"
        if not ledger_path.exists():
            sys.exit(f"error: {ledger_path.relative_to(ROOT)} does not exist. "
                      f"Reconciliation runs after the ledger is written (§30 stage 13 comes "
                      f"after stage 12), not before.")
        serial = args.serial
    else:
        sys.exit("error: need either --serial, or both --article and --ledger")

    print(PROMPT_TEMPLATE.format(
        serial=serial,
        ledger_path=str(ledger_path.resolve()),
        article_path=str(article_path.resolve()),
    ))


if __name__ == "__main__":
    main()
