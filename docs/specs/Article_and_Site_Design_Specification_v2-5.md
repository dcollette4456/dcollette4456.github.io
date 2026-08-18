# Article and Site Design Specification v2.5
## How an issue is structured, written, rendered, and published

**Status:** Master specification for article generation and site structure
**Prepared:** 19 August 2026
**Supersedes:** v2.4, v2.3, v2.2 and v2.1, and through them v2.0, `Threat_Intelligence_Article_Design_Specification.md` v1.0, and `Design_Spec_Executive_Summary.md`
**Companion:** `Classification_System_v3-8_Spec.md`
**Project:** Knights Who Say Ni. Static Hugo site, GitHub Pages, automated publication, DoD threat hunting audience

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

## §1. WHAT CHANGED

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

Threat hunters need behavior and collection points, and they are the primary audience. Defense analysts need assessment and outlook. The reader's own model needs structured data and named sources, which is how indicators reach a SIEM. General security professionals need context without prerequisite expertise.

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

### Total length by cadence

**Measured, not guessed.** These figures come from a formatted issue built end to end, not from an estimate. Treat them as the shape a well-scoped issue lands in, and never as a limit that cuts content.

| Cadence | Target | What that buys |
|---|---|---|
| Weekly | around 3,000 words | Two activity threads, six to eight sources, two hunt blocks |
| Thirty-day | around 6,000 words | Four to five threads, a cross-cutting section, four or five hunt blocks |

**There is no hard limit and none should be introduced.** A window that produced more publishes longer. A quiet window publishes shorter and says so. The numbers exist so an authoring pass knows roughly what a normal issue looks like, and so nobody pads a thin cycle to hit a length.

**Hunt blocks are the reason issues run long, and that is correct.** The maroon analyst blocks carry more weight per word than anything else in the product, and a thread that earns three paragraphs of hunting reasoning should get them. Length spent there is not padding. Length spent on furniture, metadata, or restating a source is.

### Component ceilings

Word counts are outputs, not targets. These are ceilings that keep any one component from swallowing the issue, applied within the totals above.

| Component | Ceiling |
|---|---|
| Executive summary | 400 words |
| Scope and sourcing | 250 words |
| Source summary entry | 130 words |
| Per actor section | 700 words including the Hunt Priority block |
| Operational domain section | 600 words |
| Emerging tradecraft | 200 words per pattern |
| Assessment and outlook | 500 words |
| Cross-source convergence | 400 words |
| Standing assessments | 300 words |
| Coverage continuity | No cap. One line per cluster |
| Operational Context box | 250 words |
| Appendix A card | 120 words including the evaluation |

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
Classification system v3.8 &middot; Article and site specification v2.5 &middot;
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

**Title.** `Evocative Hook: Concrete Specific`. The country or actor is carried by the template kicker, so the title is free to be purely behavioral.

Good: `Disabling the Fail-Safes: CyberAv3ngers' PLC Attacks on U.S. Water Systems`. Also good: `Access Through the Front Door: Trusted Channel Compromise in PRC-Nexus Operations`. Bad: a bare noun phrase like `Infrastructure Brokerage and Agentic Tooling`, which describes the contents rather than saying anything.

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

**Scope and sourcing.** Ceiling 250 words, carrying five things:

1. The reporting window and what was and was not in scope
2. **The gated position.** How many cited sources were gated, or that none were. A pool with no gated sources skews toward free vendor content, and that is worth stating rather than leaving a reader to notice
3. **The source pool origin distribution.** Where every cited source is US or US-aligned in an issue about a foreign state actor, say so. Not because those sources are wrong, but because a hunter should know they are looking through one lens
4. **Disputed and unarchived counts,** with one sentence each on what they mean here. `One claim is marked disputed: our grading passes read the artifact test differently and we published the conservative reading.`
5. **Out-of-window sources,** where any were used to establish corroboration rather than to introduce a claim

---

## §6. THREAT ACTOR SECTIONS

The densest part of the issue and the part with the most required furniture.

### Subheading and dossier strip

The heading states what was found, in plain language a reader could repeat. "A signed VPN client shipped a backdoor for eleven months" is a heading. "N-central exploitation and downstream managed estates" labels a topic and tells a reader nothing.

Directly beneath it sits the **dossier strip**: a single line of quiet editorial furniture, 10px monospace, letter-spaced, muted, uppercase, closed by a hairline rule. Three fields separated by pipes.

```
CLUSTER NAMES  |  TECHNIQUE IDENTIFIERS  |  ATTRIBUTION CAVEAT
```

Cluster names come first with the canonical name in a heavier weight. Technique identifiers are the handful that matter for this section, not the full mapping, which lives in the source. The attribution caveat is one clause: who declined to attribute, who hedged, or what is disputed.

This replaces the multi-line alias block, which ran two or three lines of dense metadata directly under the heading and stopped a reader before they reached a sentence. Full alias provenance with assigning source and date lives in the cluster table and at `/coverage/sources/`. The strip carries what a reader needs in passing.

### Body

Prose. No bullet lists in narrative. Each graded claim carries its tag inline with `data-claim`, plus the corroboration and disputed marks where they apply. State what was observed and who observed it, and leave what it means to the Hunt Priority block and any `ANL` block.

**Write the behavior, not the indicator list.** "Three signed drivers loaded from a user-writable directory, then kernel-mode termination of security processes" is what a hunter works with. The hashes of those drivers belong in the source, and the IOC extraction field points there.

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

### `ANL` blocks

Rendered per the classification spec, naming the claim identifiers they rest on. One per major section, excluding the Hunt Priority block, S4, and S9, which are themselves `ANL` sections.

---

## §7. CITATIONS

Two systems running together, both specified.

**Superscript citations** attach to any number, date, version string, CVE, named infrastructure, or source-stated confidence appearing in prose. They resolve to the reference list. They never appear inside an `ANL` block or a Hunt Priority block, because those are the author speaking and citing them blurs the boundary the format exists to protect.

**`[REF-NNN]` identifiers** are used in S12, in the IOC extraction field, and anywhere a source is named as an object rather than cited as support.

**`data-claim` on every tag.** Every tagged sentence carries its ledger claim identifier in the markup. This is what makes the reconciliation pass in classification spec §15 possible, and it is also the join a reader's own tooling uses to pull the ledger entry behind any sentence. A tag without it blocks publication.

**Every superscript resolves to an anchor that exists.** A superscript pointing at a missing anchor blocks publication.

**Bylines, titles, and publication dates are transcribed from the retrieved document or omitted.** Never inferred, never reconstructed from a house style. Also a publication block in the classification spec, and it appears here because it is an authoring failure before it is a ledger failure.

**Appendix A card format** is in classification spec §16, including the rules governing the evaluation sentence. One card per source cited, no fixed count. The evaluation is an `ANL` construct that may assert only what is derivable from the fields printed on that card and the claims cited from that source in this issue.

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

**The grade digit is never colored differently by grade.** A five-color scale reads as a quality verdict and it is not one. Source-type prefix does carry a background tint (four tints, matching the site's original four categories, extended to the nine-type vocabulary by mapping several types to the nearest existing tint rather than inventing five more colors).

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

## §9. HUGO FRONT MATTER

The authoring pass emits front matter. Nobody adds it afterward.

```yaml
---
title: "Access Through the Front Door: Trusted Channel Compromise in PRC-Nexus Operations"
date: 2026-08-17
issueNumber: 36
serial: "TI-20260817-001"
reportSerial: "TI-20260817-001"
version: 1
classification_version: "3.8"
article_spec_version: "2.5"
kicker: "PRC"
primaryThreat: "PRC"
dateRange: "18 JUL – 17 AUG 2026"
window_start: 2026-07-18
window_end: 2026-08-17
excerpt: "Open-source intelligence summary on PRC-nexus trusted-channel compromise: a trojanized VPN client and a remote management platform breach, 18 July to 17 August 2026."
standfirst: "Open-Source Intelligence Summary: 18 July - 17 August 2026. Threat Operations Assessment."
author: "not important"
sourceBasis: "Open-source reporting from threat intelligence firms, vendor disclosures, government advisories, and security research. See References for full citations."
disclaimer: "This report synthesizes open-source threat intelligence to support threat-hunting operations and risk assessment. All material is publicly available. Information sourced, dated, and classified for transparency and verification."
glance:
  - label: "Window"
    value: "30 days"
  - label: "Threat"
    value: "PRC-nexus"
  - label: "Sectors"
    value: "Technology, Finance"
  - label: "Hunt surface"
    value: "2 behaviors"
glanceNote: "Seven sources, three of them press relaying a single primary each."
---
```

`serial` is canonical; `reportSerial` is carried alongside it for backward compatibility with the template code that predates the field rename and is not deprecated, since duplicating the value costs nothing and nothing depends on removing it.

`clusters`, `clusters_quiet`, `actors_subject`, `actors_referenced`, `sectors_confirmed`, `sectors_context`, `actionable_for`, `claims_graded`, `claims_huntable`, `claims_disputed`, `claims_unarchived`, and `pool` are all grading-pipeline output. **An issue authored without the pipeline (by a model working from the specs directly, as `TI-20260817-001` was) leaves every one of these absent rather than guessing at a value.** A zero or an empty list is a claim about the world, and an honest absence is not the same thing as one.

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

---

## §11. VOICE

**Do.** Lead with the finding. Active voice. Terse sentences. Separate observation from interpretation. Be specific, so "GitHub Raw Content API calls" rather than "GitHub activity". Describe behavior in terms a defender could build a detection from. Write hunting guidance as guidance and background as background. Respect the reader's expertise.

**Do not.** No em dashes anywhere, including inside templates, comments, and commit messages. No "notably", "it's worth noting", "interestingly", "bottom line". No AI tells. No bullet lists inside narrative prose. No hedging by adverb, since uncertainty belongs in the tag or in an `ANL` confidence word. No telling readers what the finding means for their organization, which is their own tooling's job.

**Do not overstate a claim past its ledger entry.** The reconciliation pass in classification spec §15 checks for exactly this and blocks it. A sentence that widens a source's observation is the most likely honest-looking failure this product can make, and it is easier to avoid at writing time than to fix at block time.

**Spelling is American throughout,** in the article, in both specifications, and in templates.

**On confidence.** Do not restate a source's confidence as though it were the product's. The source's hedging is a gate input. Where the author disagrees with a source, that is an `ANL` block naming the claim it disputes, never an adjective attached to the source's claim.

**Tone.** Someone who has reverse-engineered malware, correlated infrastructure across campaigns, and knows what a hunter needs before lunch.

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

**No longer blocking.** `/coverage/sources/` exists, so the v2.4 publication block tied to its absence no longer applies.

**Nav discipline.** A section in the nav returning 404 costs more credibility than a missing section, particularly for a product whose entire pitch is that you can check its work. Current nav: Latest, Archive, Academics, Coverage, Projects.

**Empty states, never placeholder data.** A registry rendering fabricated numbers would be a worse failure than a registry rendering nothing.

**Migration banner.** Renders when `classification_version` is **absent or lower than the current version**. Absence is the common case, because those issues predate the field. A banner keyed only on a declared older version would match nothing.

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
Ledger     /data/ledger/[SERIAL].json            when the pipeline exists; absent for a hand-authored issue
Queue      [SERIAL]_visual_queue.md
Output     staged for review, then the site repo
```

Every issue emits, at minimum, the content file. Under the full automated pipeline, it also emits the ledger JSON and the visual queue. An issue written directly against these specs, without the pipeline, may omit the ledger and the queue, but must then leave every pipeline-derived front matter field absent rather than fabricated (see §9). The queue, when it exists, is never committed to the published site.

---

## §14. PUBLICATION CHECKLIST

Checks owned by this document. The classification spec carries its own publication blocks covering evidence, reconciliation, segmentation, grading, analytic integrity, tagging, and record integrity, and those run as well, where a pipeline is grading the issue.

**Structure**

- [ ] All mandatory article sections present and ordered: S1 to S6, S8, S9, S12, S13, S14
- [ ] No empty section headers. Optional sections S7, S10, S11 absent rather than empty
- [ ] Reader legend present: the pointer line for a current-version issue, or the unchanged legacy box for a pre-versioning issue
- [ ] At a glance present if the issue carries `glance` or `stats`, every value honest, no fabricated field to fill a grid
- [ ] Dossier strip present on every actor subheading
- [ ] Coverage continuity block present at the close of S6, or explicitly stating no prior cluster went quiet, where the pipeline tracks clusters
- [ ] Scope states window, gated position, pool origin distribution, disputed count, unarchived count
- [ ] Total length is in the neighborhood of the cadence target, and no component exceeds its ceiling

**Sourcing mechanics**

- [ ] Every tag carries `data-claim` resolving to a ledger entry, where a ledger exists
- [ ] Every superscript resolves to an anchor that exists
- [ ] Every `[REF-NNN]` resolves to an S12 entry
- [ ] IOC extraction field present on every actor section, pointing at sources rather than reproducing indicators
- [ ] Hunt Priority block on every actor section, carrying a confidence word and named input claims where gradeable
- [ ] References alphabetized and complete
- [ ] Every URL archived or marked `unarchived`, where the pipeline tracks archival
- [ ] No byline, title, or publication date that was not transcribed from the retrieved document

**Metadata**

- [ ] Serial correct, unique, recorded in the serial ledger, matching the ledger filename
- [ ] `classification_version` and `article_spec_version` set for a current issue and absent for a pre-versioning one, never guessed
- [ ] Front matter emitted honestly: pipeline-derived fields (clusters, claim counts, sectors, actors, pool) present only where actually computed, absent otherwise
- [ ] Author is `not important`, lowercase

**Rendering**

- [ ] Renders on mobile and desktop, sidebar stacking correctly below 768px
- [ ] Tables stack, monospace blocks wrap
- [ ] No links to pages that do not exist
- [ ] No visual queue content anywhere in the published HTML
- [ ] Figures self-hosted, none hotlinked, every one captioned with source and date
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

**Anything about grading, hunt value tests, or what a tag means.** Classification spec, every time.

---

**Document version:** 2.5
**Companion:** `Classification_System_v3-8_Spec.md`
**Reference implementation:** `PRC_issue_baseline_v2.html`
**Next review:** after A5, which adds the standing assessment and frago formats, or after the next round of direct feedback on the live site, whichever comes first
