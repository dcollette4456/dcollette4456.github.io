# How to publish a new issue

A practical step-by-step, not a spec. For what everything means, see
`specs/Article_and_Site_Design_Specification_v2-5.md` and
`specs/Classification_System_v3-8_Spec.md`. This is the short version for
actually doing it.

Worked example throughout: `content/issues/prc-trusted-channel-compromise.md`,
the first issue published this way.

## 1. Create the content file

```
content/issues/[slug].md
```

Pick a slug from the title, lowercase, hyphenated, no serial number in the
filename (the serial goes in front matter, not the path).

## 2. Front matter

Copy this block and fill it in. Every field here was used by the PRC issue.

```yaml
---
title: "Evocative Hook: Concrete Specific"
date: 2026-08-17
issueNumber: 37
readingTime: "9 min"
excerpt: "One sentence: open-source intelligence summary on [subject], [start] to [end]."
standfirst: "Open-Source Intelligence Summary: [start] - [end]. Threat Operations Assessment."
primaryThreat: "PRC"
kicker: "PRC"
dateRange: "18 JUL – 17 AUG 2026"
window_start: 2026-07-18
window_end: 2026-08-17
version: 1
serial: "TI-YYYYMMDD-NNN"
reportSerial: "TI-YYYYMMDD-NNN"
classification_version: "3.8"
article_spec_version: "2.5"
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
glanceNote: "One sentence: how many sources, and who this is actionable for."
---
```

**issueNumber** is display-only; use the next integer after whatever's currently
highest on the site (check `/issues/`).

**serial**: `TI-YYYYMMDD-NNN`, date of publication, `NNN` resets to `001` each
date. Check `data/serials.json` for what's already been issued and add yours
to that list once you publish (see step 6).

**classification_version / article_spec_version**: set these to the current
versions (`3.8` / `2.5` as of this writing) for any new issue. Leave both
completely absent if you're deliberately publishing something that predates
grading (you almost never want this; it's what makes Iran and DPRK render
with the migration banner and the old legend box).

**glance / glanceNote**: optional. If you don't have real numbers for a
field, leave the whole `glance` list off rather than putting in a guess. The
homepage and the article sidebar both render fine with no glance box at all.

## 3. Write the body in markdown, using the shortcodes

These are the six shortcodes built for this format. All of them are plain
Hugo shortcodes, no different from writing markdown.

**A sourced claim**, with an inline tag:

```
{{</* claim tag="VND-1" corroborated="2" claim="C001" */>}}
Prose describing what was observed and who observed it.
{{</* /claim */>}}
```

- `tag`: `TYPE-GRADE`, e.g. `VND-1`, `GOV-4`, `TEC-1`, `MED-4`. See the type
  table in the classification spec §3 and the grade scale in §4 if you're
  not sure which to use.
- `corroborated`: omit unless two or more independent sources back the same
  claim. If set, prints `×2 corroborated` etc.
- `claim`: an id like `C001`, sequential within the issue. Optional today
  (nothing downstream reads it yet, since there's no pipeline), but keep
  numbering them, since it costs nothing and this field is exactly what a
  future pipeline will key off of.

**An actor dossier strip**, directly under an `### h3` subheading:

```
{{</* dossier names="**Mustang Panda**" techniques="T1195.002 · T1574.001" caveat="attribution declined by both reporting vendors" */>}}
```

**A hunt-priority block**:

```
{{</* hunt stage="Presence" telemetry="file-write, image-load, dns" built-on="two corroborated vendor observations" sources="Fortinet publishes hashes and staging domains; point your own model at the source to pull them." */>}}
Prose: one to three paragraphs of hunting reasoning.
{{</* /hunt */>}}
```

`stage` is a Common Cyber Threat Framework stage name (Presence, Effect,
etc). `telemetry` is a comma list from the closed vocabulary in
classification spec §9. `sources` is the closing line pointing at where
indicators actually live; never paste hashes or IPs into the article itself.

**A superscript citation**, inline in a sentence:

```
eleven months{{</* cite 3 */>}}
```

The number matches a reference's `id="ref3"` in the References section
(step 4).

**A source summary card**, one per source cited, under `## Appendix A: Source Summaries`:

```
{{</* src title="[REF-003] Report Title" byline="Vendor · Date · vendor incident response" url="https://..." urltext="short-domain.com/path" */>}}
One paragraph, up to 130 words, on what the source found.
{{</* /src */>}}
```

**An analytic assessment marker**, for a section that's the product's own
judgment sitting inside otherwise sourced narrative:

```
{{</* sectiontag "Our assessment · moderate confidence" */>}}
```

## 4. Write the References section

Plain HTML list, not markdown, so each entry gets a stable anchor for the
superscript citations to jump to:

```html
<ol class="refs">
<li id="ref1">Author. "Title." <em>Publisher</em>, Date, <a href="https://...">short-url</a>.</li>
<li id="ref2">...</li>
</ol>
```

Alphabetize by author or publisher. Every `{{< cite N >}}` in the body must
have a matching `id="refN"` here.

## 5. Build and check it locally

```
hugo server --port 1313
```

Open `http://localhost:1313/issues/[slug]/` and read through it. Specifically
check:

- The kicker/title/standfirst/metadata row all show what you expect
- If you set `glance`, the sidebar box shows it; if you didn't, the sidebar
  just shows Contents (and Hunt Priorities if you set those)
- Every claim tag renders as a small chip, not raw shortcode text (if you
  see literal `{{< claim ... >}}` on the page, a shortcode tag is malformed)
- Every citation number is a working link down to the reference list
- No migration banner (that means `classification_version` didn't get read;
  check the front matter block for a typo)

Also check the homepage (`http://localhost:1313/`): your issue's "at a
glance" box should sit next to its title, not shifted down or missing. If
it's missing entirely and you did set `glance`, that's the bug fixed in
`layouts/_default/index.html` on 19 August 2026; make sure you're on a
branch that includes it.

## 6. Record the serial

Add your serial to `data/serials.json`, alphabetically or chronologically,
either is fine as long as it's consistent:

```json
[
  "TI-20260809-001",
  "TI-20260811-001",
  "TI-20260817-001",
  "TI-YYYYMMDD-NNN"
]
```

## 7. Commit, branch, PR

```
git checkout main && git pull
git checkout -b add-[slug]
git add content/issues/[slug].md data/serials.json
hugo --quiet   # rebuild public/ before committing it
git add public/
git commit -m "Add [slug] issue"
git push -u origin add-[slug]
```

Open the PR (the push output prints the compare URL), review the diff,
merge. GitHub Pages deploys automatically on merge to `main`, usually live
within a minute or two.

## What this does not cover

Grading. Nothing here computes a grade for you, checks whether a claim's
gate vector is right, or verifies a `data-claim` id resolves to a ledger
entry, because there is no ledger yet (Track D, the pipeline, is still
unbuilt). Writing an issue this way means you are doing the grading by eye,
the same way `TI-20260817-001` was written: read the source, decide the
type and grade honestly using classification spec §3-§5, and don't tag
something `VND-1` if it's really a `MED-4` relay.
