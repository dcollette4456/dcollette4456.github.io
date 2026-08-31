#!/usr/bin/env python3
"""
Claim ledger writer. Step 6 of CLAUDECODEBRIEF ledger-and-evidence.md.

Computes the fields classification spec §30 calls deterministic --
grade (§5), gate_vector, relay_depth, fingerprint (§2), and
assertion_license (§27) -- from a human-authored claim draft, so an
author states what a source did rather than picking a grade by feel.
It does not compute the fields that are the model's or the grader's own
judgment (segmentation, hunt value mapping, sector/actor extraction,
corroboration, grader identity/passes/agreement): the caller supplies
those, honestly, or leaves them for a genuine grading pass. This tool
mechanizes the arithmetic; it is not itself a grading pipeline.

No claim has been written with this yet, on purpose -- brief §6: "Do
not attempt to generate claim ledgers for the six published issues from
their prose... The first real ledger arrives with the first issue
authored against v4.1."

Usage:
  python3 scripts/claim_writer.py <draft.json>

Draft JSON shape -- see scripts/claim_draft.example.json for a worked
one. Required top-level keys:
  serial, source_id, source_type, text
  gates: {
    origin_identified: bool,        # gate 2: is anyone named as having found this?
    primary_reachable: bool|null,   # gate 2: null if no primary is named at all
    document_retrieved: bool,       # gate 2: did the pipeline fetch the doc it's grading?
    gated: bool,                    # gate 2: paywalled/subscription
    own_observation: bool,          # gate 3: did THIS document observe it itself?
    named_primary: bool,            # gate 3: if relay, did it name who it's relaying?
    relay_depth: int|"unresolved",  # gate 3: hops from the observation, if a relay
    self_interested_only: bool,     # gate 3: only the party the claim benefits vouches
    aggregate: bool,                # gate 4
    artifact_test: "pass"|"fail"|"n/a",
    method_test: "pass"|"fail"|"n/a",   # n/a is mechanical for TEC/feed, never chosen freely otherwise
    hedge_test: "pass"|"fail"|"n/a"
  }
  evidentiary_status: observed|alleged|adjudicated|self_reported
  polarity: positive|negative
  volatility: durable|perishable|superseding
  scope: string|null   # required (non-null) if polarity is negative, else grade 6 per §29
  document_sha256_normalized: string  # from the evidence manifest for this citation
  origin_named: string|null           # who/what this document points at, in the pipeline's own words
  time: { observed_period: {...}|null, source_published, fetched }
  grader: { model, spec_version, normalizer, run, passes, agreement, ... }
  ... plus everything else the schema requires that this tool does not compute:
  segmentation, hunt_value, sectors, actors, entities, provenance, corroboration (optional)
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from jsonschema_mini import validate, SchemaError  # noqa: E402


def compute_grade(g, polarity, scope):
    """Classification spec §5, applied in order, first match wins.
    Returns (grade, access_addendum, relay_depth, gates_block, gate_vector)."""

    retrievable = True
    origin_stated = bool(g.get("origin_identified"))
    access = None

    # Gate 2
    if g.get("origin_identified") and g.get("primary_reachable") is False and not g.get("document_retrieved"):
        # named origin, nothing anyone can open
        gates = _gates_block(retrievable=True, origin_stated=True, direct_observation=False,
                              aggregate=False, artifact="n/a", method="n/a", hedge="n/a")
        return 5, None, 0, gates, _vector("", gates)

    if g.get("gated"):
        access = "gated"

    # Gate 3
    direct_observation = bool(g.get("own_observation"))
    if not direct_observation:
        if g.get("self_interested_only"):
            gates = _gates_block(True, origin_stated, False, False, "n/a", "n/a", "n/a")
            return 6, access, None, gates, _vector("", gates)

        relay_depth = g.get("relay_depth")
        if relay_depth == "unresolved" or (not g.get("named_primary") and relay_depth is None):
            gates = _gates_block(True, origin_stated, False, False, "n/a", "n/a", "n/a")
            return 6, access, "unresolved", gates, _vector("", gates)

        if isinstance(relay_depth, int) and relay_depth >= 2:
            gates = _gates_block(True, origin_stated, False, False, "n/a", "n/a", "n/a")
            return 5, access, relay_depth, gates, _vector("", gates)

        # depth 1: named primary
        gates = _gates_block(True, origin_stated, False, False, "n/a", "n/a", "n/a")
        return 4, access, (relay_depth if isinstance(relay_depth, int) else 1), gates, _vector("", gates)

    # Gate 4
    if g.get("aggregate"):
        gates = _gates_block(True, origin_stated, True, True, "n/a", "n/a", "n/a")
        return 3, access, 0, gates, _vector("", gates)

    # Gate 5
    artifact = g.get("artifact_test", "fail")
    method = g.get("method_test", "fail")
    hedge = g.get("hedge_test", "n/a")
    gates = _gates_block(True, origin_stated, True, False, artifact, method, hedge)

    all_pass = all(t in ("pass", "n/a") for t in (artifact, method, hedge))
    grade = 1 if all_pass else 2

    # §29: a negative claim with no stated scope is unassertable, grade 6
    if polarity == "negative" and not scope:
        return 6, access, 0, gates, _vector("", gates)

    return grade, access, 0, gates, _vector("", gates)


def _gates_block(retrievable, origin_stated, direct_observation, aggregate, artifact, method, hedge):
    return {
        "retrievable": retrievable,
        "origin_stated": origin_stated,
        "direct_observation": direct_observation,
        "aggregate": aggregate,
        "artifact_test": artifact,
        "method_test": method,
        "hedge_test": hedge,
    }


def _vector(source_type, gates):
    def flag(v):
        return "y" if v is True else ("n" if v is False else "na")

    def test(v):
        return {"pass": "p", "fail": "f", "n/a": "na"}[v]

    return (f"{source_type}|R:{flag(gates['retrievable'])}|D:{flag(gates['direct_observation'])}"
            f"|A:{flag(gates['aggregate'])}|art:{test(gates['artifact_test'])}"
            f"|meth:{test(gates['method_test'])}|hedge:{test(gates['hedge_test'])}")


def compute_fingerprint(source_id, doc_hash, gate_vector):
    return f"{source_id}|{doc_hash}|{gate_vector}"


def compute_assertion_license(grade, evidentiary_status, volatility, observed_period_end):
    """Classification spec §27's table, plus §28 expiry for perishable claims."""
    table = {
        1: {"may_assert": "attributed_observation", "may_present_as_fact": False,
            "required_form": "name the source; do not say established, confirmed, or verified"},
        2: {"may_assert": "attributed_observation_unchecked", "may_present_as_fact": False,
            "required_form": "name the source; do not imply the artifacts can be independently checked"},
        3: {"may_assert": "attributed_aggregate", "may_present_as_fact": False,
            "required_form": "name the source; present the figure as a fact about that source's population, not about the world"},
        4: {"may_assert": "relayed_finding", "may_present_as_fact": False,
            "required_form": "name the relay and the named primary; never present as the primary's own words"},
        5: {"may_assert": "reported_unverifiable_finding", "may_present_as_fact": False,
            "required_form": "name the party reported to have found this; state no document is available; never assert it happened"},
        6: {"may_assert": "unattributed_assertion_exists", "may_present_as_fact": False,
            "required_form": "state only that the assertion was made and by whom; nothing else"},
    }
    base = dict(table[grade])
    base["attribution_required"] = True
    base["may_ground_recommendation"] = grade in (1, 2, 3, 4)

    if evidentiary_status != "observed":
        base["required_form"] += f"; carries evidentiary status '{evidentiary_status}' at every hop"

    expires = None
    if volatility == "perishable" and observed_period_end:
        import datetime
        end = datetime.date.fromisoformat(observed_period_end)
        expires = (end + datetime.timedelta(days=30)).isoformat()
    base["expires"] = expires

    return base


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    draft_path = Path(sys.argv[1])
    draft = json.loads(draft_path.read_text(encoding="utf-8"))

    serial = draft["serial"]
    ledger_path = ROOT / "data" / "ledger" / f"{serial}.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() and ledger_path.stat().st_size else []

    grade, access_addendum, relay_depth, gates, gate_vector = compute_grade(
        draft["gates"], draft["polarity"], draft.get("scope")
    )
    gate_vector = f"{draft['source_type']}|{gate_vector.split('|', 1)[1]}"

    fingerprint = compute_fingerprint(draft["source_id"], draft["document_sha256_normalized"], gate_vector)

    observed_end = None
    if draft.get("time", {}).get("observed_period"):
        observed_end = draft["time"]["observed_period"].get("end")
    license_ = compute_assertion_license(grade, draft["evidentiary_status"], draft["volatility"], observed_end)

    claim_num = len(ledger) + 1
    claim_id = f"{serial}-C{claim_num:03d}"

    claim = {
        "claim_id": claim_id,
        "fingerprint": fingerprint,
        "issue": serial,
        "first_issue": serial,
        "citation_count": 1,
        "text": draft["text"],
        "source_id": draft["source_id"],
        "source_type": draft["source_type"],
        "grade": grade,
        "relay_depth": relay_depth,
        "evidentiary_status": draft["evidentiary_status"],
        "polarity": draft["polarity"],
        "volatility": draft["volatility"],
        "language": draft.get("language", "en"),
        "synthetic": draft.get("synthetic", False),
        "gates": gates,
        "gate_vector": gate_vector,
        "segmentation": draft["segmentation"],
        "grader": draft["grader"],
        "hunt_value": draft["hunt_value"],
        "sectors": draft["sectors"],
        "actors": draft["actors"],
        "assertion_license": license_,
        "entities": draft["entities"],
        "time": draft["time"],
        "provenance": draft["provenance"],
        "disposition": "open",
    }
    if draft.get("origin_named") is not None:
        claim["origin_named"] = draft["origin_named"]
    if access_addendum:
        claim["access"] = access_addendum
    if "corroboration" in draft:
        claim["corroboration"] = draft["corroboration"]
    if draft.get("fetch"):
        claim["fetch"] = draft["fetch"]
    if draft.get("extracted"):
        claim["extracted"] = draft["extracted"]
    if draft.get("archive"):
        claim["archive"] = draft["archive"]

    schema = json.loads((ROOT / "data" / "schema" / "ledger-4.json").read_text())
    try:
        validate([claim], schema)
    except SchemaError as e:
        print(f"REJECTED: {e.path}: {e.message}", file=sys.stderr)
        sys.exit(1)

    ledger.append(claim)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"wrote {claim_id}: grade {grade}, {gate_vector}")
    print(f"  fingerprint: {fingerprint}")
    print(f"  {ledger_path.relative_to(ROOT)} now has {len(ledger)} claim(s)")


if __name__ == "__main__":
    main()
