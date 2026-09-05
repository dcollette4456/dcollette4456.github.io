#!/usr/bin/env python3
"""
Aggregate the three independent reconciliation passes (classification
spec §30 stage 14, agreement rule stated under §30's "reconciliation
agreement requirement") into one pass/fail result per claim.

Each pass is a JSON object a fresh Agent call returned, per the prompt
scripts/build_reconciliation_prompt.py builds:
  {"pass_reads_ok": [claim_id, ...], "pass_flags_drift": [{"claim_id", "ledger_text", "article_sentence", "why"}, ...]}

The rule is deliberately asymmetric: any pass reporting drift fails the
sentence, not majority. §30: "Reconciliation disagreement means at least
one reader saw the prose overclaim, and the cheap fix is to rewrite the
sentence" -- so a 2-1 split toward "fine" still fails, and is recorded as
disagreement (grader.reconciliation_dissent) rather than resolved by
outvoting the one pass that caught something.

A pass's raw text often isn't clean JSON on the first attempt (a model
narrating its own correction before landing on the final object is a
known failure mode observed during testing) -- extract_last_json pulls
the last valid JSON object out of the text rather than assuming the
whole string parses.

Usage:
  python3 scripts/aggregate_reconciliation.py pass1.json pass2.json pass3.json
"""
import json
import re
import sys


def extract_last_json(text):
    """Find every top-level {...} block and return the last one that
    parses. Handles a pass that talks before settling on its answer."""
    depth = 0
    start = None
    candidates = []
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                candidates.append(text[start:i + 1])
    for candidate in reversed(candidates):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def aggregate(pass_texts):
    """Returns {claim_id: {"status": "ok"|"fails", "dissent": bool,
    "flags": [pass results that flagged it]}}"""
    parsed = []
    for i, text in enumerate(pass_texts, start=1):
        obj = extract_last_json(text)
        if obj is None:
            sys.exit(f"error: pass {i} produced no parseable JSON object")
        parsed.append(obj)

    all_claim_ids = set()
    for obj in parsed:
        all_claim_ids.update(obj.get("pass_reads_ok", []))
        all_claim_ids.update(f["claim_id"] for f in obj.get("pass_flags_drift", []))

    result = {}
    for claim_id in sorted(all_claim_ids):
        flags = []
        oks = 0
        for obj in parsed:
            hit = next((f for f in obj.get("pass_flags_drift", []) if f["claim_id"] == claim_id), None)
            if hit:
                flags.append(hit)
            elif claim_id in obj.get("pass_reads_ok", []):
                oks += 1
        status = "fails" if flags else "ok"
        dissent = bool(flags) and oks > 0
        result[claim_id] = {"status": status, "dissent": dissent, "flags": flags, "clean_passes": oks}
    return result


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: python3 scripts/aggregate_reconciliation.py pass1.json pass2.json pass3.json")
    pass_texts = [open(p, encoding="utf-8").read() for p in sys.argv[1:4]]
    result = aggregate(pass_texts)

    failing = {k: v for k, v in result.items() if v["status"] == "fails"}
    if not failing:
        print(f"reconciliation clean: {len(result)} claim(s) checked, none flagged")
        return

    print(f"reconciliation FAILED: {len(failing)} of {len(result)} claim(s) flagged\n")
    for claim_id, v in failing.items():
        dissent_note = f" (dissent: {v['clean_passes']} pass(es) read this clean)" if v["dissent"] else ""
        print(f"  {claim_id}{dissent_note}")
        for f in v["flags"]:
            print(f"    ledger:  {f['ledger_text']}")
            print(f"    article: {f['article_sentence']}")
            print(f"    why:     {f['why']}")
    sys.exit(1)


if __name__ == "__main__":
    main()
