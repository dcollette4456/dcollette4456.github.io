---
title: "Build Log: The Grading-to-Ledger Gap, First Isolated Re-Grade, v4.2/v2.9"
date: 2026-09-05
year: "2026"
status: "Build notes"
excerpt: "Closing the gap between the classification system and the ledger: the claim draft (§15A), isolated gate evaluation, fresh-instance reconciliation, and the first real re-grade run against TI-20260817-001, which found a composite-claim bug, a genuine grading disagreement, and a shell-capture failure the integrity check couldn't see."
type: "projects"
tags: ["classification v4.2", "article spec v2.9", "build notes", "re-grade", "isolation"]
---

**Covers:** the change request closing the grading-to-ledger gap, the first
isolated re-grade run against TI-20260817-001, and the specification revisions
that resulted.
**Status:** amendments applied to both specifications, now versioned at
`docs/specs/`. Code and schema changes committed to `claude/v4-2-amendments`.
Several items open, tracked below.

## What this project is for

The website is the current application. It is not the goal.

The goal is a system for making an AI's judgments auditable: every determination
traceable to a recorded reason, computed values never authored, and a measurable
rate at which the same input produces the same output. Threat intelligence is
the first domain it has been applied to. The intended range is any research task
where the reasoning behind a conclusion has to be inspectable, and eventually
SIEM alert triage, where an agent's disposition of an alert has to arrive with
the reasoning that produced it.

That framing decides most of the calls below. Where the durable system and the
current website pull in different directions, the system wins.

## The gap that started this

The classification system defined how a claim is graded. The ledger defined what
a finished grade looks like. Nothing defined the artifact in between, so the
reasoning that produced a grade lived nowhere and the ledger's arithmetic could
not be re-run by anyone, including its author.

Section 30 had always required the ledger to be complete before authoring began,
which meant stages 3 through 11 had always been obliged to produce something.
The gap was that nothing named it. The fix, now §15A, adds no stage and changes
no order. It names an artifact that was already required and requires it to be
kept.

## Decisions taken

**Gate evaluation runs isolated.** One claim, one source, one call. Where two
claims draw on the same document they are still graded separately, because a
context that has worked a document once is not blind for the second pass. The
alternative considered was disclosing contamination rather than preventing it.
Rejected: blindness is load-bearing for the claim that a grade is a property of
the document rather than of the issue.

**No contamination flag.** A field where a grader reports whether its own
judgment was influenced can only capture influence the grader noticed, and
noticing is most of correcting. It would read clean every time while real
contamination passed unmarked, and a control that always reads clean is worse
than no control because a reader takes it as an answer. This is the same
objection §18 raised to a per-claim bias tag, applied to the grader instead of
the source.

**Conditions are recorded instead.** `gate_evaluation` states isolation mode,
what was in context, how many assertions were graded in the call, the
specification and prompt versions, and whether the prompt carried topic framing.
Every field is a mechanical fact about the call. `topic_framing_present` is
admissible where a contamination flag is not, because framing is a property of
the prompt text rather than an introspective judgment, and once context is
isolated the prompt is the remaining vector.

**Reconciliation runs in a fresh instance.** The instance that wrote the prose
cannot check the prose. Reconciliation and isolation address opposite failures
and neither substitutes for the other: a grade contaminated at stage 4 produces
a ledger entry that is wrong but internally coherent, and prose faithful to it
reconciles clean.

**`grader.agreement` always carries an explicit value.** `single_pass` where one
pass was run. An omitted field is indistinguishable from one a bug dropped.

**Claim drafts are retained and committed.** They are the only record of the
authored inputs to a computed output. Discarding them makes the ledger's
arithmetic permanently uncheckable at the exact point where checkability is the
product's whole claim.

**No retroactive ledgers.** A published issue never gains a ledger it did not
have. A draft written now for an issue authored months ago is reconstructed
rather than recorded.

## The re-grade run

Six claims from TI-20260817-001, re-graded blind, one source per call, model and
published grade withheld, completed drafts run through `claim_writer.py` for the
arithmetic. Two multi-source claims split, so eight grading calls.

**Three matched cleanly.** C001, C003, C004, all `VND-1`. C005 matched on gate
reasoning at `TEC-1` and surfaced a schema gap rather than a grading one.

**One composite claim was never segmented.** Published C002 asserted two
different things about two different subjects: that a vendor declined to
attribute confidently, and that trade coverage compressed that refusal into a
flat attribution. Graded separately under isolation those land at grade 2 and
grade 4. Published tag was `VND-1`, which neither underlying assertion supports.

This was first written up as a merge-rule violation. It is not. A bad merge is a
decision somebody made and leaves a record that can be disputed. This was an
absence: step two of segmentation was skipped, a composite reached the gates as
though it were atomic, and nothing recorded that it had happened. The diagnostic
is now in §2. A claim draft carrying more than one `source_id` is invalid on its
face, since a grade attaches to a claim-source pair.

**One genuine grading disagreement.** C002a graded 2 against a published 1, on
the artifact test: whether technical overlap described in prose counts as a
published, checkable artifact. Two careful readers can answer that differently.
This is the first recorded disagreement under the published rule and it is the
kind of result the sampling programme in §32 exists to produce.

**One source could not be graded at all, and the failure is the pipeline's, not
the publisher's.** GovInfoSecurity published a real page. The stored capture of
it contains no article: share dialogs, a registration form, a cookie notice, an
unrelated promotion, zero occurrences of any term the claim depended on. What
failed is the fetcher that captured it, not the reporting it was supposed to
capture.

The consequence is worse than the capture. `hash_vs_original_manifest` read
`match`, meaning this was also what was captured at citation time, so §14's
silent-edit detection will report, correctly and forever, that this document has
not changed. The integrity check returns clean on a document nobody ever
captured. There is a second gap underneath it: the article was written citing
this source, so a person read the page. The capture pipeline and the reading
pass saw different documents and nothing compares them. That is independent of
JavaScript rendering.

`retrieval_failed` now covers the empty capture explicitly, content presence is
verified before a capture is written, and the retroactive audit over the
existing corpus is open work below.

## Specification drift

Four instances found in one session, all the same class: a specification
stating something about the repository that was not true.

| Claimed | Actual |
|---|---|
| `data/serials.json` unpopulated, uniqueness the author's to verify by hand | Populated, allocated by script, uniqueness enforced in CI |
| Admission parses the References section | Replaced by `data/citations/{serial}.json` |
| Ledger gate object has seven fields | Implementation takes twelve |
| Three site routes listed "Not built" | `/coverage/vocab/`, `/coverage/standing/`, `/data/export/` all live |

**The root cause, found last and the most consequential thing in this session:
neither specification was in the repository.** Not on `main`, not on any active
branch. The only spec commit anywhere was on an abandoned branch at v3.8 and
v2.5 that predates everything built since. Both documents had been living as
chat artifacts and downloads, outside version control, with no history and no
diff.

A specification that cannot see the code will describe a plausible repository,
and plausible is wrong often enough to matter. §1's first requirement for
reproducibility is a published rule. That requirement was unmet for the rule
itself, and is not any longer: both documents now live at `docs/specs/` on
`claude/v4-2-amendments`. §24 carries a standing check going forward: every
statement of the form "until X exists" carries the path to X so the claim is
testable.

## Errors made in the process, recorded rather than quietly fixed

The amendment document handed to Claude Code contained two instructions that
were wrong, and the handoff prompt contained two more.

- Amendment I directed the retirement of §17 rows on multi-pass grading and on a
  contamination record. Neither row exists. Those were decisions taken in
  discussion and written up as though they were existing table entries. Refusing
  to guess which rows were meant was correct; guessing would have deleted real
  open decisions
- Amendment N placed content in article §15, which is "What This Document Does
  Not Cover." §13 is the deliverables and handoff table and is the correct home
- The handoff fenced off article §§1 through 8 as the voice and structure
  sections. Voice is §11 and site structure is §12. The fence protected the
  wrong range, left the one section that should not be edited open, and locked
  out the two sections where the stale content actually was
- The handoff asserted both specifications were in the repository

The first two were caught because the instruction was to report divergence
rather than resolve it. That instruction earned its place.

## Built this session

Schema 6 with the required `gate_evaluation` block and `time.publication_model`,
additive against schema 5. `claim-draft-1.json`. `citations-2.json` carrying
`type_basis`. The anti-fabrication check enforcing that a ledger entry has a
draft behind it. Draft retention wired into `claim_writer.py`. Specifications at
v4.2 and v2.9, now versioned.

## Open

**Immediate, closed since this log was first drafted.** Both specifications are
now in version control, at `docs/specs/`, committed to the branch this work
lives on. Article §12 and §5 were reopened and corrected: the three stale
"Not built" rows, the two missing list routes (`/entities/`, `/claims/`, live as
list-only routes with no per-item detail page yet), and the footer credit that
still read v4.1 and v2.8. `claim_writer.py`'s handling of an omitted
`provenance` was checked directly rather than inferred: it fails cleanly
through the normal schema-validation path (`SchemaError`, not a crash) because
`provenance.pool` is a required ledger field with no injection logic behind it
yet, which matches what the code's own comments already claimed but had not
actually been exercised. That gap, no issue-metadata source for `pool` to be
injected from, is still real and still open; what changed is that it is now a
verified gap rather than an assumed one. This section is being corrected here,
in place, rather than treated as settled and left to go stale the same way the
specifications themselves did.

**Near.** Run the content-presence check retroactively over every stored
capture across all published issues and publish the count of shells. The scope
of the rendering problem is not knowable until that number exists, and no
decision about a JavaScript-rendering fetcher should be made before it. Settle
the second archive provider, which is a copyright posture question rather than
a tooling task, since one of its two candidates is a copy and §14's principle is
that none of its tiers is a copy.

**Toward the goal.** Split the kernel from the domain pack. What is currently
one document is two things: a warrant grammar (unit of judgment, ordered gates
that cap rather than block, computed-never-authored, the null discipline,
isolation, the disclosure vocabulary) and a threat-intelligence pack (source
types, hunt value, sectors, actors, entities, the specific gate wording). The
split is cheaper now than it will ever be again and it is what makes a second
domain possible.

Build the conformance corpus: fixed documents with frozen gate answers, run
against every specification revision, prompt change and model swap. The
re-grade run was its prototype and it already found real defects. Build an
adversarial corpus alongside it, documents constructed to break the gates,
which tests the rule rather than its application. Publish the divergence rate
with its denominator. Six claims is not a rate.

## Observations from the implementing session

**Schema gaps did not surface from reading the amendments. They surfaced from
running real drafts through the writer.** `single_pass` and `superseding` were
both already agreed in conversation before this session started, and both were
still missing from the schema when the first real completed draft tried to use
them. Reading a decision and encoding it as a schema constraint are different
acts, and the distance between them is invisible until something concrete fails
against it. The `observed_period`-as-string case (C003, a malware family whose
check-in behavior wasn't tied to one dated window) was not anticipated by
anyone writing either specification; the fix, accept a string carrying a
stated basis, and drop it from the ledger's `time` block with a printed note
rather than force it into `{start, end, basis, precision}`, came directly out
of one grader answering an honest question the schema had never been asked.

**"Set to `null`" and "left out" are not the same instruction to a validator,
and the null discipline this whole system asks of a grader runs straight into
that.** A grader following the rule exactly, writing `null` rather than
guessing, produced drafts that were correct and schema-invalid at the same
time, because a typed property rejects `null` unless the schema says
explicitly that it may be null. `_strip_nulls()` in `claim_writer.py` exists
because the alternative was asking every grader to also know an
implementation detail of the validator, which is precisely the kind of leak
between judgment and arithmetic this project exists to keep out. This is not a
defect in the null discipline. It is a cost of taking it seriously that nobody
priced in until a real draft hit it.

**`provenance` is the one field category that cannot be checked by writing a
good example.** Every other required field can be verified by looking at a
filled-in draft and confirming the value is there. `provenance.pool` is
deliberately absent from every draft by design (§15A: an isolated grader
cannot know whether its source arrived in a scheduled sweep or was
backfilled), which means the only way to find out whether the writer's
fallback behavior is correct is to omit the field on purpose and read what
happens, not to run the tool against realistic input. Doing that this session
found the honest answer: an omitted `provenance` fails cleanly through the
same schema-validation path as every other rejected write, rather than
crashing or silently defaulting to a guess. A documented gap that fails loudly
and a bug that happens to fail the same way are indistinguishable by reading
the code. They are only distinguishable by provoking the failure and checking
what actually comes out.

**A handoff instruction can be confidently wrong about a document in exactly
the shape §24's specification-drift check now watches for, one level up.** Two
of the amendments in this session were written against a remembered decision
or a remembered document structure rather than against the text as it
actually stands: one directed the retirement of two open-decision rows that
do not exist in the table, the other placed new content in a section titled
for something else entirely because its actual subject is named elsewhere.
Both read as perfectly reasonable instructions and both were wrong in the
same specific way the specifications themselves kept turning out to be wrong
about their own repository. There is no schema or lint rule that catches
this. The only thing that did was the standing instruction to check the
amendment against the actual document before applying it, rather than
trusting that whoever wrote the instruction had already checked.

**Where two explicit instructions pulled in different directions, the
resolution needed to be visible, not just correct.** "Touch only §9, §13, §14,
§15 of the article specification" and "bump the version and write a changelog
entry" are both clear instructions individually, and the article
specification's own changelog convention lives in §1, outside the permitted
range. Writing the changelog there anyway, on the reasoning that a version
bump is a delivery requirement rather than one of the amendments the section
fence was written to constrain, was a judgment call made in the moment rather
than a rule handed down in advance. It is recorded here for the same reason
everything else in this log is recorded: so a reader checking the work later
has the reasoning, not just the result.
