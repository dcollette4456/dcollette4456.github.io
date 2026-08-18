# Classification System v3.8
## Mechanical grading, source measurement, and tagging for an automated intelligence product

**Prepared:** 19 August 2026
**Status:** Consolidated and implementable. Single authoritative document.
**Supersedes:** `Classification_System_v3-7_Spec.md` and `Classification_System_v3-6_Spec.md` and `Classification_System_v3-5_Spec.md` and `Classification_System_v3-4_Spec.md` and every earlier version and module document, all folded in here.
**Companion:** `Article_and_Site_Design_Specification_v2-5.md`
**Project:** Knights Who Say Ni. Static Hugo site, GitHub Pages, automated publication, DoD threat hunting audience.

### The two standards this system serves, in order

**First. Give the reader the best factual information available to conduct threat hunting.** Threat hunting is conducted against behavior. Indicators are for blocking and for SIEM population, and the reader's own tooling handles those. What this product owes a hunter is observed behavior, where it would be visible, and how much of it can be checked.

**Second. Keep the model generating the articles as honest as possible.** Every grade computed from observable properties of a document, every judgment fenced and traceable, nothing asserted that a reader cannot check or that the product cannot show its work for.

Where the two conflict, the first wins. Section 1A states how.

### What changed from 3.7

Presentation only, and only in §16. No grading rule, gate, schema, or block changed, and a 3.7 ledger is a valid 3.8 ledger.

Section 16 was rewritten in 3.7 against a reference implementation that was live for about one release. Direct feedback after publishing the first issue under it: the new typeface and the margin-hanging tag weren't wanted, and printing the full type/grade legend inline read as clutter rather than an aid. Section 16 now describes the site as it actually renders after that feedback, which is the second reference implementation in as many versions.

1. **Typography and color revert to the pre-3.6 system.** Spectral serif, JetBrains Mono, maroon `#7d2231`, the two-tone paper-on-page background. Georgia, SF Mono, crimson `#a8385a`, and teal `#1a3d5f` are retired after one release
2. **The page shell reverts to the two-column article layout:** a 236px sidebar (Contents, Hunt Priorities, At a Glance) beside an 860px article body, inside a 1400px centered card, breakpoint at 768px. The 190px sticky rail, 112px page-grid gap, and 960px breakpoint from 3.7 are retired
3. **The claim tag no longer hangs in the margin.** It renders as an inline chip at the start of the claim, because the two-column layout reserves no gutter for a hanging tag to hang into. This is also, not coincidentally, the convention the site used before the margin-tag idea was tried
4. **The reader legend no longer prints its full explanation inline for a current-version issue.** One line prints where the box used to be, pointing to `/coverage/legend/`. A pre-versioning issue (Iran, DPRK) keeps its original four-category box unchanged, since that content was never the complaint
5. **At a Glance reverts to the vertical sidebar box** every issue on the site has always used, rather than the four-field horizontal grid tried in 3.7. It renders whatever fields the issue actually carries, including as few as two, with no fabricated fields to fill a fixed grid shape
6. **The hunt block keeps its 3.5 prose-first structure** (label, then reasoning, then a footer line for stage and telemetry) but is restyled from the blue-tinted card to the site's original maroon hunt-priority box
7. **Source summaries keep their 3.5 content shape** (title, byline, date, one paragraph) but are restyled to the original bordered card rather than the blue-adjacent 3.7 treatment

`PRC_issue_baseline_v2.html` replaces `PRC_issue_sitelayout.html` as the reference implementation and remains authoritative over this document on presentation. The superseded file described a page shell that shipped and was reverted within about a day; it is kept for the historical record in the 3.7 changelog above but should not be used to build anything new.

### What changed from 3.6

Section 16 gained "The page shell," a masthead fixed at five fields, the full title in the `h1`, the reader legend as a bordered box, a corrected responsive breakpoint, and a corrected margin-tag offset. All of the presentation specifics from that pass were superseded one release later by the 3.8 changes above; the structural ideas that survived (masthead order, five-field metadata row, dossier strip, prose-first hunt blocks, pointer-not-inline-dump legend) are described under their current, reverted styling in this version's §16.

### What changed from 3.5

Two groups. Six defects found by executing this specification by hand against real sources, and a rendering rewrite driven by reading the result.

**Defects found in the dry run.** Each was a rule that produced wrong output, not a matter of taste.

1. **Gate 5 no longer applies the method test to `TEC` claims.** A catalog entry states no observation method because the record *is* the observation. Under 3.5 every structured record graded 2 instead of 1, permanently, across the whole type
2. **Section 6's duplicate block keys on document version, not source.** Two articles from one publisher in one issue is routine, the fingerprint correctly keeps them separate, and 3.5 would then have held the issue
3. **`huntable` is restricted to grades 1, 2 and 3.** A relay describes hunt surface another source established. Counting both double-counted the headline metric
4. **A third pool value, `corroborating`,** for out-of-window sources cited only to establish independence. Neither `live` nor `backfill` was correct and 3.5 offered no third option
5. **The reconciliation pass compares against the assertion list,** not only the claim `text`. A merged claim's text is vaguer than the assertions behind it, which would have let the pass under-fire
6. **Section 12's threshold estimate is corrected** from five months to seven or eight at monthly cadence. A dense vendor report yields about two claims, not the three or four assumed

**Rendering rewrite, section 16.** The measurement system had crowded out the article. Tags interrupted sentences, source entries became scorecards about sources rather than summaries of what they found, and metadata that belongs in the ledger was printed on the page. Section 16 is rewritten around one rule, stated there and worth stating here: **grading metadata is machine layer and coverage-page material, and does not appear in the article.**

### What changed from 3.4

Eleven changes. Three follow from restating the standards above, which corrected a bias in 3.4 toward indicators over behavior.

1. **Section 1A states the disclosure doctrine.** Label rather than withhold. Withholding a claim is no longer a mechanism anywhere in this system
2. **Section 9 redefines actionability around behavior.** 3.4 made a claim actionable if it carried "an artifact or an ATT&CK technique identifier," which counted a bare file hash as hunt value. Hashes are blocklist entries. The new tests are `behavioral`, `huntable`, and `indicator_bearing`, and they are separate axes. The collection point behind `huntable` may be derived by mapping onto a closed telemetry class vocabulary rather than requiring the source to name one, because SIEM architectures differ too much for a vendor's naming to travel
3. **Section 9 states why indicators are pointed at rather than published,** so a future revision does not helpfully "fix" it
4. **Section 15 removes withholding from the review path.** Grader disagreement now publishes at the most conservative disputed vector with a `disputed` mark
5. **Section 14 removes the archive publication block.** A failed archive is disclosed on the claim, not grounds to drop it or hold the issue
6. **Section 16 governs the Appendix A evaluation sentence,** which was the last piece of ungoverned model prose in the product
7. **Section 6 adds a body-to-ledger reconciliation block.** A legitimate tag on an overstated sentence was the most likely real failure and was unguarded
8. **Section 14 extends the prose rule to the ledger `text` field**
9. **Section 8 makes the Hunt Priority block an `ANL` construct** with named inputs, since it is analyst opinion and the reader is entitled to see it framed that way
10. **Section 9 adds coverage continuity,** resolving open decision 9. Silence is now distinguishable from not looking
11. **Section 18 names the `ANL-High` limit** rather than leaving it to be discovered

---

## 1. WHAT THIS SYSTEM IS FOR

Two questions, answered separately, for every issue this product publishes.

**Per claim:** how much of this can a reader establish without trusting anyone? Answered by a grade, `1` through `5`, computed from observable properties of the source document.

**Per source:** how has this source behaved across everything ever cited from it? Answered by a record that accumulates automatically and that nobody assigns.

The second question is the one no other OSINT product answers, and it is only answerable because the first one is mechanical. If grading required judgment, the record would measure the grader rather than the source.

**The defensible claim is not neutrality.** It is this:

> Every grade is produced by a published rule applied to observable properties of a source document. The same document read twice grades the same. Anyone running the procedure against the same sources reaches the same numbers.

**Stated precisely, because the loose version is not quite true.** Reproducibility has four requirements and the system has to carry all of them. The rule must be published, which section 5 does. The unit the rule applies to must be defined, which section 2 does. That unit must be stable across time, which the fingerprint in section 2 provides. And the identity of whatever executed the rule must be recorded, which section 15 does.

**One human touchpoint exists.** Override publication is human-initiated, section 11. Grader disagreement is routed to human review, but review is not a gate: the claim publishes first, marked, and review happens afterward. Nothing in the pipeline waits on a person.

**What the system does not do.** It does not predict. A grade 1 observation of infrastructure staging is not a forecast that the infrastructure will be used. It does not filter, because weak material publishes at a weak grade rather than being suppressed. And it does not decide anything for the reader. Two analysts can read an issue and disagree completely about what happens next, which is fine, as long as they cannot disagree about what was observed and who observed it.

---

## 1A. THE DISCLOSURE DOCTRINE

**Label rather than withhold.**

The product's default is to publish what it found and describe honestly what is wrong with it. A weak claim publishes at a weak grade. A contested claim publishes marked as contested. A claim whose archive attempt failed publishes with the failure printed. A claim built on an unreachable primary publishes at grade 5 with the legend telling the reader not to build a hunt on it.

**Withholding a claim is not a mechanism in this system.** 3.4 withheld claims on grader disagreement and dropped them on archive failure. Both removed real information from a hunter to protect a tidier-looking output, and both were wrong under the first standard. If a hunter needs to know something, the answer is to publish it and say what is uncertain about it. Readers of this product are professionals who form their own judgments, and the tag exists so they can.

**Three things still stop publication, and all three are integrity failures rather than weakness.** Fabrication, an unresolvable contradiction between the article and the ledger, and a missing grader record. Section 6 lists them. In each case the issue is held until the failure is corrected, because the fault is in the product rather than in the evidence. Nothing is held because the evidence is thin.

**The one asymmetry.** A grade 5 claim may not stand alone as the basis of a hunt recommendation, per section 6. That is not withholding. The claim publishes, in full, tagged; it simply cannot be the only thing underneath a directive telling a hunter where to spend an afternoon.

---

## 2. THE UNIT OF CLASSIFICATION

**A grade attaches to a claim-source pair. Never to a document, never to an organization.**

One vendor report can produce a `VND-1` on the infection chain it reconstructed and a `VND-3` on the prevalence figure three paragraphs later. Both correct, different evidence.

**Tag the source actually read.** If a trade outlet reports a Microsoft finding and the pipeline did not retrieve Microsoft's post, the tag is `MED`. The grade then describes how far the document read sits from the observation.

**The source record counts claims, not documents.** A vendor that publishes one excellent report a year and gets cited forty times from it does not thereby have forty good documents.

### What counts as one claim

Every published number in this system is a ratio whose denominator is a count of claims. Fifteen claims before a record publishes. Seventy-two percent grade 1. The grade 5 rate, which section 12 calls the headline number. If two runs can decompose the same report into twelve claims and four claims, both defensibly, then those percentages are not comparable across sources, across issues, or across time, and no amount of rigor in the gates repairs it. The gates are the reproducible part of this system. Segmentation is the part that has to be made reproducible.

**The rule.** A claim is the largest span of assertion from a single document version that returns identical answers on every gate in section 5. Where a gate answer changes, the span splits. Where no gate answer changes, it does not.

**The procedure.** Three steps, in order, and the count is an output of step three rather than a decision made in step one.

1. **Extract the assertions the issue uses.** Not the whole document. Segmentation runs over what the issue actually cites from a source, which is what the source record is measuring. A forty page report contributes the four assertions the issue drew from it
2. **Reduce to atomic assertions.** One subject and one predicate, stated by the source, standing alone as a statement of fact. Compound sentences split here. Do not merge or judge at this stage
3. **Merge on identical gate vectors.** Run the gates against each atomic assertion. Any two assertions from the same document version with identical vectors across type, retrievability, direct observation, aggregate, artifact, method, and hedge become one claim. Adjacency in the document is irrelevant

The merge step is what makes the count deterministic. Two people disagreeing about whether a paragraph is one thought or three will still produce the same final count, because the gate vector decides and the vector is computed rather than chosen.

### The claim fingerprint, and why claims persist

**A claim is identified by its fingerprint, and the fingerprint is stable across issues.**

```
claim_fingerprint = source_id | document_sha256_normalized | gate_vector
```

This is the merge rule with its scope widened past the issue boundary. If two assertions from the same version of the same document hold the same gate vector, the system has already decided they are one claim. That decision does not stop being true next month.

**What this fixes.** Under 3.3, claims were per issue and the record recounted from scratch, so a claim cited in twelve consecutive issues contributed twelve entries to the source's distribution. A single unsubstantiated government assertion, referenced monthly while a story stayed live, would have driven that agency's grade 5 rate on the strength of one claim. The headline number would have measured how often the product mentioned something rather than how often the source failed to substantiate anything.

**Two counters, both printed.**

| Counter | Meaning | Used for |
|---|---|---|
| `unique_claims` | Distinct fingerprints ever built on this source | The denominator for every published distribution and rate |
| `citations` | How many times those claims were used across issues | Displayed separately. Never a denominator |

**Consequences.**

- A recurring story inflates `citations` and leaves `unique_claims` untouched, which is correct
- A source revising a document produces a new normalized hash and therefore new fingerprints. That is also correct: a revised document is different evidence, and the revision is separately recorded under section 14
- The claims index at `/data/claims/index.json` holds every fingerprint with its first issue, its grade, and its citation list. It is the join between the per-issue ledgers and the source records
- Fingerprint collision within one issue is the section 6 duplicate block. Fingerprint recurrence across issues is expected and is the citation increment

**Consequences of the merge rule, worth stating so they do not get relitigated.**

- A claim never spans two sources. Two sources asserting the same thing is corroboration, section 7, and it is counted there
- Restatement is not a second claim. A finding stated in a summary and again in the body is one claim, because the vectors are identical
- Compound assertions split where the evidence differs. "The actor compromised the water utility and the regional grid operator," with published artifacts for the first and none for the second, fails the artifact test on one half and passes on the other. Two claims, grades 1 and 2
- Grade and sector are not merge criteria. Two assertions can both grade 2 and stay separate if they got there through different gate answers, because the vector is the test, not the digit
- A claim cited in three sections of one issue is one claim in the ledger

**The check.** Two claims from the same source in the same issue holding identical gate vectors means step three did not run. That is a publication block in section 6, and it is mechanically checkable against the ledger without anyone reading the article.

**Worked example.** A vendor report contributing five atomic assertions to an issue: the infection chain with hashes and an IR engagement described, the C2 infrastructure with domains from the same engagement, the loader behavior with no artifact published, a prevalence figure from the vendor's telemetry, and an attribution to a named actor carried from a different vendor's earlier report. Vectors: the first two are identical and merge. The third differs on the artifact test. The fourth is caught at gate 4. The fifth is caught at gate 3. Four claims, grades 1, 2, 3 and 4, from one document.

Cite the same report again next cycle for the same four assertions and the source gains zero unique claims and four citations.

---

## 3. TYPE VOCABULARY

Assigned once per source in the registry, looked up thereafter.

| Tag | Covers | Standing bias to disclose |
|---|---|---|
| `GOV` | Government agency, advisory, statement, court filing, indictment | Publication timing and attribution naming are policy acts. Advisories often rest on vendor reporting without saying so |
| `VND` | Commercial security vendor research, IR reporting, blog | Sells something. Telemetry is a customer population. Does not publish on actors it cannot see |
| `MED` | News and trade press | Relay. Compresses source hedging into flat assertion. Headline incentive |
| `ACA` | Academic and peer-reviewed | Slow, usually rigorous, often superseded on arrival |
| `TEC` | Structured record: CVE entry, KEV catalog, RFC, repository, patch note, certificate log | Minimal interpretation. States what it states |
| `IND` | Independent researcher, personal blog, conference talk | No editorial layer, no correction process. Reputation is the only filter |
| `NPO` | Non-profit and community: Shadowserver, Spamhaus, Team Cymru, ISACs, non-governmental CERTs | Mission-driven rather than commercial, but scan and sinkhole populations are still populations |
| `ADV` | Adversary-controlled: leak site, ransom note, actor claim, forum ad | Self-serving. The post is evidence the claim was made, not that the event occurred |
| `ANL` | The author. Not a source | This product's own judgment |

**Structured records take `TEC` regardless of publisher.** A CISA KEV entry is `TEC`. A CISA intrusion advisory is `GOV`. Without this rule one organization produces two very different kinds of evidence under one prefix.

**New sources.** The pipeline creates registry entries autonomously on first citation, assigning type from the publisher's self-description and domain. New entries carry `record: insufficient` until the sample threshold in section 12 is met.

---

## 4. THE GRADE SCALE

| Grade | Name | What it tells the reader |
|---|---|---|
| **1** | Direct, fully evidenced | The source saw it and showed its work. You can check the artifacts |
| **2** | Direct, partially evidenced | The source saw it but did not publish enough for you to check |
| **3** | Direct, aggregate | The source saw it in data only it holds. Nobody outside can reproduce the number |
| **4** | Relay | The source is repeating a named finding it did not observe |
| **5** | Unretrievable | The evidence trail ends somewhere nobody can open |

The digit means the same thing under every prefix, because it measures the claim's evidentiary posture rather than the industry the publisher sits in.

**The digit does not describe how easily a reader can obtain the document.** That is the `access` mark, section 5A.

**The digit does not describe hunt value.** A grade 1 claim can be useless to a hunter and a grade 3 aggregate can change how a hunt is scoped. Hunt value is measured separately in section 9 and the two are deliberately independent.

---

## 5. THE GATES

**The gates cap the grade. They do not block publication.** A claim that fails everything publishes at grade 5 with the tag saying so. Suppressing weak material would hide the part of the news cycle a reader most needs to learn to read.

Apply in order. First match wins. Every gate is a yes or no question about text in front of the model.

**Gate 0. Is the author the source?**
Own inference, synthesis, correlation, forecast, or recommendation is not a sourced claim. Takes `ANL` and a confidence word. Stop.

**Gate 1. Assign type.**
Registry lookup. Where no entry exists, create one from the publisher's self-description and domain, mark it `record: insufficient`, and proceed. A missing entry is a first citation, not an error. Structured record overrides to `TEC`.

**Gate 2. Can the reader reach the evidence?**

- **The trail ends in something nobody can open.** Unnamed researchers, a private briefing, a deleted or unarchived post, or a firm's finding existing only as a press quote with no published report: **grade 5.** Stop
- **The primary is a real document the pipeline could not retrieve,** and the claim therefore rests on someone else's account of it. Grade the document actually read. That document is a relay and gate 3 will land it at 4, which is correct because the pipeline did not see the primary either
- **The document was retrieved but sits behind a paywall or subscription a reader may not pass.** Grade normally through the remaining gates and attach `access: gated`. Continue

**Gate 3. Did the cited source observe this itself?**

Own IR engagement, own sensors, own scan or sinkhole, own artifact recovery, own network, own catalog, own repository, own court record.

- If it is reporting a named finding from elsewhere: **grade 4.** Stop. A government advisory built on vendor reporting is `GOV-4` unless the advisory states its own collection. Common, and usually invisible
- **If the document neither describes an observation of its own nor names another source as the origin, the assertion has no traceable origin at all.** Return to gate 2's first outcome: **grade 5.** Stop

**On the no-origin rule.** Under 3.3 an outlet asserting a technical finding on its own authority, naming nobody and describing no method, could pass gate 3 as its own observer, fail the artifact and method tests, and land at grade 2. That is badly wrong. It is also the default mode of trade press and of a certain kind of vendor blog. Section 13's worked example depends on the correct outcome: an assertion made with nothing behind it is unretrievable, because there is nothing to retrieve.

**Observation basis is established per document or per engagement, not per sentence.** A report that says "we responded to an intrusion at a European manufacturer" has stated its basis for every assertion arising from that engagement. Requiring the basis restated per assertion would fail almost everything and would be a misreading.

**Gate 4. Is the claim an aggregate over the source's private data?**
Population statistics, prevalence figures, percentages, trend counts. If yes: **grade 3.** Stop.

The test is not whether the source has telemetry. It is whether this claim is a statement about a population nobody else can recount.

**Gate 5. Evidence completeness.**

| Test | Question | Applies to |
|---|---|---|
| **Artifact** | Does the document publish at least one independently checkable artifact for this claim: hash, IP, domain, URL, file path, registry key, certificate, CVE ID, ATT&CK technique ID, detection rule? | Every claim |
| **Method** | Does the document say how it observed this: IR engagement, honeypot, sinkhole, scan, sample provenance, telemetry? | Every claim except `TEC` |
| **Hedge** | Where the claim is inferential, does the document state a confidence level or explicitly decline to assert? | Attribution, intent, actor linkage. Not applicable to direct factual observation |

All applicable tests pass: **grade 1.** Any applicable test fails: **grade 2.**

**The method test does not apply to `TEC` claims.** A structured record does not describe an observation because it constitutes one. A CVE record, a KEV entry, a certificate log, a repository commit: none of them state a collection method and none of them can. Where the type is `TEC`, `method_test` returns `n/a` and does not bear on the grade.

Without this carve-out every `TEC` claim caps at grade 2 forever, which is what 3.5 did. It was found by walking a KEV entry through the gates by hand, and it would have marked the most checkable source class in the system as partially evidenced on every issue.

**The artifact test here measures checkability, not hunt value.** A hash satisfies it. That does not make the claim huntable, and section 9 keeps the two apart.

---

## 5A. THE ACCESS MARK

Separate from the grade, because it answers a separate question.

| Value | Meaning |
|---|---|
| `open` | A reader can reach the document at no cost. Default, not printed |
| `gated` | The document was retrieved and graded, but a reader may need a paid subscription or registration to reach it. Printed |
| `withdrawn` | The document has since returned 404 or 410. The archive pointer becomes the citation. Printed |
| `unarchived` | No archive provider captured it. The citation stands and the reader is told the copy is not backed up. Printed |

**Rendering.** `VND-1 · gated`. The mark never changes the digit.

**Why `gated` exists.** A paywalled direct observation with published artifacts is not a relay and is not unreachable. A reader can check it, for money, which is a materially different position from both. Sharing the grade 4 digit with relay was wrong in three ways at once: it told readers the source was repeating someone else's finding when it was not, it tripped the block requiring a grade 4 claim to name its primary, which a primary cannot do, and it barred the claim from contributing corroboration when it is exactly the kind of independent observation corroboration is for.

**Why `unarchived` exists.** 3.4 blocked publication of a grade 1 or 2 claim that no archive provider captured. Under the disclosure doctrine that is the wrong trade: it removes a real, well-evidenced observation from a hunter because a third-party service was unavailable. The claim publishes, the reader is told the copy is not backed up, and the exposure is on the page rather than hidden by omission.

**Corroboration.** `gated` and `unarchived` do not affect eligibility. The independence gate does not care what a document costs or whether a crawler reached it.

**Disclosure.** The Scope and Sourcing section of every issue states the gated position and the unarchived count.

---

## 6. PUBLICATION BLOCKS

**The floor is fabrication and self-contradiction, never weakness.** Under the disclosure doctrine, no claim is ever held for being thin, contested, unarchived, or unpopular. An issue does not publish if any of the following are true, and in every case the fault is in the product rather than in the evidence.

**Evidence integrity**
- A claim tagged grade 1 or 2 with no fetch record
- A claim tagged grade 1 whose cited artifacts do not appear in the extracted artifact list
- A claim tagged grade 4 that does not name its primary in the text
- A byline, publication date, title, or quotation not transcribed from the retrieved document
- A citation with `archive: not_attempted`. Attempting is required. Succeeding is not
- A ledger entry containing prose from a source document, outside the bibliographic carve-out. This includes the claim `text` field

**Article to ledger reconciliation**
- A tagged sentence in the article carrying no `data-claim` identifier
- A `data-claim` identifier with no matching ledger entry
- A tagged sentence asserting more than its ledger claim asserts, as determined by the reconciliation pass in section 15

That last block is the one that catches the most likely real failure. A fabricated tag is easy to detect and rare. A legitimate tag attached to a sentence that quietly widens the claim is the default drift direction for a model writing prose from structured input, and until 3.5 nothing looked for it.

**Segmentation and grader integrity**
- Two claims from the same **document version** in the same issue with identical gate vectors, which means the merge in section 2 did not run. The check runs on fingerprints, which already encode document version. It does **not** key on source: two articles from one publisher in one issue is routine, they carry different document hashes, and section 2 correctly keeps them separate
- Two claims in the same issue sharing a fingerprint
- A claim whose recorded gate vector does not match its published grade, unless the claim is marked `disputed`, in which case the published grade must match the most conservative recorded vector
- A claim with no `grader` block, or a `grader` block naming a spec version other than the one the issue was built under

**Grading integrity**
- A grade assigned with no corresponding ledger entry
- A claim whose grade cites information dated after the source's publication date
- A corroboration count above 1 with no recorded independence basis
- An alias equivalence recorded with no source statement behind it
- A canonical actor name that does not match the earliest dated attribution in the table

**Analytic integrity**
- An `ANL` block that does not name its input claim identifiers. This includes Hunt Priority blocks and Appendix A evaluation sentences
- An `ANL-High` with no grade 1 or grade 2 input
- A grade 5 claim standing alone underneath a hunt recommendation
- An Appendix A evaluation sentence asserting anything not derivable from the record fields printed on that card or from claims cited from that source in this issue

**Tagging integrity**
- A sector tag with no justifying claim identifier
- An actor tag with no justifying claim identifier
- A `huntable` mark carrying no telemetry class from the section 9 vocabulary, or carrying a value outside it
- A `huntable` mark on a claim not marked `behavioral`

**Record integrity**
- A backfill claim pooled into a live distribution
- A derived standing signal computed from anything other than the live pool
- A published distribution whose denominator is `citations` rather than `unique_claims`

Each block logs `blocked: reason` and holds the issue. Every one is a checkable contradiction between what the article asserts and what the ledger contains, or an instance of the product inventing something. None require a judgment about whether a claim is any good.

**A pipeline is not required for these blocks to apply as authoring discipline.** An issue written directly against these specs without a ledger (see article spec §13 and §15) cannot be mechanically checked against these blocks, but the author, human or model, should still follow the reconciliation and integrity rules by hand: no claim widened past what its source said, no tag without a reason, no fabricated field.

**Removed in 3.5.** The block on a withheld claim appearing in the body, and the block requiring a successful archive for grades 1 and 2. Both existed to enforce mechanisms the disclosure doctrine retired.

---

## 7. CORROBORATION

A separate mark on the claim: `×2`, `×3`.

**The independence gate.** For each additional source, one question: did this source publish evidence drawn from data the first source did not provide or publish?

Rules that follow:

- Only grades 1, 2 and 3 can contribute. A relay has no independent data by definition. Four outlets repeating one vendor disclosure is `×1` and the relays tag `MED-4`
- `access` values do not affect eligibility
- Two documents from the same publisher never count as two, including across corporate boundaries that exist only on paper
- Two vendors analyzing the same public sample are `×1`. One sample, two readings, zero independent collection
- A government advisory citing vendor reporting the issue also cites is `×1` unless the advisory names its own collection
- The basis string is recorded and printed: `independent victim populations, three month separation`

**The alias gate.** Corroboration across sources using different actor names requires a stated equivalence in the cluster table. See section 10. A disputed or absent mapping blocks the increment rather than assuming identity.

This is the single most important rule in the system, because it is where "everybody is reporting this" gets correctly downgraded to "one organization is reporting this and everyone else is quoting them."

---

## 8. ANALYST BLOCKS

`ANL` takes no digit. `ANL-High`, `ANL-Moderate`, `ANL-Low`, from ICD 203.

- Every block names the specific claim identifiers it rests on. No exceptions, and section 6 blocks the omission
- Confidence is capped by inputs. Only grade 4 and 5 inputs caps at `ANL-Low`. No grade 1 or 2 input means it cannot be `ANL-High`
- One per major section, except where noted below

### What is an `ANL` block

Four things in this product are the author speaking, and all four carry `ANL` treatment.

| Element | Notes |
|---|---|
| Standalone analyst notes | The general case. One per major section |
| **Hunt Priority blocks** | New in 3.5. See below |
| **The executive summary** | Synthesis across sources is gate 0. It is the section's `ANL` block and is exempt from the one-per-section limit |
| **Assessment and outlook** | Forecast. Same exemption |
| **Appendix A evaluation sentences** | Governed in section 16 |

3.4 left three of those five unmarked, which meant the published issues tagged synthesis as though it were sourced material. It is not, and a reader is entitled to see which is which.

### Hunt Priority blocks

**A Hunt Priority block is the product's suggestion, not a sourced finding, and it says so.**

It is built from corroborated observation plus the product's own reading of where that observation would be visible. The reader knows the reading came from a model, and framing it as anything else would be dishonest. What the reader is owed is the inputs.

```
Hunt Priority [Presence-stage indicator]
[ANL-Moderate | inputs: C014, C019, C022]
Collection point: EDR driver-load telemetry, Sysmon Event ID 6
```

- The block names its input claim identifiers, like every other `ANL` construct
- Confidence is capped by inputs, like every other `ANL` construct
- **It is not blocked for lacking a huntable input.** Where the observed behavior is real but no source named a collection point, the product proposing one is useful and the `ANL` framing plus the confidence cap already tells the reader what it is. Blocking it would leave a hunter with less than they came for
- Where every input is grade 4 or 5, the block caps at `ANL-Low`, which is the honest signal that the suggestion rests on thin ground

**The one hard rule survives:** a grade 5 claim may not stand alone as the sole input. Section 6 blocks it. A directive telling a hunter where to spend an afternoon needs at least one claim someone can reach.

### Forecasts

Marked and entered into standing assessments for later disposition:

```
[ANL-Moderate | forecast | 60-day horizon | inputs: C031, C044]
```

---

## 9. HUNT VALUE, SECTOR, AND ACTOR TAGGING

### The extraction rule

**A sector or actor is tagged only when a graded source claim names it. Never inferred.**

Not from actor history, not from plausibility, not from "Iran usually targets energy." If the pipeline wants to say a sector is at risk without a source saying so, that is an `ANL` block, not a tag. Every tag carries the claim identifier that justified it, and a tag without one blocks publication.

**Where the justifying claim is a merged claim, the tag names the specific merged assertion.** Section 15's `segmentation.assertions` list exists so this reference resolves.

### Hunt value: three independent tests

**This product is read by people who hunt behavior.** Indicators are for blocking and for populating a SIEM, and the reader's own tooling does that from the sources. What a hunter needs from an article is the described behavior, where it would show up, and how much of it is checkable.

3.4 defined a claim as actionable if it carried "an artifact or an ATT&CK technique identifier." That counted a bare file hash as hunt value, which is wrong: a hash is a blocklist entry and tells a hunter nothing about what to look for. The tests are now separate and behavior-first.

| Test | Question, answerable from the document | Meaning |
|---|---|---|
| **`behavioral`** | Does the source describe an observable action, sequence, technique, or relationship, something detectable by its shape rather than by matching a string? | An ATT&CK technique ID, a described execution chain, a persistence mechanism, a protocol or timing pattern, a tooling relationship, a described evasion. **Not** a bare hash, IP, or domain |
| **`huntable`** | Is it `behavioral`, **and** is the grade 1, 2 or 3, **and** can at least one telemetry class from the vocabulary below be named for it? | A defender can determine where to look in their own environment |
| **`indicator_bearing`** | Does the claim carry at least one matchable artifact: hash, IP, domain, URL, certificate? | Feeds the IOC extraction pointer. Says nothing about hunt value |

A claim can be any combination. A described BYOVD driver-load sequence with no hashes is `behavioral` and `huntable` and not `indicator_bearing`, and it is the most valuable kind of claim this product carries. A list of forty hashes with no described behavior is `indicator_bearing` only, and it is nearly worthless to a hunter reading an article.

### The collection point is derived, not required to be stated

**A source naming a log source is not a precondition for a claim being huntable.**

SIEM architectures differ enough that requiring the document to name a collection point would undercount badly and would serve the wrong reader. Vendors write for their own product's telemetry, or for none. A hunter's job is to take a described behavior and map it onto whatever they actually collect, and the product's job is to make that mapping obvious rather than to wait for a vendor to do it.

**What keeps derivation mechanical is a closed vocabulary.** The pipeline does not invent a collection point in free text. It maps the described behavior onto one or more telemetry classes from the fixed list below. Mapping to a closed list reproduces between runs; writing a sentence about where to look does not.

**Telemetry class vocabulary.** Vendor-neutral by design, so it maps onto any SIEM. Extend as needed, the same way the sector vocabulary extends.

`process-execution` · `process-injection` · `image-load` · `driver-load` · `file-write` · `registry` · `scheduled-task` · `service-creation` · `authentication` · `directory-service` · `network-flow` · `dns` · `proxy-http` · `tls-metadata` · `email-gateway` · `web-server-access` · `database-audit` · `cloud-audit` · `saas-audit` · `identity-provider` · `container-runtime` · `ci-cd-pipeline` · `vpn-appliance` · `network-device-config` · `ot-ics-protocol` · `plc-config-audit` · `edr-generic`

**Provenance is recorded and printed.** Every huntable claim carries whether its collection point was `stated` by the source or `derived` by the pipeline.

| Basis | Meaning |
|---|---|
| `stated` | The document named the log source, telemetry type, or sensor placement |
| `derived` | The pipeline mapped the described behavior onto telemetry classes from the vocabulary |

That distinction costs one field and it matters. A `stated` collection point is a source's claim about where its own observation came from. A `derived` one is the product's mapping, which is a judgment even though the vocabulary is closed, and a reader is entitled to know which they are looking at. The source card prints the split, so a vendor that routinely names its own telemetry is visibly different from one whose reporting has to be mapped for them.

**The mapping is not a Hunt Priority block.** Telemetry classes say which surfaces the behavior touches. The Hunt Priority block is `ANL` and says what the product suggests doing about it, in prose, with a confidence word. Keeping them separate is what lets the huntable count stay a mechanical measure rather than a measure of how enthusiastically the product wrote a recommendation.

**Only grades 1, 2 and 3 may be marked `huntable`,** mirroring the corroboration rule in section 7. A relay describes hunt surface that another source established and adds none of its own, so counting both double-counts. `behavioral` remains available at any grade, because a relay can describe behavior accurately and that is worth recording. This was found in the dry run, where a press relay of a vendor infection chain would have produced two huntable claims for one hunt surface.

**Grade and hunt value are otherwise independent.** A grade 1 claim with no described behavior is real and unhuntable. A grade 3 aggregate can reshape how a hunt is scoped. Neither implies the other and the rendering keeps them apart.

**Printed, not blocked.** At a Glance carries the counts so a hunter can triage before reading, where the pipeline computes them. There is no minimum and no floor. An issue reporting a window in which nothing huntable emerged is a legitimate finding and publishes as one, plainly stated, rather than being held or padded.

### Why indicators are pointed at rather than published

**Deliberate. Do not "fix" this.**

The IOC extraction field names which cited sources carry structured indicators and what kinds. It does not reproduce them. The intended workflow is that a defender points this document at their own model, which retrieves the indicators from the named sources and populates their SIEM in their own schema. The article's job is the behavior a hunter will hunt with.

Reproducing indicator lists in the article would inflate every issue, duplicate work the reader's tooling does better and in their own format, and shift the product's center of gravity from behavior to feeds. The pipeline does extract artifacts into the ledger under section 14, because the gates need them and the record needs them. That is a grading input, not the deliverable.

### Sector vocabulary

Flat, no subcategories, extend as needed.

`water` · `energy` · `critical-infrastructure` · `defense` · `government` · `finance` · `healthcare` · `technology` · `supply-chain` · `telecom` · `media` · `education` · `aviation` · `petrochemical` · `manufacturing` · `transportation` · `legal` · `retail` · `research` · `ngo`

### Two tiers each

| Tier | Meaning |
|---|---|
| Sector `confirmed` | A graded claim in this window names the sector as affected, targeted, or compromised |
| Sector `contextual` | A graded claim names it as historically targeted, at risk, or relevant background |
| Actor `subject` | Profiled in this issue with graded claims about current activity |
| Actor `referenced` | Named as related, historical, or contextual without in-window claims |

The Iran issue is the worked example. Water and energy were confirmed. Finance and aviation appeared as February pre-positioning context. A hunter deciding where to spend an afternoon needs those separated.

### Coverage continuity

**Resolves open decision 9.** Silence and absence of collection are different facts and a hunter acts differently on each.

Where a cluster profiled in a previous issue produced no in-window claims, the issue states it:

```
COVERAGE CONTINUITY
CLU-0031  no in-window reporting across the standing source list.
          Last claim TI-20260711-001-C008, 11 July 2026.
CLU-0044  not swept this cycle. Out of scope for this issue's subject.
```

Two values, and the distinction is the whole point. `no in-window reporting` means the sweep ran and found nothing, which is a finding: the actor may have gone quiet, or nobody with visibility published. `not swept` means the pipeline did not look, which is not a finding about the actor at all.

This is mechanical. The pipeline knows which clusters it swept and which produced claims.

---

## 10. ACTOR ALIASING

### The position

Talos calls a cluster UAT-7810. Microsoft calls it Storm-1175. CrowdStrike has a third name and will not use either. The industry standard response is to pick one and quietly note the rest.

This product does the opposite. Every name is printed with the source that assigned it and the date. The reader sees the disagreement as it stands, and the accumulated record of who names what, when, and whether they ever acknowledge anyone else becomes another measured property of the sources.

### The rule that keeps it mechanical

**The alias table contains only equivalences a source stated. The pipeline never infers that two names refer to the same actor.**

| Case | What the document says | Table result |
|---|---|---|
| **Stated equivalence** | "UAT-7810, which Microsoft tracks as Storm-1175" | Equivalence recorded, attributed, dated |
| **No statement** | Neither source mentions the other's name | No equivalence. Clusters stay separate |
| **Stated non-equivalence** | "We assess this is distinct from Storm-1175" | Recorded as disputed, carries `[CONFLICT]` |

Case two is the common one and it is a finding, not a gap. Where it matters, the `ANL` block says so:

```
[ANL-Moderate | inputs: C019, C027]
Talos UAT-9977 and Microsoft Storm-1175 share three C2 addresses and an
identical loader hash across the two reports. Neither vendor acknowledges the
other's designation. Corroboration is counted at ×1 because no source states
the equivalence, but the infrastructure overlap is on the record above.
```

The reader gets the finding, the count stays honest, and nothing was inferred.

### The cluster table

```json
{
  "cluster_id": "CLU-0031",
  "canonical": "CyberAv3ngers",
  "names": [
    { "name": "CyberAv3ngers", "assigned_by": "CISA", "source_id": "REF-001",
      "first_seen": "2023-11-28", "cited": "2026-07-22" },
    { "name": "Soldiers of Solomon", "assigned_by": "Check Point",
      "source_id": "REF-034", "first_seen": "2026-03-14", "cited": "2026-03-14" },
    { "name": "UAT-9977", "assigned_by": "Cisco Talos", "source_id": "REF-041",
      "first_seen": "2026-08-05", "cited": "2026-08-05" }
  ],
  "equivalences": [
    { "names": ["CyberAv3ngers", "Soldiers of Solomon"], "stated_by": "Check Point",
      "date": "2026-03-14", "status": "stated" }
  ],
  "disputes": [],
  "sponsor_claims": [
    { "sponsor": "IRGC-CEC", "claimed_by": "CISA", "date": "2026-07-22",
      "claim_id": "TI-20260811-001-C003", "grade": 1 }
  ],
  "coverage": {
    "last_claim": "TI-20260711-001-C008",
    "last_swept": "TI-20260817-001"
  }
}
```

**Canonical name is the earliest dated attribution.** Mechanical, stable across issues, keeps archive search working, and it rewards whoever named the cluster first.

**State sponsor attribution is a graded claim, not a table field.** "CyberAv3ngers operates under IRGC-CEC authority" goes through the gates like anything else. The table records who claimed it, when, and at what grade.

**The `coverage` block feeds continuity reporting** under section 9 and is the difference between an actor being quiet and the pipeline not looking.

---

## 11. OVERRIDE PUBLICATION

Some claims are worth printing because they are bad. A government statement the evidence contradicts. A leak site boast. A viral claim that evaporates.

```
[MED-5 | OVR]
An unconfirmed post attributed to a PRC ministry account claimed successful
penetration of US infrastructure. The post was removed within thirty minutes.
No corroborating evidence exists and the account's authenticity is unverified.

[ANL-Low | inputs: C041]
Published because the claim's existence is the intelligence, not its content.
Explicit intrusion claims in English from PRC-attributed accounts are rare
enough that the messaging itself is worth logging, whether the account is
authentic or not.
```

**Rules.**
- The override never improves the grade. A forced grade 5 stays grade 5
- Override claims count toward the source's record. Otherwise the override launders the dataset
- Every override carries an `ANL` block stating why
- `OVR` is recorded in the ledger with the reason
- Human-initiated only, per section 17

The strongest version is a provable contradiction:

```
[GOV-2 | OVR | contradicted]
Ministry statement of 17 July asserts no evidence of intrusion in the July window.

[ANL-High | inputs: C012, C018, C023]
Three independent sources documented active exploitation between 12 and 16 July,
two with published artifacts. The statement is a policy position rather than an
intelligence assessment and is recorded here as such.
```

---

## 12. SOURCE RECORDS

The background product. Computed, never assigned.

At the close of each issue, for every source cited, the pipeline recomputes the record from the claims index.

```json
{
  "source_id": "REF-TALOS",
  "name": "Cisco Talos Research",
  "type": "VND",
  "origin": "US",
  "access": "open",
  "live": {
    "unique_claims": 47,
    "citations": 61,
    "distribution": { "1": 34, "2": 10, "3": 2, "4": 1, "5": 0 },
    "percent": { "1": 72.3, "2": 21.3, "3": 4.3, "4": 2.1, "5": 0.0 },
    "grade_5_rate": 0.0,
    "record_status": "established"
  },
  "backfill": {
    "unique_claims": 18,
    "citations": 18,
    "distribution": { "1": 11, "2": 5, "3": 2, "4": 0, "5": 0 },
    "record_status": "established",
    "from_issues": ["TI-RETRO-004", "TI-RETRO-007"]
  },
  "hunt_value": {
    "behavioral": 39,
    "huntable": 31,
    "huntable_stated": 22,
    "huntable_derived": 9,
    "indicator_bearing": 34,
    "behavioral_rate": 0.83,
    "huntable_rate": 0.66
  },
  "naming": {
    "actor_reports": 22,
    "first_to_name": 6,
    "alias_acknowledgment_rate": 0.68,
    "alias_lag_median_days": 41,
    "sponsor_attribution_rate": 0.55,
    "disputes_raised": 2
  },
  "revision": {
    "checks": 94,
    "revised_disclosed": 5,
    "revised_silent": 2,
    "silent_revision_rate": 0.021,
    "first_check": "2026-03-11",
    "check_window_note": "cadence varies by citation recency, see section 14"
  },
  "disputed_claims": 1,
  "unarchived_claims": 2,
  "first_cited": "2026-03-11",
  "last_cited": "2026-08-17"
}
```

**Grading is blind to the record.** The pipeline never consults a source's history when grading a claim. Otherwise the record becomes a self-fulfilling prior and stops measuring anything.

**The `hunt_value` block is the metric a hunter will actually use.** The `huntable_stated` and `huntable_derived` split is a second, quieter signal: a source that routinely names the telemetry its own observation came from is doing work a defender would otherwise have to do, and over enough claims that difference is visible. Grade distribution says how checkable a source is. `huntable_rate` says how often that source publishes behavior a defender can do something with. Those are different questions and the second is closer to why anyone reads this product. A vendor at 90 percent grade 1 and 20 percent huntable publishes immaculate malware analysis that a hunt team cannot operationalize, and a reader deciding where to spend reading time is entitled to know that.

**Every rate prints its denominator.** A rate without a denominator is not checkable, which is the one thing every number in this product has to be.

**Revision observation windows are uneven and the card says so.** Re-fetch cadence in section 14 is set by citation recency, so a source cited last week has been checked far more often than one cited last year.

**Fifteen unique claims per pool before a distribution publishes.** Below that, print `insufficient (n unique claims)`. Live and backfill pools are counted and thresholded independently and never summed.

**Citations are never a denominator.** They are displayed because they say something real about how much weight the product has placed on a source, and they are excluded from every ratio because a recurring story would otherwise distort the ratio in the direction that looks worst.

**The grade 5 rate is the headline number.** A source producing unsubstantiated claims 30 percent of the time is telling a reader something no editorial judgment could establish as defensibly. It is also the number most likely to be disputed, which is why every claim behind it traces to a fingerprint, an issue, a date, a fetch hash, and a gate outcome.

**Naming metrics** come from the cluster table and are counts rather than judgments.

**Time to usefulness, measured rather than estimated.** A dry run against real vendor reporting produced roughly **two unique claims per source per issue**, not the three or four earlier drafts assumed. The merge rule in section 2 is aggressive by design: a dense three thousand word vendor report whose findings all share a gate vector collapses to one claim, plus one more for its hedged attribution statement. A typical source therefore crosses the fifteen-claim threshold after seven or eight issues, which at monthly publication is seven to eight months during which the registry shows `insufficient` for nearly everything. The retrospective program in section 13 is the only way the registry has content at launch and should be scheduled alongside the first live issues rather than after them. Cadence therefore sets the rate at which the product's flagship dataset becomes real.

**Reserved for A5.** `self_correction_rate` and `external_contradiction_rate`, which point in opposite directions and are the genuinely novel part of this dataset.

---

## 13. RETROSPECTIVES AND BACKFILL

A window-bounded sweep of a past event, graded normally, published as an article under the Academics section, ingested into the backfill pool.

Pick an event. Pick the thirty day window around its disclosure. Sweep it the way the pipeline would sweep a live window. Grade everything. Write up who said what, who was early, who overclaimed, who corrected themselves, who never acknowledged being wrong.

**Why it is worth doing.** Live publication produces dispositions at the speed of events. A retrospective produces dozens in an afternoon, because the outcome is already known. That is the A5 dataset arriving early, and per section 12 it is also the only thing standing between launch and five months of empty source records.

**Why it is dangerous for the same reason.** Knowing the outcome is exactly the contamination.

### Point-in-time grading

**The grade is computed from what the document showed on the day it published. Nothing later may enter it.**

Symantec's 2010 Stuxnet reporting did not name a state sponsor. Grading that as a failure to attribute would be look-ahead bias, because in August 2010 nobody could attribute it. Declining to attribute passes the hedge test, exactly as it would have then.

The inverse matters more. An outlet that flatly asserted Israeli authorship in August 2010 with no evidence was right, and it was still grade 5. **Being right by guessing is not evidence, and a system that rewards it produces a scoreboard favoring whoever shouts earliest.**

That sentence is the clearest statement of what this system is for and belongs in reader-facing material, not only here.

| Field | Computed from | May use hindsight |
|---|---|---|
| `grade` | The document as published, on its publication date | Never |
| `disposition` | Everything that happened afterward | Always |

### Selection discipline

The threat is survivorship bias. Sweeping a 2010 window from memory returns Symantec and Langner. Sweeping it properly returns the trade press that ran six months of wrong things and no longer exists. The second group is where the grade 5 rate lives.

- Sweep by window, never by source
- Never skip a source because it looks weak. The weak ones are the measurement
- Include sources that no longer exist. Archive retrieval is expected
- Record what could not be retrieved and why
- The window is fixed before collection and does not move to improve the result

### Backfill never lowers a record

**Backfilled claims are recorded and published, but never roll up into derived standing.**

The reasoning is selection, not sentiment. Windows are human-chosen around events that seemed worth studying. That choice is not random and cannot be made random, and a pooled number built on it would carry a selection effect nobody could quantify.

- Pools are displayed separately and never summed
- Where a single derived signal is needed, it comes from the live pool only
- **A third pool, `corroborating`,** holds claims from out-of-window sources cited only to establish that an in-window finding is independently confirmed. It is counted and displayed separately and is excluded from derived standing for the same reason backfill is: citing the source was an editorial act taken *because* it corroborated, which is a selection effect that cannot be made random. A source cited only ever as a corroborator shows a visible record without that record affecting its standing
- A strong backfill record can be cited as supporting context. A weak one cannot lower standing
- A source with no live record shows `insufficient` regardless of backfill volume

**What this costs.** The folded outlet with a terrible 2010 record cannot be scored as bad, only shown as having produced weak claims in one studied window. That is the correct trade, because the alternative is a headline number whose value depends on which events somebody found interesting.

### Vocabulary

| Term | Meaning here |
|---|---|
| **Backfill** | Loading historical records into a system that lacks them |
| **Cold start** | The condition being solved: no interaction history, nothing to score |
| **Point-in-time correctness** | Every value recorded as it was known at that timestamp |
| **Look-ahead bias** | Letting later information into a point-in-time computation |
| **Survivorship bias** | Measuring only what still exists |
| **Seed data** | The initial dataset that makes a system useful before organic accumulation |

**Not training data.** Nothing is being fit and no model learns from this.

### Article format

Serial `TI-RETRO-NNN`. Human-triggered, since choosing the event is editorial. Structure:

- The event and the window, fixed before collection
- What was knowable at the time, graded point-in-time
- Who reported what, in publication order
- Dispositions, the section only a retrospective can write
- Source record contribution: what this sweep added, and for which sources

That last section is the honest disclosure that the article is also a data collection exercise, and it is what makes the scheme defensible rather than sneaky.

---

## 14. EVIDENCE RETENTION

Static site, no server, no document storage. Nothing in the system needs a copy of any source.

The gates never ask what a document said. They ask whether it published an artifact, whether it stated a method, whether it hedged. So the retention target is **proof of what was determined, and the facts that produced it.**

### Three tiers, none of which is a copy

**Tier 1, fetch record.** Proof a byte stream existed at a URL at a time. Under 400 bytes.

```json
"fetch": {
  "url": "https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a",
  "retrieved": "2026-08-11T09:14:00Z",
  "http_status": 200,
  "content_type": "text/html",
  "content_length": 84213,
  "sha256_raw": "9f2c1a...",
  "sha256_normalized": "4d81be...",
  "normalizer": "v1",
  "last_modified": "2026-07-22T14:00:00Z"
}
```

**Two hashes, and they do different jobs.** Almost every modern page carries something that changes on every request: a rotating ad slot, a view counter, a session identifier in an inline script, a related-articles block, a build timestamp. A raw-byte comparison would have reported undisclosed revision on the large majority of sources, driving `silent_revision_rate` toward 1.0 and destroying the metric in the direction that looks worst for everyone.

| Hash | Computed over | Used for |
|---|---|---|
| `sha256_raw` | The response body as received | Fetch receipt. Proof of what was retrieved |
| `sha256_normalized` | The normalized extraction below | Revision detection and the section 2 claim fingerprint |

**Normalizer v1.** Applied in order, and versioned because changing it changes every downstream comparison.

1. Select the main content region. Where the document declares one, use it. Otherwise strip `nav`, `header`, `footer`, `aside`, and elements whose class or id matches a maintained boilerplate list
2. Remove `script`, `style`, `noscript`, `iframe`, and HTML comments entirely
3. Strip all attributes
4. Collapse consecutive whitespace to a single space and trim
5. Lowercase

`normalizer` is recorded on every fetch. A normalizer change is a grader generation change under section 15 and is disclosed the same way, because it can move a fingerprint.

**What this cannot do.** Normalization is heuristic and will occasionally miss a dynamic element or strip a real one. Expect a residual false positive rate on revision detection and expect it to be visible in the numbers. That is acceptable, because the alternative is a metric that is wrong on purpose.

**Tier 2, extracted facts.** The elements the gates ran on.

```json
"extracted": {
  "title": "Iranian-Affiliated Cyber Actors Exploit Programmable Logic Controllers",
  "published": "2026-07-22",
  "byline": ["CISA", "FBI", "NSA", "EPA", "DOE"],
  "artifacts": {
    "cve": ["CVE-2026-18577"],
    "hashes": ["a3f9...", "b7e2..."],
    "ipv4": ["198.51.100.14"],
    "domains": ["example-c2.net"],
    "attack_techniques": ["T0839", "T0836"],
    "artifact_count": 47
  },
  "method_stated": true,
  "method_type": "victim site forensics, FBI observation",
  "confidence_stated": true,
  "primary_named": null,
  "actor_names_used": ["CyberAv3ngers"],
  "sectors_named": ["water", "energy", "manufacturing"],
  "collection_points_named": ["PLC configuration audit logs", "engineering workstation process logs"],
  "collection_points_stated": true
}
```

Indicators of compromise are facts about the world. A hash, an IP, a CVE identifier, a technique ID, a date, a byline. None are the author's expression and a list of them does not substitute for reading the source.

`collection_points_named` records what the document itself named, where it named anything, and sets `collection_points_stated`. It is a short factual descriptor written in the pipeline's own words. The `huntable` test in section 9 does not depend on it: where the document names nothing, the pipeline derives telemetry classes from the described behavior and records the basis as `derived`.

**Hard rule: no field in any ledger block contains prose from the source.** No quotations, no summaries in the source's phrasing, no excerpts. This covers the `extracted` block and the claim `text` field, which 3.4 left ambiguous by placing the rule only on `extracted`. Descriptors are written in the pipeline's own words and kept to a few words. This is a publication block.

**Bibliographic carve-out.** `title`, `byline`, and `published` are transcribed exactly and are exempt. A title is a citation element rather than expression borrowed for its content, the references section and every source card already print it, and a system that could not name what it read would be uncitable. The exemption covers those three fields and nothing else, and specifically does not cover `text`.

This is not legal advice and the posture is worth confirming with someone qualified before first publication. But the design deliberately retains nothing copyrightable.

**Tier 3, archive pointer.** At citation time the pipeline submits the URL to an archive provider and keeps the returned snapshot URL.

```json
"archive": {
  "attempts": [
    { "provider": "web.archive.org", "snapshot_url": "https://web.archive.org/web/2026...",
      "requested": "2026-08-11T09:14:02Z", "status": "captured" }
  ],
  "status": "captured"
}
```

Status values: `captured`, `failed`, `blocked`, `not_attempted`. Expect failures and record them.

**Attempting is required. Succeeding is not.** 3.4 blocked publication of a grade 1 or 2 claim that no provider captured. Under the disclosure doctrine that removes a well-evidenced observation from a hunter because a third-party service was unavailable, which is the wrong trade. The rules now:

- A citation with `archive: not_attempted` blocks. The pipeline must always try
- Where the first provider fails, a second is attempted
- Where all providers fail, the claim publishes with `access: unarchived`, the mark prints, and the count appears in Scope and on the source card
- The exposure is stated rather than hidden: if that source later returns 404, there is no backup copy and the reader has been told so

### Silent edit detection without a copy

Re-fetch on a schedule, hash the normalized extraction, compare.

| Outcome | Meaning | Action |
|---|---|---|
| Normalized hash matches | Unchanged | Nothing |
| Differs, modification disclosed on page | Disclosed revision | Record `revised_disclosed` |
| Differs, no disclosure | Undisclosed change | Record `revised_silent`, flag |
| 404 or 410 | Withdrawn | Record `withdrawn`, set `access: withdrawn`, archive pointer becomes the citation |
| Timeout or DNS failure | Unreachable | Retry, then record `unreachable`. Not a revision |

Detecting the change never required the old copy, only the old hash. What cannot be established is *what* changed, which is an acceptable loss.

**A revision does not regrade a published claim.** Published grades never change, per section 18. A revised document produces new fingerprints for future citations, and the revision is recorded against the source.

Re-fetch cadence: weekly for anything cited in the last ninety days, monthly thereafter. `revision.checks` records how many comparisons have actually run, because that is the denominator.

### Storage layout

```
/data/ledger/TI-20260811-001.json     claims, grades, gate answers, fetch records
/data/claims/index.json               fingerprints, first issue, citation lists
/data/sources/registry.json           source entries, types, records
/data/sources/aliases.json            actor cluster table, coverage blocks
/data/monitor/fetch-history.json      re-fetch results over time
/data/review/queue.json               disputed claims routed for later review
/data/serials.json                    flat list of issued serials
```

Roughly one to two kilobytes per claim. Forty claims an issue, fifty issues a year, a few megabytes annually. Git handles it without noticing and the commit history is itself a tamper-evident record. Hugo reads `/data/*.json` natively.

**All seven files exist today, scaffolded with correct empty schemas and nothing else.** No sample records, no backfill, no seed data. They populate as the pipeline (Track D) comes online.

---

## 15. THE LEDGER

One JSON file per issue, emitted alongside the HTML. This is the dataset.

```json
{
  "claim_id": "TI-20260811-001-C014",
  "fingerprint": "REF-001|4d81be...|TEC|R:y|D:y|A:n|art:p|meth:p|hedge:na",
  "issue": "TI-20260811-001",
  "first_issue": "TI-20260811-001",
  "citation_count": 1,
  "text": "Project file injection disabling safety shutdown logic",
  "source_id": "REF-001",
  "source_type": "TEC",
  "grade": 1,
  "access": "open",
  "disputed": null,
  "gates": {
    "retrievable": true,
    "origin_stated": true,
    "direct_observation": true,
    "aggregate": false,
    "artifact_test": "pass",
    "method_test": "pass",
    "hedge_test": "n/a"
  },
  "gate_vector": "TEC|R:y|D:y|A:n|art:p|meth:p|hedge:na",
  "segmentation": {
    "atomic_assertions": 2,
    "merged": true,
    "merge_basis": "identical gate vector",
    "assertions": [
      { "key": "A1", "descriptor": "project file injection technique" },
      { "key": "A2", "descriptor": "safety shutdown logic disabled" }
    ]
  },
  "grader": {
    "model": "claude-opus-4-6-20260401",
    "spec_version": "3.8",
    "normalizer": "v1",
    "run": "2026-08-11T09:16:22Z",
    "passes": 3,
    "agreement": "unanimous",
    "dissent": null,
    "reconciliation": "pass"
  },
  "hunt_value": {
    "behavioral": true,
    "behavioral_basis": "described injection technique and disabled logic path",
    "huntable": true,
    "telemetry_classes": ["plc-config-audit", "file-write", "network-device-config"],
    "collection_point_basis": "stated",
    "collection_point_source": "REF-001, assertion A1",
    "indicator_bearing": true
  },
  "corroboration": {
    "count": 3,
    "sources": ["REF-001", "REF-006", "REF-007"],
    "basis": "independent detection engineering against separate platform sets",
    "alias_resolved": true
  },
  "sectors": {
    "confirmed": ["water", "energy"],
    "contextual": [],
    "justified_by": "REF-001, assertion A2, names water and wastewater systems as targeted"
  },
  "actors": {
    "subject": ["CLU-0031"],
    "referenced": [],
    "names_used_by_source": ["CyberAv3ngers"],
    "equivalences_stated": [],
    "justified_by": "REF-001, assertion A1, names CyberAv3ngers as responsible actor"
  },
  "override": null,
  "provenance": {
    "pool": "live",
    "source_published": "2026-07-22",
    "window": "2026-07-12/2026-08-11",
    "capture_is_retrospective": false
  },
  "fetch": { "...": "see section 14" },
  "extracted": { "...": "see section 14" },
  "archive": { "...": "see section 14" },
  "disposition": "open"
}
```

`disposition` ships now at `open` and is populated by the A5 work.

### The segmentation block

`gate_vector` is the string the section 6 duplicate check runs against, and it is the same vector the section 2 merge used.

`segmentation.assertions` carries short descriptors for each merged assertion. 3.3 recorded that two assertions merged and did not record which two, while claiming the block existed so a disputed count could be reconstructed. A count alone reconstructs nothing. The gap bit hardest on tagging: a merged claim covering "used domain X" and "targeted sector Y" left a sector tag pointing at a claim whose recorded text described only the domain. Assertion keys are referenced by `justified_by` and by `collection_point_source`, which is what makes a disputed tag traceable.

### The grader block

`grader` is what makes this dataset survive its own maturity. The record in section 12 is longitudinal by design, so it will eventually span model versions, prompt revisions, spec revisions, and normalizer revisions. Without this block, a vendor's grade 5 rate moving from four percent to eleven percent over two years is uninterpretable, because nothing distinguishes the vendor changing behavior from the pipeline changing its reading.

**Rules.**

- `model`, `spec_version` and `normalizer` are required. A grade without them does not publish
- Grading runs more than once per claim. `passes` records how many, `agreement` records whether they matched
- A model, spec, or normalizer change never regrades published claims
- Source records may be filtered by grader generation. Where a distribution spans more than one, the source card says so

### Grader disagreement publishes, marked

3.3 held the issue on disagreement and named no resolver. 3.4 withheld the claim. **3.5 publishes it.**

Under the disclosure doctrine, a disagreement between passes is information the reader should have, not a reason to remove a fact.

1. Where passes disagree, the claim publishes **at the most conservative disputed vector.** Conservative means the higher digit, and where the vectors disagree on type, the type further from direct observation
2. The claim carries a `disputed` mark inline. Both vectors are recorded in the ledger under `disputed`
3. The count prints in At a Glance and in Scope and Sourcing
4. The claim is written to `/data/review/queue.json` for later human reading. Nothing waits on it
5. The claim counts toward the source's record at its published grade. Re-grading on review is a correction and follows the correction path, not a silent edit

```json
"disputed": {
  "vectors": [
    "VND|R:y|D:y|A:n|art:p|meth:p|hedge:na",
    "VND|R:y|D:y|A:n|art:f|meth:p|hedge:na"
  ],
  "published_grade": 2,
  "basis": "passes disagreed on artifact test; published at the conservative reading",
  "queued": "2026-08-11T09:16:25Z"
}
```

**Why publishing beats withholding.** A disagreement usually means the passes read the artifact or hedge test differently, which is a narrow disagreement about completeness rather than about what happened. Publishing at the conservative reading gives the hunter the observation, gives them the safer grade, and tells them the reading was contested. Withholding gave them nothing and called it rigor. Readers of this product are professionals and can weigh a marked disagreement themselves.

**Why not majority.** Two of three passes agreeing looks like a resolution and is not: a disagreement means either the document is ambiguous or the specification is defective, and both are worth a human reading. Resolving by majority would silently convert a specification defect into a published grade. The claim publishes at the conservative reading, which is not the same as resolving the disagreement, and the queue keeps the question open.

### The reconciliation pass

**A separate pass comparing every tagged sentence in the article against its ledger claim.**

The failure it catches is not a fabricated tag, which is easy to detect and rare. It is a legitimate tag on a sentence that widens the claim. The ledger says the source observed a loader using DLL sideloading. The prose says the actor has standardized on DLL sideloading across its toolkit. Same tag, same claim identifier, materially larger assertion. For a model writing prose from structured input, drift in that direction is the default, not an edge case.

- Every tagged sentence in the article carries `data-claim` with its identifier
- The pass answers one question per sentence: does this sentence assert anything the ledger claim does not?
- **The comparison runs against `segmentation.assertions`, not only the claim `text`.** A merged claim's text is a single descriptor standing for several assertions and is necessarily vaguer than any of them, so comparing prose against the text alone would let the pass under-fire on exactly the claims most likely to drift
- A sentence that does blocks publication under section 6 and is reported with both texts so the fix is obvious
- `grader.reconciliation` records the outcome, `pass` or `fail`, per claim

This is one of the few checks that needs a model rather than a string comparison. It runs as its own pass with its own agreement requirement, the same way grading does.

---

## 16. RENDERING

**The rule everything here follows: grading metadata is machine layer and coverage-page material. It does not appear in the article.**

The article carries the finding, the reasoning, and one quiet mark per claim saying how far the source sat from the observation. Grade distributions, hunt value counts, telemetry class lists, collection point provenance, claim identifiers, pool status, and evaluation judgments about sources all live in the ledger and at `/coverage/sources/`. A reader who wants them follows a link. A reader who wants to know what happened reads the page.

Earlier versions printed all of it inline. The result was measurable: tags interrupted sentences mid-thought, source entries became report cards about sources rather than summaries of what they found, and a reader could finish a section without learning what the actor did. That is the failure this section exists to prevent.

**A second, narrower failure showed up in 3.7 and is why this section was rewritten again in 3.8.** A new typeface and a margin-hanging tag, tried for one release, drew immediate direct feedback that they didn't read well, specifically the compact legend box. This section now describes the reverted, current state, and the rule above still holds: what changed is presentation, not what the article discloses.

**Everything prints.** Analysts live on copy and paste, and an article has to survive being pasted into a report or read on paper with no hover state and no JavaScript. There are no tooltips anywhere in this system. Nothing may depend on color alone; every mark must be distinguishable in grayscale. This was verified directly: a grayscale filter applied to a live rendered issue left every tag fully legible by its text label.

### The page shell

An issue renders inside the site shell already in production, not in a layout of its own. The reference implementation `PRC_issue_baseline_v2.html` is the target: a captured render of `TI-20260817-001`, the first issue published under this version.

**Site chrome above the article.** A header carrying the logo, the site name, the motto, and the primary nav. A footer carrying the subscription line, recent issues, method links, and elsewhere links. Neither is issue-specific and neither belongs in an issue's content file.

**Two-column article layout.** A 236px sidebar on the left (Contents, then Hunt Priorities if the issue has any, then At a Glance if the issue carries `glance` or `stats`), an 860px article body on the right, both centered inside a 1400px card that sits on a slightly darker page background. This is a reversion from a one-release attempt at a 190px sticky rail plus a 700px column at a 112px gap; see the 3.7 to 3.8 changelog above.

```css
.article-layout{display:grid;grid-template-columns:236px 1fr;max-width:1120px;margin:0 auto}
.article-sidebar{border-right:1px solid #e2ded6;padding:36px 24px;display:flex;
     flex-direction:column;gap:26px;align-self:start;position:sticky;top:0}
.article-body{padding:36px 56px 56px;display:flex;flex-direction:column;
     gap:22px;max-width:860px}
@media (max-width:768px){
  .article-layout{grid-template-columns:1fr}
  .article-sidebar{position:static;border-right:none;border-bottom:1px solid #e2ded6}
}
```

**Masthead order:** kicker, title, standfirst, metadata row, legend (pointer line or legacy box), then At a Glance. The kicker is the actor or region, the window, and the version, in crimson monospace. The full title goes in the `h1`; do not split it across a title and a subtitle. The standfirst is one line naming the product and the window.

**The metadata row is five fields:** Report Serial, Author, Published, Version, Source Basis. Source Basis is a sentence rather than a value and takes the wide cell.

```css
.article-info-grid{margin-top:34px;padding-top:22px;border-top:1px solid #e2ded6;
     display:grid;grid-template-columns:repeat(4,auto) 1fr;gap:44px;max-width:1000px}
.info-label{font:500 9.5px/1 'JetBrains Mono',monospace;letter-spacing:.14em;color:#6b665e}
.info-value{font:400 15px Spectral,serif;color:#1c1a17}
```

### Claim tags: inline, not hanging

**Reverted in 3.8. A tag is a small inline chip at the start of the claim, the same convention the site used before the margin-tag experiment.**

```html
<div class="claim"><span class="tag">VND-1<span class="corr">&times;2 corroborated</span></span>
<p>The compromise was two lines of JavaScript added to a single HTML file&hellip;</p>
</div>
```

```css
.claim{display:block}
.claim>.tag{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:10px;
  font-weight:600;letter-spacing:.04em;color:#6b665e;background:#e4e0d6;padding:3px 6px;
  margin-right:6px;vertical-align:1px}
.claim>.tag .corr,.claim>.tag .disputed{display:inline;margin-left:5px;font-weight:400;
  color:#7d2231}
```

**One tag per claim block, at the start of the block, never mid-paragraph.** Where a paragraph carries more than one claim, split the paragraph.

**The corroboration count sits inside the tag** rather than beneath it, lighter weight, spelled out as `×2 corroborated` rather than a bare symbol.

**`data-claim` carries the ledger identifier** on the tag span for the reconciliation pass in section 15 and for a reader's own tooling. It is an attribute, never rendered text.

**The access marks do not appear in the article body.** `gated`, `unarchived`, and `withdrawn` are facts about reaching a document, so they belong in that document's source summary entry and in the scope paragraph's counts. Printing them beside every claim in an earlier dry run added a column of noise that told a reader nothing about the finding.

**The `disputed` mark does appear**, appended to the tag, because a contested reading is something the reader should weigh while reading the claim.

### Analyst sections carry no tag

An executive summary is self-evidently the product speaking. So is a section headed with an analytic question. Marking them adds a label that earns nothing.

Where an analytic block sits inside otherwise sourced narrative and could be mistaken for a source's finding, it carries a single small line above it naming the confidence, in the amber `ANL` treatment:

```html
<div class="section-tag">Our assessment &middot; moderate confidence</div>
```

```css
.section-tag{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.09em;
  color:#b8862c;text-transform:uppercase;margin:0 0 14px;font-weight:600}
```

The `ANL` confidence word and its input claim identifiers are recorded in the ledger for every analytic block whether or not the marker prints.

### At a glance

**Reverted in 3.8.** A vertical box, matching the site's original sidebar treatment: a header reading "AT A GLANCE," then one row per field, label left, value right, between hairline rules. Not a fixed four-column grid; an issue prints whatever fields it actually carries.

```html
<div class="sidebar-box">
  <div class="sidebar-header">AT A GLANCE</div>
  <div class="sidebar-row"><span>Window</span><span class="value">30 days</span></div>
  <div class="sidebar-row"><span>Threat</span><span class="value">PRC-nexus</span></div>
  <div class="sidebar-row"><span>Sectors</span><span class="value">Technology, Finance</span></div>
  <div class="sidebar-row"><span>Hunt surface</span><span class="value">2 behaviors</span></div>
</div>
<p class="glance-note">Seven sources, three of them press relaying a single primary
each. Actionable for managed service providers and software distributors.</p>
```

```css
.sidebar-box{border:1px solid #ded9d1;background:#f5f2ec}
.sidebar-header{padding:14px 18px;border-bottom:1px solid #ded9d1;
     font:500 10px/1 'JetBrains Mono',monospace;letter-spacing:.14em;color:#6b665e}
.sidebar-row{display:flex;justify-content:space-between;gap:14px;padding:13px 18px;
     border-bottom:1px solid #e6e1d9;font:400 14px Spectral,serif;color:#3f3b35}
.sidebar-row:last-child{border-bottom:none}
.sidebar-row .value{text-align:right;font-family:'JetBrains Mono',monospace;font-size:13px}
```

**Every value is derived from tags, never written by hand, where the pipeline computes it.** Where a count is zero it prints zero rather than being omitted, so a reader can tell nothing from a dropped field. An issue authored without a pipeline (see article spec §9, §13) carries whatever fields honestly apply and nothing invented.

**Claim, disputed, and unarchived counts do not appear here.** They go in the scope paragraph as prose, where a sentence can say what they mean.

### The dossier strip

One line under each section heading. Quiet editorial furniture, not a data dump. Three fields separated by pipes, closed by a hairline rule.

```
MUSTANG PANDA · TWILL TYPHOON · CLU-0129  |  T1195.002 · T1574.001 · T1480  |  ATTRIBUTION DECLINED BY BOTH REPORTING VENDORS
```

```css
.dossier{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.055em;
   color:#a09a91;text-transform:uppercase;line-height:1.9;margin:0 0 16px;
   padding-bottom:8px;border-bottom:1px solid #e2ded6}
.dossier b{font-weight:600;color:#6b665e}
```

Canonical cluster name first in heavier weight, then competing names, then the cluster identifier. Technique identifiers are the handful that matter for this section, not the full mapping, which lives in the source. The attribution caveat is one clause naming who declined, who hedged, or what is disputed.

**Full alias provenance does not print here.** Assigning source, first-seen date, and citation date for every name live in the cluster table at `/data/sources/aliases.json` and render at `/coverage/sources/`. Earlier versions printed all of it under the heading and stopped a reader before they reached a sentence. Where a `[CONFLICT]` exists it is named in the caveat clause.

### The hunt block

**Prose first. Machine detail demoted to a footer.** Restyled in 3.8 to the site's original maroon hunt-priority box; content shape unchanged since 3.5.

```html
<div class="hunt">
  <div class="hunt-label">How this would be hunted</div>
  <p>[Reasoning. One to three paragraphs.]</p>
  <div class="hunt-foot"><b>Stage</b> Presence-stage &middot; <b>Look in</b> file-write,
    image-load, proxy-http, dns &middot; <b>Built on</b> two corroborated observations</div>
  <div class="hunt-sources">Indicators for your SIEM live in the sources, not here.
    [Which sources carry what.]</div>
</div>
```

```css
.hunt{border-left:3px solid #7d2231;background:#f5f2ec;padding:20px 24px;
      display:flex;flex-direction:column;gap:14px;margin:20px 0}
.hunt-label{font:400 13px/1.6 'JetBrains Mono',monospace;color:#1c1a17;font-weight:500}
.hunt p{margin:0;font:400 16px/1.65 Spectral,serif;color:#1c1a17}
.hunt-foot{font:400 11.5px/1.7 'JetBrains Mono',monospace;color:#6b665e;
      text-transform:uppercase;letter-spacing:.03em;border-top:1px dashed #d8c2c7;
      padding-top:12px}
.hunt-foot b{color:#7d2231;font-weight:500}
.hunt-sources{font:italic 400 13.5px/1.6 Spectral,serif;color:#6b665e}
```

**The label is "How this would be hunted."** It frames the block as the product's suggestion, which is what it is, without an `ANL` chip. The confidence word and input claim identifiers are recorded in the ledger and may optionally print at the end of the footer line.

**The footer carries stage, telemetry classes, and what the block rests on.** Collection point provenance, `stated` or `derived`, is recorded in the ledger and rendered at `/coverage/sources/` rather than printed here.

**The closing line points at indicators rather than reproducing them,** per section 9.

### Source summaries

**Not a scorecard. A summary of what the source found, with a link to it.** Restyled in 3.8 to the site's original bordered card; content shape unchanged since 3.5.

```html
<div class="src">
  <h4>QuickFox Supply Chain Attack Used to Deploy FDMTP Implant</h4>
  <div class="byline">Fortinet FortiGuard Incident Response Team &middot;
       4 August 2026 &middot; vendor incident response</div>
  <a class="url" href="https://...">fortinet.com/blog/threat-research/...</a>
  <p>[What the source found. One paragraph, up to 130 words.]</p>
  <div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>
```

```css
.src{border:1px solid #e2ded6;background:#fbfaf8;padding:20px 24px;
     display:flex;flex-direction:column;gap:8px;margin:0 0 20px}
.src h4{font:600 15px/1.4 Spectral,serif;color:#1c1a17;margin:0}
.src .byline{font:400 12px/1.5 'JetBrains Mono',monospace;color:#857f74}
.src .url{font:400 11px/1.5 'JetBrains Mono',monospace;word-break:break-all;color:#6b665e}
.src p{font:400 15px/1.6 Spectral,serif;color:#3f3b35;margin:4px 0 0}
.src .rec{font:400 10px/1.5 'JetBrains Mono',monospace;color:#a09a91;
     text-transform:uppercase;margin-top:4px}
```

Title, byline as transcribed, date, a two or three word source-type descriptor, the link, and a paragraph describing the finding. Nothing else.

**Everything measured about the source lives at `/coverage/sources/`.** Grade distribution, claim and citation counts, hunt value rates, naming metrics, revision rate, access status, and the evaluation sentence. An issue may carry an unobtrusive `Source record` link on the entry; it does not carry the record.

The evaluation sentence remains governed exactly as before, and its rules apply to the registry page rather than to the article: it is an `ANL` construct, it names the record fields it interprets, and it may assert only what is derivable from those fields and from claims cited from that source. Section 6 blocks a violation wherever it renders.

### Superscript citations

Attach to any number, date, version string, CVE, named infrastructure, or source-stated confidence appearing in prose, resolving to the reference list. Never inside a hunt block or an analytic block.

```css
sup.cite{font-size:10px;line-height:0;vertical-align:super;font-family:'JetBrains Mono',monospace}
sup.cite a{color:#7d2231;border:none;font-weight:600;padding:0 1px}
```

### Coverage continuity

Printed at the close of the actor sections.

```
COVERAGE CONTINUITY
CLU-0031  no in-window reporting across the standing source list.
          Last claim TI-20260711-001-C008, 11 July 2026.
CLU-0044  not swept this cycle. Out of scope for this issue's subject.
```

### Data attributes

```html
<article data-issue="TI-20260811-001"
         data-primary-actor="iran"
         data-clusters="CLU-0031,CLU-0007"
         data-sectors-confirmed="water,energy"
         data-sectors-context="defense,finance"
         data-actionable-for="critical-infrastructure,defense"
         data-classification-version="3.8"
         data-claims-graded="41"
         data-claims-huntable="26"
         data-claims-disputed="1"
         data-claims-unarchived="0">
```

Cluster identifiers rather than names, so a vendor rename never breaks an archive query. This layer carries the counts the article no longer prints. An issue authored without a pipeline carries only the attributes it has an honest value for; the rest are simply absent from the tag rather than zeroed.

### Reader legend

**Revised in 3.8, in the direction of less rather than more.**

**Canonical copy lives at `/coverage/legend/`, versioned by classification version.** Every issue links to it from the masthead.

**For a current-version issue, one line prints in the masthead where a compact box used to be:**

```html
<p class="legend-link-line">Every sourced claim below carries a tag such as
<code>VND-1</code>. See <a href="/coverage/legend/">the full tag legend</a>
for what the letters and the number mean.</p>
```

The full type table, grade scale, and corroboration explanation that printed inline under 3.6 and 3.7 no longer print in the article at all. Direct reader feedback was that it read as clutter between the metadata row and the content, and the argument for keeping it (protecting the honesty case) is still served, just entirely by the versioned page at `/coverage/legend/` rather than partly there and partly repeated on every issue.

**For an issue that predates classification versioning** (no `classification_version` in front matter: Iran, DPRK), the original four-category legend box still prints, unchanged, since that content is not what prompted this revision:

```html
<div class="classification-box">
  <div class="sidebar-label">INFORMATION CLASSIFICATION SYSTEM</div>
  <div class="classification-rows">
    <div class="classification-row"><span class="tag-badge tag-am">[AM]</span>
      <span><strong>Ambient:</strong> Widely distributed information, standard
      training data, general public knowledge</span></div>
    <div class="classification-row"><span class="tag-badge tag-ix">[IX]</span>
      <span><strong>Indexed:</strong> Publicly available but requires deliberate
      searching, academic databases, archived materials</span></div>
    <div class="classification-row"><span class="tag-badge tag-gt">[GT]</span>
      <span><strong>Gated:</strong> Behind access restrictions, paywalls,
      subscriptions, authentication requirements</span></div>
    <div class="classification-row"><span class="tag-badge tag-sp">[SP]</span>
      <span><strong>Specialized:</strong> Requires domain expertise to interpret
      correctly. Lay interpretation may differ significantly from expert
      analysis.</span></div>
  </div>
  <p>This issue predates the current classification system. See
  <a href="/coverage/legend/">coverage/legend</a> for what these tags meant at
  the time.</p>
</div>
```

**This is a change from 3.7,** which printed the compact box inline for every issue, current or not. The 3.6 reasoning for a compact-plus-linked-out approach still holds; 3.8 just moves further along the same axis, all the way to a single line, because a compact box was still enough friction to draw complaint after a reader actually saw it in production.

## 17. OPEN DECISIONS

| # | Decision | Lean |
|---|---|---|
| 1 | Is the per-issue ledger published | Yes. It contains facts and determinations rather than content |
| 2 | Who may submit analyst feedback, through what channel | Open. Named accounts of some kind, to limit abuse from disputed vendors |
| 3 | Vendor dispute path for a published record | Publish the path before the first complaint arrives |
| 4 | May the pipeline self-initiate an override | No. Human-initiated only |
| 5 | Correction notice when the error was upstream | Yes, with the disposition recording upstream origin |
| 6 | Cadence | Track E. Sets the rate at which records accumulate, a five month question at monthly publication |
| 7 | Cluster splitting and merging rules | Needed eventually, when a vendor decides one cluster was two |
| 8 | Source identity across acquisition and rebrand | Interacts with the claim fingerprint, since `source_id` is one of its three components |
| 9 | Which second archive provider | Load-bearing since section 14 requires two attempts. Candidates are archive.today and a self-hosted WARC of the normalized extraction |
| 10 | Boilerplate list maintenance for normalizer v1 | A stale list degrades revision detection quietly |
| 11 | Whether `citations` is worth printing at all | Retained. Revisit if readers read it as a quality signal |
| 12 | Telemetry class vocabulary maintenance | Extends like the sector list. Additions are additive and never retroactive, since a claim graded before a class existed cannot have used it |
| 13 | Whether the dossier strip keeps technique identifiers or drops to cluster names and the attribution caveat | Kept through 3.8. They scan as reference furniture rather than content at 10px. Revisit if readers report them as noise |
| 14 | Whether a `corroborating` pool claim should count toward the huntable total printed in At a Glance | Excluded. The count describes what the issue found in its own window |
| 15 | Whether the margin-hanging claim tag or the 190px rail layout should be revisited later, as a separate proposal | Open. Reverted for now per direct feedback; not rejected forever, just not bundled with a tagging-system change again |

**Resolved and removed from this table:** gated access sharing the grade 4 digit with relay, the undefined review path, negative observation, whether a collection point must be stated or may be derived, the `TEC` method test, the duplicate-block unit, hunt value on relays, the pool for out-of-window corroboration, and what the reconciliation pass compares against.

---

## 18. WHAT THIS SYSTEM DELIBERATELY LEAVES OUT

**Withholding claims.** Retired in 3.5. See section 1A. Weakness is labeled, never hidden.

**An actionability floor.** Considered and rejected. An issue reporting a quiet window is a legitimate finding and blocking it would be the only block in the system that measures a threshold rather than detecting a contradiction. The counts print instead and the reader decides.

**Publishing indicator feeds.** Deliberate, see section 9. The article carries behavior. Indicators live in the named sources and the reader's own tooling collects them.

**Model self-reported confidence scores.** A number like `0.87` on the model's certainty about its own reading is not an observable property of anything, does not reproduce between runs, and cannot be audited by a reader. Review triggers are gate contradictions, pass disagreement, and reconciliation failure instead, which anyone can check.

**Retroactive regrading.** The grade is what was knowable from the document when it was read. A model change, a spec change, a normalizer change, and a source revision are all things that happen after, and none of them touch a published grade.

**Majority resolution of grader disagreement.** See section 15.

**Prediction.** The system grades observations. Forecasts are `ANL` blocks with a horizon, tracked in standing assessments, judged later on whether they held.

**A per-claim bias tag.** Bias lives in the standing disclosure attached to each type and in the governed evaluation sentence.

**Accessibility as a grade dimension.** What survives is the `access` mark in section 5A, which records a fact about reader reach and never touches the digit.

**Two-part confidence notation.** The "source states HIGH, author assesses MODERATE" proposal cannot survive the automation constraint, because the second value is exactly the judgment a pipeline cannot make reproducibly.

**A semantic check on `ANL` inputs.** `ANL-High` requires a grade 1 or 2 input. It does not and cannot verify that the input actually supports the conclusion. That is a floor, not a check, and no mechanical rule closes it. Stated here so nobody assumes it is stronger than it is. The reconciliation pass in section 15 covers sourced prose; author judgment is fenced by its inputs and its confidence cap and nothing more.

**Grading metadata in the article.** Section 16. The measurement belongs in the ledger and on the coverage pages. An issue that prints its own instrumentation stops being an intelligence product and becomes a report about itself.

**A full reader legend above the executive summary.** Changed in 3.6 to a compact version plus a canonical versioned page, set as a bordered box in 3.7, and reduced to a single pointer line in 3.8. See section 16.

**A margin-hanging claim tag and a 190px contents rail, for now.** Tried in 3.7, reverted in 3.8 on direct feedback. See section 17, decision 15, for the door left open to revisit this later as its own proposal.

**An incident timeline section.** Removed in article spec v2.3. It duplicated the contents rail and restated in a table what the prose already carried.

**Tooltips.** Everything prints.

---

**Document version:** 3.8
**Doctrinal basis:** ODNI ICD 203 for analytic confidence vocabulary and for the principle that source quality and analytic confidence are separate expressions. ICD 206 for the source descriptor set behind Appendix A. ODNI Common Cyber Threat Framework for the stage vocabulary in Hunt Priority blocks. Point-in-time correctness and the look-ahead and survivorship bias framing are borrowed from quantitative finance backtesting. The Admiralty vocabulary of STANAG 2511 is set aside: its credibility digit requires assessing whether a claim conflicts with known target behavior, which is not computable from a document and fails the automation constraint.
**Reference implementation:** `PRC_issue_baseline_v2.html`, a captured render of `TI-20260817-001`, the first issue published under this version. Where this document and that file disagree about presentation, the file is the intent and this document is the bug.
**Next work package:** A5, dispositions and standing assessments, before the first automated issue ships.
