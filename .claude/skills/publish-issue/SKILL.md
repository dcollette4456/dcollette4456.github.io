---
name: publish-issue
description: Run a drafted threat-intel issue through the full pipeline -- citation extraction, evidence capture, claim segmentation, isolated grading, ledger writing, fresh-instance reconciliation, and a pushed branch ready for a PR. Use when the user hands over a drafted article (prose with citations, using either the {{< src >}} shortcode or a raw <li id="ref-NNN"> References list) and wants it turned into a published, ledger-backed issue.
---

# Publish an issue: draft to pushed branch

This is the procedure built and proven across `docs/specs/Automation_Pipeline_Scope.md`'s
design and the `claude/pipeline-automation` work: citation extraction and segmentation are
scripted and deterministic; isolated grading and reconciliation are **your own `Agent` tool
calls**, not a script, because the whole point is a context with no memory of this
conversation. Nothing here is optional ceremony -- each step exists because an earlier run
found the failure it prevents. Follow it in order. Do not skip stages 4 or 8 by grading or
reconciling from inside this same conversation; that defeats the isolation the classification
spec requires and produces a ledger entry that only looks audited.

**Before starting, check network egress.** Stage 2 needs to fetch every cited URL. If this
session's environment blocks arbitrary outbound domains (confirmed true for the standard
Claude Code on the web / cloud session), stages 2 onward cannot run here. Say so plainly and
stop, rather than grading against nothing or fabricating capture data. This procedure needs to
run somewhere with real internet: Claude Code CLI on the user's own machine, or a differently
configured environment.

## Inputs you need before starting

- The draft (a file path, or pasted content saved to a file first)
- A serial: run `python3 scripts/allocate_serial.py --date <today> --title "<title>" --path
  /issues/<slug>/ [--issue-number N]` if one hasn't been allocated yet. Do this at this point,
  not earlier, per classification spec §15 -- allocating early risks a collision with another
  issue authored in parallel.

## Stage 1: extract citations

```
python3 scripts/extract_citations_from_draft.py <draft> --serial <SERIAL>
```

If it reports `NEEDS_TYPE` entries, that's a real stop, not a warning to skim past. Read what
each flagged publisher actually says about itself (its About/masthead page, or its own
self-description if the draft names one) and hand-edit `data/citations/<SERIAL>.json` to
replace `"NEEDS_TYPE"` with the correct type from `{GOV, VND, MED, ACA, TEC, IND, NPO, AGG,
SOC, ADV, ANL}`, plus a `type_basis` string carrying what the publisher's self-description
actually said. This is an admission judgment (classification spec §21), not something to
default or guess at.

## Stage 2: sync the registry and capture evidence

```
python3 scripts/build_registry.py
python3 scripts/capture_evidence.py --only <SERIAL>
```

Read the output. A `content_check.status: "insufficient"` warning on any entry means that
capture is a likely shell page (classification spec §5A) -- note which `REF-NNN` it is; the
isolated grader for that source needs to know, so it can mark `retrieval_failed` rather than
grade a document that may not actually be there.

## Stage 3: segment the draft's claims

```
python3 scripts/segment_draft.py <draft> --serial <SERIAL>
```

This requires the draft to already carry `{{< claim tag="..." claim="Cxxx" >}}...{{< /claim
>}}` blocks with `{{< cite N >}}` markers inside them. If it doesn't, that's a real gap, not
something this step can paper over: segmentation (deciding where one assertion ends and
another begins) is an authoring judgment, classification spec §2, and has to happen before
this stage, either by the person who wrote the draft or by you reading it now and adding the
tags. Do not let this script guess claim boundaries.

Read `data/claim_segments/<SERIAL>.json`. Each entry needs a `source_id` -- if any are `null`,
stage 2 didn't fully sync; re-run `build_registry.py`.

## Stage 4: isolated grading -- one Agent call per segment

For **each** entry in the segment list, dispatch a fresh `Agent` call (subagent, not a
continuation of this conversation). Give it:

- The classification spec (point it at wherever this session's copy lives -- it is
  deliberately not committed to this public repository; see `content/projects/grading-to-ledger-gap-v4-2.md`
  for why)
- `data/schema/claim-draft-1.json`
- The one source document's text for that segment's `ref` (fetched fresh in stage 2; if you
  need the raw text again, re-fetch that one URL directly rather than pulling it from the
  manifest, which stores only hashes, never the body)
- The segment's `assertion_text` as the claim description
- The segment's `source_id` and `source_type` (admission facts, not for the grader to
  re-derive)
- Explicit instructions: read only what's given, no web search, no outside knowledge, work the
  gates before forming a grade opinion, leave a field null rather than guess, and return the
  completed draft as JSON plus a note on which gate produced the grade cap

The proven prompt shape is in `scripts/prepare_regrade_test.py`'s `PROMPT_TEMPLATE` --
reuse its structure (what you have / what you do / what you must not do / record your
conditions) rather than writing a new one from scratch each time.

Collect each Agent's returned JSON. Add `"provenance": {"pool": "..."}` yourself before
writing it out -- this is issue-context (was this source part of this issue's scheduled sweep,
or backfilled?), not something the isolated grader can know, per classification spec §15A.
Write the completed draft to a temp file and run:

```
python3 scripts/claim_writer.py <draft.json>
```

This appends to `data/ledger/<SERIAL>.json` and retains the draft at
`data/claim_drafts/<SERIAL>/<claim_id>.json` automatically. If it rejects the draft, fix the
draft, not the writer -- the writer's checks are the anti-fabrication guarantee, not friction
to route around.

Repeat for every segment before moving on. Do not start authoring against a partial ledger.

## Stage 5: author or revise the article

If the draft's prose already exists (the common case, per this project's actual workflow),
this stage is reconciliation's job to check, not yours to pre-validate. If prose doesn't exist
yet, write it now, against the completed ledger, following the article specification's voice
and structure rules in full.

## Stage 6: reconciliation -- three independent Agent calls

```
python3 scripts/build_reconciliation_prompt.py --serial <SERIAL>
```

Take the printed prompt and dispatch it as **three separate fresh `Agent` calls**, each with no
memory of this conversation, each holding only the ledger and the article. Save each call's
raw output to a file, then:

```
python3 scripts/aggregate_reconciliation.py pass1.txt pass2.txt pass3.txt
```

Any pass reporting drift fails that sentence -- not majority, per classification spec §30's
agreement rule. If it reports failures, rewrite the flagged sentences in the article to match
what the ledger actually supports, then re-run all three passes once more. If a sentence still
fails after one rewrite, stop and surface it to the user rather than looping indefinitely or
weakening the sentence until reconciliation stops complaining.

## Stage 7: validate

```
python3 scripts/validate_data.py
```

Must pass clean. If it doesn't, fix the underlying data -- do not proceed to stage 8 on a
failing validation.

## Stage 8: finalize and open the PR

```
python3 scripts/finalize_issue.py --serial <SERIAL>
```

This refuses to run if validation fails, then branches, stages exactly this issue's files,
commits, and pushes. It does not open the PR -- do that yourself with the GitHub PR tool,
summarizing what graded where, any disputed claims, and any reconciliation drift that got
caught and fixed along the way. That summary is worth writing carefully: it's the only place a
reviewer sees the arithmetic that happened, since the ledger itself doesn't narrate.

## What this does not automate, on purpose

- **Topic and source selection** stay yours. This procedure starts from a draft that already
  exists.
- **Segmentation** (stage 3's prerequisite) is an authoring judgment about where one assertion
  ends and another begins, not something a script infers.
- **New-source type assignment** (stage 1) is an admission judgment, classification spec §21.
- **The merge itself** stays a human action, per this project's own stated boundary --
  automation stops at a pushed, reviewable PR.
