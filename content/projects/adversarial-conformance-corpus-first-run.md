---
title: "Build Log: The Adversarial Conformance Corpus, First Run, 50% Divergence"
date: 2026-09-05
year: "2026"
status: "Build notes"
excerpt: "Ten documents built to make the wrong gate path look tempting instead of the right one obvious. Five diverged from the intended answer on a real isolated grading pass -- and every divergence traced back to the same underlying fault line: where gate 0's own-inference stop actually ends and normal grading, with its hedge and aggregate tests, begins."
type: "projects"
tags: ["classification v4.2", "build notes", "conformance", "isolation", "adversarial"]
---

**Covers:** the adversarial half of the conformance corpus the [first conformance run](/projects/conformance-corpus-first-run/)
left as open work -- documents built to make a wrong reading of the gates look defensible, rather than making one
path the only defensible reading.
**Status:** ten cases built, self-checked against the real grading arithmetic, and run for real. **5/10 divergence**
on this run -- high on purpose, and every divergence investigated rather than patched away. Corpus at
`tests/conformance/adversarial/`, harness extended in `scripts/run_conformance_corpus.py` (now takes `--corpus-dir`
and a real negative-claim path it did not have before).

## Why a 50% divergence rate is the right number to publish, not a failure

The first corpus measured whether the *mechanism* still means what the specification says: eleven documents, each
built to make one gate path the only defensible reading, and every isolated grader landed exactly where the answer
key said it should. That is the right test for catching a specification revision or a prompt rewrite that quietly
moves what "pass" means. It does not tell you anything about how a grader behaves at the edges, because none of the
eleven documents had an edge -- they were built to be easy.

This corpus is the opposite exercise: ten documents, each built to place a real distractor directly next to the
gate-relevant fact, so that a grader reading momentum instead of gates lands on the wrong branch. A high divergence
rate here is not a defect in the grading pipeline. It is the corpus doing its job -- and reading the divergences
closely turned up something more useful than a bug count: **four of the five divergences trace back to one
unresolved boundary in the specification itself**, not four unrelated mistakes.

## The boundary the corpus found

Gate 0 stops an assertion before it is ever graded, if it is "the author's own inference, synthesis, correlation,
forecast, or recommendation." Gate 4 grades an aggregate over the source's own private data at grade 3. Gate 5's
hedge test explicitly contemplates grading inferential claims about intent and attribution, provided they are
hedged. Read together, these three are supposed to divide cleanly: a claim resting on the source's own observed
data is a sourced claim (gated normally, capped by whichever test it fails), and only a claim that is genuinely the
author's own synthesis -- unmoored from any specific observation, of the kind CONF-011 modeled with "this is our own
synthesis across publicly reported incidents" -- stops at gate 0.

Three of these ten documents sat exactly on that line, on purpose, and none of them resolved the way the answer key
predicted:

- **ADV-002** grounded a targeting assessment in the source's own cross-client telemetry pattern ("based on the
  pattern... we have observed across our client base this quarter"), phrased with analytic language ("we assess").
  The answer key called this gate 4 -- an aggregate over the source's own data, same shape as the population
  statistic in CONF-004. The isolated grader called it gate 0, reading "we assess" as synthesis rather than as an
  aggregate finding. Both readings apply the letter of the rule; neither the gate 0 text nor the gate 4 text says
  which one wins when a claim is grounded in the source's own data but *phrased* as an assessment.
- **ADV-004** was a genuine behavioral observation ("the operators spaced out their post-compromise actions"), given
  an inferred motive in the same sentence ("to avoid triggering time-based detection thresholds"), from the source's
  own IR engagement. The answer key called this a gate-5 intent claim, hedge test not applicable since it reads as
  behavioral rather than attributional, artifact fail on a distractor's account. The isolated grader called the
  whole sentence gate 0, on the theory that inferring *why* the operators did something is itself an inference
  rather than an observation -- which is a defensible reading of gate 0's own wording, and is in tension with gate
  5's hedge test explicitly listing "intent" as a category of claim that gets graded, not stopped.
- **ADV-010**, built as the clean control for this same boundary, worked exactly as intended: explicit,
  repeated self-declaration ("this is our own analytic judgment... not based on any single observed campaign")
  left no real doubt, and the grader correctly stopped at gate 0.

Read side by side, ADV-010 shows the boundary is findable when a document is explicit about which side it's on.
ADV-002 and ADV-004 show that when a document is *not* explicit -- when it grounds a conclusion in real data but
states the conclusion in the specification's own gate-0 vocabulary ("we assess") -- two careful, isolated readings
of the same rule can land on opposite sides. That is a specification gap, not a grading error, and it is now a
concrete candidate for classification spec section 17's open-decisions list: **does an inference drawn from a
source's own directly-observed data stop at gate 0, or proceed to gate 4 or gate 5 on the strength of that
observation?** The current text does not say, and this corpus is what surfaced that it needed to.

## The other two divergences, and one of them found a bug in the harness, not the grader

**ADV-003** tested whether "with certainty" satisfies the hedge test. The answer key expected the hedge test to
fail, on the theory that a flat, overconfident attribution is exactly what hedging is supposed to catch. The
isolated grader marked it a pass, on the theory that the hedge test's actual wording -- "does the document state a
confidence level" -- is satisfied by *any* stated confidence level, including the maximal one. Read literally, the
grader is right: the rule asks whether a confidence level was stated, not whether it was stated *modestly*. This is
a second real specification gap, smaller than the gate-0 boundary but the same shape: the rule's letter and its
evident purpose diverge at exactly the case built to test it.

**ADV-008** is the one divergence that turned out to be a defect in the scoring script rather than in either
reading. The document was a negative claim (a vendor's "we have not observed X") with only vague, non-specific
"scope" language, and both the answer key and the isolated grader agreed the claim should record no real scope and
grade 6 under section 29. But `scripts/run_conformance_corpus.py`'s recomputation step called `compute_grade()`
with polarity hardcoded to `"positive"` and scope hardcoded to `None`, regardless of what the graded result actually
said -- a leftover from a harness that had never yet been asked to score a negative-polarity case, because none of
the original eleven documents was one. That call would have silently graded every future negative claim as though
it were positive, passing or failing it for the wrong reason every time. Fixed in the same commit: the harness now
reads `polarity` and `scope` from the actual result, per document, the same way a real ledger write would. The one
field-level mismatch that remains on ADV-008 (`method_test` recorded `n/a` instead of `fail`) is real and stands: the
`n/a` carve-out is textually reserved for `TEC` claims in section 5, and applying it to a `VND` claim with no
described method -- even a negative one -- is the same category of misapplication ADV-009 was built to test
directly.

**ADV-009** was built to test whether table/bullet formatting gets mistaken for a genuine structured (`TEC`) record
when a narrative author is actually present, and the grader passed that specific test cleanly -- it correctly kept
the source `VND`. It then went further than the answer key anticipated: rather than granting own-observation credit
for the "actively exploited" status on the strength of the publisher's own watchlist entry, it held that tracking
something in your own watchlist establishes observation of *the tracking*, not of the underlying exploitation
status the watchlist entry asserts, and found no stated basis for that specific claim at all -- landing on grade 6
(no traceable origin) rather than the answer key's expected grade 2. On reflection this is the tighter and more
defensible reading: "own catalog" as a legitimate observation basis, per gate 3's own list, describes cataloging
something you directly hold or directly encountered, not re-publishing a status your source doesn't say how it
determined. The answer key under-scoped what counts as an established basis here, and the grader's stricter reading
is the one being kept as instructive rather than corrected away.

## What's not being done here, on purpose

None of these five findings changed the answer key to match whatever a grader returned. Two are now documented as
open specification questions worth a future revision's attention. One is a defect in the scoring harness, now fixed
in `scripts/run_conformance_corpus.py`. One (ADV-009) is a case where the grader's answer looks more correct than
the one that was written down, and is recorded as such rather than silently reconciled. This is the same rule the
first corpus's build log stated for its own construction errors: a mismatch is a finding to investigate, not the
key to correct to match whatever came back.

## What this corpus adds to the standing conformance programme

The cooperative corpus (0/11 divergence) and this one (5/10 divergence) measure different things and are both kept,
per classification spec section 32's own limits on what any fixed corpus can tell you: passing eleven memorized-shape
cases does not mean a grader generalizes, and a high divergence rate on a corpus built specifically to be hard does
not mean the pipeline is unreliable on ordinary material. What it means is that four real, specific boundary
questions in the specification's gate 0 / gate 4 / gate 5 text are now written down with concrete failing examples
attached, instead of being an ambiguity nobody had reason to notice yet.
