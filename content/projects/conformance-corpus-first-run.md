---
title: "Build Log: The Conformance Corpus, First Run, 0% Divergence"
date: 2026-09-05
year: "2026"
status: "Build notes"
excerpt: "Fixed synthetic documents with frozen, hand-derived correct gate answers, checked against the actual grading arithmetic before ever running a real grader against them -- which caught three real errors in the answer key itself. Then run for real: eleven isolated Agent calls, zero divergence from the frozen key."
type: "projects"
tags: ["classification v4.2", "build notes", "conformance", "isolation"]
---

**Covers:** building and running the conformance corpus classification spec §32 calls for
(fixed documents, frozen gate answers, checked on every specification revision, prompt
change, or model swap), as a companion to §32's sampling of real issue claims rather than a
replacement for it.
**Status:** eleven cases built, self-checked, and run for real. Zero divergence on this run.
Corpus and harness committed at `tests/conformance/` and `scripts/run_conformance_corpus.py`.

## What this measures, and what it doesn't

§1 stakes this system on two claims: that the same document read twice grades the same, and
that the gates are being applied the way the specification actually states them. §32's
sampling programme measures the first, against real claims from a real issue, which is
expensive to run often and only exists once an issue does. This corpus measures the second,
against fixed documents built specifically to exercise one path through the gates each, and it
can run on demand -- every time the specification changes, every time the grading prompt
changes, every time the underlying model changes.

It is not a substitute for §32. A grader could pass every case here by having correctly
memorized eleven answers and still drift on a real, messier document. What it catches is
cheaper and different: a specification revision, or a prompt rewrite, that quietly changes what
"pass" means for the artifact test, say, would very likely move one of these eleven cases, and
would move it immediately, without waiting for a real issue to surface the drift.

## Eleven cases, one path through the gates each

Grade 1 (clean pass, and separately the `TEC` method-test carve-out), grade 2 (twice: an
artifact-test failure and a hedge-test failure, since those are different tests failing for
different reasons), grade 3 (the aggregate gate), grade 4 (a relay of a named finding), grade 5
(twice: an identified-but-unreachable origin, and a relay two hops deep), grade 6 (twice: no
origin at all, and the self-interested-only case), and gate 0 (the author's own analysis,
which never reaches a grade digit at all).

Each case is a short synthetic document, written to make exactly one path through the gates the
only defensible reading, with a frozen answer key recording the expected gate values, the
expected grade, and the reasoning tying the expected answer back to the specific spec
paragraph it tests.

## The corpus caught its own errors before it caught anything else's

The answer key was checked against the real arithmetic before a single real grader was run
against it -- `scripts/claim_writer.py`'s actual `compute_grade()` function, not a description
of what the function is supposed to do. That check failed on the first pass, three times:

- **CONF-004** (the aggregate case) was missing `"aggregate": true` from its own expected gate
  values. Without it, `compute_grade()` never reaches gate 4 at all and returns grade 1.
- **CONF-006** (the unreachable-origin case) was missing `"origin_identified": true`. Without
  it, gate 2's special branch never triggers and the case falls through to gate 3's
  unresolved-relay branch, returning grade 6 instead of the intended grade 5.
- **CONF-009** (the self-interested-only case) had `own_observation` recorded as `true`. That's
  wrong on a careful reading of gate 3, not just wrong for the code: gate 3's own header lists
  what counts as a legitimate own-observation (own IR engagement, own sensors, own scan, own
  artifact recovery, own network, own catalog, own repository, own court record), and an
  attacker's unevidenced leak-site boast about its own breach fits none of those. It is gate
  3's separate self-interested-only failure case, which the actual code only checks inside the
  branch reached when `own_observation` is false. Marking it true would have skipped that check
  entirely and produced grade 2 instead of the intended grade 6.

All three were caught by treating the answer key's own claimed-correct values as a hypothesis
and running them through the same function a real grade run would use, before spending a
single real grading call on the corpus. That is the same discipline the corpus itself asks of
a grader -- check against the actual mechanism, not against what you expect it to say -- turned
on the corpus's own construction.

## The real run

Eleven fresh, isolated `Agent` calls, one per document, each holding only the classification
specification and that one document -- no memory of each other, no memory of building the
corpus, no access to the answer key. Every one of the eleven matched the frozen key exactly,
including on the two distinctions most likely to get flattened by a careless reading:

- **`primary_reachable` versus `document_retrieved`** (CONF-005): the grader correctly held
  that a report existing and being publicly findable is a different fact from this particular
  reading pass having fetched it, and reached grade 4 rather than grade 5 on that basis.
- **Counting relay hops** (CONF-007): the grader correctly read a document relaying a document
  that itself named a further source, and counted two hops rather than one.

**Divergence rate: 0/11 (0%).** Published as a rate, with its denominator, because six claims
is not a rate and neither, really, is eleven -- this run is a floor to compare future runs
against, not a result to treat as settled. `tests/conformance/results/_run_log.json` records
this run and is meant to be appended to, not overwritten, the next time the specification, the
prompt, or the model changes.

## What's next for this corpus

Eleven cases cover the grade scale's major paths once each. Real drift is more likely to show
up at the edges: the no-unnecessary-intermediary rule, the negative-claim gate in §29, the
`evidentiary_status` interaction with grade 6 in §4A, and cases built specifically to be
adversarial -- documents constructed to *look* like they should pass a test they should
actually fail, which is a different and harder thing to build than documents that cleanly
exercise one path. That adversarial corpus is still open work; this one is the artifact-rich,
cooperative-case half of what §32 asks for.
