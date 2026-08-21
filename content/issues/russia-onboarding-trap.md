---
title: "Install to Continue: How Russia-Nexus Operators Turned Routine Prompts Into Initial Access"
date: 2026-08-21
type: "issues"
issueNumber: 37
readingTime: "10 min"
serial: "TI-20260822-001"
reportSerial: "TI-20260822-001"
version: 1
classification_version: "3.8"
article_spec_version: "2.5"
kicker: "RUS"
primaryThreat: "RUS"
dateRange: "23 JUL – 22 AUG 2026"
window_start: 2026-07-23
window_end: 2026-08-22
excerpt: "Open-source intelligence summary on Russia-nexus initial access: captive-portal Wi-Fi credential theft attributed to a Midnight Blizzard sub-cluster, and a Sandworm-linked fake hiring campaign trojanizing WireGuard, 23 July to 22 August 2026."
standfirst: "Open-Source Intelligence Summary: 23 July - 22 August 2026. Threat Operations Assessment."
author: "not important"
sourceBasis: "Open-source reporting from threat intelligence firms, vendor disclosures, government advisories, and security research. See References for full citations."
disclaimer: "This report synthesizes open-source threat intelligence to support threat-hunting operations and risk assessment. All material is publicly available. Information sourced, dated, and classified for transparency and verification."
glance:
  - label: "Window"
    value: "30 days"
  - label: "Threat"
    value: "Russia-nexus"
  - label: "Sectors"
    value: "Hospitality, cross-sector travelers, IT/MSP"
  - label: "Hunt surface"
    value: "2 behaviors"
glanceNote: "Four sources, two of them vendor incident research and two press relaying one unretrieved government advisory."
---

## Executive Summary

Two disclosures this window show a Russia-nexus pattern of reaching a target through a step the victim expected to take anyway, rather than through an exploit. A cluster Microsoft tracks as Storm-2945, assessed as a Midnight Blizzard sub-cluster, compromised the Wi-Fi gateways of hotels and conference venues and used administrative control of those gateways to redirect corporate travelers into credential theft and malware delivery, no phishing email required{{< cite 3 >}}. Separately, CERT-UA reported a Sandworm-linked cluster tracked as UAC-0145 running a months-long fake hiring process against Ukrainian system administrators, ending in a trojanized WireGuard client that the candidate was talked into installing as part of a bogus technical interview{{< cite 2 >}}.

Neither operation asked the victim to click a suspicious link. The Wi-Fi campaign relied on a captive portal login every traveler already goes through. The hiring campaign relied on a VPN client every remote technical candidate is asked to install. Both actors built a plausible reason for the install to fail on the first try, then supplied the malicious file as the fix.

The two disclosures also differ in exactly the way a hunter should care about. The Wi-Fi campaign is corroborated by two vendors working from separate telemetry, with one, Microsoft, publishing an unusually complete artifact set: hashes, C2 infrastructure, and hunting queries against Defender and Sentinel data{{< cite 3 >}}. The hiring campaign rests on a single government advisory that no vendor has yet corroborated with an independent technical report, and that advisory could not be retrieved directly for this issue{{< cite 1 >}}{{< cite 2 >}}. Both are worth a hunter's attention. Only one of them is currently checkable against a second, independent source.

A secondary finding from the Wi-Fi campaign deserves separate note. Microsoft's attribution of the specific malware-delivery activity to a Midnight Blizzard sub-cluster rests on technical overlaps ReliaQuest's earlier report did not have access to. ReliaQuest's own investigation of the same window of gateway compromises found tradecraft resembling a different, GRU-linked actor's earlier campaign and declined to attribute further{{< cite 4 >}}. The two vendors are not contradicting each other. They are describing overlapping infrastructure from different vantage points, and the overlap itself, not either single report, is the more interesting hunt lead.

## Scope and Sourcing

Reporting window is 23 July to 22 August 2026. Four sources: two vendor incident research publications and two trade press outlets, both relaying the same government advisory. No subscription sources were consulted. No source in this issue is gated.

One claim in this issue could not be graded past a relay position. CERT-UA's advisory on the UAC-0145 hiring campaign is cited by both press sources but the advisory page itself did not render retrievable content for this pipeline; the document actually read in both cases is the press account, not the agency's own text, and that is what is tagged. Zero claims are marked disputed. Zero cited sources sit outside the window.

Three of four sources are US-headquartered vendors or US trade press; the fourth is a Ukrainian government agency, cited only through American press relay. A reader should weigh that a Ukrainian technical response to an operation against Ukrainian IT workers is being read here at two removes from its source.

## Trusted Channel Compromise

### A hotel Wi-Fi login became a malware delivery channel

{{< dossier names="**Storm-2945 (Midnight Blizzard)**" techniques="T1584 · T1557 · T1204.002 · T1071.001" caveat="attributed to a Midnight Blizzard sub-cluster by Microsoft; ReliaQuest notes separate TTP overlap with APT28 without attributing" >}}

{{< claim tag="VND-1" claim="C001" >}}
Since at least June 2026, an actor gained administrative control of Wi-Fi gateways at hotels and conference venues across multiple US cities, India, and Saudi Arabia, then used that control to forge DNS responses for every connecting guest{{< cite 4 >}}. Because the gateway is the DHCP-assigned resolver for the network, no endpoint had to be touched individually: a query for a Microsoft authentication domain was silently answered with an attacker-controlled address, and the redirected session then flowed through infrastructure built to imitate Microsoft's login pages. Traffic to the compromised gateways came from organizations across financial services, professional services, legal, healthcare, energy, and retail, which ReliaQuest reads as targeting of the traveling employee rather than any one sector{{< cite 4 >}}.
{{< /claim >}}

{{< claim tag="VND-2" claim="C002" >}}
How the gateways were first compromised is not established. ReliaQuest assesses with low-to-medium confidence that exposed management interfaces, SSH, SNMP, and web administration consoles, combined with weak or reused administrator credentials, but states plainly that visibility constraints prevented confirming this{{< cite 4 >}}.
{{< /claim >}}

{{< claim tag="VND-1" claim="C003" >}}
In roughly a third of cases, the actor also attempted to abuse Windows' automatic proxy discovery feature, a technique not documented in the vendor's own earlier reporting on a related SOHO router campaign. Where it succeeded, it would route most of a device's application traffic, not just authentication traffic, through the attacker's proxy{{< cite 4 >}}.
{{< /claim >}}

{{< claim tag="VND-1" claim="C004" >}}
On at least one domain, ms365-live[.]com, ReliaQuest directly observed the redirect flow abusing Microsoft's device code authentication, a legitimate protocol for sign-in on devices without a normal browser. A user approving what looks like an ordinary sign-in prompt actually authorizes a session the attacker initiated, handing over MFA-satisfied access without the attacker ever touching a password{{< cite 4 >}}.
{{< /claim >}}

{{< claim tag="VND-1" corroborated="2" claim="C005" >}}
Microsoft's own investigation, published eight days later, describes the same window of captive-portal traffic manipulation and attributes it to Storm-2945, which it assesses is an operational sub-cluster of Midnight Blizzard. The attribution rests on named technical and operational overlaps with Storm-2372, a Midnight Blizzard sub-cluster previously tracked for device code and OAuth phishing, plus shared victimology{{< cite 3 >}}. Beyond the redirect infrastructure ReliaQuest had already reported, Microsoft's own telemetry adds a second stage that ReliaQuest's report does not describe: malware delivered through fake browser and operating system update prompts. A Go-language remote access tool the vendor calls CornFlake establishes persistence as a disguised Windows service and provides keylogging, clipboard and screenshot capture, audio and video surveillance, and browser credential theft. A companion PowerShell tool, ChocoShell, runs entirely in memory, disables the Windows antimalware interface, and extracts browser session cookies, saved passwords, and Microsoft 365 single sign-on tokens, including from browsers using the newer app-bound encryption scheme{{< cite 3 >}}.
{{< /claim >}}

{{< claim tag="VND-4" claim="C006" >}}
Both reporting vendors, and Microsoft directly, state that Midnight Blizzard is attributed by the US and UK governments to Russia's Foreign Intelligence Service, the SVR{{< cite 3 >}}.
{{< /claim >}}

#### Operational Context: Device Code Phishing

Device code authentication is an OAuth flow built for sign-in on devices with no browser of their own, like a streaming box or a CLI tool. A user visits a generic sign-in page and types in a short code shown elsewhere. Abused, an attacker starts that flow on the victim's behalf and needs only to talk the victim into typing the attacker's code into a legitimate Microsoft page. The resulting token belongs to the attacker's session, not the victim's device, and it satisfies MFA because the victim really did complete a valid sign-in, just not their own.

**Key points:**
- No credential is intercepted or guessed; the victim authorizes the attacker's session directly
- Works over an already-compromised network channel or through a simple social engineering prompt
- Blockable at the identity provider by disabling the device code flow in Conditional Access where it has no legitimate business use

{{< hunt stage="Presence" telemetry="dns, proxy-http, authentication, file-write, process-execution" built-on="two vendor observations of overlapping but not identical infrastructure" sources="ReliaQuest{{< cite 4 >}} publishes the gateway-redirect IP addresses, four impersonation domains, and the registrant email tying them together. Microsoft{{< cite 3 >}} publishes a separate, non-overlapping infrastructure set for the malware-delivery stage, two file hashes, and four Kusto hunting queries for Defender and Sentinel. Point your own model at both reports; they do not share an indicator set." >}}
The redirect infrastructure is the durable surface, not any single implant. A captive-portal compromise gives an actor DNS for every guest on the network, and endpoint controls see nothing until a device already following the poisoned resolver's answers reaches out for an update. The single control that closes this path for corporate devices is an always-on, full-tunnel VPN that establishes before internet access is permitted, so DNS never reaches the venue's resolver at all. Where that is not yet universal, hunt for Windows devices making automatic proxy discovery lookups shortly after joining a new network, followed within minutes by a download of an executable, installer, or archive: that sequence is what a hunter can query for now against data most managed fleets already keep.

Device code abuse deserves its own watch independent of the network layer. A sign-in risk policy or a Conditional Access rule blocking the flow entirely removes the technique regardless of which network the victim is on, and detecting anomalous device code completions after a captive-portal session is a query worth running even in an estate that has not confirmed exposure to this specific campaign.

On the attribution: Storm-2945's link to Midnight Blizzard rests on data only Microsoft holds, chiefly its comparison to a previously tracked sub-cluster's tradecraft. ReliaQuest's independent look at overlapping gateway-compromise infrastructure points toward tradecraft it has separately linked to a different Russian military intelligence actor, without committing to either identity. A hunt scoped to "Midnight Blizzard" alone would miss infrastructure that ReliaQuest's report describes and that Microsoft's does not fully subsume, and the reverse is also true.
{{< /hunt >}}

### A months-long fake hiring process delivered a trojanized VPN client

{{< dossier names="**Sandworm (UAC-0145)**" caveat="attributed by CERT-UA only; no independent vendor technical report" >}}

{{< claim tag="MED-4" claim="C007" >}}
CERT-UA reports that a Sandworm-linked cluster it tracks as UAC-0145, a sub-cluster of UAC-0002, has since at least May 2026 been posing as recruiters on legitimate Ukrainian job platforms to target system administrators and other IT professionals. After reviewing a candidate's resume, the operators made contact claiming to represent a staffing firm called Atlas Business Group hiring for a project with Sopra Steria Bulgaria, part of a real international IT services company. Contact moved from the job site's chat to Telegram, then to a Zoom interview with an English-speaking interviewer CERT-UA could not confirm was a live participant{{< cite 1 >}}{{< cite 2 >}}.
{{< /claim >}}

{{< claim tag="MED-4" claim="C008" >}}
The candidate was then sent, by an email address styled to resemble a regional Sopra Steria address, WireGuard configuration files for a claimed technical assessment. Those files were built to fail. When the candidate reported a connection error, the fake interviewer directed them to a custom client called SopraVPN, hosted on SourceForge and linked from a spoofed site at soprasteria-bg[.]com{{< cite 1 >}}{{< cite 2 >}}.
{{< /claim >}}

{{< claim tag="MED-4" claim="C009" >}}
SopraVPN is built from the legitimate, unmodified WireGuard open-source codebase with one addition: a custom configuration option, SymmetricKey, that the client uses along with the connection's private key to decrypt a payload embedded in the configuration file itself using AES-256-GCM. On successful decryption, the Windows variant creates a scheduled task and retrieves an additional payload; a Linux variant uses curl to fetch an executable from attacker infrastructure{{< cite 1 >}}. CERT-UA did not disclose a victim count or a stated objective for the operation{{< cite 2 >}}.
{{< /claim >}}

{{< claim tag="MED-4" claim="C010" >}}
CERT-UA attributes the cluster to Sandworm, also tracked as APT44, Seashell Blizzard, and UAC-0002, long linked by Western governments to Russia's GRU military intelligence service and to some of the most disruptive cyberattacks recorded against Ukrainian infrastructure{{< cite 2 >}}.
{{< /claim >}}

{{< hunt stage="Initial access" telemetry="file-write, process-execution, scheduled-task, network-flow" built-on="one government advisory, unretrieved, read through press relay" sources="Neither press account reproduces file hashes, IP addresses, or the full SourceForge project names CERT-UA's advisory reportedly documents. Point your own model at CERT-UA's advisory directly if your environment can reach it; this issue could not." >}}
Nothing about this chain requires a vulnerability. The choke point is the moment a candidate is asked to run an unfamiliar installer as part of a legitimate-seeming hiring process, and that moment is defined by human process, not by network telemetry alone. An organization's own recruiting workflow is the place to start: does any legitimate technical assessment at this organization ever require installing software from outside a managed catalog, and if the answer is no, that policy is worth restating to staff explicitly rather than assumed to be obvious.

Where telemetry can help, the useful signal is a WireGuard-derived binary that is not the organization's sanctioned client, particularly one that decrypts and executes content pulled from its own configuration file. Endpoint tooling that inspects configuration files as inert text will not catch a payload hidden inside one; file integrity or application control policies scoped to installed VPN clients, keyed on binary hash or publisher signature rather than file name, would.

The wider pattern is not new. State actors from more than one country have used fake recruiters to reach specific technical roles this year, and a hunt team's screening process for its own hiring pipeline is a legitimate place to apply the same suspicion it would apply to an unsolicited email.
{{< /hunt >}}

## What Connects Them

{{< sectiontag "Our assessment · moderate confidence" >}}

Both operations moved the point of compromise away from anything an endpoint security stack is built to watch. One redirected DNS at the network gateway, upstream of every device on it. The other redirected trust through a hiring process, upstream of any file an email gateway would have scanned. In both cases the actor did not need the target to make a mistake; they needed the target to complete a step that looked like the next reasonable one in a process already underway.

The failure-then-fix structure appears in both chains independently, and it is worth naming as a pattern rather than a coincidence specific to either actor. A provided WireGuard configuration engineered to fail, followed by a "fix" that is the actual payload, and a captive portal connectivity check that never succeeds until a fake update is accepted, are the same move: manufacture a small, plausible obstacle, then hand the victim the malicious file as the solution to a problem the actor created. A defender briefing staff on phishing awareness alone will miss this, because nothing about either lure resembles a phishing email.

Confidence on the connection is moderate rather than high because the two clusters are tracked separately, by different reporting organizations, with no source in this issue asserting operational coordination between them. The pattern is a tradecraft observation, not an attribution claim.

## Appendix A: Source Summaries

{{< src title="[REF-001] Sandworm-Linked UAC-0145 Uses Fake Job Interviews to Push VPN That Can Run Commands" byline="The Hacker News · 11 August 2026 · trade press" url="https://thehackernews.com/2026/08/sandworm-linked-uac-0145-uses-fake-job.html" urltext="thehackernews.com/2026/08/sandworm-linked-uac-0145-uses-fake-job.html" >}}
Relays a CERT-UA advisory on UAC-0145, a Sandworm/UAC-0002 sub-cluster, running a months-long fake recruitment operation against Ukrainian IT staff since May 2026. Describes SopraVPN, a modified WireGuard client that decrypts an AES-256-GCM payload embedded in its own configuration file via a custom SymmetricKey option, and quotes CERT-UA directly on the client's construction. Notes a second, non-downloadable SourceForge project using similar branding. Publishes no independently verified indicators of its own.
{{< /src >}}

{{< src title="[REF-002] Russian Military Hackers Pose as Recruiters to Target Ukrainian IT Workers" byline="The Record from Recorded Future News · Daryna Antoniuk · 10 August 2026 · trade press" url="https://therecord.media/russian-military-hackers-pose-as-recruiters-ukraine-it-workers" urltext="therecord.media/russian-military-hackers-pose-as-recruiters-ukraine-it-workers" >}}
Relays the same CERT-UA advisory with additional detail on the recruitment sequence: initial contact through a job site's chat feature, a move to Telegram, and a Zoom interview with an unconfirmed participant. States CERT-UA did not disclose a victim count. Notes fake-recruiter tradecraft previously reported against PRC and DPRK-linked operations as points of comparison, not evidence of coordination.
{{< /src >}}

{{< src title="[REF-003] CaptiveCrunch: Midnight Blizzard Targets Travelers Worldwide for Malware Delivery and Credential Theft" byline="Microsoft Threat Intelligence · 31 July 2026 · vendor research" url="https://www.microsoft.com/en-us/security/blog/2026/07/31/captivecrunch-midnight-blizzard-targets-travelers-worldwide-for-malware-delivery-and-credential-theft/" urltext="microsoft.com/en-us/security/blog/2026/07/31/captivecrunch-midnight-blizzard-targets-travelers-worldwide-for-malware-delivery-and-credential-theft" >}}
Documents Storm-2945, assessed as a Midnight Blizzard sub-cluster, manipulating DNS and HTTP traffic on hospitality captive portals since May 2026 and delivering a Go-language RAT (CornFlake) and an in-memory PowerShell infostealer (ChocoShell) via ClickFix-style fake update prompts. Publishes domains, IP addresses, two file hashes, and four Kusto hunting queries for Defender and Sentinel. Cites and builds on ReliaQuest's July 23 report for the device-code phishing portion of the campaign. States the initial compromise vector for captive portal networks remains under investigation.
{{< /src >}}

{{< src title="[REF-004] DNS Poisoning Tactics Expand to Hospitality Wi-Fi" byline="ReliaQuest Threat Research · 23 July 2026 · vendor research" url="https://reliaquest.com/blog/threat-spotlight-dns-poisoning-tactics-expand-to-hospitality/" urltext="reliaquest.com/blog/threat-spotlight-dns-poisoning-tactics-expand-to-hospitality" >}}
Documents administrative compromise of hotel and conference captive-portal gateways used for DNS response forgery against corporate travelers across the US, India, and Saudi Arabia since June 2026. Publishes redirect infrastructure, a registrant email, and cross-sector victim traffic data from the firm's own investigation. Assesses initial access vector at low-to-medium confidence, explicitly unconfirmed. Notes tradecraft overlap with an APT28-attributed SOHO router campaign disclosed in April 2026 without attributing this campaign to APT28.
{{< /src >}}

## References

<ol class="refs">
<li id="ref1">The Hacker News. "Sandworm-Linked UAC-0145 Uses Fake Job Interviews to Push VPN That Can Run Commands." 11 Aug. 2026, <a href="https://thehackernews.com/2026/08/sandworm-linked-uac-0145-uses-fake-job.html">thehackernews.com/2026/08/sandworm-linked-uac-0145-uses-fake-job.html</a>.</li>
<li id="ref2">Antoniuk, Daryna. "Russian Military Hackers Pose as Recruiters to Target Ukrainian IT Workers." <em>The Record from Recorded Future News</em>, 10 Aug. 2026, <a href="https://therecord.media/russian-military-hackers-pose-as-recruiters-ukraine-it-workers">therecord.media/russian-military-hackers-pose-as-recruiters-ukraine-it-workers</a>.</li>
<li id="ref3">Microsoft Threat Intelligence. "CaptiveCrunch: Midnight Blizzard Targets Travelers Worldwide for Malware Delivery and Credential Theft." <em>Microsoft Security Blog</em>, 31 Jul. 2026, <a href="https://www.microsoft.com/en-us/security/blog/2026/07/31/captivecrunch-midnight-blizzard-targets-travelers-worldwide-for-malware-delivery-and-credential-theft/">microsoft.com/en-us/security/blog/2026/07/31/captivecrunch-midnight-blizzard-targets-travelers-worldwide-for-malware-delivery-and-credential-theft</a>.</li>
<li id="ref4">ReliaQuest Threat Research. "DNS Poisoning Tactics Expand to Hospitality Wi-Fi." 23 Jul. 2026, <a href="https://reliaquest.com/blog/threat-spotlight-dns-poisoning-tactics-expand-to-hospitality/">reliaquest.com/blog/threat-spotlight-dns-poisoning-tactics-expand-to-hospitality</a>.</li>
</ol>
