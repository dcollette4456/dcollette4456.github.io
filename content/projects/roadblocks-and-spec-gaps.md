---
title: "Roadblocks & Spec Gaps: Building TI-20260822-001"
date: 2026-08-21
year: "2026"
status: "Build notes"
excerpt: "Notes from authoring the Russia-nexus issue by hand against Classification System v3.8 and Article & Site Design Specification v2.5, no pipeline yet."
type: "projects"
tags: ["classification v3.8", "article spec v2.5", "build notes"]
---

Written while authoring the Russia-nexus issue directly against both specs, no pipeline, the same way `TI-20260817-001` was built. Every item below is something that actually happened during that process, not a hypothetical gap.

## 1. Non-US, non-English primary sources fail silently at Gate 2, and nothing distinguishes "unfetchable by this tool" from "unfetchable by anyone"

CERT-UA's advisory on UAC-0145 (the Sandworm fake-hiring campaign) is a real, named, dated document. It is not a private briefing or a deleted post, the two examples Gate 2 gives for a true grade-5 dead end. It simply would not render through the fetch tool available to me, a JavaScript-driven Ukrainian government site. Both press accounts of it are US trade press.

Gate 2's second bullet already covers "the primary is a real document the pipeline could not retrieve," and correctly routes to grading the relay at 4. That part works. What's missing is that this outcome is indistinguishable, in the published tag, from a case where the primary genuinely cannot be reached by anyone. A hunter reading `MED-4` has no way to know whether a better-resourced reader could pull the CERT-UA page directly and get a `GOV-1`, or whether the trail really does end at a press paraphrase. Over a run of issues, this will systematically demote non-English, non-US government sources, CERT-UA, BSI, ANSSI, JPCERT, relative to US and UK vendor and government sources that happen to render cleanly in a browser, and that demotion has nothing to do with the evidentiary quality of the underlying document.

**Suggested addition to the classification spec, Gate 2 or the access mark (5A):** a fourth access value, something like `retrieval_failed`, distinct from `unarchived`. `unarchived` means no archive provider captured a document the pipeline did see. This new value would mean the pipeline's own tooling failed against a document that appears to exist and be open, and would prompt a retry with a different method (translation-aware fetch, a different renderer, a human check) before the claim is graded down permanently. Whether that retry is worth building is a pipeline question outside this document's scope, but the tag distinction is a classification question and belongs here.

## 2. The 30-day cadence target (four to five threads) is contradicted by the only 30-day issue that has actually shipped

Article spec §3 sets the 30-day target at four to five activity threads and roughly 6,000 words. `TI-20260817-001`, the reference implementation, is a 30-day issue with two threads and well under that length. Building this issue, the real search turned up exactly two threads that cleared the corroboration and evidence bar the specs set, one well-corroborated, one resting on a single relayed advisory. Padding to four or five would have meant including weaker material just to hit a count, which the disclosure doctrine's own logic argues against, thin material is fine to publish, but manufacturing volume to meet a target is a different thing than reporting what a window produced.

The spec anticipates something like this in the open item on cadence (§3, "Open, pending Track E") but frames it as a future editorial decision, not as guidance for what to do right now when a real window's evidence doesn't fill the stated shape. Nothing currently tells an author or a model whether the reference implementation's two-thread issue is the actual template to follow, in which case the four-to-five figure should be marked aspirational or provisional rather than a target, or whether that issue under-delivered and a real 30-day issue should be pushed harder to find more threads.

**Suggested fix:** either mark the cadence table explicitly provisional pending Track E, with a note that the reference implementation is the current authority on shape, not the table, or state directly that thread count is bounded by what clears the evidence bar and never padded, the way length already is ("A quiet window publishes shorter and says so").

## 3. ATT&CK technique IDs in the dossier strip have no sourcing rule when the vendor doesn't publish them

Gate 5's artifact test lists "ATT&CK technique ID" as one of several things that can satisfy checkability. Article spec §6 says the dossier strip carries "technique identifiers... the handful that matter for this section, not the full mapping, which lives in the source," which reads as an assumption that the source states them.

Microsoft's CaptiveCrunch post, the best-sourced document in this issue, does not. It gives a table of tactics and Defender detection names, not MITRE technique IDs. Reconstructing IDs from the described behavior (a captive-portal DNS redirect, an AitM position, a ClickFix-style lure) is a mapping judgment made by whoever writes the issue, not a fact transcribed from the document. Nothing in either spec flags that this mapping is interpretive, requires it to carry any marker distinguishing it from a source-stated ID, or says what to do when confidence in the mapping is low. A wrong self-assigned ID would sit in the dossier strip looking exactly like a transcribed fact, and a reader has no way to tell the difference. That's a real integrity gap given how much weight both documents put on never asserting something a reader can't check.

**Suggested addition:** state explicitly, probably in classification spec §5 alongside the artifact test, that a technique ID not stated by the source is an analytic mapping, not a sourced fact, and either (a) requires an `ANL` marker of its own even inline in the dossier strip, or (b) is barred from the strip entirely when the source doesn't name it, with the mapping left to a hunter's own tooling the same way indicator extraction already is per §9.

## 4. Partial corroboration inside one narrative thread has no attachment point

ReliaQuest and Microsoft both cover the captive-portal Wi-Fi campaign, but only partially overlap. Microsoft explicitly cites ReliaQuest's July 23 report for the device-code phishing slice of the finding, meaning that specific piece is not independent under the §7 independence gate, "did this source publish evidence drawn from data the first source did not provide." But Microsoft's malware-delivery findings (CornFlake, ChocoShell) are not in ReliaQuest's report at all and are genuinely new data.

Section 2's segmentation rule is the correct mechanical fix here, split into separate claims wherever the gate vector changes, and a corroboration mark attaches per claim, not per paragraph or per thread. That did resolve it in this issue. But nothing in either document names this as a recognizable failure pattern the way §6 names the reconciliation-pass drift risk ("a legitimate tag on an overstated sentence... is the default drift direction"). The natural authoring impulse, especially writing prose about "the campaign" as a single narrative, is to inherit one corroboration mark for the whole thread once two vendors are both cited in it, exactly the drift the merge rule in §2 already guards against for grades. Worth stating in plain language, next to that reconciliation-drift note, since it's the same underlying risk applied to corroboration instead of grade.

**Suggested addition to classification spec §7:** a short paragraph naming this pattern directly: two sources covering overlapping ground almost never corroborate uniformly across everything they both touch, and a `×2` mark earned on one sentence must not be allowed to color the reader's sense of the whole thread.

## 5. Vendor-stated government attribution: cite the vendor's paraphrase, or go find the government's own document?

Microsoft's post states, in its own prose, that Midnight Blizzard is attributed by the US and UK governments to Russia's SVR. Gate 3's guidance ("a government advisory built on vendor reporting is GOV-4 unless...") is written for the GOV-citing-VND direction. It doesn't say what to do in the reverse case, a vendor stating a government attribution as background, without citing a specific advisory or indictment.

I graded this `VND-4`, reporting a named finding (the government's designation) it did not itself make. But a stricter reading of the disclosure doctrine argues the correct move is to go find the actual NCSC or CISA document making that designation and cite it directly, since it's a checkable, findable primary and using it would upgrade a `VND-4` boilerplate line to a real `GOV` claim. Neither document tells the author which is required, and the choice materially changes how corroborated a "this is a Russian state actor" claim looks to a reader, at a category of claim, state attribution, that both documents already flag elsewhere as one of the most consequential categories to get right.

**Suggested addition:** a short rule in Gate 3 or §1A stating that a standing government attribution repeated as background by a vendor should be re-sourced to the government's own document when one is findable, rather than graded from the vendor's restatement, since the primary is by definition public and citable and the whole point of the grading system is not to launder a checkable fact through an unnecessary intermediary.

## 6. Neither spec's worked examples cover a CVE-free, pure-tradecraft campaign, which is what most of this window's Russia-nexus reporting actually was

Every worked example in classification spec §2 and §13 involves vendor IR reporting with hashes, CVE identifiers, or KEV entries, artifact-rich material. Both threads in this issue were pure social-engineering and infrastructure-abuse campaigns with no CVE, no KEV entry, and no `TEC` source anywhere. That's not a rare case, it's the profile of a growing share of Russia-nexus reporting this window (device-code phishing, DNS gateway compromise, a trojanized VPN client distributed through a fake hiring process). The gates themselves handled it fine once applied by hand, but there's no worked example anywhere in either document showing segmentation and grading run against a campaign with zero structured records and zero named CVEs, so an author has to extrapolate the CVE-heavy examples rather than follow one.

**Suggested addition:** one worked example in classification spec §2, alongside the existing vendor-IR one, that walks a pure-tradecraft, no-CVE campaign through segmentation and the gates end to end, since this shape of evidence is exactly where an author is least likely to have a template to check their own segmentation against.

## 7. Two mechanical front-matter questions with no stated answer for a hand-authored issue

- **`issueNumber`.** Article spec §4 and §9 both describe it as generated by Hugo from publication order, never authored by hand, and never used to reference an issue in prose. But nothing tells a hand-authored issue, one written outside the pipeline the way this one and `TI-20260817-001` were, whether to omit the field, guess a placeholder, or leave a note for whoever runs the actual Hugo build to fill it in. I omitted it. That's consistent with the spirit of §9's rule for pipeline-derived fields ("absent rather than fabricated"), but `issueNumber` isn't in that list, and the omission is my inference, not a documented instruction.
- **Serial uniqueness.** §14's checklist requires the serial be "recorded in the serial ledger" and unique. There is no serial ledger available to an author working outside the pipeline. I assigned `TI-20260822-001` by the stated date-stamping rule and asserted uniqueness without any way to check it.

**Suggested addition:** a short note in §9 or §13 stating explicitly what a hand-authored, pipeline-less issue should do with both fields, most simply, omit `issueNumber` explicitly per the existing absent-not-fabricated rule, and treat serial uniqueness as provisional, flagged for a human check at commit time, until the pipeline and its ledger exist.

## Not a gap, worth noting anyway

The disclosure doctrine and the gates themselves worked exactly as designed on genuinely awkward material: a partially-hedged initial-access assessment (ReliaQuest's low-to-medium-confidence, explicitly unconfirmed claim about how the gateways were first compromised) graded cleanly to `VND-2` without any temptation to either suppress it or round it up to something more confident than the source stated. That's the system doing its job. The gaps above are all about what happens at the edges the two documents' own worked examples don't reach yet, not about the core mechanism, which held up well under real sourcing.
