---
title: "Build Log: First End-to-End Dry Run of the Draft-to-PR Pipeline"
date: 2026-09-05
year: "2026"
status: "Build notes"
excerpt: "The publish-issue pipeline's eight scripted stages had only ever been proven piece by piece. Run for real, end to end, against a synthetic issue and a local fixture server standing in for the network this environment doesn't have -- and it found a real, live bug: two sources sharing a domain silently collide, and one already does, in production data."
type: "projects"
tags: ["classification v4.2", "build notes", "pipeline", "automation", "isolation"]
---

**Covers:** the first full run of the `publish-issue` skill's eight scripted stages (citation
extraction through finalize) against one synthetic issue, isolated from live data and from the
real GitHub repository, built specifically to answer a question the skill's own PR left open:
does this pipeline actually work end to end, or only in the pieces it's been tested in?
**Status:** ran clean start to finish on the second attempt. One real, live bug found and fixed
on the first attempt -- a source-resolution collision that was already sitting in production
data, not just a defect in synthetic test material. Fix shipped in this PR; no synthetic test
data went anywhere near the real repository.

## Why this needed a dry run at all

The `publish-issue` skill (this repo's documented draft-to-PR procedure) states plainly that its
next real test is running start to finish against an actual new draft, and that stages 2 onward
need real network egress this kind of session doesn't have. Both of those are still true. What
changed is that "can't fetch the real internet" and "can't test the pipeline" turned out to be
different problems: the scripts that do the fetching, hashing, resolving, writing, and validating
don't care whether the bytes on the other end of a URL came from a real news site or from a local
process serving fixed content on `127.0.0.1`. A local HTTP server standing in for the network, and
a local bare git repository standing in for GitHub, let every stage run its real code against real
requests and real git plumbing, with zero chance of either touching this site's live data or its
actual GitHub history.

## The setup

- A scratch clone of the repository, entirely separate from the working copy, with its `origin`
  repointed at a throwaway local bare repository instead of GitHub.
- A synthetic two-source issue: a vendor bulletin describing its own direct forensic recovery of
  a loader (expected grade 1), and a government advisory relaying that vendor's finding without
  independent verification (expected grade 4) -- deliberately the two most basic paths through
  the gates, so a wrong result would be unambiguous.
- Both sources served as real HTTP responses from a local Python server, so `capture_evidence.py`
  ran its actual fetch, hash, normalize, and content-presence-check code against real requests
  rather than hand-written manifest entries standing in for what a capture would produce.

## What ran, stage by stage, for real

`allocate_serial.py` → `extract_citations_from_draft.py` → (hand-filled admission judgment, per
the skill's own instructions) → `build_registry.py` → `capture_evidence.py` against the local
server → `segment_draft.py` → two genuinely isolated `Agent` grading calls, one per source,
holding nothing but that one document → `claim_writer.py` → `build_reconciliation_prompt.py` →
three genuinely isolated `Agent` reconciliation passes → `aggregate_reconciliation.py` →
`validate_data.py` → `finalize_issue.py`, which branched, staged, committed, and pushed to the
throwaway remote.

Both claims graded exactly as designed: grade 1 for the vendor's own forensic recovery, grade 4
for the government relay. The two archive.org submission attempts failed, as expected with no
real internet -- and `capture_evidence.py` correctly recorded that failure without blocking the
attestation it doesn't depend on, exactly as its own design intends.

## Reconciliation caught a real overclaim, on the first pass

The synthetic article's first draft described the vendor as having "confirmed" the persistence
mechanism. All three independent reconciliation passes flagged it, unanimously, on the first try:
the claim's own computed assertion license explicitly states "do not say established, confirmed,
or verified" for a grade 1 attributed observation, and the word was sitting right there in the
tagged sentence. This wasn't a contrived test of the reconciliation prompt -- it was an ordinary
authoring mistake, the same kind classification spec §30 describes reconciliation existing to
catch, and it got caught by three fresh instances that had never seen the mistake being made.
Rewriting the sentence to attribute the finding rather than assert it as confirmed fact cleared
all three passes on the re-run, and the aggregated result was clean.

## The bug: two sources, one domain, one dict key

`extract_citations_from_draft.py` and `segment_draft.py` both resolve a citation's registered
source by looking its domain up in a dictionary built as `{canonical_domain: entry for entry in
registry}`. That comprehension keeps only the last entry for any domain that appears more than
once. In the synthetic test, both fixture URLs happened to share a domain (the local server), and
the second call silently overwrote the first: `segment_draft.py` resolved *both* claims to the
second source's ID, meaning the first claim would have been graded correctly but ledgered as
though the vendor bulletin were the government advisory.

**This is not a synthetic-only failure mode.** The live registry already has one domain with two
distinct registered sources -- `cisa.gov`, carrying both "CISA Cybersecurity Advisories" and the
"CISA Known Exploited Vulnerabilities (KEV) Catalog" as separate entries -- and one already-drafted
citations file (`data/citations/TI-20260903-001.json`) cites both of them in the same issue. No
ledger has been written yet for that issue (no `data/ledger/` directory existed before this dry
run), so nothing shipped wrong. But the very next real run touching that issue would have hit this
collision for real, silently, with no error and no warning -- exactly the failure mode a script
whose whole job is removing manual retyping is supposed to prevent, not introduce.

**The fix.** `segment_draft.py` now resolves against `(domain, canonical_name)`, matching the key
`build_registry.py` itself already uses -- unambiguous, since by the time segmentation runs, the
citation's `canonical_name` is an admission judgment a human has already confirmed.
`extract_citations_from_draft.py` runs earlier, before that confirmation exists, so a domain with
more than one registered candidate is resolved by matching the guessed name against the
candidates; where that still doesn't land on exactly one match, the citation is left `NEEDS_TYPE`
with the ambiguity and the candidate names spelled out, rather than guessing. That's the same
admission discipline the script already applies to a genuinely new domain, extended to cover a
domain that's new to *this specific source* even though it isn't new to the registry.

Both fixes were checked against the live registry's actual `cisa.gov` collision, not just the
synthetic fixture: a new CISA URL with an unmatched name correctly lands on `NEEDS_TYPE` with both
existing candidates listed, and a URL whose name exactly matches one of them still resolves
cleanly to that one.

## What this dry run didn't test

`capture_evidence.py`'s archive.org submission path failed for a real reason (no internet) rather
than being verified against a working archive call. The `--refresh` and `--retry-archive` flags,
the multi-source composite-claim split in `segment_draft.py` (a claim citing more than one
source), and a claim that reconciliation genuinely can't resolve after one rewrite (the skill's
own instruction to stop and surface it rather than loop) are all still unexercised end to end.
Those are the next candidates for a second dry run, not evidence this one settled everything.

## What's committed here and what isn't

Only the two script fixes are part of this change. The synthetic draft, its fixture HTML, the
throwaway git remote, and every file the test run produced (citations, registry entries, ledger,
claim drafts, evidence manifest) lived entirely in an isolated scratch clone and were never staged
against, committed to, or pushed from this repository's actual working copy.
