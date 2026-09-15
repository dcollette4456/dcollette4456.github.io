---
title: "Build Log: A Working Draft-to-PR Pipeline, Without an API Key"
date: 2026-09-05
year: "2026"
status: "Build notes"
excerpt: "Scoping and building the first real slice of the automated authoring pipeline: citation extraction, claim segmentation, and isolated grading and reconciliation proven live using Claude Code's own subagent tool instead of a separate API integration. What's tested and working, and the one hard wall found along the way."
type: "projects"
tags: ["classification v4.2", "article spec v2.9", "build notes", "automation", "pipeline"]
---

**Covers:** scoping and building the first working slice of a pipeline that
takes a drafted issue from citations-in-prose to a pushed, ready-to-open pull
request, largely without a person retyping anything by hand in between.
**Status:** four new scripts and one schema change, tested individually and,
for the two steps that needed it, tested live against genuinely isolated model
calls. Committed to `claude/pipeline-automation`, branched off the v4.2/v2.9
amendments work. No PR opened yet.

## The question this answers

The classification spec has always described an "isolated grading pass" and a
"fresh instance" for reconciliation without saying how either one actually
gets invoked. Read literally, both sounded like they needed a separate
Anthropic API integration: an API key, a client library, a place to run it.
None of that exists in this environment, and setting it up would have been a
real piece of infrastructure with its own cost and its own failure modes.

It turns out not to be necessary. Claude Code's own `Agent` tool spawns a
subagent with no memory of the calling conversation, which is exactly the
property both stages actually require: a context holding one document and
nothing else, or a context holding the ledger and the article and nothing
else. That is the mechanism this session built and tested against, not a
weaker substitute for one, and it costs nothing beyond what a normal session
already has.

## What got built

**Shell-capture content-presence check.** `capture_evidence.py` fetched and
hashed cleanly even when the captured page was a consent screen or an empty
client-rendered shell, HTTP 200, healthy byte count, hashes fine, and the
silent-edit check would report the document unchanged forever. This is the
gap the previous session's re-grade run found on a live GovInfoSecurity
capture. A length heuristic now flags a capture as `content_check.status:
"insufficient"` when the normalized text is too short to plausibly be an
article. It is disclosed as a heuristic, not the full assertion-text match the
specification actually calls for, since that check needs a claim's text and
this script runs before any claim exists. `manifest-2.json` adds the field;
the nine existing manifests, captured before it existed, still validate.

**`extract_citations_from_draft.py`.** Reads a draft's own References section
and writes `data/citations/{serial}.json`, so a draft handed over doesn't need
its sources retyped. Parses both citation formats already live on the site:
the `{{</* src */>}}` shortcode and the raw `<li id="ref-NNN">` list. Reuses an
already-established source's type rather than guessing; a genuinely new
domain is flagged `NEEDS_TYPE` rather than assigned one, since that judgment
call was made author-supplied on purpose in the last round of amendments.

**`segment_draft.py`.** Turns a draft's existing `{{</* claim */>}}` tags into the
per-source grading task list, applying the same composite-claim split logic
from the earlier re-grade tooling. Deliberately does not invent claim
boundaries; deciding where one assertion ends and another begins is the
judgment call the composite-claim rule is about, and a script confidently
declaring that boundary without actually reasoning about it would be the same
failure with extra steps.

**Isolated grading, proven live.** A fresh Agent call, holding only the
specification, the schema, and one synthetic source document, produced a
schema-valid claim draft. It self-disclosed `topic_framing_present` on its
own initiative, left actor and entity fields empty where the document didn't
support them, and ran cleanly through `claim_writer.py` to a computed grade.

**Reconciliation, proven live.** Built a synthetic ledger with one hedged,
attributed claim and one plain factual claim, and an article with one
faithful restatement and one deliberate overclaim, the hedge and the
attribution both dropped, stated as flat fact. Three independent fresh Agent
calls, none aware of each other or of this session, all caught the same
overclaim and cleared the same faithful sentence. `aggregate_reconciliation.py`
implements the specification's actual agreement rule, any pass reporting
drift fails the sentence, not majority, and survived a real messy model
response encountered during testing (a pass that talked through a
self-correction before landing on its final answer).

**`finalize_issue.py`.** The last mechanical step: refuse to run if
`validate_data.py` fails, then branch, stage exactly one issue's files, commit,
push. Opening the pull request itself stays a separate step, since that's a
GitHub API call through the MCP tools in this environment, not something a
shell script holding push credentials should also do quietly.

## The wall

This remote session's network egress is blocked for arbitrary domains,
confirmed against a real government site through both a raw fetch and the
harness's own web-fetch tool. Evidence capture, and any live source fetch a
grading call would need, cannot run inside this session. That isn't a new
problem, the existing capture tooling already documented it, but it means the
network-touching steps in this pipeline have to run somewhere with open
egress: your own machine, or a Claude Code environment configured for it.
Everything that doesn't touch the network is built, tested, and ready now.

## What this adds up to

Hand this pipeline a draft with citations already in it, and extraction,
segmentation, isolated grading, and reconciliation all have working code
behind them today, including the two steps that looked like they'd need
separate infrastructure. What's left standing between this and one
continuous run is a real draft to point it at, and wherever the fetch step
actually runs.
