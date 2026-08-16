---
title: "Iran Cyber Threat Highlights - Multi-Vector Operational Escalation"
date: 2026-08-11T12:00:00
type: "issues"
issueNumber: 35
readingTime: "10 min"
excerpt: "Open-source intelligence summary on Iranian state-sponsored cyber operations across critical infrastructure, espionage, and destructive malware, 12 July – 11 August 2026."
dek: "Open-Source Intelligence Summary: 12 July - 11 August 2026. Threat Operations Assessment."
primaryThreat: "Iran"
dateRange: "12 JUL – 11 AUG 2026"
version: 1
reportSerial: "TI-20260811-002"
author: "not important"
sourceBasis: "Open-source reporting from threat intelligence firms, vendor disclosures, government advisories, and security research. See References for full citations."
classificationLegend: true
huntPriorities:
  - "Presence-stage: MuddyWater initial-access hardening (macros, MFA, password spray)"
  - "Engagement–Presence: CyberAv3ngers PLC exploitation (Rockwell/Siemens/Schneider)"
  - "Effect-stage: APT33 wiper deployment (Tickler, SHAPESHIFT)"
disclaimer: "This report synthesizes open-source threat intelligence to support threat-hunting operations and risk assessment. All material is publicly available. Information sourced, dated, and classified for transparency and verification."
slug: "iran-cyber-threat-highlights"
stats:
  - label: "Reporting window"
    value: "30 days"
  - label: "Primary threat"
    value: "Iran"
---

## Executive Summary

{{< tag "AM" >}} Open-source reporting over the past thirty days shows sustained Iranian state-sponsored cyber operations across three distinct vectors: operational technology targeting against U.S. critical infrastructure water systems, espionage and credential harvesting campaigns against global government and defense sectors, and emerging AI-assisted malware development and deployment. Four developments establish immediate defensive priorities.

{{< tag "IX" >}} Iranian-affiliated actors conducted a coordinated attack on more than thirty Minnesota municipal water systems on 26 July, four days following a CISA advisory update warning of expanded programmable logic controller exploitation across Rockwell, Siemens, and Schneider Electric platforms. The same activity is attributed to CyberAv3ngers, an IRGC-CEC affiliated group, representing a direct escalation in both scale and capability from previous water utility compromises.

{{< tag "SP" >}} MuddyWater, the primary Iranian state-sponsored espionage actor, deployed a previously undocumented Rust-based malware framework, RustyWater, targeting Israeli government and infrastructure while simultaneously maintaining active intrusions against U.S. financial, aviation, and defense-sector networks first established in February 2026, suggesting pre-positioned access for rapid disruption if geopolitical escalation occurs.

{{< tag "IX" >}} Charming Kitten continued its characteristic credential-harvesting campaigns with renewed intensity, targeting government, diplomatic, and international conference participants across Europe and the Middle East using sophisticated phishing-as-a-service infrastructure. Malware families previously associated with destructive campaigns, including wipers and disruptive code, are being redeployed operationally in coordination with infrastructure access established by espionage actors, indicating a deliberate convergence of intelligence collection and disruptive capability.

## Scope and Sourcing

{{< tag "AM" >}} This report synthesizes open-source reporting published between approximately 12 July and 11 August 2026, drawn from U.S. government agencies (FBI, CISA, NSA, EPA, Department of Energy), private threat intelligence firms (Mandiant, Proofpoint, CrowdStrike, Microsoft, Group-IB, Halcyon, Trellix), international cybersecurity researchers, and specialist threat tracking outlets (SecurityWeek, TechCrimes, Dark Reading, The Record). None of it is derived from classified or government-restricted sources; treat it as an indicator of trend and public attribution claims, not a validated intelligence assessment. Some items reference intrusions that began well before this window, including February 2026 pre-positioning activity, but were disclosed, attributed, or significantly escalated during the past thirty days. Those are flagged in the timeline below. Sourcing emphasizes primary vendor threat reporting and direct government advisories over secondary press coverage; where secondary sources provided the only pathway to a technical detail or campaign attribution, that limitation is noted.

## Incident Timeline (Last 30 Days)

| Date (2026) | Actor / Campaign | Summary | Source Confidence |
| --- | --- | --- | --- |
| Jul 22 | CyberAv3ngers (IRGC-CEC) | {{< tag "IX" >}} CISA advisory AA26-097A updated to confirm expanded PLC targeting scope: Siemens S7-1200, Schneider Electric BMX P34 / Modicon M340 confirmed alongside continued Rockwell Automation targeting. Advisory details malicious project file injection disabling safety shutdown and alarm logic. | High |
| Jul 26-27 | CyberAv3ngers (IRGC-CEC) | {{< tag "IX" >}} Coordinated attack on 30+ Minnesota municipal water and wastewater systems; confirmation of automation control functions disrupted; geographically dispersed vector consistent with expanded vendor targeting documented four days prior in CISA update. | Moderate-High |
| Jul 30 | Iran (CyberAv3ngers) | {{< tag "AM" >}} Washington Post reports U.S. intelligence assessment that Iran is likely behind Minnesota water system attacks; assessment tied to broader context of Iranian cyber operations and geopolitical tensions. | Moderate |
| Aug 10 | APT33 (IRGC) | {{< tag "SP" >}} Trellix reports APT33 deployment of Tickler and SHAPESHIFT destructive wiper malware against U.S. aerospace and petrochemical targets in active disruptive campaign. | High |

## Threat Actor Highlights

### CyberAv3ngers: Critical Infrastructure Targeting Escalation

{{< tag "IX" >}} CyberAv3ngers, operating under direct IRGC Cyber Electronic Command authority, demonstrated a substantial capability expansion in July 2026 when CISA and seven co-authoring U.S. federal agencies updated their April 2026 advisory to document active exploitation of internet-exposed programmable logic controllers across multiple major vendors. The group initially surfaced in open reporting in November 2023 targeting Unitronics PLC devices across U.S. water and wastewater facilities using default or weak credentials, a campaign that compromised at least seventy-five devices and generated widespread but ultimately limited disruption. The July 22 advisory update confirmed the group had pivoted to Rockwell Automation CompactLogix and Micro850 controllers and had expanded confirmed targeting to include Siemens S7-1200 and Schneider Electric BMX P34 / Modicon M340 platforms.

{{< tag "SP" >}} Most significantly, the advisory documented a deliberate escalation in tradecraft. Rather than simply accessing PLCs via weak authentication, the group now downloads malicious project files using engineering configuration software and injects logic that overrides specific instruction sets responsible for maintaining safe operating parameters. At one U.S. victim site, the FBI observed the injected logic retain ladder logic for downstream function while deliberately disabling shutdown procedures and alarm logic, a technique that transforms low-threat reconnaissance into an immediate containment problem if the attacker chooses to trigger it. The timing of the update and the Minnesota attack just four days later is not incidental; Dragos assessed that attack techniques have proliferated to an estimated sixty or more affiliated pro-Iranian hacktivist groups, meaning the threat persists regardless of what happens to the core CyberAv3ngers organization.

{{< hunt-priority label="Engagement to Presence-stage indicator" collection="Network-perimeter PLC scanning logs, outbound proxy logs to known Iranian infrastructure, PLC configuration and firmware audit logs" >}}
Organizations operating internet-exposed PLCs should treat this as an urgent, active threat. Detection strategy should focus on two layers: network perimeter scanning for any inbound connection attempts to ports known to serve Rockwell Automation, Siemens, or Schneider Electric PLCs (typically 44818 for Rockwell, 502 for Modbus, 21/25 for file transfer), and configuration audit for any unexpected changes to ladder logic or project files, particularly injection of logic that disables shutdown or alarm functions. The advisory provides specific IOCs; immediate prioritization should be network isolation of any PLC directly internet-connected and implementation of a jump host architecture for any legitimate remote engineering access.
{{< /hunt-priority >}}

### MuddyWater: Espionage and Pre-Positioned Access Convergence

{{< tag "SP" >}} MuddyWater, the primary Iranian Ministry of Intelligence and Security cyber arm and one of the world's most consistently active espionage actors, demonstrated a dual-track approach through July and August 2026 that suggests deliberate operational planning for rapid escalation if geopolitical circumstances warrant. The group maintained active intrusions established in February 2026 against U.S. financial, aviation, and defense-sector software company networks, documented in March public reporting as the Dindoor campaign leveraging a previously undocumented Deno JavaScript runtime backdoor and the Python-based Fakeset implant. The timing of that February pre-positioning, just weeks before the February 28 U.S.-Israeli strikes on Iranian military infrastructure, was flagged by analysts as indicative of pre-positioning rather than reactive response. In July, the group deployed RustyWater, a Rust-based remote access trojan targeting Israeli government infrastructure and diplomacy, documented by multiple independent researchers including Rescana, CrowdStrike, and Broadcom Symantec. The Rust implementation provides both stealth advantages through implementation novelty (Rust-based malware is not yet commonly seen and detection signatures lag behind C++ or C# counterparts) and evasion advantages through memory-safety guarantees that reduce certain classes of exploitation-based detection.

{{< hunt-priority label="Presence-stage indicator" collection="EDR/XDR logs for Office macro execution and PowerShell execution, cloud identity logs for anomalous sign-in patterns, proxy/firewall logs for command-and-control traffic" >}}
MuddyWater remains the Iranian threat actor with the most direct operational interest in U.S. enterprises. Defend against initial access through: mandatory disabling of Office macro execution across all enterprise systems unless explicitly whitelisted per application, enterprise-wide enforcement of multi-factor authentication on all cloud identities (Microsoft 365, Azure, AWS, Google Cloud), password-spray detection on Microsoft 365 and Azure AD targeting high-value accounts (executives, security personnel, system administrators), and behavioral detection for common MuddyWater tradecraft including use of legitimate tools (WMIC, tasklist, net.exe) for reconnaissance and credential access post-compromise. The group's reliance on spear-phishing and living-off-the-land techniques means signature-based detection is ineffective; behavioral baselines and anomaly detection are the primary detection levers.
{{< /hunt-priority >}}

### Charming Kitten: Credential Harvesting at Scale

{{< tag "IX" >}} Charming Kitten, the Iranian Islamic Revolutionary Guard Corps cyber espionage unit affiliated with the IRGC Intelligence Organization, has operated continuously since at least 2011 and maintains a reputation as one of Iran's most persistent, adaptive, and visible state-backed cyber actors. The group renewed credential-harvesting campaigns through July and August 2026 targeting government, military, academic, media, diplomatic, and international conference participants across the United States, Middle East, and Europe. Multiple threat researchers including Check Point, SilentPush, and Google Threat Analysis Group documented phishing infrastructure hosting credential-harvesting pages designed to impersonate legitimate government portals, email services, and conference event portals. The group's characteristic approach combines spear-phishing emails impersonating journalists, academics, or credible organizations with elaborately crafted fake websites mimicking legitimate services and Telegram-based operator notification channels that alert attackers in real-time when a victim visits a phishing page.

{{< hunt-priority label="Engagement-stage indicator" collection="Email security logs for inbound phishing emails from spoofed domains, web-proxy logs for access to known credential-harvesting domains, user training and reporting metrics" >}}
Charming Kitten's campaigns are highly dependent on human behavior and social engineering rather than technical exploitation. Primary defense is rapid phishing reporting and account lockout procedures for any user reporting credential compromise. Secondary defense is email authentication enforcement (DMARC, SPF, DKIM) on all government and defense-aligned domains, aggressive spoofing domain monitoring, and automated takedown procedures for phishing infrastructure. User training should emphasize that government, military, and diplomatic communications rarely occur through public email services and that legitimate government conference invitations can be verified through direct contact with the hosting organization rather than clicking email links.
{{< /hunt-priority >}}

### APT33: Destructive Capability Deployment

{{< tag "SP" >}} APT33, tracked by Microsoft as Peach Sandstorm and by CrowdStrike as Elfin, operates as the primary destructive arm of the IRGC and has been conducting cyber operations since at least 2013 with a consistent focus on U.S. and Saudi Arabian aerospace, defense, energy, and petrochemical sectors. The group has historically prioritized intellectual property theft supporting Iran's domestic aerospace and energy industries, but in early 2026 shifted operational emphasis toward disruptive and destructive malware deployment. Trellix reporting through August 2026 documents active deployment of Tickler and SHAPESHIFT wipers against U.S. aerospace and petrochemical targets in what the firm assessed as a deliberately damaging campaign coinciding with heightened Iran-U.S.-Israel tensions. The group also shifted its primary initial access method beginning in 2023 from targeted spear-phishing campaigns to large-scale password-spray attacks against Microsoft 365 and Azure Active Directory environments, moving from low-volume, high-precision targeting to high-volume, broad-based credential attacks.

{{< hunt-priority label="Effect-stage indicator" collection="Email authentication logs for password-spray attacks against cloud identities, SIEM/XDR logs for anomalous administrative account sign-ins, EDR logs for wiper malware execution signatures" >}}
APT33 represents an active threat to U.S. critical infrastructure. Password spray at scale requires defensive measures that go beyond endpoint detection: cloud identity sign-in anomaly detection tuned for geographically impossible logins, blocked-login alerting for repeated failed attempts against high-value accounts, and immediate notification to infrastructure security teams of any successful sign-in from foreign IP space. Wiper malware detection requires both signature-based detection for known variants (Tickler, SHAPESHIFT, DustMan, Shamoon) and behavioral detection for file-wiping patterns: rapid deletion or encryption of files across wide directory trees, particularly focusing on critical system and database directories.
{{< /hunt-priority >}}

## Operational Impact Assessment

{{< tag "IX" >}} The Minnesota water system attacks on 26-27 July represent the first confirmed successful operational technology disruption by Iranian-affiliated actors in the continental United States at scale. The incident is not incidental to the broader Iranian cyber posture; it is direct operational evidence of capability maturation, infrastructure pre-positioning, and willingness to target essential services. None of the open-source reporting reviewed for this assessment confirmed direct compromise of U.S. Department of Defense Information Network (DoDIN) systems during this window. However, the threat is not a future possibility but a present exposure through multiple indirect pathways. Iranian actors have demonstrated sustained interest in supply-chain compromise, targeting defense contractors and software vendors whose infrastructure interconnects with government and military networks. The convergence of espionage access established in February 2026 with operational capability demonstrated in July suggests Iranian doctrine treats cyber operations as a layered approach: maintain long-term intelligence collection access through undetected espionage, pre-position disruptive or destructive capability through the same channel, and execute disruption if geopolitical circumstances warrant.

## Emerging Tradecraft Patterns

{{< tag "SP" >}} MuddyWater's deployment of RustyWater, a Rust-based implant, signals a broader Iranian adoption of memory-safe languages for malware development. Rust malware is still uncommon in open-source reporting and detection signatures lag significantly behind C/C++ and C# variants. Organizations should anticipate expanded use of Rust, Go, and other memory-safe languages by sophisticated threat actors, which implies traditional string-signature and bytecode-signature detection will become progressively less effective. Behavioral and heuristic detection become the primary lever.

{{< tag "IX" >}} Multiple open-source sources document evidence of Iranian actors leveraging generative AI for social engineering content generation, document creation, and initial phishing lure development. This mirrors documented use by other state actors and criminal groups. The implication is straightforward: grammar-based and formatting-based phishing detection, which has historically been reliable, becomes unreliable. Organizations should not rely on user training built around "check for grammar errors" and should instead emphasize verification of sender identity through out-of-band communication channels and recognition of contextual inconsistencies in messaging.

{{< tag "SP" >}} CyberAv3ngers' evolution from default-credential exploitation to malicious project file injection represents a significant tradecraft maturation. The technique allows for persistent, stealthy manipulation of operational logic within critical infrastructure control systems. This pattern suggests Iranian operators have studied defensive measures implemented after previous campaigns and adapted their approach to evade both traditional access controls and perimeter-based detection.

## Assessment and Outlook

{{< tag "AM" >}} Open-source indicators over the past thirty days point to sustained, multi-vector Iranian cyber activity rather than a lull. Operational tempo has remained elevated through August following the February 28 U.S.-Israeli strikes on Iranian military targets, contradicting historical patterns of Iranian cyber retaliation as transient and reactive. The convergence of long-dwell espionage access established in February with demonstrated operational technology disruption capability in July suggests strategic planning beyond immediate response. Geopolitical context matters: U.S.-Iran tensions remain elevated into August, and Iranian doctrine treats cyber operations as a core component of asymmetric competition. Organizations should not interpret the absence of a directly confirmed attack on U.S. military or federal networks as an absence of Iranian capability or intent. The infrastructure is in place; the access has been established; the capability is demonstrated. The decision point is geopolitical and remains outside the purview of this assessment. Defenders of any network that touches government, critical infrastructure, or defense-industrial systems should treat the indicators documented in this report as a standing threat profile rather than a transient crisis and should invest in permanent detection and response capabilities rather than temporary surge staffing.

## Cross-Source Technical Convergence: Multi-Vendor PLC Exploitation

{{< tag "SP" >}} The single most corroborated technical finding in this reporting period comes from five independent sources: CISA, FBI, NSA, EPA, and Department of Energy publishing joint advisories, alongside analysis from SafeBreach, IOActive, ExtraHop, SOCRadar, and Tenable. All sources published within the July 22 advisory update window and document the same underlying intrusion activity against internet-exposed programmable logic controllers. The converged picture shows Iranian-affiliated actors exploiting internet-exposed PLCs from three major vendors using a deliberate escalation in tradecraft: injection of malicious project files that retain legitimate ladder logic while disabling safety shutdown and alarm logic. This technique has proliferated to approximately sixty or more affiliated pro-Iranian hacktivist groups, meaning the threat persists regardless of what happens to the core CyberAv3ngers organization. This convergence represents the strongest infrastructure evidence of the reporting cycle and validates the assessment that Iranian cyber doctrine has shifted from reconnaissance to pre-positioned disruption capability.

## Appendix A: Source Summaries

{{< source title=`[REF-001]. CISA AA26-097A: Iranian-Affiliated Cyber Actors Exploit Programmable Logic Controllers` tag="AM" meta=`FBI/CISA/NSA/EPA/DOE, "Iranian-Affiliated Cyber Actors Exploit PLCs", July 22, 2026 · CyberAv3ngers · [cisa.gov/news-events/cybersecurity-advisories/aa26-097a](https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a)` >}}
Joint advisory documenting Iranian-affiliated targeting of internet-exposed PLCs. The July update expands confirmed vendor targeting from Rockwell Automation (April) to include Siemens S7-1200 and Schneider Electric systems. Documents active exploitation technique: malicious project file injection that disables safety shutdown and alarm logic. Primary U.S. government advisory on this campaign.
{{< /source >}}

{{< source title=`[REF-002]. ExtraHop: Anatomy of an Attack - Iranian-Affiliated Actors Target U.S. Critical Infrastructure` tag="IX" meta=`ExtraHop, "Anatomy of an Attack", August 2026 · CyberAv3ngers/IRGC-CEC · [extrahop.com/blog/aoa-iranian-affiliated-actors-target-u-s-critical-infrastructure-through-plcs](https://www.extrahop.com/blog/aoa-iranian-affiliated-actors-target-u-s-critical-infrastructure-through-plcs)` >}}
Analysis of Minnesota water system attacks timing relative to CISA advisory update. Notes four-day gap between July 22 advisory and July 26-27 attacks, suggesting either rapid exploitation of newly-disclosed capability or pre-positioning attack execution timed to follow advisory. Provides operational timeline correlation.
{{< /source >}}

{{< source title=`[REF-003]. KELA: MuddyWater in 2026 - Iran's APT Hits U.S. Targets` tag="SP" meta=`KELA Intelligence, "MuddyWater in 2026", March 2026 · MuddyWater/MOIS · [kelacyber.com/blog/irans-apts-and-the-us-enterprise-in-2026-muddywater](https://www.kelacyber.com/blog/irans-apts-and-the-us-enterprise-in-2026-muddywater/)` >}}
Analysis of MuddyWater's shift to military-tempo operations against U.S. enterprises in 2026. Documents pre-positioning in U.S. financial, aviation, and defense-sector networks beginning in February 2026, weeks before U.S.-Israeli strikes. Frames MuddyWater as having matured from regionally-focused espionage actor to global intelligence capability.
{{< /source >}}

{{< source title=`[REF-004]. Washington Post: U.S. Spy Agencies Suspect Iran Behind Minnesota Water Attacks` tag="AM" meta=`Nakashima & Verma, "U.S. Spy Agencies Suspect Iran", The Washington Post, July 30, 2026 · Iran/CyberAv3ngers · [washingtonpost.com/national-security/2026/07/30/us-spy-agencies-suspect-iran-launched-cyberattack-minnesota-water-facilities](https://www.washingtonpost.com/national-security/2026/07/30/us-spy-agencies-suspect-iran-launched-cyberattack-minnesota-water-facilities/)` >}}
Public reporting of U.S. intelligence assessment that Iran was responsible for coordinated attack on 30+ Minnesota municipal water systems on July 26-27. Creates direct operational link between newly disclosed capability (CISA advisory, July 22) and active exploitation (water system attacks, July 26-27). Establishes timeline of escalation.
{{< /source >}}

{{< source title=`[REF-005]. Rescana: RustyWater - Iranian MuddyWater APT Targets Israeli Government` tag="SP" meta=`Rescana, "RustyWater", February 24, 2026 · MuddyWater/MOIS · [rescana.com/post/rustywater-iranian-muddywater-apt-targets-israeli-government-and-infrastructure-with-advanced-rust](https://www.rescana.com/post/rustywater-iranian-muddywater-apt-targets-israeli-government-and-infrastructure-with-advanced-rust)` >}}
Documents MuddyWater deployment of RustyWater, a Rust-based remote access trojan, targeting Israeli government and infrastructure during heightened Middle East tensions. Describes technical advancement in stealth, persistence, and evasion capabilities. Rust implementation represents emerging tradecraft to evade detection signatures.
{{< /source >}}

{{< source title=`[REF-006]. SafeBreach: CISA AA26-097A Iranian PLC Attacks Coverage` tag="SP" meta=`SafeBreach Labs, "CISA AA26-097A Coverage", July 2026 · CyberAv3ngers/IRGC-CEC · [safebreach.com/blog/cisa-aa26-097a-iranian-plc-exploitation-safebreach-coverage](https://www.safebreach.com/blog/cisa-aa26-097a-iranian-plc-exploitation-safebreach-coverage/)` >}}
Deep technical analysis of PLC exploitation techniques documented in CISA advisory. Provides detection engineering guidance for organizations defending Rockwell, Siemens, and Schneider platforms. Includes MITRE ATT&CK mapping for Iranian-linked PLC targeting campaigns.
{{< /source >}}

{{< source title=`[REF-007]. SOCRadar: Iranian Hackers Broaden PLC Attacks on US Critical Infrastructure` tag="IX" meta=`SOCRadar, "Iranian Hackers Broaden PLC Attacks", July 2026 · CyberAv3ngers/IRGC-CEC · [socradar.io/blog/iranian-hackers-plc-us-critical-infrastructure](https://socradar.io/blog/iranian-hackers-plc-us-critical-infrastructure/)` >}}
Analysis of July 2026 advisory update and Minnesota water system attacks. Documents shift from single-vendor targeting (Unitronics, 2023) to multi-vendor campaigns (Rockwell, Siemens, Schneider, 2026). Details escalation in tradecraft from weak-credential exploitation to malicious project file injection.
{{< /source >}}

{{< source title=`[REF-008]. TechTimes: Iranian Hackers Infiltrate Siemens and Schneider PLCs` tag="IX" meta=`TechTimes, "Iranian Hackers Infiltrate Siemens and Schneider", July 23, 2026 · CyberAv3ngers/IRGC-CEC · [techtimes.com/articles/321335/20260723/iranian-hackers-infiltrate-siemens-schneider-plcs-blinding-operators-fake-readings.htm](https://www.techtimes.com/articles/321335/20260723/iranian-hackers-infiltrate-siemens-schneider-plcs-blinding-operators-fake-readings.htm)` >}}
Coverage of Iranian-linked PLC compromise techniques that inject logic disabling operator displays and safety functions. Documents scope of vulnerable systems across U.S. critical infrastructure. Emphasizes that dominant share of installed ICS equipment from major vendors is now confirmed attack target category.
{{< /source >}}

{{< source title=`[REF-009]. Trellix: The Iranian Cyber Capability 2026` tag="SP" meta=`Trellix Threat Research, "The Iranian Cyber Capability 2026", August 2026 · Multiple actors · [trellix.com/blogs/research/the-iranian-cyber-capability-2026](https://www.trellix.com/blogs/research/the-iranian-cyber-capability-2026/)` >}}
Comprehensive threat assessment covering MuddyWater, OilRig (APT34), APT33, APT35, and affiliated actors. Documents APT33 deployment of Tickler and SHAPESHIFT destructive malware against aerospace and petrochemical targets. Discusses infrastructure diversification by MuddyWater suggesting deliberate pre-positioning ahead of geopolitical escalation.
{{< /source >}}

## References

- Cybersecurity and Infrastructure Security Agency. "Iranian-Affiliated Cyber Actors Exploit Programmable Logic Controllers Across US Critical Infrastructure." Joint Cybersecurity Advisory AA26-097A, Updated July 22, 2026. https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a
- ExtraHop. "Anatomy of an Attack: Iranian-Affiliated Actors Target U.S. Critical Infrastructure Through PLCs." Published August 2026. https://www.extrahop.com/blog/aoa-iranian-affiliated-actors-target-u-s-critical-infrastructure-through-plcs
- KELA Intelligence. "MuddyWater in 2026: Iran's APT Hits U.S. Targets." Analysis and ATT&CK-mapped detection guidance, Published March 2026. https://www.kelacyber.com/blog/irans-apts-and-the-us-enterprise-in-2026-muddywater/
- Nakashima, Ellen and Pranshu Verma. "U.S. Spy Agencies Suspect Iran Launched Cyberattack on Minnesota Water Facilities." The Washington Post, July 30, 2026. https://www.washingtonpost.com/national-security/2026/07/30/us-spy-agencies-suspect-iran-launched-cyberattack-minnesota-water-facilities/
- Rescana. "RustyWater: Iranian MuddyWater APT Targets Israeli Government and Infrastructure With Advanced Rust-Based Malware." Published February 24, 2026. https://www.rescana.com/post/rustywater-iranian-muddywater-apt-targets-israeli-government-and-infrastructure-with-advanced-rust
- SafeBreach. "CISA AA26-097A: Iranian PLC Attacks Coverage." Published July 2026. https://www.safebreach.com/blog/cisa-aa26-097a-iranian-plc-exploitation-safebreach-coverage/
- SOCRadar. "Iranian Hackers Broaden PLC Attacks on US Critical Infrastructure." Blog post analyzing July 2026 advisory update. https://socradar.io/blog/iranian-hackers-plc-us-critical-infrastructure/
- TechTimes. "Iranian Hackers Infiltrate Siemens and Schneider PLCs, Blinding Operators With Fake Readings." July 23, 2026. https://www.techtimes.com/articles/321335/20260723/iranian-hackers-infiltrate-siemens-schneider-plcs-blinding-operators-fake-readings.htm
- Trellix. "The Iranian Cyber Capability 2026." Threat Research Blog. Published August 2026. https://www.trellix.com/blogs/research/the-iranian-cyber-capability-2026/
