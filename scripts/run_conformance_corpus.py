#!/usr/bin/env python3
"""
Compare isolated grading results against the frozen conformance corpus
answer key, tests/conformance/answer_key.json.

This is the standing check classification spec §32 calls for, applied
to fixed documents with a known-correct answer rather than to a sample
of a real issue's claims: §1 stakes this system on the claim that the
same document read twice grades the same, and on the gates being
applied the way the specification actually states them, not just the
way a person reading the specification hastily might apply them. A
sample of real claims measures the first property. This corpus measures
the second -- it is not a substitute for §32's sampling, it is a
cheaper, faster check that runs on every specification revision, prompt
change, or model swap, since the correct answer is fixed and known in
advance rather than needing a second independent grading pass to
compare against.

Each document in tests/conformance/documents/ is graded exactly like a
real claim (classification spec §30 stage 4: one document, one call, no
other context, no answer key) and the returned gate answers are checked
two ways: individually, against the specific gate values the answer key
records as correct, and by running the real compute_grade() -- the same
function that grades a real issue -- to confirm the grader's answers
actually resolve to the expected grade. A gate answer can be
individually wrong in a way that happens to still produce the right
grade by coincidence; this catches both kinds of failure separately.

This script does not dispatch the grading calls. Grading calls are
isolated Agent calls with no memory of this repository or this script,
same as classification spec §30 stage 4 requires for a real claim --
run this corpus's documents through the same isolated-grading procedure
scripts/prepare_regrade_test.py's PROMPT_TEMPLATE describes, save each
result as tests/conformance/results/{id}.json, then run this script to
score them.

Usage:
  python3 scripts/run_conformance_corpus.py
  python3 scripts/run_conformance_corpus.py --results-dir /path/to/results
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from claim_writer import compute_grade  # noqa: E402

CORPUS_DIR = ROOT / "tests" / "conformance"


def load_answer_key():
    return json.loads((CORPUS_DIR / "answer_key.json").read_text(encoding="utf-8"))


def check_case(case, actual):
    """Returns (passed, list of mismatch descriptions)."""
    expected = case["expected"]
    mismatches = []

    if expected.get("gate_0_is_analysis"):
        if not actual.get("gate_0_is_analysis"):
            mismatches.append("expected gate_0_is_analysis=true (ANL, gate 0 stops before grading) "
                               f"but result did not flag it; result: {actual}")
        return (len(mismatches) == 0), mismatches

    if actual.get("gate_0_is_analysis"):
        mismatches.append("result flagged gate_0_is_analysis=true but this case is a sourced claim "
                           "expected to reach the gates, not stop at gate 0")
        return False, mismatches

    # Check each individually-specified gate field the answer key cares about.
    field_map = {
        "own_observation": "own_observation",
        "relay_depth": "relay_depth",
        "named_primary": "named_primary",
        "self_interested_only": "self_interested_only",
        "origin_identified": "origin_identified",
        "primary_reachable": "primary_reachable",
        "document_retrieved": "document_retrieved",
        "aggregate": "aggregate",
        "artifact_test": "artifact_test",
        "method_test": "method_test",
        "hedge_test": "hedge_test",
        "source_type": "source_type",
    }
    for key, actual_key in field_map.items():
        if key not in expected:
            continue
        exp_val = expected[key]
        act_val = actual.get(actual_key)
        if exp_val == "n/a":
            continue  # n/a in the answer key means "not load-bearing for this case", not a required value
        if act_val != exp_val:
            mismatches.append(f"{key}: expected {exp_val!r}, got {act_val!r}")

    # Recompute the grade the real way, from whatever gates the result actually gave --
    # this is what actually ships, not a description of it. No defensive defaults here:
    # a field the grader left unanswered stays unanswered (None), which is itself a fact
    # worth compute_grade() seeing rather than papering over with a guessed default that
    # could silently mask a wrong or missing answer (found while building this: a naive
    # `document_retrieved` default of True would have made the CONF-006 gate-2 check
    # unreachable even when the grader answered correctly).
    gates_for_compute = {
        "origin_identified": actual.get("origin_identified"),
        "primary_reachable": actual.get("primary_reachable"),
        "document_retrieved": actual.get("document_retrieved"),
        "gated": actual.get("gated"),
        "own_observation": actual.get("own_observation"),
        "named_primary": actual.get("named_primary"),
        "relay_depth": actual.get("relay_depth"),
        "self_interested_only": actual.get("self_interested_only"),
        "aggregate": actual.get("aggregate"),
        "artifact_test": actual.get("artifact_test"),
        "method_test": actual.get("method_test"),
        "hedge_test": actual.get("hedge_test"),
    }
    try:
        actual_grade, _access, _relay, _gates_block, _vector = compute_grade(gates_for_compute, "positive", None)
    except Exception as e:
        mismatches.append(f"compute_grade() raised {type(e).__name__}: {e} on gates {gates_for_compute}")
        return False, mismatches

    if actual_grade != expected["expected_grade"]:
        mismatches.append(f"expected_grade: expected {expected['expected_grade']}, "
                           f"compute_grade() returned {actual_grade} from the result's own gate answers")

    return (len(mismatches) == 0), mismatches


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results-dir", default=str(CORPUS_DIR / "results"))
    args = p.parse_args()
    results_dir = Path(args.results_dir)

    key = load_answer_key()
    cases = key["cases"]

    passed = 0
    missing = 0
    failed_cases = []

    for case in cases:
        result_path = results_dir / f"{case['id']}.json"
        if not result_path.exists():
            print(f"MISSING  {case['id']}: no result at {result_path.relative_to(ROOT) if results_dir.is_relative_to(ROOT) else result_path}")
            missing += 1
            continue
        actual = json.loads(result_path.read_text(encoding="utf-8"))
        ok, mismatches = check_case(case, actual)
        if ok:
            print(f"PASS     {case['id']}: {case['path_tested']}")
            passed += 1
        else:
            print(f"FAIL     {case['id']}: {case['path_tested']}")
            for m in mismatches:
                print(f"           {m}")
            failed_cases.append(case["id"])

    total = len(cases)
    scored = total - missing
    print(f"\n{passed}/{scored} scored case(s) passed ({missing} missing, {total} total in corpus).")
    if scored > 0:
        print(f"Divergence rate: {len(failed_cases)}/{scored} "
              f"({100 * len(failed_cases) / scored:.1f}%) -- classification spec §32: "
              f"published as a rate, with its denominator, not as a bare pass count.")

    if failed_cases or missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
