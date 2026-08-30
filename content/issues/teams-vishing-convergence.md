---
title: "Teams-Based Voice Phishing as Initial Access: Convergent Adoption Across Unrelated Threat Clusters, February–July 2026"
date: 2026-08-30
type: "issues"
issueNumber: 39
readingTime: "13 min"
kicker: "STAC4749 · MUDDYWATER"
dateRange: "13 FEB – 28 JUL 2026"
window_start: 2026-02-13
window_end: 2026-07-28
version: 1
serial: "TI-20260830-001"
reportSerial: "TI-20260830-001"
classification_version: "3.8"
article_spec_version: "2.5"
excerpt: "Open-source intelligence summary: two unrelated intrusion sets, one financially motivated and one contested as Iran-nexus, converged independently on the same initial access behavior between February and July 2026."
standfirst: "Open-source intelligence summary: two unrelated intrusion sets, one financially motivated and one contested as Iran-nexus, converged independently on the same initial access behavior between February and July 2026."
author: "not important"
sourceBasis: "Vendor incident response and managed detection reporting, plus corroborating trade press published between 6 May and 30 August 2026. See References for full citations."
disclaimer: "This report synthesizes open-source threat intelligence to support threat-hunting operations and risk assessment. All material is publicly available. Information sourced, dated, and classified for transparency and verification."
huntPriorities:
  - "External Teams chat or call from a newly created tenant, followed within minutes by launch of Quick Assist, RemSupp, AnyDesk, or DWAgent"
  - "Registry Run key creation under HKCU disguised as an audio driver component, immediately after a remote-support session"
  - "PowerShell Invoke-WebRequest to a freshly registered domain with a --token-raw argument pattern"
glance:
  - label: "Window"
    value: "13 Feb – 28 Jul 2026"
  - label: "Clusters"
    value: "2, unattributed to each other"
  - label: "Sectors"
    value: "Services, mfg, energy, legal"
  - label: "Hunt surface"
    value: "3 behaviors"
glanceNote: "Nine sources, two of them vendor incident response with named methodology and one carrying a published indicator repository. The rest relay those two."
---

## Executive Summary

Between February and July 2026, two intrusion sets that nobody has connected to each other converged on the identical opening move: an external Microsoft Teams account, dressed up as internal IT support, calling an employee and talking them into a remote-support session.

<div class="claim"><span class="tag">VND-1</span><p>Sophos, tracking the larger and better-documented set as STAC4749, describes a financially motivated operation that worked dozens of North American organizations between February and June, with three confirmed intrusions ending in Chaos ransomware and one of those going from first contact to encrypted disks in under seventeen hours.<sup class="cite"><a href="#ref-sophos">1</a></sup></p></div>

<div class="claim"><span class="tag">VND-2</span><p>Rapid7 separately investigated an intrusion in early 2026 that also used Chaos branding and Teams-based social engineering, but assessed with moderate confidence that the operator behind it was MuddyWater, the Iranian Ministry of Intelligence and Security-linked group also tracked as Mango Sandstorm and Seedworm, running the ransomware branding as cover for an espionage operation that never actually encrypted anything.<sup class="cite"><a href="#ref-rapid7">2</a></sup></p></div>

Sophos looked directly for a link between the two and did not find one.

<div class="claim"><span class="tag">VND-1</span><p>The hands-on-keyboard artifacts in STAC4749 intrusions, including a command typed with a Russian keyboard layout, point away from an Iranian state operator and toward something else entirely, and Sophos states plainly that attribution remains unresolved.<sup class="cite"><a href="#ref-sophos">3</a></sup></p></div>

That is the finding worth sitting with. Two operators, almost certainly unrelated, arrived at the same initial access technique inside the same few months, aimed it through the same collaboration platform, and in at least one case wrapped it in the same ransomware brand to blur what kind of operation a defender was even looking at. A third and fourth data point in the same direction showed up before the window closed: a Unit 42 campaign pairing a phishing email with a Teams voice call to push a Node.js loader, and a DragonForce intrusion, tied by researchers to the Scattered Spider ecosystem, that tunneled its command and control traffic through Microsoft's own TURN relay infrastructure rather than reaching out to attacker domains directly.<sup class="cite"><a href="#ref-bc-etherrat">4</a></sup><sup class="cite"><a href="#ref-bc-dragonforce">5</a></sup>

None of this runs through a phishing email a filter can catch or a spelling error a trained employee can spot. The lure is a phone call. The payload delivery is a legitimate remote-support tool the employee installs willingly, at the caller's direction. A hunter reading this issue gets three behaviors that hold regardless of which operator is on the other end of the call, and that is the point: attribution is the part still in dispute, and it is also the part a defense program does not need settled before it acts.

## Scope and Sourcing

The reporting window runs 13 February through 28 July 2026, covering the earliest dated STAC4749 activity Sophos observed through the publication of its full writeup. The MuddyWater-attributed Chaos incident that Rapid7 investigated falls earlier in the window and was reported on 6 May, five days before the Rapid7 disclosure became the basis for wider trade coverage. Two further items, the Unit 42 EtherRAT campaign and the DragonForce Teams-relay abuse, fall inside the window on their own publication dates and are treated here as corroborating evidence of a broader pattern rather than as fully profiled clusters in their own right; neither receives its own actor section.

No source cited below sits behind a paywall. The pool tilts toward one vendor: Sophos's own MDR and SophosLabs teams supply the only source in this issue with a published indicator repository, and Rapid7's report is the sole basis for the MuddyWater attribution, which no other outlet in this pool independently re-derived rather than relayed. That is a single-vendor attribution and it is treated as one below. No claim in this issue is marked disputed in the formal sense; the open question is whether STAC4749 and the MuddyWater-attributed intrusion share an operator, and both sources on that question agree they do not, which is itself the finding. Every URL below is marked unarchived.

## Threat Highlights

### STAC4749 and the Chaos Ransomware Trail

<div class="dossier"><b>STAC4749</b> (SOPHOS) &middot; NOT PUBLICLY LINKED TO A NAMED APT &nbsp;|&nbsp; T1656 &middot; T1219 &middot; T1547.001 &middot; T1036 &nbsp;|&nbsp; ATTRIBUTION: FINANCIALLY MOTIVATED, ORIGIN UNRESOLVED, RUSSIAN-LANGUAGE ARTIFACT NOTED</div>

<div class="claim"><span class="tag">VND-1<span class="corr">&times;3 corroborated</span></span>
<p>Sophos analysts tracked STAC4749 operators contacting employees at dozens of North American organizations through Teams chats and calls, posing as helpdesk or IT support staff under names like AnthonyBrooks and DylanHarper, tied to freshly registered domains on the <code>.top</code> top-level domain rather than the spoofed Microsoft tenant names earlier vishing campaigns favored.<sup class="cite"><a href="#ref-sophos">6</a></sup></p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>Calls ran anywhere from ninety seconds to twenty minutes, most closing in around two and a half, and nearly all of them pushed the target toward starting Microsoft Quick Assist. Sophos observed a shift starting in April toward a cloud-based remote monitoring and management tool called RemSupp, likely because it survives application blocklists more often than Quick Assist does. Every intrusion in the set also included an attempt to enable RDP on the first compromised host through <code>msconfig</code>, which is how the operators moved past that one machine.<sup class="cite"><a href="#ref-sophos">7</a></sup></p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>Once inside the remote session, operators launched PowerShell to pull a loader staged in the user's own AppData folder. The loader's filename changed on a schedule, from a string beginning <code>sekv</code> in mid-March to <code>helper</code> by late March and a four-character alphanumeric prefix by mid-April, each followed by a random ten-digit number. It talked to three hard-coded IP addresses over gRPC and refused to run unless it found a specific log file already present on the host, a check Sophos reads as a dependency on some other product rather than an anti-analysis trick.<sup class="cite"><a href="#ref-sophos">8</a></sup></p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>Persistence ran through an HKCU Run key disguised as a Realtek audio component, a naming convention that rotated in step with the payload filenames and picked up a WinAudio variant in May. Later-stage command and control used Golang implants launched with a <code>--token-raw</code> argument carrying two Base64 blobs, connecting to servers behind Cloudflare and, in several observed builds, validating the C2 server's TLS certificate against a hard-coded issuer name before completing the handshake, a form of certificate pinning that let the operators segment infrastructure by build without exposing the whole backend to any one compromised sample.<sup class="cite"><a href="#ref-sophos">9</a></sup></p></div>

<div class="claim"><span class="tag">VND-1<span class="corr">&times;2 corroborated</span></span>
<p>At least three intrusions ended in Chaos ransomware, deployed after the operators had already expanded across multiple hosts and, in one case, exfiltrated data first. One of those three went from the first Teams call to encrypted endpoints in under seventeen hours. In the run-up to encryption, operators layered in DWAgent or AnyDesk as a second remote access channel independent of whatever foothold Teams had given them, and in one intrusion added a custom reverse SOCKS proxy for good measure.<sup class="cite"><a href="#ref-sophos">10</a></sup><sup class="cite"><a href="#ref-bc-stac4749">11</a></sup></p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>Sophos assesses with high confidence that STAC4749 is financially motivated, whether operating the ransomware directly or coordinating with an affiliate, based on how tightly the time from access to encryption tracks prior Chaos incidents the firm has responded to. Targeting skewed heavily toward Canada and the United States, and while the sector spread was broad, every legal-sector victim in the set specialized in intellectual property work, a detail Sophos flags without further interpretation.<sup class="cite"><a href="#ref-sophos">12</a></sup></p></div>

<div class="hunt">
<div class="hunt-label">How this would be hunted</div>
<p>The chain has a fixed shape from first contact to persistence, and every step of it is visible to an EDR agent that is already watching process lineage. Alert on <code>quickassist.exe</code>, <code>remsupp.exe</code>, <code>anydesk.exe</code>, or <code>dwagent.exe</code> appearing as the parent of <code>powershell.exe</code> or <code>pwsh.exe</code>, particularly where that PowerShell process issues an outbound <code>Invoke-WebRequest</code> within the same session. Layer in the persistence signature separately: a new HKCU Run key whose value string names an audio driver component but whose target path sits in AppData rather than System32 will catch this family and most of its imitators, since the naming convention is disguise, not obfuscation.</p>
<p>Because Teams is the delivery channel rather than email, the earliest visible signal sits outside conventional endpoint telemetry entirely. Any tenant-level logging available for Microsoft Teams external access, specifically new chat requests or calls originating from tenants created in the days or weeks before contact, is worth alerting on directly, since a legitimate helpdesk vendor relationship does not usually begin with a cold call.</p>
<div class="hunt-foot"><b>Stage</b> Initial access and persistence &middot; <b>Look in</b> process-create, registry-set, dns, proxy-http, Teams external-access audit logs &middot; <b>Built on</b> one corroborated vendor incident response account with published indicators</div>
<div class="hunt-sources">Indicators for your SIEM live in the sources, not here. Sophos and SophosLabs publish the full STAC4749 indicator set, including C2 IP addresses, domains, registry key values, and file hashes, in a dated GitHub repository. Point your own model at that repository and at the Sophos writeup itself to extract indicators and populate your SIEM in your own schema.</div>
</div>

### MuddyWater's Chaos-Branded False Flag

<div class="dossier"><b>MUDDYWATER</b> &middot; MANGO SANDSTORM &middot; SEEDWORM &middot; STATIC KITTEN &middot; COBALT ULSTER &nbsp;|&nbsp; T1656 &middot; T1219 &middot; T1556 &nbsp;|&nbsp; ATTRIBUTION MODERATE CONFIDENCE, RAPID7 ONLY, NOT INDEPENDENTLY RE-DERIVED</div>

<div class="claim"><span class="tag">VND-2</span>
<p>Rapid7 investigated an intrusion in early 2026 that carried every surface marking of an opportunistic Chaos ransomware attack, extortion notes and all, but never actually encrypted a file. The operators reached employees through Teams chat requests, moved to interactive screen-sharing sessions, and used that direct access to walk victims through entering credentials and approving multi-factor authentication changes, in one case persuading a user to type a password into a locally created text file rather than a password manager or login prompt.<sup class="cite"><a href="#ref-rapid7">13</a></sup></p></div>

<div class="claim"><span class="tag">VND-2</span>
<p>Post-access tooling included a custom downloader and a remote access trojan, with persistence and remote control layered through DWAgent and AnyDesk, the same second-stage tools Sophos separately observed in the unrelated STAC4749 set. Rapid7 ties the intrusion to MuddyWater at moderate confidence on the strength of a reused code-signing certificate and command-and-control infrastructure overlapping the group's known footprint, alongside a "high-touch" operating style, direct, sustained, hands-on-keyboard engagement with the victim, that the firm reads as more consistent with an intelligence service's tradecraft than a ransomware affiliate's.<sup class="cite"><a href="#ref-rapid7">14</a></sup></p></div>

<div class="claim"><span class="tag">MED-4</span>
<p>Rapid7 frames the Chaos branding itself as the operational choice: MuddyWater has increasingly leaned on an "IT support" persona through 2026, and dressing an espionage intrusion as a criminal ransomware incident, threats and a leak-site countdown included, buys the operators a plausible cover story and a slower, less scrutinized incident response from the victim than a suspected nation-state breach would draw.<sup class="cite"><a href="#ref-thn-muddywater">15</a></sup></p></div>

{{< operational-context topic="Why a false flag changes the hunt, not the detection" >}}
A ransomware brand painted over an espionage operation does not change what the intrusion looks like on the wire. It changes what a defender assumes about intent, and intent drives triage priority, not detection logic. A SOC that reads "Chaos ransomware" and routes the case to the ransomware playbook may miss that the attacker's actual objective was data theft that had already happened by the time any encryption threat arrived, if one arrived at all.

**Key points:**
- The Teams vishing and screen-share chain described here is identical whether the eventual objective is extortion or espionage
- Ransom notes and leak-site threats are not evidence against a state-linked motive; MuddyWater's own operation used them as cover
- Data staging and exfiltration timing, not the presence or absence of encryption, is what separates the two outcomes, and both deserve the same initial detection response
{{< /operational-context >}}

<div class="hunt">
<div class="hunt-label">How this would be hunted</div>
<p>This cluster carries fewer published technical artifacts than STAC4749, and the confidence on the attribution itself is moderate from a single source, so the hunting guidance here rests more on behavior than on named indicators. Screen-sharing session initiation immediately followed by MFA re-registration or a new MFA method enrollment on the same account, within the same short window, is the highest-signal sequence Rapid7's reporting supports, and it is rare enough in legitimate helpdesk workflows to be worth alerting on directly rather than tuning down as noise.</p>
<p>Watch identity provider logs for MFA method changes originating from a session that also shows a Teams external contact in the hour prior. Where DWAgent or AnyDesk installation follows a Teams call rather than a known internal deployment process, treat it as the same behavior class as the STAC4749 chain above regardless of whether the two clusters share an operator, because the defensive response to unauthorized remote-tool installation does not depend on getting attribution right first.</p>
<div class="hunt-foot"><b>Stage</b> Initial access and credential access &middot; <b>Look in</b> identity-provider MFA event logs, Teams external-access audit logs, process-create for remote-access tool installers &middot; <b>Built on</b> one moderate-confidence vendor attribution, not independently corroborated</div>
<div class="hunt-sources">Indicators for your SIEM live in the sources, not here. Rapid7's own writeup names the reused code-signing certificate and associated command-and-control infrastructure behind its attribution. Point your own model at that report to extract what it publishes and populate your SIEM in your own schema.</div>
</div>

{{< continuity >}}
CLU-STAC4749 first profiled this issue. No prior-issue baseline exists.

CLU-MUDDYWATER last profiled TI-20260817-001 (PRC-nexus trusted-channel issue did not cover this cluster; no DPRK or Iran issue since 11 August carried MuddyWater specifically). Treat as a new thread for this cluster rather than a continuation.
{{< /continuity >}}

## Emerging Tradecraft

{{< sectiontag "Our assessment · moderate confidence" >}}

Two more data points, neither profiled above as its own cluster, point at the same underlying shift.

<div class="claim"><span class="tag">MED-4</span><p>In July, Unit 42 documented a campaign combining a conventional phishing email, an "Employee Survey" lure with a malicious PDF, and a follow-up Teams voice call impersonating IT support, to deliver a Node.js-based loader tracked as EtherRAT. The email in that chain is not the payload delivery mechanism; it is the appointment-setting step for the call that actually gets the victim to install something.<sup class="cite"><a href="#ref-bc-etherrat">16</a></sup></p></div>

<div class="claim"><span class="tag">MED-4</span><p>In June, researchers at Symantec tied a DragonForce ransomware intrusion, part of an operation researchers associate with the Scattered Spider ecosystem, to custom Go-based malware that tunneled its command-and-control traffic through Microsoft Teams' own TURN relay infrastructure, using an anonymously obtained Teams visitor token to blend outbound C2 traffic with legitimate Teams call setup rather than reaching out to attacker-registered infrastructure directly.<sup class="cite"><a href="#ref-bc-dragonforce">17</a></sup></p></div>

Read together with STAC4749 and the MuddyWater-attributed intrusion, that is four distinct operator sets, financially motivated, state-linked, and at least two more without a settled attribution at all, independently treating a collaboration platform as both the social engineering channel and, in DragonForce's case, the transport layer itself. None of the four needed a single AI-written phishing email to get in. The behavioral throughline is not a text artifact a filter can score. It is a live human interaction over voice or chat, followed by the victim's own hands installing a tool the attacker asked for by name.

## Assessment and Outlook

{{< sectiontag "Our assessment · moderate confidence" >}}

Whether STAC4749 and the MuddyWater-attributed intrusion ever get resolved into a shared operator or stay two coincidentally similar campaigns matters less to a defender than it might seem to. Sophos looked for the link directly and did not find one, and a Russian-language keystroke error is a real if imperfect signal pointing away from Tehran. The more useful reading is that Teams vishing has become common enough tradecraft, documented publicly since Microsoft's own mid-2024 disclosure and reinforced by a steady climb in Sophos's own MDR case volume through early 2026, that state and criminal operators are converging on it independently, the way multiple unrelated actors converge on any technique once its cost and success rate both look good.

The near-term outlook is that this keeps growing rather than plateauing. Sophos's own MDR data shows case volume rising in three separate jumps between January 2025 and May 2026, which reads as adoption still accelerating rather than a technique reaching saturation. A defender's realistic posture is to stop asking whether a given Teams contact is a known APT or a known ransomware affiliate before responding to it, and to instead treat any unsolicited external contact requesting a remote-support session as hostile by default, regardless of which persona or brand is attached to it, since the group behind the call is the one part of this pattern that has consistently turned out to be the wrong question to ask first.

## Source Summaries

<div class="src">
<h4>Chaos in Teams vishing</h4>
<div class="byline">Sophos (Morgan Demboski, Sophos MDR and SophosLabs) &middot; 28 July 2026 &middot; vendor managed detection and response</div>
<a class="url" href="https://www.sophos.com/en-us/blog/chaos-in-teams-vishing">sophos.com/en-us/blog/chaos-in-teams-vishing</a>
<p>The primary technical account of STAC4749. Documents the Teams vishing personas and domains, the loader and backdoor evolution, registry persistence naming, certificate-pinned C2, victimology, and links to a published indicator repository.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Muddying the Tracks: The State-Sponsored Shadow Behind Chaos Ransomware</h4>
<div class="byline">Rapid7 &middot; 6 May 2026 &middot; vendor incident response</div>
<a class="url" href="https://www.rapid7.com/blog/post/tr-muddying-tracks-state-sponsored-shadow-behind-chaos-ransomware/">rapid7.com/blog/post/tr-muddying-tracks-state-sponsored-shadow-behind-chaos-ransomware</a>
<p>Rapid7's own investigation of the Chaos-branded intrusion it attributes to MuddyWater at moderate confidence, citing a reused code-signing certificate and infrastructure overlap. Describes the Teams screen-sharing phase, MFA manipulation, and the case for false-flag ransomware branding.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Microsoft Teams vishing attacks lead to Chaos ransomware attacks</h4>
<div class="byline">BleepingComputer &middot; 30 July 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://www.bleepingcomputer.com/news/security/microsoft-teams-vishing-attacks-lead-to-chaos-ransomware-attacks/">bleepingcomputer.com/news/security/microsoft-teams-vishing-attacks-lead-to-chaos-ransomware-attacks</a>
<p>Relays the Sophos STAC4749 writeup, adding a note that Sophos found no link between this set and the MuddyWater-attributed Chaos incident reported in May.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>MuddyWater Uses Microsoft Teams to Steal Credentials in False Flag Ransomware Attack</h4>
<div class="byline">The Hacker News &middot; 6 May 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://thehackernews.com/2026/05/muddywater-uses-microsoft-teams-to.html">thehackernews.com/2026/05/muddywater-uses-microsoft-teams-to.html</a>
<p>Relays the Rapid7 report in full, including the direct quote characterizing the intrusion's social engineering phase, and adds background on Chaos's ransomware-as-a-service history and extortion model.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Fake IT support calls on Microsoft Teams push EtherRAT malware</h4>
<div class="byline">BleepingComputer, citing Palo Alto Networks Unit 42 (Brian Janower) &middot; 14 July 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://www.bleepingcomputer.com/news/security/fake-it-support-calls-on-microsoft-teams-push-etherrat-malware/">bleepingcomputer.com/news/security/fake-it-support-calls-on-microsoft-teams-push-etherrat-malware</a>
<p>Describes a campaign pairing a phishing email lure with a follow-up Teams voice call impersonating IT support, delivering a Node.js-based loader. Cited here as corroborating evidence of the broader pattern rather than as a profiled cluster.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Ransomware gang abuses Microsoft Teams relays to hide malicious traffic</h4>
<div class="byline">BleepingComputer, citing Symantec &middot; 16 June 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://www.bleepingcomputer.com/news/security/ransomware-gang-abuses-microsoft-teams-relays-to-hide-malicious-traffic/">bleepingcomputer.com/news/security/ransomware-gang-abuses-microsoft-teams-relays-to-hide-malicious-traffic</a>
<p>Reports Symantec's finding that a DragonForce intrusion, linked to the Scattered Spider ecosystem, tunneled command-and-control traffic through Microsoft Teams' own TURN relay infrastructure using a custom Go-based backdoor.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Threat actors misusing Quick Assist in social engineering attacks leading to ransomware</h4>
<div class="byline">Microsoft Threat Intelligence &middot; 15 May 2024 &middot; vendor original disclosure, background</div>
<a class="url" href="https://www.microsoft.com/en-us/security/blog/2024/05/15/threat-actors-misusing-quick-assist-in-social-engineering-attacks-leading-to-ransomware/">microsoft.com/en-us/security/blog/2024/05/15/threat-actors-misusing-quick-assist-in-social-engineering-attacks-leading-to-ransomware</a>
<p>Out-of-window background, cited by Sophos as the first public documentation of IT-themed vishing abusing Quick Assist. Included here to establish that this is a two-year-old technique still gaining adopters rather than a new discovery.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Iranian APT Intrusion Masquerades as Chaos Ransomware Attack</h4>
<div class="byline">SecurityWeek &middot; 7 May 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://www.securityweek.com/iranian-apt-intrusion-masquerades-as-chaos-ransomware-attack/">securityweek.com/iranian-apt-intrusion-masquerades-as-chaos-ransomware-attack</a>
<p>Relays the Rapid7 findings with additional framing on why an espionage operation dressed as ransomware complicates a defender's initial triage.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

## References

<ol class="refs">
<li id="ref-bc-dragonforce">BleepingComputer, citing Symantec. "Ransomware gang abuses Microsoft Teams relays to hide malicious traffic." 16 June 2026. <a href="https://www.bleepingcomputer.com/news/security/ransomware-gang-abuses-microsoft-teams-relays-to-hide-malicious-traffic/">bleepingcomputer.com/news/security/ransomware-gang-abuses-microsoft-teams-relays-to-hide-malicious-traffic/</a> <span class="access-note">unarchived</span></li>
<li id="ref-bc-etherrat">BleepingComputer, citing Palo Alto Networks Unit 42. "Fake IT support calls on Microsoft Teams push EtherRAT malware." 14 July 2026. <a href="https://www.bleepingcomputer.com/news/security/fake-it-support-calls-on-microsoft-teams-push-etherrat-malware/">bleepingcomputer.com/news/security/fake-it-support-calls-on-microsoft-teams-push-etherrat-malware/</a> <span class="access-note">unarchived</span></li>
<li id="ref-bc-stac4749">BleepingComputer. "Microsoft Teams vishing attacks lead to Chaos ransomware attacks." 30 July 2026. <a href="https://www.bleepingcomputer.com/news/security/microsoft-teams-vishing-attacks-lead-to-chaos-ransomware-attacks/">bleepingcomputer.com/news/security/microsoft-teams-vishing-attacks-lead-to-chaos-ransomware-attacks/</a> <span class="access-note">unarchived</span></li>
<li id="ref-microsoft">Microsoft Threat Intelligence. "Threat actors misusing Quick Assist in social engineering attacks leading to ransomware." 15 May 2024. <a href="https://www.microsoft.com/en-us/security/blog/2024/05/15/threat-actors-misusing-quick-assist-in-social-engineering-attacks-leading-to-ransomware/">microsoft.com/en-us/security/blog/2024/05/15/threat-actors-misusing-quick-assist-in-social-engineering-attacks-leading-to-ransomware/</a> <span class="access-note">unarchived, background, out of window</span></li>
<li id="ref-rapid7">Rapid7. "Muddying the Tracks: The State-Sponsored Shadow Behind Chaos Ransomware." 6 May 2026. <a href="https://www.rapid7.com/blog/post/tr-muddying-tracks-state-sponsored-shadow-behind-chaos-ransomware/">rapid7.com/blog/post/tr-muddying-tracks-state-sponsored-shadow-behind-chaos-ransomware/</a> <span class="access-note">unarchived</span></li>
<li id="ref-securityweek">SecurityWeek. "Iranian APT Intrusion Masquerades as Chaos Ransomware Attack." 7 May 2026. <a href="https://www.securityweek.com/iranian-apt-intrusion-masquerades-as-chaos-ransomware-attack/">securityweek.com/iranian-apt-intrusion-masquerades-as-chaos-ransomware-attack/</a> <span class="access-note">unarchived</span></li>
<li id="ref-sophos">Sophos, Demboski, M. "Chaos in Teams vishing." 28 July 2026. <a href="https://www.sophos.com/en-us/blog/chaos-in-teams-vishing">sophos.com/en-us/blog/chaos-in-teams-vishing</a> <span class="access-note">unarchived, carries linked indicator repository</span></li>
<li id="ref-thn-muddywater">The Hacker News. "MuddyWater Uses Microsoft Teams to Steal Credentials in False Flag Ransomware Attack." 6 May 2026. <a href="https://thehackernews.com/2026/05/muddywater-uses-microsoft-teams-to.html">thehackernews.com/2026/05/muddywater-uses-microsoft-teams-to.html</a> <span class="access-note">unarchived</span></li>
</ol>

This piece was authored directly against Article and Site Design Specification v2.5 and Classification System v3.8 without the automated grading pipeline, filed as a numbered issue rather than an industry-watch item because both profiled clusters are established intrusion sets rather than a survey of unrelated disclosures. It carries no ledger file, and every pipeline-derived field on the article element (clusters, claim counts, sectors, actionable-for) reflects the author's own reading rather than a reconciled ledger entry. Grades above are a first pass against the mechanical tests in classification spec section 4, not a substitute for pipeline grading.

Title departs from Article Spec §5's "Evocative Hook: Concrete Specific" format in favor of a standard intelligence-report title, subject followed by judgment and date range. This is a deliberate deviation pending a spec revision, not an oversight; §5 still describes the old format until the build guide is updated to match.
