# Article and Site Design Specification v2.9
## How an issue is structured, written, rendered, and published

**Status:** Master specification for the issue product line and for site structure
**Prepared:** 5 September 2026
**Supersedes:** v2.8, v2.7, v2.6, v2.5, v2.4, v2.3, v2.2 and v2.1, and through them v2.0, `Threat_Intelligence_Article_Design_Specification.md` v1.0, and `Design_Spec_Executive_Summary.md`
**Companion:** `Classification_System_v4-2_Spec.md`
**Project:** Knights Who Say Ni. Static Hugo site, GitHub Pages, automated publication, threat hunting and intelligence analysis audience

---

## THE TWO STANDARDS, IN ORDER

**First. Give the reader the best factual information available to conduct threat hunting.** Threat hunting runs on behavior. Indicators are for blocking and for populating a SIEM, and the reader's own tooling does that from the sources this product names. What an issue owes a hunter is described behavior, where it would be visible, and how much of it can be checked.

**Second. Keep the model generating the articles as honest as possible.** Every claim graded by a published rule, every judgment fenced and traceable, nothing asserted that cannot be checked.

**Where they conflict, the first wins.** The operating consequence is the disclosure doctrine in classification spec §1A: label rather than withhold. A weak claim publishes at a weak grade. A contested claim publishes marked contested. If a hunter needs to know something, the answer is to publish it and say plainly what is uncertain about it.

---

## READING THIS DOCUMENT

- **Document sections** are cited with a section symbol: §7, §12
- **Article sections** are cited with an S prefix: S1, S6, S12
- **Cross-document references name the document:** "classification spec §16"

Nothing in this document defines a tag. If a tag definition appears here in full, that is a bug and the classification spec wins.

---

## §0. THE BOUNDARY BETWEEN THESE TWO DOCUMENTS

**The classification spec owns** what a tag means, how a grade is computed, what a claim is, the claim fingerprint, corroboration, the access and disputed marks, hunt value tests, coverage continuity, actor aliasing, sector and actor tagging, source records, retention, the ledger, the reconciliation pass, and the exact wording of the reader legend and the tag CSS.

**This document owns** what sections an issue contains and in what order, the voice, the HTML and styling, citation mechanics, front matter, file naming, the visual queue, the publication checklist, and site structure.

**Where they touch,** this document points rather than restates.

---

## §0A. PRODUCT LINES

**This document specifies one product line. It is not the house style for everything the site publishes.**

| Line | Status | Governed by |
|---|---|---|
| **Issue** | Live. Serial `TI-YYYYMMDD-NNN` | This document, in full, plus the classification spec |
| **Retrospective** | Specified, none published. Serial `TI-RETRO-NNN` | This document, with the structure in classification spec §13 replacing §3 |
| **Short form** | Reserved, not specified | The classification spec, in full. A separate design document, not yet written |

**The split exists because voice and format are separable from grading, and only one of them should be reusable.** A shorter, sharper piece on a single finding does not want a masthead, a five-field metadata row, a scope paragraph, or fourteen sections. It does want every claim graded by the same rules, tagged with the same vocabulary, and traceable the same way, because that is the product's entire credibility argument and it cannot be turned off for a format that happens to be shorter.

**What a second line inherits, without exception:** the type vocabulary, the grade scale, the gates, corroboration, the access and disputed and contested marks, `ANL` treatment and its confidence caps, the extraction rule for sectors and actors, the publication blocks, and the disclosure doctrine.

**What it does not inherit:** the section order in §3, the component ceilings, the masthead, the reader legend placement, the scope paragraph's five items, the front matter beyond `serial` and `classification_version`, and the voice rules in §11 beyond the ones that are integrity rules rather than style ones. The no-em-dash rule and American spelling are house style and apply everywhere. "Do not overstate a claim past its ledger entry" is an integrity rule and applies everywhere. "No bullet lists inside narrative prose" is a style rule for this line and a second line may decide otherwise.

**When the second line is written, the boundary in §0 gets a third column rather than a second document splitting in two.** The classification spec stays neutral about format, which is why it was worth keeping separate in the first place.

---

## §1. WHAT CHANGED

### From v2.8 to v2.9

Written against classification spec v4.2 and the re-grade run of `TI-20260817-001`. All of it is in §9, §13, and §14; §1 through §8 are unchanged.

| v2.8 said | v2.9 |
|---|---|
| §13: an issue emits the content file, and under the pipeline also the ledger and the queue | Adds the citations file, `data/citations/{serial}.json`, emitted for every issue whether or not a ledger follows, and the claim drafts, `data/claim_drafts/{serial}/{claim_id}.json`, written before authoring and retained. Classification spec §15A, §21 |
| §9: pipeline-derived front matter fields are left absent "rather than guessing," stated as one rule | Replaced with two checks: front matter pipeline fields present if and only if the ledger exists, and, separately, a claim draft exists for every claim in the ledger. The second is the one that catches fabrication |
| §9: serial uniqueness is provisional for a hand-authored issue, checked by a person at commit | `data/serials.json` and `scripts/allocate_serial.py` now allocate serials mechanically and `validate_data.py` enforces uniqueness in CI. No longer a hand check |
| §14: archive attempts phrased against a two-attempt requirement | One attempt against `web.archive.org` is the current standard; a second provider is undecided per classification spec §17 decision 9, and the position is disclosed in Scope and Sourcing rather than presented as a guarantee |
| §14: serial uniqueness checked by hand at commit | Removed. CI enforces it |
| §14: Scope and Sourcing checklist silent on `retrieval_failed` and archive position | Adds both |

### From v2.7 to v2.8

Three fixes from published build notes, plus the render side of classification v4.1. Small, and every item came from something that actually happened while authoring an issue.

| v2.7 said | v2.8 |
|---|---|
| §3: the 30-day cadence target is four to five threads and around 6,000 words | The table is marked provisional pending Track E, and thread count is explicitly bounded by what clears the evidence bar. Both 30-day issues shipped so far carry two threads, and padding to hit a count is the one thing the disclosure doctrine cannot license |
| §6: the dossier strip carries technique identifiers | It carries transcribed ones. A technique identifier the product mapped from described behavior is an analytic judgment and is barred from the strip, per classification spec §5 |
| §9: `issueNumber` is generated by Hugo, with no instruction for a hand-authored issue | Omitted, like every other pipeline-derived field, and serial uniqueness is provisional until a person checks it at commit. This has already failed once |
| Nothing about volatility or expiry | §6 and §8A: a perishable claim's age is visible where it is presented, and a syndicated surface never carries a perishable claim in the present tense |

### From v2.6 to v2.7

The render side of classification system v4.0. That version added evidentiary status, entity naming beyond actors, claim addressability, format families, and a collection boundary, and five of those produce something a reader sees. Nothing in this version changes structure, voice, length, titling, or front matter beyond one field.

| v2.6 said | v2.7 |
|---|---|
| Claim blocks carry `data-claim` as an attribute and nothing else | §6 and §7: every claim block carries an `id` and a printing permalink. A reader can cite one sentence of one issue, which they could not do before |
| The claim tag carries type, grade, corroboration, disputed, contested | Adds the evidentiary status mark, where the status is not `observed`. `alleged` and `self_reported` are the two a reader will see most and both change how a sentence should be read |
| The dossier strip names cluster names, technique identifiers, attribution caveat | Cluster names link to entity pages. Malware family and tool names, where the section covers them, are entities too and are named in the strip's first field |
| §7 covered superscript citations and `[REF-NNN]` | Adds citation rules for the formats v4.0 admitted: a talk cites a timecode, a repository cites a commit, a query prints the query and says rerunning it returns something else |
| Nothing addressed how a person is named in an issue | §11 defers to classification spec §20 and adds the one authoring rule: the product reports that a document alleges something, never that the person did it |
| §12 listed taxonomy pages as an unbuilt recommendation | Entity pages, the claim resolver, and the export routes are specified as routes with owed content, since classification spec §25 now depends on them |
| `/coverage/` held the legend, sources, corrections | Adds the vocabulary pages, the standing source list, and the schema directory |

### From v2.5 to v2.6

The first substantive pass since v2.2 that is not about presentation. Three drivers: titles were the only part of an issue that travels off the site and were specified in one line, the companion classification system went to v3.9 and changed a scale this document renders, and one issue authored by hand against v2.5 produced a build note listing questions the specification did not answer.

| v2.5 said | v2.6 |
|---|---|
| §5: title format is `Evocative Hook: Concrete Specific`, one line, one example each way | §5 is rewritten as the longest single subsection in this document. The title is the only component that survives leaving the page, so it now carries the actor or subject and the lead behavior in its own right, with five tests, a length ceiling, a slug rule, and a calibration table rewriting every title published to date |
| Nothing distinguished one issue format from another | §0A names the product lines. This document specifies the issue. A second line, shorter and in a different voice, is reserved and inherits the classification spec without inheriting this one |
| §3 assumed every issue is built around named actors | §3 names three issue types, actor, thematic, and retrospective, and states which fields each one owes. Issue 38's predecessor, the AI-failures issue, is a thematic issue that the v2.5 field list had no room for |
| §3: per-actor-section ceiling of 700 words | The ceiling is per thread, not per section. A section covering two distinct infection chains gets two allocations. Under v2.5 the only ways to handle that were to cut real content or to waive the number by hand |
| §5: the pool origin distribution is disclosed | Unchanged, plus a rule for small pools: below ten sources, state counts rather than proportions |
| §5: scope carries five things | Six. The sixth is the authoring environment disclosure, which says which mechanical checks could not run and why |
| §6: coverage continuity block, or a statement that no prior cluster went quiet | Adds the bootstrap case. A subject returning after a versioning boundary has no clusters to carry forward, and the issue states that continuity tracking begins here rather than omitting the block |
| §7: every tag carries `data-claim` | Unchanged where a ledger exists. Where none does, the attribute is omitted rather than emptied or invented, and the issue says so once in Scope |
| §10: figures are self-hosted and captioned | Adds provenance. A figure fetched by the pipeline and a figure handed to the author are different artifacts and the queue records which |
| Nothing covered RSS, email, link previews, or the homepage grid | §8A. These surfaces strip everything except the title, the excerpt, and one image, which is why §5 got longer |
| Accessibility appeared only as print and grayscale rules | §11A. Alt text, heading order, contrast, and the fact that every tag already carries a text label |
| §12: one migration banner for any issue not on the current classification version | Two variants. A v3.8 issue is neither current nor pre-versioning, and the existing banner overstates the gap for it. Classification spec §16 carries the wording |
| §9: front matter example is the PRC issue verbatim | A neutral example. The live values had started reading as required rather than illustrative |

**What did not change.** Voice, structure, the section order, the citation mechanics, the two standards, and every presentation decision made in v2.5. The typography and layout question from v2.4 stays closed.

### From v2.4 to v2.5

A presentation reversal, made after publishing one issue under v2.4's page shell and getting direct, immediate feedback: the new Georgia/SF Mono typography and the margin-hanging claim tag weren't wanted, and the compact legend box read as clutter rather than an aid. This version documents what actually shipped after that feedback, which is now the live baseline. Nothing about structure, voice, sourcing, front matter, classification, or the publication checklist changed. Presentation only, and this time in the other direction from v2.3 to v2.4.

| v2.4 said | v2.5 |
|---|---|
| §8: Georgia/Iowan Old Style serif, SF Mono, crimson `#a8385a`, paper `#fdfcfa` | §8 reverts to the pre-v2.3 system: Spectral serif, JetBrains Mono, maroon `#7d2231`, the two-tone paper-on-page background (`#fbfaf8` card on `#e8e5df` page) |
| §8: two-column grid, 190px sticky contents rail, 700px reading column, 112px gap | §8 reverts to the two-column article layout: 236px sidebar (Contents, Hunt Priorities, At a Glance stacked) plus an 860px article body, breakpoint at 768px |
| §6: the claim tag hangs 102px into the page-grid gap, outside the text column | The claim tag renders as an inline chip at the start of the claim, the same convention the site used before v2.0's rewrite, because the two-column layout has no reserved margin for a hanging tag to hang into |
| §5: the reader legend prints as a bordered box on every issue, with the full type/grade/corroboration breakdown | For issues under the current classification version, only one line prints where the box used to be: a pointer to the canonical legend at `/coverage/legend/`. Issues predating classification versioning keep their unchanged four-category box, since that content isn't the part anyone objected to |
| §5: At a Glance is a four-field horizontal grid, its own component | At a Glance, for any issue that carries it, renders through the same vertical sidebar box every issue has always used (label over value, one row per field), rather than a separate horizontal grid component |
| §8: hunt block is `.hunt`, blue-tinted, background `#f2f6fb` | Hunt block keeps the v2.3 prose-first structure and the "How this would be hunted" label, but is now styled to match the site's original hunt-priority box: maroon left border, cream background, footer line in muted mono instead of a blue-tinted card |
| §12: Coverage, Academics, and Projects listed as not built | All three are live. The publication block that prevented an issue publishing without `/coverage/sources/` no longer applies; the route exists |
| §12: known corrections to Iran and DPRK still open | Both corrected. Iran carries `TI-20260811-001`, DPRK carries `TI-20260809-001` and is dated 9 August 2026 |
| Reference implementation `PRC_issue_sitelayout.html` | `PRC_issue_baseline_v2.html`, a captured render of the first issue actually published under this version, `TI-20260817-001`. The earlier file describes a page shell that was live for about a day and is superseded |

**On typography specifically, because it will come up again:** this is not a rejection of the v2.4 page shell's ideas, several of which survive (the masthead order, the five-field metadata row, the dossier strip, prose-first hunt blocks, the pointer-not-inline-dump legend). It is a rejection of asking a reader to accept a new typeface and a new layout in the same release as a new tagging system. Revisit the v2.4 typography and margin-tag layout as a separate, later proposal if there's appetite for it, evaluated on its own rather than bundled with everything else that changed.

### From v2.3 to v2.4

The layout pass. v2.3 was written against a fragment with no site furniture around it, and the published site already had a better shell than the fragment implied. This version described an issue as it rendered inside that production layout, on the Iran issue, for about one release before v2.5 reverted the typography and layout parts of it.

| v2.3 said | v2.4 |
|---|---|
| §8 carried the v1.0 sans-serif blue palette, a 900px container, and component CSS for `.analyst-note`, `.hunt-priority-tag`, and `.ioc-extraction` | §8 was rewritten against a reference implementation built on warm paper, serif body, monospace furniture, in a new typeface. Reverted in v2.5; see above |
| Nothing about the site header, footer, or contents rail | §8 and classification spec §16 both covered the page shell, the two-column grid, and the gap the margin tag depended on. The grid survives conceptually; the exact dimensions reverted in v2.5 |
| Masthead metadata field list left to the reference implementation | §5 fixed it at five fields: Report Serial, Author, Published, Version, Source Basis. This held through v2.5 unchanged |
| Title split across an `h1` and a standfirst | The whole title goes in the `h1`. The standfirst is one line naming the product and the window. Held through v2.5 |
| Reader legend described as four loose lines | A bordered box under the metadata row for one release; in v2.5, replaced by a one-line pointer for current-version issues |
| §5 still printed a six-line hunt value count table above the fold | Removed. It contradicted classification spec §16 and was left in by mistake |
| Reference implementation `PRC_fragment_formatted.html` | `PRC_issue_sitelayout.html`. Itself superseded in v2.5 |

Nothing about structure, voice, sourcing, front matter, or the publication checklist changed in v2.4, and nothing about those things changed again in v2.5.

### From v2.2 to v2.3

A presentation pass. Nothing about grading changed. Every item came from reading a formatted issue and finding the instrumentation had crowded out the content.

| v2.2 said | v2.3 |
|---|---|
| Tags rendered inline at the start of a claim block | Proposed hanging tags in the left margin. Tried for one v2.4 release, reverted to inline in v2.5 for the reason given above |
| Source cards carried grade distributions, hunt value counts, and an evaluation line | Source summaries: title, byline, date, and a paragraph on what the source found. The record lives at `/coverage/sources/` and the entry links to it. Held through v2.5 |
| The alias line ran two or three lines of cluster metadata | One dossier strip under each heading: cluster names, technique identifiers, attribution caveat, at 10px in muted mono. Held through v2.5 |
| Hunt Priority led with a monospace header of stage and telemetry | It leads with prose under a quiet label. Stage and telemetry drop to a footer line under a hairline rule. Held through v2.5, restyled to the maroon box in v2.5 |
| At a Glance was a stacked list of six to eight fields | Four fields, one row, label over value, between two rules, plus one summary sentence, for one release. In v2.5, reverted to the site's original vertical sidebar box, whatever fields an issue actually carries |
| The executive summary carried an `ANL` marker | Dropped. A section headed Executive Summary is self-evidently the product speaking |
| Incident timeline was a mandatory section | Removed. It duplicated the contents rail and restated in a table what the prose already carried |
| Length was governed only by per-component ceilings | Cadence targets added, measured from a built issue |

**The rule these all follow, and it belongs in a spec so it stops being relearned:** grading metadata is machine layer and coverage-page material. It does not appear in the article. The article carries the finding, the reasoning, and one quiet mark per claim saying how far the source sat from the observation.

### From v2.1 to v2.2

Seven changes, all following from the two standards being stated in order.

| v2.1 said | v2.2 |
|---|---|
| At a Glance carried a withheld-claim count | Withholding is retired. At a Glance carries the hunt value block, disputed count, and unarchived count |
| Hunt Priority was mandatory furniture with no stated provenance | It is an `ANL` construct: the product's suggestion, named as such, naming its input claims. Not blocked for lacking a huntable source input |
| Hunt value was undefined | Three tests in classification spec §9: `behavioral`, `huntable`, `indicator_bearing`. A bare hash is not hunt value. Collection points may be derived onto a closed telemetry vocabulary rather than requiring a source to name one |
| Executive summary and Assessment were unmarked | Both are `ANL` sections. Synthesis and forecast are gate 0 |
| Nothing tied a tagged sentence to its ledger claim | Every tag carries `data-claim`. The reconciliation pass and its publication block depend on it |
| Nothing distinguished an actor going quiet from an actor not being swept | S6 closes with a coverage continuity block |
| The IOC extraction field's purpose was implicit | Stated, with the reasoning, so a future revision does not "improve" it into an indicator dump |

### From v2.0 to v2.1, retained

Article sections were prefixed with S to stop colliding with document section numbers. The visual queue became a separate build artifact rather than an appendix specified three incompatible ways. Spelling settled on American. The corroboration mark became outlined.

### From v1.0, retained for the record

| v1.0 said | Now |
|---|---|
| Five-dimension classification, `[AM]` `[IX]` `[GT]` `[SP]` | Removed for issues published under the current classification version. Tags are `TYPE-N` per the classification spec. Issues published before classification versioning existed keep their original four-category tags, described as what they meant at the time, not translated |
| Confidence words `CERTAIN` through `UNCONFIRMED` on source claims | Removed. The source's hedging is a gate input, not a printed value |
| `[CONSENSUS]` and `[CONFLICT]` aggregation markers | Replaced by the corroboration mark and the independence gate. `[CONFLICT]` survives only on alias disputes |
| Verification difficulty dimension | Removed. It measured how good someone's search engine is |
| Appendix A contains exactly 9 sources | One card per source cited. The count is an output |
| Body 2,500 to 3,500 words | Per-component ceilings. Length is an output of scope |
| Title format `[Country] Cyber Threat Highlights - [Focus]` | `Evocative Hook: Concrete Specific` |
| Em dash in the description and footer format | No em dashes anywhere |
| Teaching Moments linking to `/hunts/academy/` | Operational Context boxes linking to `/academics/` |
| Analyst Note format, specified twice and differently | One format, §6 |
| Superscript citations, live in an issue and in no spec | Specified, §7 |

---

## §2. PURPOSE AND AUDIENCE

Issues analyze actor behavior, tradecraft evolution, and geopolitical context from open-source reporting. They prioritize behavioral patterns and actionable hunting guidance over malware minutiae.

**Principles.**

- Behavioral over technical. A capability shift matters more than a variant, and a described technique matters more than a hash
- Actionable over comprehensive. Hunt directives first
- Sourced over confident. Every claim carries a tag computed by the classification system
- Scannable over narrative. Hunters extract and move
- Everything prints. No tooltips, no hover states, no JavaScript dependency

**Readers.**

**Two primary audiences, and they read the same issue for different things.** Threat hunters need behavior and collection points, and they read from the actor sections outward. Intelligence analysts need attribution posture, tradecraft change over time, and outlook, and they read from the executive summary and the assessment inward. Both already know what DLL sideloading is, what a KEV entry is, and what a nexus label means, and neither needs the concept explained before the finding.

The reader's own model needs structured data and named sources, which is how indicators reach a SIEM. General security professionals are a real but secondary audience, and the Operational Context box in §6 exists for them without slowing anyone else down.

**Writing for both at once is what the format is for.** The behavioral prose and the hunt block serve the hunter. The dossier strip, the attribution caveat, the cross-source convergence section, and the tags serve the analyst. Neither audience gets a version of the issue that condescends to them, and neither gets a section they have to skip.

**No organizational affiliation appears anywhere.** Author is `not important`, lowercase, exactly that text.

**Automated, not unsupervised, and the reader is told.** Grading, drafting, and emission run without a human. One touchpoint is human: override publication. Grader disagreement is routed to human review but never gates publication. The product's own judgments are marked `ANL` wherever they appear, including in Hunt Priority blocks, so a reader always knows when a model is the one talking.

---

## §3. STRUCTURE

### Article section order

```
 S1. HEADER                     title, kicker, standfirst, masthead metadata
 S2. READER LEGEND              classification spec §16, verbatim
 S3. AT A GLANCE                fields carried by the issue, plus one summary sentence
 S4. EXECUTIVE SUMMARY          BLUF first. An ANL section, unmarked
 S5. SCOPE AND SOURCING         gated position, disputed and unarchived counts, pool origin
 S6. THREAT ACTOR HIGHLIGHTS    dossier strip, Hunt Priority, coverage continuity
 S7. OPERATIONAL DOMAIN         variable heading, optional
 S8. EMERGING TRADECRAFT        patterns observed
 S9. ASSESSMENT AND OUTLOOK     what changed, what to watch. An ANL section
S10. CROSS-SOURCE CONVERGENCE   optional, collapses when empty
S11. STANDING ASSESSMENTS       optional, reserved pending A5
S12. SOURCE SUMMARIES           one entry per source cited
S13. REFERENCES                 alphabetized, full citations
S14. FOOTER
```

**Mandatory:** S1 through S6, S8, S9, S12, S13, S14.

**Optional, and collapsed entirely when empty:** S7, S10, S11. An empty section header is worse than an absent one.

**The visual queue is not an article section.** It is a separate file and never enters the HTML. See §10.

### Issue types

**Three, and the type decides which fields the issue owes rather than which sections it carries.** Section order in §3 is the same for all three. What changes is what At a Glance can honestly print and what the kicker says.

| Type | Organized around | Kicker | At a Glance owes |
|---|---|---|---|
| **Actor** | One nexus or one named cluster set | The actor or nexus | Window, threat, sectors, hunt surface |
| **Thematic** | A behavior, a technology, or a class of failure across unrelated actors | The subject domain | Window, subject, whatever count the issue actually established, hunt surface |
| **Retrospective** | A past event and a fixed window | `RETRO` | Window, event, sources swept, dispositions |

**A thematic issue is not an actor issue with the actor field left blank.** An issue covering four unrelated AI security disclosures has no nexus, no cluster continuity to report, and no shared attribution posture, and forcing a `Threat` row into its At a Glance box would require inventing one. It still carries graded claims, source summaries, hunt blocks where a behavior is huntable, and every integrity rule in both documents. What it does not carry is the actor furniture, and the dossier strip under each subheading names the affected product or platform in the cluster slot instead.

**The type is declared in front matter as `issueType`** and the template keys the At a Glance field set on it. Declaring it is what prevents the homepage grid from misaligning when a thematic issue carries different rows than the issue above it. See §14.

**Actor is the default and should stay the default.** A thematic issue is easy to write and hard to make useful, because a survey of four things that happened is a news roundup unless it establishes something the four have in common. If the common thread is only the calendar, it is four issues or it is none.

### Total length by cadence

**Measured, not guessed.** These figures come from a formatted issue built end to end, not from an estimate. Treat them as the shape a well-scoped issue lands in, and never as a limit that cuts content.

**Provisional, pending Track E.** The figures below were measured from one built issue and both 30-day issues published since have carried two threads rather than four or five. Until Track E settles cadence, the reference implementation is the authority on shape and this table is an expectation rather than a target.

| Cadence | Target | What that buys |
|---|---|---|
| Weekly | around 3,000 words | Two activity threads, six to eight sources, two hunt blocks |
| Thirty-day | around 6,000 words | Provisional. Four to five threads was the estimate; two is what the windows have produced |

**Thread count is bounded by what clears the evidence bar and is never padded to hit a number.** This is the same rule length already follows, and it needs saying separately because a count feels more like a requirement than a word target does. A window that produced two threads publishes two threads and says so. Including a third that does not clear the bar, to fill the shape, is the one thing the disclosure doctrine cannot be read to license: publishing thin material is fine, and manufacturing volume is a different act. Where a window produces less than the table expects, Scope says what was swept and what it found, and that sentence is the finding.

**There is no hard limit and none should be introduced.** A window that produced more publishes longer. A quiet window publishes shorter and says so. The numbers exist so an authoring pass knows roughly what a normal issue looks like, and so nobody pads a thin cycle to hit a length.

**Hunt blocks are the reason issues run long, and that is correct.** The maroon analyst blocks carry more weight per word than anything else in the product, and a thread that earns three paragraphs of hunting reasoning should get them. Length spent there is not padding. Length spent on furniture, metadata, or restating a source is.

### Component ceilings

Word counts are outputs, not targets. These are ceilings that keep any one component from swallowing the issue, applied within the totals above.

| Component | Ceiling |
|---|---|
| Executive summary | 400 words |
| Scope and sourcing | 250 words |
| Source summary entry | 130 words |
| Per thread within an actor section | 700 words including the Hunt Priority block |
| Operational domain section | 600 words |
| Emerging tradecraft | 200 words per pattern |
| Assessment and outlook | 500 words |
| Cross-source convergence | 400 words |
| Standing assessments | 300 words |
| Coverage continuity | No cap. One line per cluster |
| Operational Context box | 250 words |
| Appendix A card | 120 words including the evaluation |

**Ceilings are per thread, not per section, and the distinction is new in v2.6.** A thread is one activity chain with its own entry vector, its own tooling, and its own hunt surface. Where a single actor section covers two distinct chains that happen to share an exploit, it carries two threads and gets two allocations, each with its own hunt block. This is not a loophole. The test is whether a hunter would run different queries for the two, and if the answer is yes then compressing them to fit one ceiling was always going to cost the reader the second chain.

Under v2.5 an author facing that situation had two options, both bad: cut a real infection chain to fit a number, or blow the ceiling and note it. Naming the thread as the unit resolves it, and it also stops the reverse abuse, which is one chain described twice at length to claim two allocations.

**The incident timeline is removed.** It duplicated the contents rail, which already gets a reader to any section, and it restated in a table what the prose already carried. Chronology that matters belongs in the narrative.

A four-actor issue with two domain sections runs long, and that is correct. Scope drives length, and the cadence targets above describe where scope usually lands rather than where it must stop.

**Open, pending Track E.** Cadence. Weekly issues would drop to one or two actor sections and would make S10 usually empty. These ceilings hold either way. Classification spec §12 notes that cadence also sets how long the source registry reads `insufficient`, which makes it a data decision as much as an editorial one. The site footer must not promise a frequency until the decision is made.

---

## §4. METADATA

```
REPORT SERIAL      AUTHOR          PUBLISHED         VERSION   SOURCE BASIS
TI-YYYYMMDD-NNN    not important   17 August 2026    1         Open-source reporting from
                                                               threat intelligence firms,
                                                               vendor disclosures, government
                                                               advisories, and security
                                                               research. See References.
```

Five fields, one row, uppercase monospace label over value, between two hairline rules. Source Basis takes the wide cell.

**Serial is canonical.** `TI-YYYYMMDD-NNN`, sequence resets to 001 each date. Every cross-report reference uses the serial. The issue number visible on the site is a display convenience generated by Hugo from publication order and is never used to reference an issue in prose.

**Retrospectives use `TI-RETRO-NNN`** and never carry an issue number.

**Both spec versions are printed, in the build note at the foot of the issue rather than in the masthead, and only on issues published under the current classification version.** A reader comparing an issue from this year against one from next year needs to know whether the tags mean the same thing, and that reader is looking for it deliberately. Putting it above the first sentence charges every other reader for it. Issues published before classification versioning existed carry no build note at all; the migration banner at the top of those issues covers the same disclosure.

```html
<div class="buildnote">
Classification system v4.2 &middot; Article and site specification v2.9 &middot;
Grading metadata for this issue lives in the ledger at /data/ledger/ and renders at
<a href="/coverage/sources/">coverage/sources</a>.
</div>
```

**Version field.** `1` on first publication. Increment on any substantive revision. Corrections ship as follow-up articles in frago format rather than silent edits. A silent edit to a published issue is the same failure the system measures sources for, and classification spec §14 detects it in sources by re-fetch and hash comparison.

```html
<dl class="meta">
  <div><dt>Report Serial</dt><dd>TI-20260817-001</dd></div>
  <div><dt>Author</dt><dd>not important</dd></div>
  <div><dt>Published</dt><dd>17 August 2026</dd></div>
  <div><dt>Version</dt><dd>1</dd></div>
  <div><dt>Source Basis</dt><dd>Open-source reporting from threat intelligence firms,
    vendor disclosures, government advisories, and security research. See
    <a href="#refs">References</a> for full citations.</dd></div>
</dl>
```

---

## §5. HEADER, LEGEND, AT A GLANCE, AND SCOPE

### The title

**The title is the only component of an issue that survives leaving the page, and it should be written as though nothing else exists.**

Every earlier version of this document treated the title as the top of a masthead, which is why it was one line of specification and why the actor was allowed to live in the kicker. That is correct for a reader who is already looking at the page. It is wrong for every other way this product actually reaches somebody. In an RSS reader, an email subject line, a browser tab, a link pasted into a hunt channel, a search result, a bookmark, or a citation in someone else's report, the kicker does not travel, the standfirst does not travel, the dossier strip does not travel, and At a Glance does not travel. The title arrives alone and it has to do the whole job by itself.

**Format.** `Hook: Subject and lead behavior`

The hook is two to five words and sets the register. The right side names the actor, nexus, or subject domain, and the single lead behavior, in the words an analyst would use for them.

**The right side carries the actor even though the kicker also carries it, and the redundancy is deliberate.** A hunter scanning forty archive entries, or triaging a link somebody dropped in a channel, is deciding whether this issue is about their problem. Making them open the page to find out is the failure this rule exists to prevent.

#### Five tests, applied in order

**1. The stranger test.** Pasted into a channel with no kicker, no standfirst, and no site chrome around it, can a hunter tell which actor or subject this is about and what behavior it describes? A title that fails this is a magazine headline. It may be a good one, and it is still the wrong artifact.

**2. The archive test.** Set beside every other title in `/issues/`, does this one distinguish itself? Two issues about DPRK supply chain compromise must not have interchangeable titles, and the way they distinguish themselves is on the right side, by behavior, never by adding a date or a number.

**3. The query test.** Does the right side contain the words an analyst will search for eight months from now? The actor or cluster name, the technique, the affected product, platform, registry, or protocol. Abstractions like "trusted channel compromise" and "initial access" are correct and unsearchable, because nobody types them.

**4. The no-verdict test.** The title asserts only what the issue's graded claims assert, at the specificity they assert it. A title naming an actor the sources hedged on is an attribution escalation performed by the headline, which is the failure classification spec §10 spends a whole subsection on. Where attribution is contested, the title uses the nexus rather than the cluster name.

**5. The hook test.** The hook has to be about this finding. `Disabling the Fail-Safes` is about safety logic being switched off, which is what the issue found. `Compile to Compromise` is about a compromise arriving through a build step, which is what the issue found. A hook that would fit any issue in the archive is decoration, and decoration in the one component that travels is expensive.

#### Length

**Aim under 70 characters. Never exceed 90.**

The ceiling is not aesthetic. Search results truncate near 60, most email clients truncate the subject line between 60 and 78 depending on client and window width, and a link preview in a chat client wraps or clips around 70. Past those points the reader loses the end of the title, and the end of the title is where the behavior sits.

**The title names the issue's lead thread, not its contents.** This is what keeps a two-thread issue inside the ceiling. An issue covering a kernel exploit and a poisoned package registry does not name both. It names the one that leads, and the standfirst names the rest. A title that enumerates threads is a table of contents, it always runs long, and it always truncates in the place that matters.

#### What a title may not do

- Carry a grade, a confidence word, a claim count, or a source count. Grading metadata is machine layer, and that rule does not stop applying because the text is large
- Name a victim organization no cited source named
- State a forecast. Outlook is `ANL` and belongs in S9
- Use an em dash, a question mark, an exclamation point, or an ellipsis. A question mark in a title is trade press asking the reader to click to find out, and this product answers questions rather than posing them
- Reach for "revealed", "exposed", "uncovered", "inside the", "what you need to know", "shocking", "silent", "invisible", or a numeral opening a listicle
- Name the product line, the cadence, or the window. The standfirst and the kicker carry those
- Use a colon more than once. One colon, one hook, one right side

#### Thematic and retrospective issues

**A thematic issue puts the subject domain in the actor slot** and the common thread in the behavior slot. The common thread is the hard part and it is the whole reason the issue exists: if the title can only say that four things happened in a month, the issue has not established a thread and the title is telling the truth about that.

**A retrospective names the event and the window's subject,** not the verdict reached about it. `Who Was Right About Stuxnet` is a verdict. `Six Months of Stuxnet Reporting: Who Named a Sponsor and When` is the finding.

#### Calibration, against every title published to date

Applied to the live archive, because a rule that has never been run against real output is a preference.

| Published | Chars | Reads as | Under v2.6 |
|---|---|---|---|
| `Disabling the Fail-Safes: CyberAv3ngers' PLC Attacks on U.S. Water Systems` | 74 | Passes all five. Actor, behavior, sector, and a hook about the finding | Unchanged. This is the reference title |
| `AI-Assisted Espionage: Kimsuky's Automated Document Analysis` | 60 | Passes. Right side is exact and searchable | Unchanged. The hook is slightly generic and the right side carries it |
| `Access Through the Front Door: Trusted Channel Compromise in PRC-Nexus Operations` | 81 | Fails the query test. "Trusted channel compromise" is the correct abstraction and nobody searches for it | `Access Through the Front Door: A PRC-Nexus Backdoor in a Signed VPN Client`, 74 |
| `Compile to Compromise: A Poisoned Rust Crate and Five Weeks Inside a Windows Kernel Driver` | 90 | Fails the stranger test, no actor, and enumerates two threads at the ceiling | `Compile to Compromise: DPRK Poisoning of the Rust Crate Registry`, 64. The kernel driver thread moves to the standfirst |
| `Install to Continue: How Russia-Nexus Operators Turned Routine Prompts Into Initial Access` | 90 | "How X turned Y into Z" is a feature-article construction, and "initial access" is a category rather than a behavior | `Install to Continue: Russia-Nexus Captive-Portal Credential Theft`, 65 |
| `Nothing Held: Four AI Security Failures in Ten August Days` | 58 | Strong hook, and the right side is a count and a window rather than a thread | `Nothing Held: Prompt Injection, Poisoned Crates, and an Agent-Run Breach`, 72 |

**Do not retitle published issues.** The slug is the permalink, the serial is the reference, and changing either after publication breaks archives and citations. The table above is calibration for what comes next, not a work order. Where a published title is actively misleading rather than merely weak, that is a correction and ships as one under §4.

#### Slug

**Derived from the right side, never from the hook.** Hooks do not survive search and a URL is read by machines and by people scanning a link before clicking it.

- Lowercase, hyphenated, under 60 characters
- Actor or subject first, behavior second: `prc-signed-vpn-backdoor`, `dprk-rust-registry-poisoning`, `iran-plc-failsafe-disable`
- No date, no serial, no issue number. Those live in front matter and the serial is the canonical reference
- **The slug never changes after publication.** A changed slug is a broken link in every place the issue was ever cited, including in this product's own archive, and the site's entire pitch is that its work can be checked

**The whole title goes in the `h1`.** Do not split it across a title line and a subtitle line. An issue has one headline.

**Kicker.** `[Primary threat] · [date range] · V[version]`, monospace, uppercase, crimson, above the title.

**Standfirst.** One line under the title: `Open-Source Intelligence Summary: [start] to [end]. [Product line].` No em dash.

**Description.** `Open-source intelligence summary on [subject], [start] to [end].` No em dash. This is the front matter field, not printed text.

**Masthead order.** Kicker, title, standfirst, metadata row, legend line or box (see below), At a Glance, then the executive summary.

**The metadata row is five fields, in this order:** Report Serial, Author, Published, Version, Source Basis. Monospace, uppercase labels over values, between two hairline rules. Source Basis is a sentence rather than a value, names the kinds of source the issue rests on, and links to the reference list. Author is `not important`, lowercase, exactly that text. No organizational affiliation appears anywhere. CSS in classification spec §16.

**Reader legend, revised in v2.5.** For an issue published under the current classification version, the full compact legend box (type table, grade scale, corroboration explanation) does not print inline in the article. Direct reader feedback was that it read as clutter between the metadata row and the content. Instead, one line prints in its place:

> Every sourced claim below carries a tag such as `VND-1`. See [the full tag legend](/coverage/legend/) for what the letters and the number mean.

The canonical, versioned, complete legend still lives at `/coverage/legend/`, unchanged, and this line is the only thing pointing at it from inside an issue now.

**For an issue published before classification versioning existed** (no `classification_version` in front matter), the original four-category box still prints, unchanged, because that content isn't what readers objected to: only the newer type/grade legend was. That box also carries a line pointing to `/coverage/legend/` for what those tags meant at the time.

Exact wording of both the pointer line and the legacy box is in classification spec §16 and is taken verbatim.

**At a glance, revised in v2.5.** Renders through the same vertical sidebar box every issue on this site has always used: a header reading "AT A GLANCE," then one row per field, label on the left, value on the right, between hairline rules. This replaced a proposed four-field horizontal grid that was live for one release. An issue built under the current pipeline carries a `glance` field (window, threat, sectors, hunt surface, in that order is typical but not required) and an optional `glanceNote` sentence printed beneath the box. An issue that predates the pipeline carries whatever `stats` it always carried (as few as two fields, on Iran and DPRK) and renders identically, through the same box, with no fabricated fourth field. **Every value is still derived from tags where the pipeline exists, never written by hand for a piloted issue.**

**Scope and sourcing.** Ceiling 250 words, carrying six things:

1. **The reporting window** and what was and was not in scope. Where the window is not the standard cadence length, why. The first issue after a cadence change widens to close the gap against the previous issue on that subject rather than leaving one, and says so in a clause. A gap is a period nobody swept, and an undisclosed gap reads as a period in which nothing happened
2. **The gated position.** How many cited sources were gated, or that none were. A pool with no gated sources skews toward free vendor content, and that is worth stating rather than leaving a reader to notice
3. **The source pool origin distribution.** Where every cited source is US or US-aligned in an issue about a foreign state actor, say so. Not because those sources are wrong, but because a hunter should know they are looking through one lens. **Below ten sources, state counts rather than proportions.** "Three of nine sources are European, none are Korean-region" is checkable. "Thirty-three percent European" on a pool of nine implies a precision the sample cannot carry
4. **Disputed, contested, and unarchived counts,** with one sentence each on what they mean here. `One claim is marked disputed: our grading passes read the artifact test differently and we published the conservative reading.` Disputed and contested are different conditions and are never combined into one number. Classification spec §7 and §15
5. **Out-of-window sources,** where any were used to establish corroboration rather than to introduce a claim
6. **The authoring environment.** New in v2.6. Which mechanical checks ran and which could not, in one sentence, where any could not. Whether grading was single-pass or ran across independent passes. Whether archive capability existed at all, and where it did not, that the count is unavailable rather than zero. An issue authored directly against these specs without a pipeline is a legitimate artifact and is not the same artifact as a pipeline-graded issue, and the difference is invisible from the tags. Classification spec §6 and §14

---

## §6. THREAT ACTOR SECTIONS

The densest part of the issue and the part with the most required furniture.

### Subheading and dossier strip

The heading states what was found, in plain language a reader could repeat. "A signed VPN client shipped a backdoor for eleven months" is a heading. "N-central exploitation and downstream managed estates" labels a topic and tells a reader nothing.

Directly beneath it sits the **dossier strip**: a single line of quiet editorial furniture, 10px monospace, letter-spaced, muted, uppercase, closed by a hairline rule. Three fields separated by pipes.

```
CLUSTER NAMES  |  TECHNIQUE IDENTIFIERS  |  ATTRIBUTION CAVEAT
```

Cluster names come first with the canonical name in a heavier weight, **and every name in that field links to its entity page.** As of classification spec v4.0 the entity vocabulary covers malware families, tools, campaigns, and vulnerabilities as well as clusters, and a section whose finding turns on a named implant carries that name in the first field alongside the cluster. The link is what makes the strip useful rather than decorative: a reader who wants everything this product has published about that implant is one click away instead of reading the archive. Technique identifiers are the handful that matter for this section, not the full mapping, which lives in the source. **They are transcribed only.** A technique identifier the product mapped from described behavior is an analytic judgment under classification spec §5, and the strip is styled as reference furniture, which means everything in it reads as transcribed fact. A derived identifier there would be indistinguishable from a sourced one and a wrong one would be undetectable. Where no cited source names a technique identifier, that field carries fewer identifiers or none, and the mapping is left to a hunter's own tooling the same way indicator extraction already is. The attribution caveat is one clause: who declined to attribute, who hedged, or what is disputed.

This replaces the multi-line alias block, which ran two or three lines of dense metadata directly under the heading and stopped a reader before they reached a sentence. Full alias provenance with assigning source and date lives in the cluster table and at `/coverage/sources/`. The strip carries what a reader needs in passing.

### Body

Prose. No bullet lists in narrative. Each graded claim carries its tag inline with `data-claim`, plus the corroboration and disputed marks where they apply. State what was observed and who observed it, and leave what it means to the Hunt Priority block and any `ANL` block.

**Write the behavior, not the indicator list.** "Three signed drivers loaded from a user-writable directory, then kernel-mode termination of security processes" is what a hunter works with. The hashes of those drivers belong in the source, and the IOC extraction field points there.

**Where sources name an actor at different levels of confidence, the prose says so, in the actor section, in a sentence.** A vendor documenting infrastructure overlap without naming a cluster, a trade outlet naming the cluster while paraphrasing that vendor, and a third source copying the outlet is a chain in which the published attribution ends up more specific than anything its origin asserted. The article publishes the least specific attribution any source actually made, names which source escalated, and carries the `attribution_contested` mark on the claim. Classification spec §10 owns the rule and the recording. What this document owns is that it appears as a sentence a reader will actually encounter rather than only as a mark, because a reader who does not open the ledger would otherwise never learn that the confident-sounding name came from the least direct source in the chain.

**A perishable claim's age is visible wherever the claim is.** Classification spec §28 marks a claim `perishable` where it asserts a current state that stops being true without anyone publishing a correction, which in practice means live infrastructure, version currency, and campaign activity. In the article the observation date appears in the sentence rather than only in the mark, because an issue is read from the archive months later and a sentence in the present tense will be read in the present tense. "As of mid-August, the domains were serving the portal page" is the form. This costs four words and it is the difference between a correctly graded claim and a misleading one.

**Where a claim's evidentiary status is not `observed`, the mark prints and the prose carries it too.** Classification spec §4A. A mark reading `alleged` beside a tag tells a reader the assertion has not been tested by anything designed to test it. That is necessary and it is not sufficient, because a sentence written as though the thing happened will be read that way regardless of what sits beside it. An indictment describing intrusion activity is written as "the indictment alleges" or "according to the indictment," every time, and a `self_reported` breach disclosure names the disclosing party in the sentence. The mark is for the reader scanning. The sentence is for the reader reading.

**Write behavior specifically enough that it maps to telemetry.** Classification spec §9 derives a huntable claim's telemetry classes from the described behavior, using a closed vendor-neutral vocabulary, because SIEM architectures differ too much for a vendor's own naming to travel. That derivation only works if the prose describes what happened at the level a defender could look for. "Used DLL sideloading" maps to nothing. "A signed executable loaded an unsigned DLL from the same user-writable directory it ran from" maps to `image-load` and `file-write` and a hunter can write that query against whatever they collect.

### Operational Context box, optional

Foundational knowledge, when a reader needs a prerequisite to understand why something matters. One per issue. Placed after the actor description and before the Hunt Priority block.

```html
<div class="operational-context">
    <h4>Operational Context: [Topic]</h4>
    <p>[Two or three sentences of foundational explanation.]</p>
    <p><strong>Key points:</strong></p>
    <ul>
        <li>[Point]</li>
        <li>[Point]</li>
        <li>[Point]</li>
    </ul>
    <p><strong>Learn more:</strong> <a href="/academics/[topic]/">[Topic]</a></p>
</div>
```

`/hunts/` is planned to hold detection and hunt code: KQL for Defender and Sentinel, SQL for large-data platforms, and query languages added later. It is not built and does not appear in the nav; see classification spec §16 and §12 below. Foundational material lives at `/academics/`, which is live.

**The link renders only if the target exists.** Conditional rendering in the Hugo template, so a missing Academics page suppresses the containing sentence rather than shipping a dead link.

### Hunt Priority block

**This is the product's suggestion and it says so.** It is an `ANL` construct per classification spec §8: built from corroborated observation plus the product's own reading of where that behavior would be visible. The reader knows a model wrote it. What they are owed is the inputs.

```html
<div class="hunt">
<div class="hunt-label">How this would be hunted</div>

<p>[Hunting guidance, prose, one or two paragraphs.]</p>

<div class="hunt-foot"><b>Stage</b> Presence-stage &middot; <b>Look in</b> EDR driver-load
telemetry, Sysmon Event ID 6 &middot; <b>Built on</b> two corroborated observations
[ANL-Moderate | inputs: C014, C019, C022]</div>

<div class="hunt-sources">Indicators for your SIEM live in the sources, not here.
[REF-001] CISA AA26-097A (IOCs: IP addresses, domains, file hashes),
[REF-006] SafeBreach (IOCs: ATT&amp;CK-mapped detection indicators).
Point your own model at these sources to extract indicators and populate
your SIEM in your own schema.</div>
</div>
```

**Rules.**

- Required for every actor section
- Names its input claim identifiers, like every other `ANL` construct. Section 6 of the classification spec blocks the omission
- Confidence capped by inputs. All grade 4 and 5 inputs caps at `ANL-Low`, which is the honest signal that the suggestion rests on thin ground
- **Not blocked for lacking a huntable source input.** Where the behavior is real but no source named a collection point, the product proposing one is useful, and the `ANL` framing plus the confidence cap already tells the reader exactly what it is. Blocking it would leave a hunter with less than they came for. The whole point of the block is to give a start; ideally it gives more
- A grade 5 claim may not be the sole input. A directive telling a hunter where to spend an afternoon needs at least one claim someone can reach

The label is "How this would be hunted," framing the block as the product's suggestion without an `ANL` chip cluttering the header. Stage, telemetry, and the confidence word drop to the footer line under a hairline rule. **Stage vocabulary** comes from the ODNI Common Cyber Threat Framework, and an Academics page explaining the taxonomy is high value in the backlog.

### The IOC extraction field, and why it points rather than publishes

**Required for every actor section. Do not turn it into an indicator dump.**

The field names which cited sources carry structured indicators and what kinds. It does not reproduce them. The intended workflow is that a defender points this document at their own model, which retrieves indicators from the named sources and populates their SIEM in their own schema. The article's job is the behavior the hunt runs on.

Reproducing indicator lists here would inflate every issue, duplicate work the reader's tooling does better and in their own format, and shift the product's center of gravity from behavior to feeds. The pipeline does extract artifacts into the ledger, because the gates and the record need them, but that is a grading input rather than the deliverable.

Where no cited source carries structured indicators for that actor, the field says so plainly rather than being omitted. Every `[REF-NNN]` must resolve to an entry in S12.

### Coverage continuity

S6 closes with the continuity block from classification spec §9 and §16. One line per cluster profiled in a previous issue that produced no in-window claims.

```
COVERAGE CONTINUITY
CLU-0031  no in-window reporting across the standing source list.
          Last claim TI-20260711-001-C008, 11 July 2026.
CLU-0044  not swept this cycle. Out of scope for this issue's subject.
```

The two values mean different things and a hunter acts differently on each. `no in-window reporting` means the sweep ran and found nothing, which is a finding. `not swept` means the pipeline did not look, which is not a finding about the actor at all. Before v3.5 a reader could not tell those apart, and an actor disappearing from an issue read as an actor going quiet.

**The bootstrap case, new in v2.6.** A subject profiled before classification versioning existed has no cluster identifiers to carry forward. There is nothing to put in the block and constructing identifiers to fill it would be fabrication wearing continuity's clothes. The block is still emitted, carrying one line:

```
COVERAGE CONTINUITY
Continuity tracking for this subject begins with this issue. The previous
issue on it predates cluster identifiers and none can be assigned to it
after the fact.
```

**This is required rather than optional, and the reason is that omitting it says something.** An absent continuity block reads as "no previously profiled cluster went quiet," which is a claim about the world, and in this case it would be a claim nobody checked. Classification spec §10 carries the cluster-side rules, including what the new cluster entry records about the old issue.

### `ANL` blocks

Rendered per the classification spec, naming the claim identifiers they rest on. One per major section, excluding the Hunt Priority block, S4, and S9, which are themselves `ANL` sections.

---

## §7. CITATIONS

Two systems running together, both specified.

**Superscript citations** attach to any number, date, version string, CVE, named infrastructure, or source-stated confidence appearing in prose. They resolve to the reference list. They never appear inside an `ANL` block or a Hunt Priority block, because those are the author speaking and citing them blurs the boundary the format exists to protect.

**`[REF-NNN]` identifiers** are used in S12, in the IOC extraction field, and anywhere a source is named as an object rather than cited as support.

**Every claim block is addressable.** New in v2.7. The block carries an `id` equal to the claim's short identifier and a permalink affordance that prints, because an analyst pasting one finding into a report needs to cite the finding rather than the issue. The permalink resolves through `/claims/{serial}-{id}/`, which redirects to this anchor and lists every issue that has cited the claim since. Classification spec §25 owns the route and the resolver; this document owns the fact that the anchor exists in the markup and that the affordance is visible rather than hidden behind a hover, which would violate §8.

```html
<div class="claim" id="C014" data-claim="TI-20260822-001-C014">
  <span class="tag">VND-1<span class="corr">&times;2 corroborated</span></span>
  <a class="claim-link" href="#C014" aria-label="Permalink to claim C014">&para;</a>
  <p>[Claim text.]</p>
</div>
```

The identifier is stable, survives retitling and reslugging, and is the thing a reader cites. The issue URL is not, which is why §5 makes the slug immutable rather than making the URL the reference.

**`data-claim` on every tag, where a ledger exists.** Every tagged sentence carries its ledger claim identifier in the markup. This is what makes the reconciliation pass in classification spec §15 possible, and it is also the join a reader's own tooling uses to pull the ledger entry behind any sentence. A tag carrying an identifier that resolves to nothing blocks publication.

**Where no ledger exists, the attribute is omitted. Not emptied, not invented.** An issue authored directly against these specs has no ledger and therefore no identifiers, and `data-claim=""` or a plausible-looking `C014` is a fabricated field, which is the one class of failure that holds an issue. The tag itself still renders, because the tag states something about the evidence that remains true with or without a ledger behind it. The issue discloses the absence once, in Scope and Sourcing, under §5 item 6. Classification spec §6 carries the same rule from the grading side, and v2.6 states it in both places because it was previously implied by neither.

**Every superscript resolves to an anchor that exists.** A superscript pointing at a missing anchor blocks publication.

**Bylines, titles, and publication dates are transcribed from the retrieved document or omitted.** Never inferred, never reconstructed from a house style. Also a publication block in the classification spec, and it appears here because it is an authoring failure before it is a ledger failure.

**Appendix A card format** is in classification spec §16, including the rules governing the evaluation sentence. One card per source cited, no fixed count. The evaluation is an `ANL` construct that may assert only what is derivable from the fields printed on that card and the claims cited from that source in this issue.

### Citing what is not a web page

Classification spec v4.0 admits formats whose citations cannot be a bare URL. The reference entry carries whatever makes the source reachable at the granularity the claim rests on.

| Format | Reference carries |
|---|---|
| Talk, webinar, podcast | The media URL and the timecode the claim rests on. An hour of video is not a citation |
| Repository, commit, package | The commit SHA or the exact version string, never only the project URL |
| PDF | The URL, the document title, and the page. Where the file was replaced at the same URL, the archive pointer is the citation |
| Feed record | The record identifier and the feed, plus the record's own upstream reference where it has one |
| Query result | The platform, the query string as run, and the execution date, printed so a reader can rerun it, **followed by a plain statement that rerunning it will return something different** |

That last one is the only place in the product where a citation openly tells a reader it cannot be reproduced. Printing it that way is better than printing a URL that implies it can.

**References** are alphabetized, full citation format, and include every source cited anywhere in the issue.

---

## §8. HTML AND STYLING

An issue renders inside the site shell. Embedded CSS in the issue is acceptable and is what the published issues do today, but a shared stylesheet inlined at build time satisfies the same requirement and is preferred once the template exists. No external stylesheet fetched at runtime, no JavaScript, UTF-8.

The reference implementation `PRC_issue_baseline_v2.html` is a captured render of the first issue published under this version. Where this section and the reference implementation disagree, the file wins.

### Type and color

**Reverted in v2.5.** Warm paper, serif body, monospace for every label and every piece of furniture, same as it has always been on this site. A one-release experiment with Georgia and SF Mono is retired along with the crimson `#a8385a` and teal `#1a3d5f` it introduced.

```css
body {
    background: #e8e5df;
    font-family: Spectral, Georgia, serif;
    color: #3f3b35;
}

main {
    max-width: 1400px;
    margin: 0 auto;
    background: #fbfaf8;
    border-left: 1px solid #ded9d1;
    border-right: 1px solid #ded9d1;
}

a { color: #7d2231; }
```

Body 17px serif at 1.68 inside the article, 16px sitewide default. `h1` inside an issue's masthead is 40px serif, light weight. `h2` is not a headline; it is a small uppercase monospace rule line in the crimson accent, which is what keeps a long issue readable as a sequence of sections rather than a stack of competing titles. `h3` is 30px serif and is where a subsection actually announces itself.

**The article body column is 860px,** inside the wider two-column layout described below. Longer lines cost more than the extra words are worth in a document read on screen.

**The grade digit is never colored differently by grade.** A five-color scale reads as a quality verdict and it is not one. Source-type prefix does carry a background tint (four tints, matching the site's original four categories, extended across the full type vocabulary by mapping several types to the nearest existing tint rather than inventing a color per type). Classification spec v3.9 added `AGG` and `SOC`, which map to the same tint as `IND`, since all three describe a publisher with no editorial or correction layer between the author and the reader.

### Layout

**Reverted in v2.5.** Two-column article layout: a 236px sidebar (Contents, then Hunt Priorities if the issue carries any, then At a Glance) on the left, an 860px article body on the right, the whole thing centered inside the 1400px main card described above. The one-release experiment with a 190px sticky rail, a 112px page-grid gap, and a margin-hanging claim tag is retired; see §1 and §6.

Breakpoint at 768px. Below it, the sidebar stops being sticky and stacks above the article body instead of beside it.

Site header and site footer are not issue-specific and are defined once in the base template rather than per issue.

### Components

The claim block (now an inline chip, not a margin tag), the dossier strip, the hunt block (maroon, not blue), source summary entries, superscript citations, the reader legend (pointer line for current-version issues, unchanged box for legacy issues), and At a Glance (the vertical sidebar box) are all specified with working CSS in classification spec §16 and are not duplicated here.

```css
.migration-banner{background:#fdf6e3;border:1px solid #d9a441;
     padding:12px 16px;margin:0 0 24px;font-family:'JetBrains Mono',monospace;
     font-size:11px;line-height:1.7;color:#7a5c14}

.buildnote{font-family:'JetBrains Mono',monospace;font-size:10px;line-height:1.8;
     color:#a09a91;border-top:1px solid #e2ded6;margin-top:32px;padding-top:16px;
     letter-spacing:.03em}
```

The operational context box points at `/academics/` through the conditional link partial so it renders nothing when the target page does not exist yet.

### Tables

Tables are for incident timelines and technical lists, not for prose. Hairline rules, monospace head, 13.5px, full width, stacking below 768px. No zebra striping; on warm paper it reads as damage.

### Print and grayscale

Everything prints. No tooltip, no hover-dependent behavior, no JavaScript. Every mark distinguishable in grayscale, since a printed issue and a pasted-into-a-report issue are both normal ways this gets read. Every mark in this system carries its own text label rather than relying on color alone, which was verified directly against a grayscale-filtered render of a live issue.

### Machine layer

The `<article>` element carries the data attributes in classification spec §16, including cluster identifiers rather than actor names so a rename never breaks an archive query, plus `data-classification-version`, `data-claims-graded`, `data-claims-huntable`, `data-claims-disputed`, and `data-claims-unarchived`. This layer carries the counts the article no longer prints.

---

## §8A. SYNDICATION SURFACES

**Everywhere the issue appears without the page around it.** The homepage grid, the archive list, RSS, the email edition, a link preview in a chat client, a search result. None of them render the masthead, the sidebar, the tags, or the article body, and this document had nothing to say about any of them through v2.5 even though the subscribe box has been live the whole time.

**Four things travel and nothing else does:** the title, the excerpt, one image, and the reading time. §5 is as long as it is because of the first one.

| Surface | Renders | Owed by |
|---|---|---|
| Homepage grid | Kicker line, title, excerpt, reading time, At a Glance cell | Front matter, plus `issueType` for the field set |
| Archive list | Issue number, title, date | Front matter |
| RSS | Title, `excerpt`, date, full or partial body per template | Front matter |
| Email | Subject line from title, `excerpt` as preview text | Front matter |
| Link preview | Title, `excerpt`, OG image | Front matter, plus the image rule below |
| Search result | Title, whatever the engine extracts | The title and the first paragraph of S4 |

**A syndicated surface never carries a perishable claim in the present tense.** The excerpt, the homepage summary, and the link preview are read long after publication with no date attached to the sentence, and they are the surfaces most likely to be quoted onward. Where the lead thread rests on a perishable claim, the excerpt carries the window rather than the state.

**Excerpt rules.** One or two sentences, under 200 characters where possible, and never a truncation of the standfirst. It names the threads the title did not. It is the second and third thread's only chance to reach a reader who is deciding whether to open the issue, which is why it should read as an inventory rather than a tease. No em dash. No trailing ellipsis.

**Reading time is computed, never written.** Hugo derives it from word count. It appears on the homepage and the archive. It is not front matter, is never rounded up to look substantial, and is not a component ceiling in disguise.

**The link preview image, where one exists, is the issue's lead figure or nothing.** No generated graphic, no stock imagery, no logo card standing in for a figure the issue does not have. §10's rule against substituting a diagram applies with more force here, not less, because a preview image is the part a reader is least able to check. An issue with no figure has no OG image and the preview falls back to the site card, which is the honest outcome.

**The homepage grid alignment is a real failure mode and it is silent.** Every issue on the grid needs a matching At a Glance cell for its row, or the two-column CSS grid misaligns for that issue and for every issue below it. It breaks when a `glance` or `stats` field is missing, misnamed, or carries a field set the row template does not expect, which is exactly what happens when a thematic issue lands beside actor issues. Declaring `issueType` is what lets the template resolve it. This is in the §14 checklist and it is worth naming here as well, because nobody looks at the checklist item until after the grid is already broken.

---

## §9. HUGO FRONT MATTER

The authoring pass emits front matter. Nobody adds it afterward.

**The example below is illustrative and its values are placeholders.** Earlier versions used a live issue's front matter verbatim, and the specific values started being read as required rather than as an example of shape.

```yaml
---
title: "[Hook]: [Subject and lead behavior]"
date: YYYY-MM-DD
issueNumber: NN
serial: "TI-YYYYMMDD-NNN"
reportSerial: "TI-YYYYMMDD-NNN"
version: 1
classification_version: "4.2"
article_spec_version: "2.9"
issueType: "actor"
kicker: "[ACTOR OR SUBJECT]"
primaryThreat: "[actor or nexus]"
dateRange: "[DD MON] to [DD MON YYYY]"
window_start: YYYY-MM-DD
window_end: YYYY-MM-DD
excerpt: "Open-source intelligence summary on [subject]: [lead thread] and [second thread], [start] to [end]."
standfirst: "Open-Source Intelligence Summary: [start] to [end]. [Product line]."
author: "not important"
sourceBasis: "Open-source reporting from threat intelligence firms, vendor disclosures, government advisories, and security research. See References for full citations."
disclaimer: "This report synthesizes open-source threat intelligence to support threat-hunting operations and risk assessment. All material is publicly available. Information sourced, dated, and classified for transparency and verification."
glance:
  - label: "Window"
    value: "[N days]"
  - label: "Threat"
    value: "[actor or nexus]"
  - label: "Sectors"
    value: "[from confirmed sector tags]"
  - label: "Hunt surface"
    value: "[N behaviors]"
glanceNote: "[One sentence on the pool's shape.]"
---
```

`issueNumber` is not authored by hand. An issue written outside the pipeline omits it entirely, per the two checks below, and the Hugo build supplies it from publication order. **Serial uniqueness is not provisional and is not the author's to verify by hand.** `data/serials.json` is populated, `scripts/allocate_serial.py` allocates mechanically, and `validate_data.py` enforces uniqueness in CI. Classification spec §15.

`issueType` is new in v2.6 and takes `actor`, `thematic`, or `retrospective`. It decides the At a Glance field set, per §3, and it is what keeps the homepage grid aligned when issue types are mixed. It is authored rather than derived, since it is an editorial decision about how the issue is organized.

`serial` is canonical; `reportSerial` is carried alongside it for backward compatibility with the template code that predates the field rename and is not deprecated, since duplicating the value costs nothing and nothing depends on removing it.

`clusters`, `clusters_quiet`, `actors_subject`, `actors_referenced`, `sectors_confirmed`, `sectors_context`, `actionable_for`, `claims_graded`, `claims_huntable`, `claims_disputed`, `claims_unarchived`, and `pool` are all grading-pipeline output, and their presence is now a checkable fact rather than a rule of thumb.

1. **Front matter pipeline fields are present if and only if `data/ledger/{serial}.json` exists.** Present with a ledger, absent without one. Never fabricated, never partially filled. An issue authored without the pipeline (by a model working from the specs directly, as `TI-20260817-001` was) leaves every one of these absent rather than guessing at a value. A zero or an empty list is a claim about the world, and an honest absence is not the same thing as one
2. **Where the ledger exists, a claim draft exists for every claim in it.** This is the separate check, and it is the one that matters for fabrication. Drafts can exist without a ledger, when the writer has not run; a ledger cannot exist without drafts. Classification spec §15A

**`classification_version` and `article_spec_version` are what the migration banner keys on.** An issue that carries them is read as current. An issue that does not, or that carries an older version than what these two documents currently declare, gets the banner. Do not add these fields to Iran or DPRK; their absence is what identifies them as pre-dating the classification system, and back-filling a version number onto them would misrepresent what was actually true when they were written.

**The ledger path is derived, not declared.** Hugo constructs `/data/ledger/{{ .Params.serial }}.json` from the serial, and a hand-carried path is one more thing that can disagree with the filename.

---

## §10. THE VISUAL QUEUE

**A separate artifact. It never appears in the published HTML.**

```
[SERIAL]_visual_queue.md
```

A table of insert location, visual sought, source URL, and caption, followed by build instructions. Emitted as its own file rather than as an appendix a later stage has to remember to remove.

**Never hotlink a vendor CDN path.** Every image is self-hosted at `/static/img/reports/[SERIAL]/[slug].[ext]` with the source credited in the caption. A hotlinked diagram breaks silently when the vendor reorganizes, and citing an image whose bytes you do not control is the same failure the retention design exists to avoid.

```html
<figure class="source-visual">
  <img src="/img/reports/TI-20260817-001/slug.png" alt="[descriptive alt text]">
  <figcaption>Figure N. [What the figure shows]. Source: [Vendor], [Date].</figcaption>
</figure>
```

**Limits.** One to two per section. **Prefer figures that carry behavior:** infection chains, execution flows, network topology, targeting distributions. An annotated screenshot of a hash list is decoration. This is the same priority that governs the prose.

**Never generate a substitute diagram.** Where an asset cannot be retrieved, the row stays in the queue with a note and the figure is omitted.

### Figure provenance

**Self-hosting means the product controls the bytes it captured. Where it did not capture them, the queue records that.** New in v2.6, after an issue self-hosted a figure that had been handed to the author rather than fetched by the pipeline, and the distinction had nowhere to live.

| Value | Meaning |
|---|---|
| `fetched` | The pipeline retrieved the image from the cited source's URL and hashed it |
| `supplied_verified` | The image was provided to the author, and the author re-fetched the source page and confirmed it depicts the same figure with the same labels |
| `supplied_unverified` | The image was provided and the source page was not checked. Not publishable |

`supplied_verified` is a visual confirmation rather than a byte comparison, and it is the right bar for a hand-authored issue and the wrong bar for a pipeline, which can simply fetch. Recording which one applies costs one field and preserves the ability to tell later how a given figure got there.

**Alt text describes the behavior in the figure, not the figure.** "Infection chain diagram" tells a screen reader user nothing that the caption did not. "Signed executable loads an unsigned DLL from its own directory, which downloads a second-stage implant over HTTPS" is the content, and it is also the thing a hunter would have taken from looking at it. §11A.

---

## §11. VOICE

**Do.** Lead with the finding. Active voice. Terse sentences. Separate observation from interpretation. Be specific, so "GitHub Raw Content API calls" rather than "GitHub activity". Describe behavior in terms a defender could build a detection from. Write hunting guidance as guidance and background as background. Respect the reader's expertise.

**Do not.** No em dashes anywhere, including inside templates, comments, and commit messages. No "notably", "it's worth noting", "interestingly", "bottom line". No AI tells. No bullet lists inside narrative prose. No hedging by adverb, since uncertainty belongs in the tag or in an `ANL` confidence word. No telling readers what the finding means for their organization, which is their own tooling's job.

**Do not overstate a claim past its ledger entry.** The reconciliation pass in classification spec §15 checks for exactly this and blocks it. A sentence that widens a source's observation is the most likely honest-looking failure this product can make, and it is easier to avoid at writing time than to fix at block time.

**Spelling is American throughout,** in the article, in both specifications, and in templates.

**On confidence.** Do not restate a source's confidence as though it were the product's. The source's hedging is a gate input. Where the author disagrees with a source, that is an `ANL` block naming the claim it disputes, never an adjective attached to the source's claim.

**Naming people.** Classification spec §20 owns the rule. What this document owns is how it reads on the page: the product reports that a document alleges something and never restates the allegation as fact, including in the executive summary, where compression makes the slip easiest. "The indictment names three GRU officers" is correct. "Three GRU officers ran the campaign" is the product asserting something no source observed. Victim organizations appear only where a source named them, individual victims never appear, and no sentence anywhere carries a name that arrived through adversary-controlled material.

**Tone.** Someone who has reverse-engineered malware, correlated infrastructure across campaigns, and knows what a hunter needs before lunch.

---

## §11A. ACCESSIBILITY

**Most of this was already true and none of it was written down.** The print and grayscale rules in §8 got the product most of the way there by accident, because a document that survives being printed in black and white has already given up color-only meaning and hover-dependent behavior. What follows is the rest, stated so it stops depending on luck.

**Every mark carries a text label.** Already true. A tag reads `VND-1`, the corroboration mark reads `×2 corroborated` rather than a bare symbol, and the disputed and contested marks are words. Nothing in the system encodes meaning in a tint alone, and the type tints in §8 are decoration on top of text that already says it.

**Heading order never skips a level.** `h1` is the title, `h2` is a section rule line, `h3` is a subsection. The `h2` in this product is styled as a small monospace rule rather than as a headline, which is a visual decision and does not license using an `h3` where an `h2` belongs. A screen reader's section list is the only contents rail some readers have, and the sidebar rail is not a substitute because it is generated separately.

**Alt text is mandatory on every figure and describes the behavior rather than the artifact.** §10. A figure with no useful alt text is a figure that was decorative, and §10 already says decorative figures do not belong in an issue.

**Tables carry header cells,** marked as headers rather than styled to look like them. §8's tables are used for technical lists, which are exactly the tables a reader most needs to navigate by column.

**Contrast.** The palette is dark text on warm paper and clears the threshold comfortably in the body. The places to watch are the ones deliberately quiet: the dossier strip at 10px muted gray, the build note, the source record line, and the hunt footer. Those are furniture and they may be quiet, but 10px muted gray on cream is close enough to the line that it should be measured rather than assumed, once, and recorded here when it is.

**A skip link to the article body,** because the sidebar rail sits before the content in source order and a keyboard reader should not traverse it on every issue.

**No JavaScript dependency, no tooltips, nothing behind hover.** Already required in §8 for print reasons. It is also the accessibility rule, and stating it in one place and not the other is how a future revision talks itself into a hover state.

---

## §12. SITE STRUCTURE

| Path | Status | Notes |
|---|---|---|
| `/` | Live | Latest issue plus recent list, each with its own at-a-glance box in the two-column grid |
| `/issues/` | Live | Archive |
| `/hunts/` | Not built, not in nav | Hunt Library. Detection and hunt code: KQL, SQL, other query languages. Build when there is content for it |
| `/coverage/` | Live | Landing page |
| `/coverage/sources/` | Live | The source registry, rendering from `/data/sources/registry.json`. Empty today; renders an honest empty state rather than fabricated numbers |
| `/coverage/legend/` | Live | Canonical versioned reader legend, including a section for the v1 four-category system Iran and DPRK still use |
| `/coverage/corrections/` | Live, stubbed | Empty state. Format pending A5 |
| `/academics/` | Live, empty | Operational Context targets. Landing page exists; no content pages written yet |
| `/projects/` | Live | |
| `/actors/[cluster]/` | Not built | Entity pages, keyed on cluster identifier. Name table, equivalences, relationships, every claim in date order |
| `/entities/` | Live | List route. Renders the taxonomy across families, tools, campaigns, and vulnerabilities; no detail page per entity yet |
| `/entities/[type]/[id]/` | Not built | The per-entity detail page. Classification spec §10 and §25 |
| `/sectors/[sector]/` | Not built | Taxonomy pages on the confirmed sector vocabulary |
| `/claims/` | Live | List route |
| `/claims/[claim-id]/` | Not built | The claim resolver. Redirects to the issue and anchor, lists later citations |
| `/coverage/vocab/` | Live | Human-readable renders of the versioned controlled vocabularies. Classification spec §24 |
| `/coverage/standing/` | Live | The standing source list, with add and remove dates. Classification spec §22 |
| `/data/schema/` | Not built | Published JSON Schemas, every version retained |
| `/data/export/` | Live | `claims.jsonl` and `sources.json`. Classification spec §25 |

**No longer blocking.** `/coverage/sources/` exists, so the v2.4 publication block tied to its absence no longer applies.

**These routes are what classification spec §25 rests on, and without them the system is checkable in principle and unchecked in fact.** The product's whole argument is that somebody else can verify the work. A dataset nobody can download and a claim nobody can link to make that an assertion about rigor rather than a demonstration of it. The export now exists; of the five routes still not built (`/actors/[cluster]/`, `/entities/[type]/[id]/`, `/sectors/[sector]/`, `/claims/[claim-id]/`, `/data/schema/`), the claim resolver is the one that changes what the product is, since a reader can already reach the list routes at `/entities/` and `/claims/`. The rest make it navigable.

**Taxonomy and entity pages are nearly free.** The tagging machinery already exists: every issue records confirmed sectors and subject clusters, in front matter and in the `<article>` data attributes, justified by claim identifiers. Hugo generates taxonomy pages from exactly that. What it buys is the question a returning reader actually has, which is "what has this product published about this actor," and which today can only be answered by reading the archive list and guessing from titles.

**Build them on cluster identifiers and render the canonical name,** never the reverse. A vendor renaming a cluster then changes a heading rather than breaking every link, which is the same reasoning behind using cluster identifiers in the data attributes in §8.

**They also close a gap in the continuity design.** Coverage continuity tells a reader which clusters went quiet in one issue's window. A taxonomy page tells them the whole history, which is the version of that question anyone actually asks.

**Nav discipline.** A section in the nav returning 404 costs more credibility than a missing section, particularly for a product whose entire pitch is that you can check its work. Current nav: Latest, Archive, Academics, Coverage, Projects. Taxonomy pages need not enter the nav; they are reached from the dossier strip and from the archive.

**Empty states, never placeholder data.** A registry rendering fabricated numbers would be a worse failure than a registry rendering nothing.

**Two banners, not one, as of v2.6.** An issue carrying `classification_version: "3.8"` is neither current nor pre-versioning, and a single banner says the wrong thing about it. Its tags mean very nearly what current tags mean; one digit was split in two by classification spec v3.9. Warning that reader their tags "do not mean what tags in current issues mean" overstates the gap and reads as a caution about the entire issue.

| `classification_version` | Renders |
|---|---|
| Absent | The migration banner below. Tags are the four-category system and do not translate |
| Present, lower than current | A quieter version note naming the version the issue was graded under, linking to that version's section of the legend |
| Equals current | Nothing |

Classification spec §16 carries the wording and the styling for the version note. The distinction to preserve is that a migration banner is a warning and a version note is a footnote, and a reader should be able to tell which they are looking at before reading either.

**Migration banner.** Renders when `classification_version` is **absent**. Absence is the common case for the legacy issues, because they predate the field.

```html
<div class="migration-banner">
  This issue was published under an earlier classification system. Its tags do
  not mean what tags in current issues mean. See
  <a href="/coverage/legend/">the versioned tag legend</a> for what applied at
  the time.
</div>
```

Do not retro-fit the tags or rewrite the assessments. Rewriting published analysis to look more or less confident than it was when written is its own integrity problem.

**Corrected.** Iran carries `TI-20260811-001`. DPRK carries `TI-20260809-001`, dated 9 August 2026. Both were previously wrong; both are fixed. Note: DPRK's own incident timeline contains entries dated 10 August, one day after its corrected publish date. This is a known, disclosed inconsistency in the corrected metadata against the unrewritten body text, left as-is per the rule against retro-fitting published analysis; see the commit history for the correction rather than silently reconciling it here.

---

## §13. FILES AND DELIVERY

```
Serial     TI-YYYYMMDD-NNN                      TI-20260817-001
Article    content/issues/[slug].md              Hugo content file, front matter plus markdown body
Citations  /data/citations/[SERIAL].json         always, whether or not a ledger follows
Ledger     /data/ledger/[SERIAL].json            when the pipeline exists; absent for a hand-authored issue
Drafts     /data/claim_drafts/[SERIAL]/[CLAIM].json   one per claim-source pair, whenever a ledger is intended
Queue      [SERIAL]_visual_queue.md
Output     staged for review, then the site repo
```

| Deliverable | Path | Emitted |
|---|---|---|
| Citations file | `data/citations/{serial}.json` | Always, whether or not a ledger follows |
| Claim drafts | `data/claim_drafts/{serial}/{claim_id}.json` | Whenever a ledger is intended, one per claim-source pair |

Every issue emits, at minimum, the content file and the citations file. Under the full automated pipeline, it also emits the claim drafts, the ledger JSON, and the visual queue. An issue written directly against these specs, without the pipeline, may omit the ledger, the drafts, and the queue, but must then leave every pipeline-derived front matter field absent rather than fabricated (see §9). **The citations file is never omitted:** it is emitted by the authoring pass for every issue, ledger or not. The queue, when it exists, is never committed to the published site.

**Claim drafts are written before authoring, not after, and are committed and retained.** They are the record of the grading pass, not a production artifact like the queue, and discarding them makes the ledger's arithmetic permanently uncheckable at exactly the point where checkability is the product's whole claim. Classification spec §15A.

---

## §14. PUBLICATION CHECKLIST

Checks owned by this document. The classification spec carries its own publication blocks covering evidence, reconciliation, segmentation, grading, analytic integrity, tagging, and record integrity, and those run as well, where a pipeline is grading the issue.

**Structure**

- [ ] All mandatory article sections present and ordered: S1 to S6, S8, S9, S12, S13, S14
- [ ] No empty section headers. Optional sections S7, S10, S11 absent rather than empty
- [ ] Reader legend present: the pointer line for a current-version issue, or the unchanged legacy box for a pre-versioning issue
- [ ] At a glance present if the issue carries `glance` or `stats`, every value honest, no fabricated field to fill a grid
- [ ] Dossier strip present on every actor subheading
- [ ] Coverage continuity block present at the close of S6: cluster lines, or a statement that no prior cluster went quiet, or the bootstrap line where the subject predates cluster identifiers
- [ ] Scope states window, gated position, pool origin distribution, disputed count, contested count, unarchived count, `retrieval_failed` count, the archive attempt position (one attempt against `web.archive.org` is the current standard; a second provider is undecided per classification spec §17 decision 9), and the authoring environment
- [ ] Origin distribution states counts rather than proportions where the pool is under ten sources
- [ ] Total length is in the neighborhood of the cadence target, and no component exceeds its ceiling, counted per thread rather than per section
- [ ] `issueType` set, and the At a Glance field set matches it

**Sourcing mechanics**

- [ ] Every tag carries `data-claim` resolving to a ledger entry, where a ledger exists, and the attribute is absent rather than empty or invented where none does
- [ ] Every grade 4 claim names its primary in the text, every grade 5 claim states where the trail ends, and no grade 6 claim is written as though it were sourced
- [ ] Attribution escalation across the source chain stated in prose, where one occurred
- [ ] Every superscript resolves to an anchor that exists
- [ ] Every claim block carries an `id` and a printing permalink
- [ ] Evidentiary status marked and carried in the prose wherever it is not `observed`
- [ ] Perishable claims dated in the sentence, and absent from the excerpt in the present tense
- [ ] Technique identifiers in the dossier strip transcribed from a cited source, never mapped
- [ ] `issueNumber` omitted on a hand-authored issue. Serial uniqueness is enforced by CI, not checked by hand
- [ ] Media citations carry a timecode, repository citations a commit or version, query citations the query and the statement that it will not reproduce
- [ ] No individual named except as a byline, or as alleged or adjudicated by a named government document
- [ ] Entity names in the dossier strip link to entity pages that exist. The rule stands but is currently unexercised, since no issue links entity names; linking stays off until `/entities/` is populated from ledger data
- [ ] Every `[REF-NNN]` resolves to an S12 entry
- [ ] IOC extraction field present on every actor section, pointing at sources rather than reproducing indicators
- [ ] Hunt Priority block on every actor section, carrying a confidence word and named input claims where gradeable
- [ ] References alphabetized and complete
- [ ] Every URL archived or marked `unarchived`, where the pipeline tracks archival. One attempt against `web.archive.org` is the current standard; a second provider is undecided per classification spec §17 decision 9, and the position is disclosed in Scope and Sourcing rather than presented as a two-attempt guarantee
- [ ] No byline, title, or publication date that was not transcribed from the retrieved document

**Metadata**

- [ ] Serial correct, unique, recorded in the serial ledger, matching the ledger filename
- [ ] `classification_version` and `article_spec_version` set for a current issue and absent for a pre-versioning one, never guessed
- [ ] Front matter emitted honestly: pipeline-derived fields (clusters, claim counts, sectors, actors, pool) present only where actually computed, absent otherwise
- [ ] Author is `not important`, lowercase
- [ ] Title passes the five tests in §5, is under 90 characters, and names one thread rather than enumerating them
- [ ] Slug derived from the right side of the title, not the hook, and never changed after publication
- [ ] Excerpt names the threads the title did not, under 200 characters, no trailing ellipsis

**Rendering**

- [ ] Renders on mobile and desktop, sidebar stacking correctly below 768px
- [ ] Tables stack, monospace blocks wrap
- [ ] No links to pages that do not exist
- [ ] No visual queue content anywhere in the published HTML
- [ ] Figures self-hosted, none hotlinked, every one captioned with source and date, provenance recorded in the queue, alt text describing the behavior rather than the figure
- [ ] Heading levels never skip, tables carry header cells, skip link present
- [ ] Marks distinguishable in grayscale and in print
- [ ] No JavaScript dependency, nothing hidden behind hover
- [ ] Every issue on the homepage grid has a matching at-a-glance cell for its row, or the two-column CSS grid misaligns for every issue after it. Check this specifically when an issue's `glance`/`stats` field is missing or misnamed

**Voice**

- [ ] No em dashes, including in boilerplate and templates
- [ ] No banned constructions
- [ ] No bullet lists inside narrative prose
- [ ] American spelling throughout
- [ ] No sentence asserting more than its ledger claim, where a ledger exists to check against
- [ ] No organizational implications stated for the reader
- [ ] No source confidence restated as the product's own

---

## §15. WHAT THIS DOCUMENT DOES NOT COVER

**The pipeline.** What runs, on what trigger, in what order, and what happens when a stage fails. Track D, the largest remaining body of work. This document describes the artifact, not the machine that makes it. `TI-20260817-001` was authored directly against these specs without a pipeline, as a demonstration that the specs alone are sufficient to produce a correctly-structured issue; it carries no ledger and leaves every pipeline-derived front matter field absent.

**Dispositions and standing assessments.** S11 is reserved and empty pending A5. When A5 lands, this document gains the published format for a standing assessment inside an issue and the frago format for follow-up corrections.

**Cadence.** Track E. Classification spec §12 makes this partly a data question rather than purely an editorial one.

**The short-form line.** Reserved in §0A and specified nowhere. When it is written it gets its own document, inherits the classification spec in full, and inherits from this one only the house style rules named in §0A. Writing it before the issue line has published under v2.6 would mean designing a second voice against an unsettled first one.

**A visual language.** The product has one figure to date. Nothing here says what a house diagram would look like if the product ever drew its own, and §10's rule against generating substitute diagrams means it currently never does. If that ever changes, it changes under a rule that distinguishes a diagram of the product's own analysis from a diagram standing in for a source's, and the second stays forbidden.

**Anything about grading, hunt value tests, or what a tag means.** Classification spec, every time.

---

**Document version:** 2.9
**Companion:** `Classification_System_v4-2_Spec.md`
**Reference implementation:** `PRC_issue_baseline_v2.html`. Note that its title predates §5 as rewritten in v2.6; the file remains authoritative on presentation and is not authoritative on titling
**Next review:** after the first issue published under v2.9 and classification v4.2. The re-grade sampling rate in classification spec §32 and the claim-draft anti-fabrication check both need one real pipeline run through them before anything else changes. After that, A5, which adds the standing assessment and frago formats
