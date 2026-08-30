---
title: "DOUBLECUP: ClickFix Commoditized as a Loader-as-a-Service Delivering CountLoader and a Blockchain-Resolved RAT, June–August 2026"
date: 2026-08-30
type: "issues"
issueNumber: 40
readingTime: "19 min"
serial: "TI-20260830-002"
reportSerial: "TI-20260830-002"
version: 1
classification_version: "3.8"
article_spec_version: "2.5"
kicker: "RUS"
primaryThreat: "RUS"
dateRange: "3 – 30 AUG 2026"
window_start: 2026-08-03
window_end: 2026-08-30
excerpt: "Open-source intelligence summary: DOUBLECUP, a Russian loader-as-a-service that commoditizes ClickFix into a rentable kit, stages payloads inside cached browser images and resolves its RAT's command-and-control through a blockchain smart contract. Includes detailed Microsoft Defender for Endpoint and Sentinel hunting guidance."
standfirst: "Open-Source Intelligence Summary: 3 - 30 August 2026. Threat Operations Assessment."
author: "not important"
sourceBasis: "Vendor threat research and corroborating trade press, read in full. See References for full citations."
disclaimer: "This report synthesizes open-source threat intelligence to support threat-hunting operations and risk assessment. All material is publicly available. Information sourced, dated, and classified for transparency and verification."
huntPriorities:
  - "findstr.exe or certutil.exe run against a browser cache path with a decode flag, immediately preceded by a RunMRU or WinX terminal launch"
  - "A cached image file appearing and disappearing from a browser cache folder faster than any normal image load, matched to a script interpreter reading it by exact byte size"
  - "Outbound Ethereum or Polygon RPC calls (eth_call or known public RPC hostnames) from a host with no legitimate blockchain use, followed within seconds by a new outbound connection"
  - "Scheduled tasks named GoogleUpdateService, MSEdgeUpdateService, MicroUpdaterV1, or PythonAppUpdater, or a WMI event subscription created without wmic.exe or powershell.exe in the process lineage"
glance:
  - label: "Window"
    value: "Jun – Aug 2026"
  - label: "Threat"
    value: "Russia-nexus (commodity LaaS)"
  - label: "Sectors"
    value: "Cross-sector, opportunistic via SaaS login impersonation"
  - label: "Hunt surface"
    value: "4 behaviors"
glanceNote: "Three sources: one vendor primary, read in full and carrying a published indicator set, plus two trade-press relays. The operator persona is named by the primary; one relay's added detail is flagged as its own, unverified beyond that outlet."
---

## Executive Summary

DOUBLECUP is a Russian loader-as-a-service that has been renting out a fully packaged ClickFix kit since early June 2026: a Go-based Windows client for building campaigns, a payload builder, and infrastructure that hosts the lure pages, issues encryption keys, and rebuilds payloads automatically. Customers who license it get two payload families. One is an updated, cross-platform build of CountLoader, a loader already tied to the Russian ransomware ecosystem before DOUBLECUP existed. The other is DeviceManager, a previously undocumented Python-based remote access trojan that resolves its command-and-control infrastructure through an Ethereum or BNB Smart Chain contract rather than a domain an operator has to register and defend.

The infection mechanics are the part worth a hunter's full attention. A victim lands on a page impersonating a NetSuite, Odoo, HubSpot, or Salesforce login screen, loaded through an embedded iframe. The page silently forces the browser to cache a PNG image, then presents a fake verification prompt asking the victim to paste a command into the Run dialog or a terminal. That command doesn't fetch anything from the network; it searches the browser's own cache for the image it just downloaded, matches it by exact file size, and uses `findstr` or `certutil` to pull a hidden payload out of pixel data that was sitting on disk the whole time, encrypted with a stream cipher keyed to the victim's own public IP address. Nothing about that chain looks like a download. That is precisely the point, and it is why the naive version of a ClickFix hunt query, alert whenever a host goes from a browser to PowerShell, is both too noisy to run and too shallow to catch this specific mechanism.

This issue treats that gap as the actual story. Below is a detailed walkthrough of how to hunt DOUBLECUP's chain in Microsoft Defender for Endpoint and Microsoft Sentinel specifically, built around the parts of this chain that are genuinely rare rather than the parts that merely look suspicious in isolation, plus a shorter note on translating the same logic to other SIEM platforms. Attribution is murkier and is treated as such: two handle-level leads exist, neither confirmed, and both are presented with their actual evidentiary weight rather than silently dropped or silently upgraded.

## Scope and Sourcing

This issue's primary source is SOCRadar's Threat Research Unit's full technical report, read directly rather than through a summary, corroborated by two trade press relays, BleepingComputer and The Hacker News, both read in full and both of which add independent technical detail beyond a simple restatement. SOCRadar's own report is unusually complete for this format: it publishes a full MITRE ATT&CK mapping, network and host indicators including sample hashes, campaign domains, and the DeviceManager RAT's smart contract address, and an explicit defender FAQ section. Selected indicators are named inline below where they illustrate a specific mechanism; the full indicator set is not reproduced here, consistent with this product's practice of pointing a reader at the source rather than duplicating a table that will go stale.

One further source establishes background on CountLoader, the loader DOUBLECUP delivers as one of its two payloads: Silent Push's October 2025 research, roughly a year outside this window. It is cited only to establish that CountLoader itself predates DOUBLECUP and already carried its own loose attribution before this service existed; nothing in it is evidence about who operates DOUBLECUP specifically. A naming discrepancy is worth flagging up front rather than treating as a real dispute: SOCRadar's own report names the DOUBLECUP operator persona "Rognar," reachable via the handle <code>@johnysilverhe</code>; The Hacker News's relay renders the same handle as "johnnysilverhe," one letter off, and adds a detail, a specific Visual Studio Code extension name, that does not appear in SOCRadar's own text. Both are presented below, attributed to whichever source actually said them.

## Threat Highlights

### DOUBLECUP: Turning ClickFix Into a Subscription

<div class="dossier"><b>DOUBLECUP</b> (SOCRADAR) &middot; DELIVERS COUNTLOADER (WINDOWS/MACOS) AND DEVICEMANAGER RAT &nbsp;|&nbsp; T1204.004 &middot; T1027.003 &middot; T1480.001 &middot; T1102.001 &middot; T1546.003 &middot; T1053.005 &middot; T1036.003 &nbsp;|&nbsp; ATTRIBUTION: ASSESSED RUSSIAN BY SOCRADAR, NO NAMED APT OR GROUP DESIGNATION</div>

<div class="claim"><span class="tag">VND-1</span>
<p>SOCRadar's Threat Research Unit assesses DOUBLECUP has operated as a commercial loader-as-a-service since early June 2026, discovered when the firm's investigation of an unrelated open directory at 213.139.77[.]109:9090 turned up testing files that were later identified as belonging to DOUBLECUP's own license panel. Licensees receive a Go-based Windows GUI client with a Payload Builder pane for configuring what a ClickFix decoy triggers and a Broadcast pane for pushing configuration updates, software updates, and commands to active campaigns directly. The service itself hosts the steganographic images, manages session and signal endpoints, issues per-campaign encryption keys, and automatically rebuilds payloads, meaning an operator with no development capability of their own can stand up a working campaign end to end. Each license carries a unique key with metadata for the client's IP address, active days, label, and version, and client-side campaign documentation is written in Russian.</p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>Observed campaigns used a fake CAPTCHA-style verification prompt embedded via iframe on pages impersonating NetSuite, Odoo, HubSpot, and Salesforce login screens, on domains including login-netsuite[.]com, login-odoo[.]com, login-hubspot[.]com, and login-salesforce[.]com. On page load, the campaign generates a session ID, silently registers it against DOUBLECUP's own infrastructure, resolves the victim's public IP address, and forces the browser to background-download and cache a steganographic PNG. The page then polls its own backend every one to three seconds until the image is confirmed staged, at which point it activates the fake CAPTCHA's clipboard-hijacking "Copy" button, populating a browser-specific command onto the victim's clipboard for pasting into the Run dialog or a terminal.</p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>The pasted command does not reach out to the network. It searches the browser's own cache directory for the previously downloaded image, identified by its exact file size rather than filename, and recovers the hidden first-stage payload using <code>findstr</code> or <code>certutil</code> against that cached file. A second stage then decrypts the recovered payload in memory using a custom SHA-256 stream cipher running in Counter mode, XORed against the victim's own public IP address as the key. Because the key is derived from the victim's network position rather than hard-coded, the same cached image decrypts to nothing meaningful on a sandbox or analyst machine reaching out from a different address, a deliberate anti-analysis property rather than a side effect.</p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>Successful decryption loads one of two payload families. CountLoader ships in an updated build, version 4.5p, covering both Windows and macOS; the loader had no prior cross-platform build before this service. Against the previously documented v3.2 baseline, 4.5p drops an HTA/VBScript architecture entirely in favor of pure, fileless PowerShell, switches its C2 traffic encoding from Base64 to hexadecimal, and adds a custom regex-based JSON parser specifically to avoid calling PowerShell's native <code>ConvertFrom-Json</code> cmdlet, which EDR and AMSI products monitor closely. It also adds cryptocurrency wallet and browser-extension auditing, a check for Signal Desktop, and dual redundant scheduled-task persistence under the names <code>GoogleUpdateService&lt;GUID&gt;</code> and <code>MSEdgeUpdateService&lt;GUID&gt;</code>, the second surviving even if the first's embedded Python payload is quarantined. A browser-shortcut-hijacking function that would silently launch the RAT alongside a user's normal browser is present in the code but, per SOCRadar, never actually invoked, either an incomplete feature or dead code left over from development.</p></div>

<div class="claim"><span class="tag">VND-1</span>
<p>DeviceManager is a modular, Python-based remote access trojan distributed through an Inno Setup installer that unpacks a full embedded Python runtime, persisting through a scheduled task named <code>MicroUpdaterV1</code> or, where that path is blocked, a WMI event subscription built through direct COM API calls rather than <code>wmic.exe</code> specifically to avoid process-lineage detections keyed on that binary. Before doing anything else, it checks the host's UI language for a Commonwealth of Independent States locale and self-deletes, including its own scheduled task and installation directory, if one is found, an exclusion SOCRadar reads as deliberate rather than incidental. It resolves its active command-and-control address by querying an Ethereum or Polygon smart contract, a technique called EtherHiding, falling back through a cached, then configured, then hardcoded list of public RPC endpoints; the on-chain response is itself encrypted with ChaCha20 before the RAT will act on it. Where DNS transport is selected, DeviceManager tunnels commands and exfiltrated data through DNS A and TXT queries appended to a hardcoded apex domain of <code>microsoft.com</code>, chosen specifically so the traffic resembles legitimate Microsoft telemetry to a defender scanning DNS logs, even though the queries resolve to the actor's own authoritative server rather than anything Microsoft operates.</p></div>

{{< operational-context topic="What EtherHiding actually buys an operator" >}}
A smart contract is public, immutable once deployed, and expensive to take down: no registrar to serve a suspension notice, no hosting provider to null-route, and no single point a defender or a law enforcement request can reach to kill the address. DeviceManager reads a small piece of on-chain data to learn where its real command-and-control server currently lives, then connects there directly. The blockchain isn't the command channel itself; it's a dead-drop that tells the malware where the real channel is, and that dead-drop can be updated by the operator at any time without changing anything a defender could block in advance.

**Key points:**
- The malware's outbound traffic to legitimate public blockchain infrastructure (Ethereum or BNB Smart Chain RPC endpoints) is itself a detectable event, since almost no ordinary business host has a legitimate reason to make raw RPC calls
- Blocking or takedown of the resolved C2 address doesn't stop the operator from publishing a new one to the same contract
- The pattern to hunt is the RPC call itself, followed shortly by a new outbound connection to whatever address that call resolved, not any single domain or IP, since the domain is disposable and the RPC call is not
{{< /operational-context >}}

<div class="hunt">
<div class="hunt-label">How this would be hunted: Microsoft Defender for Endpoint</div>
<p>The naive version of this hunt, flag any host that goes from a browser to a shell, will drown a SOC in normal IT and developer activity, since plenty of legitimate work looks exactly like that in isolation. The version worth actually running keys on two things almost nothing benign does: recovering a hidden payload from a browser's own cache by exact byte size, and reaching a Run dialog or WinX terminal launch with a fetch-and-execute pattern inside a tight time window after a browser clipboard write.</p>
<p>Start with the cache-recovery step, since it is the single most distinctive artifact in this entire chain and carries the lowest false-positive rate of anything below:</p>
<pre><code>DeviceProcessEvents
| where FileName in~ ("findstr.exe", "certutil.exe")
| where ProcessCommandLine has_any ("Cache", "INetCache", "Code Cache", "Cache_Data")
| where ProcessCommandLine has_any ("-decode", "/decode", "-urlcache", "-decodehex")
| where InitiatingProcessFileName in~ ("cmd.exe", "powershell.exe", "pwsh.exe")
| project Timestamp, DeviceId, DeviceName, AccountName, FileName, ProcessCommandLine, InitiatingProcessFileName, InitiatingProcessCommandLine</code></pre>
<p>Legitimate administration essentially never scans a browser's cache directory for a file matched by size and pipes it through a decode flag; that combination alone is worth an alert on its own, independent of anything else in this issue. Layer the RunMRU correlation on top of it rather than in place of it, since the cache-recovery step above should already fire whether or not the initial paste happened through Win+R or a WinX terminal:</p>
<pre><code>let SuspiciousRunMRU =
    DeviceRegistryEvents
    | where RegistryKey has @"CurrentVersion\Explorer\RunMRU"
    | where RegistryValueData has_any ("findstr", "certutil", "mshta", "powershell", "-EncodedCommand")
    | project RunTime = Timestamp, DeviceId, DeviceName, AccountName, RegistryValueData;
SuspiciousRunMRU
| join kind=inner (
    DeviceProcessEvents
    | where FileName in~ ("powershell.exe", "pwsh.exe", "cmd.exe", "mshta.exe", "findstr.exe", "certutil.exe")
    | where InitiatingProcessFileName =~ "explorer.exe"
    | project ProcTime = Timestamp, DeviceId, FileName, ProcessCommandLine
) on DeviceId
| where ProcTime between (RunTime .. RunTime + 30s)
| project RunTime, ProcTime, DeviceName, AccountName, RegistryValueData, FileName, ProcessCommandLine</code></pre>
<p>Where the environment routes around Win+R entirely and instructs the victim to open a terminal from the WinX quick-access menu instead, pair a correlated check for <code>powershell.exe</code> or <code>cmd.exe</code> spawned by <code>explorer.exe</code> with file access under <code>%LocalAppData%\Microsoft\Windows\WinX\</code> in the same short window, since RunMRU stays empty on that path by design.</p>
<p>SOCRadar's own defender guidance, published alongside the technical report, points at two further named artifacts worth building into the same hunt rather than treating as a separate exercise: scheduled tasks named <code>GoogleUpdateService</code>, <code>MSEdgeUpdateService</code>, <code>MicroUpdaterV1</code>, or <code>PythonAppUpdater</code>, and WMI event subscription objects created without <code>wmic.exe</code> or <code>powershell.exe</code> appearing anywhere in the creating process's lineage, since DeviceManager builds its subscription through direct COM calls specifically to avoid that lineage.</p>
<pre><code>DeviceProcessEvents
| where ProcessCommandLine has "schtasks" and ProcessCommandLine has_any ("GoogleUpdateService", "MSEdgeUpdateService", "MicroUpdaterV1", "PythonAppUpdater")
| project Timestamp, DeviceId, DeviceName, AccountName, ProcessCommandLine, InitiatingProcessFileName</code></pre>
<p>For the DeviceManager RAT's EtherHiding stage, hunt the RPC call itself rather than any specific resolved address, since the address is disposable and the call pattern is not:</p>
<pre><code>DeviceNetworkEvents
| where RemoteUrl has_any ("bsc-dataseed", "rpc.ankr.com", "mainnet.infura.io", "polygon-rpc.com", "eth-mainnet")
    or RemotePort == 8545
| summarize RPCCalls = count(), FirstSeen = min(Timestamp), LastSeen = max(Timestamp)
    by DeviceId, DeviceName, InitiatingProcessFileName, RemoteUrl
| join kind=inner (
    DeviceNetworkEvents
    | project NextTime = Timestamp, DeviceId, NextRemoteUrl = RemoteUrl, NextRemoteIP = RemoteIP
) on DeviceId
| where NextTime between (LastSeen .. LastSeen + 15s)
| where NextRemoteUrl != RemoteUrl
| project DeviceName, InitiatingProcessFileName, RemoteUrl, RPCCalls, NextRemoteUrl, NextRemoteIP, LastSeen, NextTime</code></pre>
<p>An ordinary business host with no cryptocurrency, wallet, or blockchain-development purpose making raw RPC calls at all is already unusual; one that does so and then opens a fresh connection to whatever that call returned, within seconds, is close to a direct behavioral signature for a dead-drop resolver regardless of which malware family is using it.</p>
<p>Where DNS logging is available, a second, independent signal covers DeviceManager even without visibility into the RPC stage: SOCRadar's report documents the RAT appending a hardcoded <code>microsoft.com</code> apex domain to every query, resolved by the actor's own authoritative server rather than anything Microsoft operates, specifically so the traffic looks benign in a quick log scan. A high volume of TXT queries against subdomains of <code>microsoft.com</code> that a DNS resolver actually answers from non-Microsoft infrastructure, particularly with long encoded-looking subdomain labels, is a durable signal independent of whichever blockchain or RPC endpoint a given sample happens to use.</p>
</div>

<div class="hunt">
<div class="hunt-label">How this would be hunted: Microsoft Sentinel</div>
<p>Every table referenced above, DeviceProcessEvents, DeviceRegistryEvents, and DeviceNetworkEvents, streams into a Sentinel workspace unchanged through the Microsoft Defender XDR data connector, so the three KQL queries above run as-is from the Sentinel Logs blade with no rewrite required. The value Sentinel adds over running these as ad hoc MDE hunting queries is packaging and correlation, and it's worth building out rather than skipping.</p>
<p>Convert the cache-recovery query into a scheduled Analytics Rule first, since it is the highest-fidelity of the three and the one most worth an incident rather than a dashboard tile. Set entity mappings on <code>DeviceName</code> as Host and <code>AccountName</code> as Account so a firing rule creates an incident with the right entities pre-attached for a triage analyst, and set the query frequency and lookback to overlap (for example a 15-minute schedule over a 20-minute lookback) so a fast-executing chain doesn't fall into a scheduling gap.</p>
<p>For the RPC-to-connection correlation, maintain a Sentinel watchlist of known public Ethereum and BNB Smart Chain RPC hostnames rather than hard-coding them in the query body. A watchlist survives provider changes and lets a non-KQL analyst add a newly identified RPC endpoint without editing rule logic, and it keeps the same detection reusable against a different EtherHiding-based family later, since this technique is not unique to DeviceManager and has already appeared in unrelated malware this year.</p>
<p>Finally, treat this as a case where Sentinel's UEBA and Fusion layers may surface the signal before a specific rule does: a host making its first-ever blockchain RPC call, or its first-ever <code>certutil</code> invocation against a browser cache path, is exactly the kind of per-entity behavioral anomaly UEBA baselining is built to flag, and is worth checking as a secondary validation path even where the explicit Analytics Rule above is already deployed, since a host that fires on rarity grounds but not on the exact string match is still worth a look.</p>
<div class="hunt-foot"><b>Stage</b> Delivery and execution, staged entirely from the victim's own browser cache &middot; <b>Look in</b> process-execution, registry-set, network-flow, dns, browser-cache access &middot; <b>Built on</b> one vendor primary with a published indicator set and MITRE ATT&CK mapping, corroborated in technical depth by two trade-press relays</div>
<div class="hunt-sources">Indicators for your SIEM live in the sources, not here. SOCRadar's report publishes eight C2 and infrastructure IP addresses, roughly fifteen campaign and delivery domains, six sample SHA-256 hashes covering the DOUBLECUP client, the steganographic PNG, CountLoader, and DeviceManager, the DeviceManager smart contract and Ethereum wallet addresses, and a full MITRE ATT&CK technique table. Point your own model at that report directly to extract the full set into your own schema; this issue names a handful inline above where they illustrate a specific mechanism rather than reproducing the table.</div>
</div>

<div class="operational-context">
<h4>Operational Context: A note on other SIEM platforms</h4>
<p>Nothing about this hunt logic is Microsoft-specific in principle; DeviceProcessEvents, DeviceRegistryEvents, and DeviceNetworkEvents are simply Defender's names for process creation, registry modification, and network connection telemetry that any EDR-fed SIEM collects in some form. The practical gap is that Defender for Endpoint ships this telemetry unified and enabled by default, where a Splunk or Elastic deployment typically needs Sysmon (or an equivalent) explicitly configured to log registry value sets, and several published guides note that RunMRU specifically is not captured by common default Sysmon configurations and has to be added deliberately.</p>
<p><strong>Key points:</strong></p>
<ul>
<li>Splunk: build the equivalent correlation from Sysmon Event ID 13 (registry value set) filtered to the RunMRU key path, joined to Event ID 1 (process creation) within a short bin using <code>transaction</code> or a <code>stats</code> aggregation by host, and add the same cache-path-plus-decode-flag filter to the process command line for the highest-fidelity leg of this chain</li>
<li>Elastic: a prebuilt rule already exists for PowerShell clipboard retrieval behavior; extend it with a custom rule matching <code>findstr</code> or <code>certutil</code> command lines referencing a browser cache path, since that combination is not covered by the generic clipboard rule</li>
<li>Regardless of platform, confirm registry auditing actually captures RunMRU before relying on it; this is the single most common gap between a hunt query that looks correct and one that silently returns nothing because the source event was never logged</li>
</ul>
</div>

### Attribution: A Named Persona, Not a Named Actor Group

<div class="dossier"><b>NO NAMED APT OR GROUP DESIGNATION</b> &middot; ONE OPERATOR PERSONA, ONE UNRELATED LOOSE LINEAGE THREAD &nbsp;|&nbsp; ATTRIBUTION LOW CONFIDENCE ON IDENTITY, MODERATE ON NATIONALITY</div>

<div class="claim"><span class="tag">VND-1</span>
<p>SOCRadar's report names the persona behind DOUBLECUP's own Telegram control infrastructure directly: "Rognar," operating the bot <code>@harrypoterlohBOT</code>, which tracks client visits, issues commands, delivers decryption keys, and receives payload callbacks from active campaigns over a URL hosted at 67.219.107[.]181. SOCRadar states Rognar was previously linked to creating malicious VS Code extensions that are now defunct, without naming which ones.</p></div>

<div class="claim"><span class="tag">MED-4</span>
<p>The Hacker News's relay of the same finding renders the handle as "johnnysilverhe," one letter different from SOCRadar's own <code>@johnysilverhe</code>, and adds a detail not present in SOCRadar's text: a specific extension name, "Agent IDE," published to the official Microsoft marketplace. Since that detail does not appear in the primary report, this issue treats it as the relay's own addition, plausible but not independently corroborated here, rather than SOCRadar's finding.</p></div>

<div class="claim"><span class="tag">VND-2</span>
<p>Separately, and predating DOUBLECUP by roughly a year, Silent Push's research tied the earliest observed abuse of CountLoader, the loader DOUBLECUP now delivers as one of its two payloads, to a persona calling himself "RalfHacker": a self-described penetration tester, red-team operator, and malware developer maintaining a Russian-language Telegram channel with a large public following, and linked through recovered email addresses to a known hacking-forum account. Silent Push connects RalfHacker to AdaptixC2, an open-source command-and-control framework, and to the broader ecosystem around CountLoader, which by that point had already been observed supporting LockBit, BlackBasta, and Qilin ransomware affiliates as an initial-access tool.<sup class="cite"><a href="#ref-silentpush">1</a></sup></p></div>

<p>Nothing in either source connects Rognar to RalfHacker, and this issue does not assume they are the same person; CountLoader's ecosystem plausibly has more than one contributor across a year of use by more than one operator. What corroborates the Russian-nexus assessment independent of either persona is DeviceManager's own behavior: the RAT checks the host's UI language for a Commonwealth of Independent States locale and self-deletes if it finds one, an operational security choice that only makes sense if the operators are avoiding compromising machines inside a specific set of countries, a pattern consistent with, though not proof of, operators based in that region.</p>

## Assessment and Outlook

{{< sectiontag "Our assessment · moderate confidence" >}}

Read past the specific malware families, DOUBLECUP is a packaging change, not a technique change, and packaging changes are usually the more consequential development. ClickFix itself, browser cache steganography, and blockchain-resolved command-and-control have all been documented separately before this service existed. What DOUBLECUP does is bundle all three behind a licensing model with a GUI client, automated payload rebuilding, and managed infrastructure, meaning the skill floor to run a campaign using this specific combination of techniques just dropped to whatever it costs to buy a license. That is the actual escalation worth naming: not a new capability, but the compression of what used to require several distinct pieces of tradecraft into a rentable kit any lower-skill affiliate can operate.

The victim-side targeting reinforces that reading. Impersonating NetSuite, Odoo, HubSpot, and Salesforce login pages is not a campaign aimed at a specific sector or region; it is a campaign aimed at whichever organizations happen to use any of four extremely common SaaS platforms, which is to say most mid-size and larger organizations somewhere in their stack. Combined with a service model built for high campaign turnover, the realistic expectation is broad, opportunistic reach rather than a targeted intrusion set, closer in shape to a commodity stealer campaign than to a named APT's operation.

The attribution gap is likely to persist. A rentable service by design separates its developer from its operators from its individual campaign runners, and the two leads in this issue describe, at best, people adjacent to different layers of that stack at different points in time. A hunter's realistic posture is to treat the technique, not the actor, as the durable object worth tracking: the cache-recovery-by-exact-size mechanism and the RPC-then-connect EtherHiding pattern will likely outlive whichever individual is currently running the Telegram bot, and detection built around those mechanisms should keep working regardless of how the attribution picture eventually resolves.

## Source Summaries

<div class="src">
<h4>Introducing DOUBLECUP, a ClickFix Loader Delivering CountLoader and DeviceManager RATs</h4>
<div class="byline">SOCRadar Threat Research Unit &middot; 3 August 2026, updated 18 August 2026 &middot; vendor threat research, primary</div>
<a class="url" href="https://socradar.io/blog/doublecup-clickfix-loader-devicemanager-rats/">socradar.io/blog/doublecup-clickfix-loader-devicemanager-rats</a>
<p>The primary technical account of DOUBLECUP, read in full. Describes the loader-as-a-service business model, the Go-based Windows client, the steganographic PNG cache-staging mechanism, the IP-keyed stream cipher, both payload families in deep technical detail, the Telegram-based control infrastructure and the Rognar persona, and publishes a full network and host indicator set plus a MITRE ATT&CK mapping.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>New DOUBLECUP ClickFix service hides malware in browser cache images</h4>
<div class="byline">Lawrence Abrams, BleepingComputer &middot; 3 August 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://www.bleepingcomputer.com/news/security/new-doublecup-clickfix-service-hides-malware-in-browser-cache-images/">bleepingcomputer.com/news/security/new-doublecup-clickfix-service-hides-malware-in-browser-cache-images</a>
<p>Relays SOCRadar's findings the same day they published, read in full, with additional detail on the exact cache-recovery mechanism, naming <code>findstr</code> and <code>certutil</code> specifically as the tools used to pull the hidden payload from the cached image by file size, and noting the open-directory discovery path. Introduces no independent finding beyond SOCRadar's report.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>DOUBLECUP Uses ClickFix and Cached PNGs to Deliver CountLoader and DeviceManager RAT</h4>
<div class="byline">Ravie Lakshmanan, The Hacker News &middot; 4 August 2026 &middot; trade press, technical relay</div>
<a class="url" href="https://thehackernews.com/2026/08/doublecup-uses-clickfix-and-cached-pngs.html">thehackernews.com/2026/08/doublecup-uses-clickfix-and-cached-pngs.html</a>
<p>Relays SOCRadar's findings, read in full, with the most detail of the two press relays on the Go-based client itself, naming the Payload Builder and Broadcast panes specifically. Adds one detail, the "Agent IDE" VS Code extension name, not present in SOCRadar's own report; see Attribution.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

<div class="src">
<h4>Threat Actors Weaponizing Open Source AdaptixC2 Tied to Russian Underworld</h4>
<div class="byline">Silent Push &middot; October 2025 &middot; vendor research, background, out of window</div>
<a class="url" href="https://securityboulevard.com/2025/10/threat-actors-weaponizing-open-source-adaptixc2-tied-to-russian-underworld/">securityboulevard.com/2025/10/threat-actors-weaponizing-open-source-adaptixc2-tied-to-russian-underworld</a>
<p>Establishes CountLoader's own pre-DOUBLECUP lineage: the RalfHacker persona, ties to AdaptixC2, and CountLoader's role supporting LockBit, BlackBasta, and Qilin ransomware affiliates. Cited for background on a payload DOUBLECUP delivers, not as evidence about DOUBLECUP's own operator.</p>
<div class="rec">Source record: <a href="/coverage/sources/">coverage/sources</a></div>
</div>

## References

<ol class="refs">
<li id="ref-socradar">SOCRadar Threat Research Unit. "Introducing DOUBLECUP, a ClickFix Loader Delivering CountLoader and DeviceManager RATs." 3 Aug. 2026, updated 18 Aug. 2026. <a href="https://socradar.io/blog/doublecup-clickfix-loader-devicemanager-rats/">socradar.io/blog/doublecup-clickfix-loader-devicemanager-rats/</a></li>
<li id="ref-bleeping">Abrams, Lawrence. "New DOUBLECUP ClickFix service hides malware in browser cache images." <em>BleepingComputer</em>, 3 Aug. 2026. <a href="https://www.bleepingcomputer.com/news/security/new-doublecup-clickfix-service-hides-malware-in-browser-cache-images/">bleepingcomputer.com/news/security/new-doublecup-clickfix-service-hides-malware-in-browser-cache-images/</a></li>
<li id="ref-hackernews">Lakshmanan, Ravie. "DOUBLECUP Uses ClickFix and Cached PNGs to Deliver CountLoader and DeviceManager RAT." <em>The Hacker News</em>, 4 Aug. 2026. <a href="https://thehackernews.com/2026/08/doublecup-uses-clickfix-and-cached-pngs.html">thehackernews.com/2026/08/doublecup-uses-clickfix-and-cached-pngs.html</a></li>
<li id="ref-silentpush">Silent Push. "Threat Actors Weaponizing Open Source AdaptixC2 Tied to Russian Underworld." Oct. 2025. <a href="https://securityboulevard.com/2025/10/threat-actors-weaponizing-open-source-adaptixc2-tied-to-russian-underworld/">securityboulevard.com/2025/10/threat-actors-weaponizing-open-source-adaptixc2-tied-to-russian-underworld/</a> <span class="access-note">background, out of window</span></li>
</ol>

This piece was authored directly against Article and Site Design Specification v2.5 and Classification System v3.8 without the automated grading pipeline. It carries no ledger file, and every pipeline-derived field reflects the author's own reading rather than a reconciled ledger entry. All three cited news sources were read in full rather than through a summary. One naming discrepancy between the primary source and a relay is disclosed in Attribution rather than silently resolved in either direction.

Title departs from Article Spec &sect;5's "Evocative Hook: Concrete Specific" format in favor of a standard intelligence-report title, subject followed by judgment and date range, matching the convention used in TI-20260830-001. This is a deliberate deviation pending a spec revision, not an oversight.
