---
title: "Long-Baseline Threat Hunting: Fifteen Hunts a Two-Week Retention Window Can't See"
date: 2026-09-06
description: "Statistical structure, agentic execution risk, and reading a citation for what it actually is, applied to the hunts worth paying long-term storage for."
dek: "Statistical structure, agentic execution risk, and the discipline of reading a citation for what it actually is, applied to the specific menu of hunts worth paying long-term storage for once same-day alerting stops being the bottleneck."
track: "Threat Hunting"
level: "Practitioner / graduate"
prerequisites: "Working hunt program, basic statistics"
format: "Pseudocode, uncompiled"
status: "Draft"
tags: ["threat hunting", "statistics", "agentic ai"]
---

Here is the actual shape of the problem, not the abstract version of it. Same-day detection is a substantially solved problem now in a way it wasn't five years ago — a competent alerting layer, agentic or not, can watch today's telemetry and flag today's anomalies well enough that a dedicated dashboard for "what happened in the last two weeks" is often redundant engineering effort. What that layer cannot do anything about, no matter how good the model behind it gets, is data that no longer physically exists. A SIEM holding fourteen days of hot storage because a year of it is not a defensible line item has a hard boundary on what same-day alerting can ever see. Past that boundary there are exactly two options: retain more, somewhere queryable, or accept a category of adversary behavior your stack is structurally blind to — not detection-tuning blind, architecturally blind.

That constraint, not a preference for long time horizons, is why every hunt below needs weeks to months of history to function at all. Short-term is someone else's solved problem now. What's left is the genuinely interesting remainder: patterns too slow to trip a same-day rule, and too expensive to retain indefinitely on the hope a human eventually looks. So the first real decision here isn't which hunt to build — it's which of these fifteen catches something your short-term layer is structurally incapable of catching, badly enough to justify the storage line item, for your specific threat model. Treat what follows as a menu to select two or three items from, not a checklist to build in full.

One more thing, stated plainly because it's true of this document specifically: this is the kind of artifact you get when a capable model is tasked with drafting hunt logic for a dashboard build — fifteen technically coherent hunts and a wall of real citations, generated in minutes. Every citation below is real. What generating the list cannot do is tell you which citation is a standards body's own structural definition, which is a single peer-reviewed result, and which is a vendor's case study about its own product. That sorting is the actual content of this document, done inline rather than left as an exercise, and it matters more rather than less the more capable the model that drafted the underlying list.

## Part I — The Hunts

### 1. Long-Period Beaconing

*Detecting interval regularity that survives adversarial jitter*

A C2 channel on a fixed schedule is, definitionally, trying to look like nothing on any single day. The tell is not the traffic — it's the low {{< term def="How spread out a set of values is around its center — variance, standard deviation, or a more robust measure like MAD are all dispersion statistics." >}}dispersion of inter-arrival times{{< /term >}}, which is a second-moment property no amount of single-connection inspection can reveal.

```
for each (src_ip, dst_ip) pair with conn_count > threshold over window:
    compute inter-arrival times between connections
    compute robust CV = 1.4826 * MAD(intervals) / median(intervals)
    if robust_CV < 0.2 and connection_count > 20 over 60 days:
        flag as beacon candidate
    score = f(robust_CV, jitter_bucket_consistency, session_duration_variance)
```

The naive coefficient of variation (stddev/mean) is fragile here for a reason worth internalizing: a single multiplexed burst or a dropped-then-retried session injects a heavy-tailed outlier into the interval distribution, and stddev is not robust to that — one bad interval can move it enough to mask a real beacon. The {{< term def="Median of the absolute deviations from the median. Unlike standard deviation, a few extreme outliers barely move it -- the property that makes 'robust CV' actually robust." label="MAD" >}}median absolute deviation{{< /term >}}-based CV above doesn't have that failure mode. For frameworks applying randomized jitter with a heavy-tailed rather than uniform distribution — increasingly the default, not the exception — a stronger approach than any fixed-window CV test is a periodogram over irregularly-sampled event times: the {{< term def="A spectral-analysis technique for detecting periodicity in unevenly-sampled time series, originally built for astronomy (irregular telescope observation times) and directly applicable to irregular network connection timestamps." label="Lomb-Scargle periodogram" >}}Lomb-Scargle method{{< /term >}} was built for exactly this problem (unevenly-sampled astronomical observations) and transfers cleanly to connection timestamps. It surfaces the dominant frequency directly rather than inferring regularity from a single dispersion statistic, and it degrades more gracefully when jitter is deliberately non-uniform.

Retrospective confirmation over 60–90 days answers "is this a beacon." It does not answer "when did this start," which is the operationally relevant question once you've found one. Online change-point methods — {{< term def="Cumulative sum control chart. Tracks the running sum of deviations from an expected value; a sustained drift away from zero signals a change point in the underlying process, updated incrementally as new data arrives." label="CUSUM" >}}CUSUM{{< /term >}} or the Page-Hinkley test — run incrementally on the interval stream and localize the onset of regularity, which is the difference between "this host is compromised" and "this host has been compromised since approximately March 14th," a distinction that matters enormously for scoping.

{{< callout label="READING THE SOURCING" >}}
MITRE ATT&CK frames beaconing under Application Layer Protocol (T1071) and its DNS sub-technique (T1071.004), explicitly naming interval regularity as the detectable signal even under jitter{{< cite 1 >}} — that's a structural claim about how C2 frameworks are built, not an empirical result anyone had to go prove. BZAR, MITRE's own Zeek-to-ATT&CK mapping, is a reasonable translation starting point precisely because it comes from the same body that defined the technique.{{< cite 2 >}} RITA, the open-source Zeek beacon-scorer this pseudocode is closest to, is the actual empirical grounding for the multi-week window: it demonstrates that statistical periodicity survives Cobalt Strike's default jitter across hundreds of connections. That's a tool's design decision under real adversarial conditions, not a vendor's sales claim — nobody is trying to sell you RITA.
{{< /callout >}}

### 2. First-Time-Ever External Communication

*Novelty scoring at fleet scale without drowning in false discoveries*

A host contacting something absent from its entire logged history is worth inspection, especially adjacent to a patch, an incident, or onboarding. The naive version of this hunt has a scaling failure that only shows up once you run it against a real fleet.

```
maintain seen_destinations[host] from 365-day rolling history
for each new connection today:
    if dst not in seen_destinations[host]:
        p_value = benjamini_hochberg_adjust(raw_novelty_score, family_size=daily_test_count)
        if p_value < alpha AND dst is newly-registered AND newly-seen-for-host:
            flag high priority
```

"Never seen before" has enormous cardinality at fleet scale — every host onboards new CDN edge nodes, new SaaS subdomains, new third-party trackers constantly, so a naive per-connection novelty flag is running thousands of simultaneous hypothesis tests per day. Left uncorrected, the expected count of false positives at any fixed per-test threshold scales with the number of tests, not with the base rate of actual compromise — the exact failure mode {{< term def="Running many statistical tests simultaneously inflates the overall false-positive rate; a 5% per-test error rate becomes near-certain to produce false positives somewhere once you run thousands of tests. Correction methods like Benjamini-Hochberg control this." label="multiple comparisons problem" >}}multiple comparisons correction{{< /term >}} exists to prevent. {{< term def="A method for controlling the false discovery rate -- the expected proportion of false positives among all flagged results -- when running many simultaneous tests, less conservative than correcting for the worst case (Bonferroni)." label="Benjamini-Hochberg procedure" >}}Benjamini-Hochberg{{< /term >}}'s false-discovery-rate control is the right correction here rather than a Bonferroni-style worst-case adjustment, because you're optimizing for triage capacity (a bounded, tolerable rate of false leads) rather than for near-zero false positives at any cost.

{{< callout label="READING THE SOURCING" >}}
Passive DNS as a hunting substrate predates most current tooling — it's associated with Dr. Paul Vixie's early work and has its own SANS webcast history, marking it as an established discipline rather than a recent trend.{{< cite 3 >}} A Juniper Threat Labs case study used passive-DNS history to surface additional malicious infrastructure tied to one active RAT campaign — a real applied result, and also one vendor's investigation of one campaign, a narrower evidentiary base than a technique definition. Elastic's prebuilt rare-domain ML detection runs the identical logic over a shorter default window, useful as confirmation the underlying idea is common enough to productize, not as independent proof it holds at 365 days specifically.
{{< /callout >}}

### 3. Slow-Drip Data Exfiltration Trend

*Fitting a trend line to data that violates OLS's own assumptions*

Exfiltration throttled to stay under a daily volume alarm shows up, if at all, as a slope rather than a spike — invisible until enough weekly points exist to fit a line through them.

```
for each host:
    y = log1p(weekly_outbound_bytes) for 26 weeks   # variance-stabilizing transform
    fit Theil-Sen slope estimator (robust to single-week outliers)
    run CUSUM on regression residuals to test for a genuine structural break
    if slope > threshold and break_confirmed:
        flag sustained upward exfil trend
    cross-check against destination diversity (single dst vs many)
```

Ordinary least squares assumes roughly homoscedastic, near-Gaussian residuals, which weekly network byte counts essentially never satisfy — the distribution is heavy-tailed and volume growth is typically multiplicative rather than additive. Two corrections matter more than the regression's {{< term def="The proportion of variance in the outcome explained by the model -- how well the fitted line actually tracks the data, distinct from whether the slope itself is meaningfully nonzero." label="R-squared" >}}r²{{< /term >}} alone: a log transform before fitting stabilizes the variance a raw-bytes fit will otherwise misrepresent, and a {{< term def="A robust method for fitting a line's slope, computed as the median of slopes between all pairs of points rather than minimizing squared error -- largely immune to a single outlier week (a scheduled backup burst) dragging the fit." label="Theil-Sen estimator" >}}Theil-Sen estimator{{< /term >}} — the median of pairwise slopes rather than a squared-error minimizer — is close to immune to a single anomalous week (a scheduled backup, a one-off large transfer) dragging an OLS fit into a false positive or masking a real trend. A structural-break test (CUSUM on the residuals) is what actually distinguishes "this genuinely changed regime" from "one outlier week happened to sit at a slope-favorable position," which raw slope-plus-r² cannot.

{{< callout label="READING THE SOURCING" >}}
"Low and slow" exfiltration is an established framing in network behavior analysis — Plixer's writing on it treats week-to-week accumulation as the expected shape of the problem, useful for framing rather than as evidence in itself. The stronger citation is Sharma, Joshi, and Finin's peer-reviewed IEEE IRI 2013 paper arguing that slow/low exfiltration is structurally resistant to scan-and-test detection{{< cite 4 >}} — the one source here that passed peer review rather than a vendor's own editorial process, and the actual academic case for trend-fitting over point-in-time thresholds. Darktrace's public research on the same pattern is worth reading for the applied angle, with the standing discount that Darktrace sells a product built on this exact claim.
{{< /callout >}}

### 4. Rare Parent-Child Process Lineage

*Rarity as surprisal, not as a raw occurrence count*

`powershell.exe` launching something is unremarkable a million times a day fleet-wide. The same binary launched by `winword.exe` with a base64 argument, a combination with zero prior occurrences fleet-wide in a year, is a different fact — and "zero" is only meaningful against a full-year frequency table.

```
build frequency table F(parent, child, cmdline_ngrams) over 365 days, all endpoints
for each new execution e:
    surprisal = -log2( F.get(e.tuple, epsilon) / total_events )
    if surprisal > threshold AND e.child in known_LOLBins:
        flag as rare lineage, weight by asset criticality
```

A raw occurrence-count threshold treats "happened twice" and "happened never" as roughly equivalent categories, which is the wrong resolution for a frequency distribution this {{< term def="A power-law-shaped frequency distribution where a small number of items account for most occurrences and a long tail of items are individually rare -- typical of natural language, and equally typical of command-line argument patterns across a real fleet." label="Zipfian distribution" >}}Zipfian{{< /term >}}, where the long tail is enormous and the interesting cases live deep in it. Framing rarity as {{< term def="Negative log-2 of a probability: the number of bits of 'surprise' an event carries given how likely it was. Rarer events carry higher surprisal -- the same underlying idea Shannon entropy averages over an entire distribution." label="surprisal (self-information)" >}}surprisal{{< /term >}}, −log₂ of the tuple's empirical probability, gives a continuous, information-theoretically grounded score that scales correctly across that tail instead of collapsing everything below a count threshold into one bucket. Exact-tuple matching is also brittle against an adversary trivially varying flags or paths; a more durable version tokenizes the command line and scores against an n-gram or sequence model over the token stream rather than requiring an exact string match, which survives superficial argument variation that would otherwise reset the tuple's frequency count to zero every time.

{{< callout label="READING THE SOURCING" >}}
Living-off-the-land abuse sits under ATT&CK's System Binary Proxy Execution (T1218), with named sub-techniques for the specific binaries this hunt watches.{{< cite 5 >}} LOLBAS is the community-maintained reference both red teams and defenders actually use — genuinely load-bearing, not decorative, since it's where your binary list should come from.{{< cite 6 >}} Red Canary's detection reporting and Intel 471's hunting guidance converge independently on the same point: individual LOLBin usage is mostly benign, so it's combinatorial rarity that separates signal from noise. Two independent vendors reaching the same conclusion separately is meaningfully stronger evidence than either alone — the convergence itself is what's worth trusting.
{{< /callout >}}

### 5. Dormant Account Reactivation

*Reactivation as a hazard-rate problem, not a threshold problem*

A compromised credential often sits dormant before reuse. The hard part is separating that from an employee back from two months of leave — and the honest framing of "how long has it been dormant" is a censored-duration problem, not a static threshold.

```
for each account:
    T = days_since_last_login  # a duration, i.e. a survival-analysis quantity
    if T > 60:
        p_geo = categorical_likelihood(new_login.geo, user_history, laplace_smoothed)
        p_dev = categorical_likelihood(new_login.device, user_history, laplace_smoothed)
        if p_geo < tau AND p_dev < tau AND privileged_action_within(60, "minutes"):
            flag high priority
```

Treating `days_since_last_login` as a plain number discards its actual statistical nature: it's a duration until an event, exactly the object of study in {{< term def="A branch of statistics studying time-until-event data -- originally time-until-death in medicine, equally applicable to time-until-reactivation, time-until-persistence-trigger, or time-until-telemetry-loss. Handles the fact that some observations are 'censored' (still ongoing)." label="survival analysis" >}}survival analysis{{< /term >}}, the same machinery used for time-to-failure and time-to-relapse modeling. That framing matters because it naturally handles right-censoring — accounts still dormant at observation time haven't "failed to reactivate," they simply haven't yet, a distinction a naive threshold silently gets wrong. Geography and device novelty are better modeled as likelihoods under a per-user categorical distribution with Laplace smoothing than as a binary "is this new" flag, since smoothing prevents a user's first-ever value in any category from being assigned zero probability and treated as infinitely surprising — a common and avoidable failure mode in naive novelty scoring.

{{< callout label="READING THE SOURCING" >}}
This exact pattern — a dormant account adding or updating an MFA method immediately before reactivating — is a documented Microsoft Sentinel UEBA hunting pattern, grounded in what a detection vendor's own engineering team chose to build a rule around, not a hypothesis. AIMultiple's UEBA research and Sumo Logic's baselining writeup independently converge on 90 days as the point where individual login-time and access patterns become reliable — two sources landing on the same number independently is worth more than either alone.{{< cite 7 >}} Read the Sumo Logic figure knowing they sell a SIEM built to do exactly this baselining; the number still looks reasonable, the enthusiasm around it should be discounted accordingly.
{{< /callout >}}

### 6. Certificate / JA3 Infrastructure Reuse

*Fingerprinting the handshake, not the address -- and knowing when that stops working*

Attackers rotate IPs and domains cheaply. They rotate TLS client behavior and certificate issuance patterns far less often, which makes handshake-level fingerprinting stickier across infrastructure moves spaced months apart.

```
build historical index of (ja3, ja3s, cert_serial, cert_issuer_cn, cert_subject_cn)
for each new TLS session:
    match fingerprint against watchlist AND "seen but unresolved" set
    if match found after gap > 30 days:
        flag reappearance
    fuzzy-match cert subject CN against known patterns (typosquat detection)
```

The reason this survives infrastructure churn: {{< term def="A method for fingerprinting a TLS client (JA3) or server (JA3S) by hashing specific fields of its handshake -- cipher suites, extensions, elliptic curves -- in the order the client offers them, producing a fingerprint tied to the client software rather than its network location." label="JA3 / JA3S" >}}JA3{{< /term >}} fingerprints the TLS negotiation itself, a property of the client software, not of where the traffic is routed. Stated plainly for a current audience: JA3 alone is a weakening signal against modern TLS stacks that randomize ClientHello extension order specifically to defeat it (a technique popularized by uTLS and now default in several mainstream browsers for unrelated privacy reasons, with the side effect of degrading JA3's discriminative power). {{< term def="The successor fingerprinting scheme to JA3, designed to be more resistant to extension-order randomization and to cover additional protocol layers (JA4S, JA4H, JA4X, etc.) beyond the original TLS-only scope." label="JA4" >}}JA4{{< /term >}} is the current-generation successor built specifically to be more resistant to that randomization, and any real deployment of this hunt built recently should treat JA4 as the primary fingerprint family, with JA3 retained for backward comparability against older watchlist entries rather than as the frontline signal.

{{< callout label="READING THE SOURCING" >}}
JA3/JA3S was introduced by Salesforce's own engineering team specifically to fingerprint the handshake rather than the network location behind it, with published examples for Tor, Trickbot, and Meterpreter demonstrating durability across infrastructure moves — the primary source, from the people who built it.{{< cite 8 >}} Carbon Black documents JA3/JA3S as a native netconn field, useful less as evidence the technique works and more as a practical note on where you'd find this data in that specific product.{{< cite 9 >}} Recent reporting on ANY.RUN's frequency analysis is a currency check — that the signal is still active today — rather than foundational evidence, since it's aggregated commentary on someone else's platform data.
{{< /callout >}}

### 7. Long-Lived Persistence Artifacts

*The creation-to-trigger gap as an empirical hazard function*

A scheduled task created once and left inert for a month before firing is a specific, recognizable persistence shape — planted during initial access, triggered later, possibly well after any initial-access alert has scrolled off a dashboard.

```
for each persistence artifact created (task, service, run-key):
    record creation_timestamp
    on first execution: gap = execution_timestamp - creation_timestamp
    accumulate gap distribution across the fleet; fit Weibull(k, lambda)
    if gap > adaptive_threshold(fitted_distribution, percentile=95):
        flag as delayed-trigger persistence
```

A fixed 30-day cutoff is a reasonable starting heuristic and also an arbitrary one; the gap-time histogram this hunt already produces is, mathematically, an empirical estimate of a {{< term def="In survival analysis, the instantaneous rate at which an event occurs given it hasn't occurred yet -- here, the rate at which a dormant artifact fires, as a function of how long it's already been dormant." label="hazard function" >}}hazard function{{< /term >}}, and fitting a parametric duration model (Weibull is the standard choice for time-to-failure data with a shape parameter that can represent either front-loaded or back-loaded trigger risk) to that distribution yields an adaptive, environment-specific threshold rather than one borrowed wholesale from someone else's fleet. This is the same underlying mathematical object as Hunt 5's dormancy problem and Hunt 14's coverage-gap problem below — a recurring structure worth noticing once, not three unrelated techniques.

{{< callout label="READING THE SOURCING" >}}
Scheduled task persistence is ATT&CK T1053, with the Windows sub-technique (T1053.005) singled out as one of the most abused built-in components across commodity and nation-state intrusions alike.{{< cite 10 >}} Mandiant's M-Trends reporting is cited as finding scheduled tasks in a large share of Windows-based compromises — an incident-response vendor's own caseload, real signal about what they've actually seen, not a random sample of all intrusions everywhere; a firm serving particular verticals sees a caseload shaped by those verticals. ManageEngine's writeup on ATT&CK persistence makes the durability argument (surviving patching and credential rotation) that actually justifies a long window over alerting only at creation.
{{< /callout >}}

### 8. DNS Tunneling / Entropy Drift

*Why raw entropy alone flags every CDN on your network*

A throttled tunneling channel still shows two aggregate trends it can't suppress across a season: query volume rises because there's more payload to move, and label structure drifts away from natural-language shape because encoded payload doesn't follow it.

```
train char-level Markov model M on a corpus of known-legitimate hostnames
for each queried label per host, per week:
    likelihood_ratio = P(label | M_legitimate) / P(label | M_uniform)
    track weekly mean(likelihood_ratio) and weekly query_volume
    if likelihood_ratio_trend decreasing AND volume_trend increasing over 8+ weeks:
        flag as possible tunneling channel
```

Raw Shannon entropy per label is the naive version of this hunt, and it has a specific, well-known failure mode: legitimate CDN and cache-busting subdomains are frequently high-entropy by design (content hashes, cache keys), so a bare entropy threshold flags enormous amounts of ordinary infrastructure. A character-level Markov model trained on known-legitimate hostnames gives a proper {{< term def="The ratio of how probable an observation is under one model versus another -- here, how much more (or less) a queried hostname looks like natural hostname structure versus looking like uniformly random characters, a sharper test than a single entropy number." label="likelihood ratio" >}}likelihood ratio{{< /term >}} test: it's not "is this string high-entropy," it's "does this string's character-transition structure look like the training corpus of real hostnames, or does it look like base32/base64 payload wearing a hostname's shape." That distinction is what separates a tunneling channel from a hash-based CDN key, and entropy alone cannot make it.

{{< callout label="READING THE SOURCING" >}}
DNS tunneling maps to ATT&CK T1071.004, and Microsoft Sentinel's own published hunting query for this technique uses this hunt's identical approach — 90 days of A/TXT records, scanning for unusually long hostnames and distinct-query-name counts per client — citing a real Palo Alto Networks Unit 42 case as justification. That's close to the strongest sourcing available for a specific technique: a major vendor's own shipped hunting logic, grounded in a named incident from an independent research team. SafeDNS's ATT&CK-version mapping makes the same underlying point about DNS as a persistent channel precisely because tunneling throttles to survive short-window detection — reinforcement of the same reasoning, not a second independent test of it.
{{< /callout >}}

### 9. Peer-Group Deviation in Data Access

*Why z-scores on count data quietly lie to you*

One person's file-access volume creeping up 20% over six months looks like nothing against their own noisy history. It looks very different against the average of forty peers doing the same job — the correct reference population for this comparison in the first place.

```
group users by role/department
for each user, each month:
    # counts of files/bytes are not Gaussian -- use deviance under Negative Binomial, not z-score
    deviance = neg_binomial_deviance(user_count, peer_group_mu, peer_group_dispersion)
    if deviance > threshold for 2+ consecutive increasing months:
        flag for review, with FDR correction across the full user population tested monthly
```

File-access counts are count data with a long right tail — a handful of power users generate most of the volume — and a z-score computed against a Gaussian assumption systematically misjudges tail risk in exactly this shape of distribution. A {{< term def="A discrete probability distribution for count data that, unlike the Poisson distribution, allows variance to exceed the mean -- the realistic case for human behavioral counts, which are almost always 'overdispersed' relative to a naive Poisson model." label="negative binomial distribution" >}}negative binomial{{< /term >}} deviance test is the standard, better-fitting alternative for overdispersed count data, and — as in Hunt 2 — running this test across an entire user population every month is again a multiple-comparisons problem requiring FDR correction, not a one-off test that gets to skip it just because the underlying question feels qualitatively different from novel-domain detection.

{{< callout label="READING THE SOURCING" >}}
This is standard User and Entity Behavior Analytics methodology — the phrase names an entire product category, not one team's idea. Sumo Logic explicitly recommends peer-group baselining alongside individual baselining for the reason above: an individual-only baseline can't distinguish "always noisy" from "newly noisy relative to peers." AIMultiple's UEBA research cites a real deployment where CASB-plus-UEBA caught a user downloading 2,000-plus files and uploading 400-plus to a personal cloud account — a genuinely concrete result, and also exactly the kind of anecdote a firm covering the UEBA market has an interest in publishing. Read it as "this pattern caught something real at least once," not "this pattern reliably catches insider risk," a claim the anecdote alone doesn't support.
{{< /callout >}}

### 10. Seasonal / Cyclical Campaign Correlation

*Decomposition before spike-hunting, and the honesty a single cycle demands*

Phishing and credential-stuffing waves cluster around calendar events — tax season, fiscal year-end, open enrollment — because that's when a phish about a W-2 or benefits enrollment gets the best click-through. Invisible with under a year of history, because you need at least one full cycle to distinguish recurrence from coincidence.

```
decompose weekly alert_type counts: STL(trend, seasonal, residual)
identify residual spikes exceeding k * robust_sigma(residual)
cross-reference spike weeks against calendar events
if same calendar point spikes across 2+ years: flag as confirmed seasonal, not merely suspected
```

{{< term def="Seasonal-Trend decomposition using Loess -- a method for splitting a time series into trend, seasonal, and residual (noise) components, so a spike can be judged against the residual specifically rather than against raw, seasonally-confounded values." label="STL decomposition" >}}STL decomposition{{< /term >}} — Seasonal-Trend decomposition via Loess — separates a genuine seasonal effect from trend and noise before you go looking for spikes, which is a materially different (and more defensible) procedure than eyeballing raw weekly counts for statistically significant bumps against an annual mean that itself contains the seasonal signal you're trying to detect. And the honest limitation stands regardless of the decomposition method: one year of data gives exactly one observation per calendar event. "This spiked last March, consistent with a tax-season phish wave" is a hypothesis awaiting a second data point, not a confirmed cycle — say so explicitly in your own findings rather than let a single coincidence read as an established pattern.

{{< callout label="READING THE SOURCING" >}}
This hunt applies the TaHiTI framework — Targeted Hunting integrating Threat Intelligence — building on the Sqrrl hunting loop's practice of feeding findings back into future intelligence work.{{< cite 11 >}} The underlying claim — calendar-anchored business events produce recurring campaigns — is documented broadly across phishing and credential-stuffing threat reporting rather than resting on one source, which is the right shape of evidence for a claim this general: no single vendor owns "attackers time phishing around tax season," and no one citation should be expected to carry it alone.
{{< /callout >}}

### 11. Slow Lateral Spread of a Rare Binary

*Host-count-over-time as an empirical infection curve*

A hash that's globally rare and appears on one additional host every week or two isn't sitting still — it's propagating, slowly enough that a single-day snapshot only shows "a rare file exists somewhere," and only a longitudinal host count reveals movement.

```
for each newly-observed rare hash (global prevalence below threshold):
    track host_count(t) weekly since first appearance
    fit logistic diffusion curve: host_count(t) = K / (1 + exp(-r*(t - t0)))
    if fit quality (R2) is high AND r > threshold:
        flag as actively spreading, report r as comparable spread-rate metric
```

A monotonic-increase test answers only "is this spreading." Framing the host-count series explicitly as an {{< term def="Mathematical models (SIR, logistic/Bass diffusion) originally developed to describe how a disease or innovation spreads through a population over time, directly reusable for describing how a file or technique spreads across a host population." label="epidemiological diffusion model" >}}epidemiological diffusion curve{{< /term >}} — logistic or SIR-style — and fitting it gives a spread-rate parameter (`r` above) that's directly comparable across incidents, which "monotonically increasing" alone never provides. That comparability is what lets an analyst say "this is spreading twice as fast as the incident from March" rather than "this is also spreading," a materially more useful statement when prioritizing response.

{{< callout label="READING THE SOURCING" >}}
File/hash prevalence is a long-standing enrichment signal in EDR tooling. Microsoft's own published KQL hunting queries for Defender for Endpoint use the `FileProfile` function to filter for low-global-prevalence executables (rare ISO/LNK files) as an initial-access and persistence indicator — a detection vendor's own shipped logic, not a third party's theory about how their product should work.{{< cite 12 >}} OPSWAT's prevalence-search documentation frames rarity explicitly as a pivot point for infrastructure reuse and campaign clustering, confirming this is a recognized, named technique in the field rather than an invention for this document.
{{< /callout >}}

### 12. Long-Term ASN Reputation Drift

*Adoption-curve shape as the actual discriminator*

Bulletproof-hosting operators rotate IPs constantly and shift upstream ASN relationships far less often, since those require actual business arrangements to establish. A year of ASN-level data exposes adoption patterns a 30-day window reads as unrelated individual connections.

```
aggregate outbound connections by destination ASN, monthly
model each ASN's monthly unique-host count as an adoption curve
if curve shape resembles a step function (centrally pushed) rather than power-law-gradual (organic):
    flag as possible mass rollout / supply-chain compromise
cross-check ASN ownership history and recent abuse reports
```

The actual statistical discriminator worth naming explicitly: organic infrastructure adoption — a new CDN, a new SaaS vendor — tends to follow a gradual, roughly power-law adoption curve as independent teams onboard on their own schedules. A near step-function jump from near-zero to broad internal adoption in a short window is a different generative process — something pushed centrally rather than adopted independently — and that's the shape difference this hunt should actually be testing for, not merely "did the count go up a lot."

{{< callout label="READING THE SOURCING" >}}
Tracking C2 infrastructure at the ASN level against bulletproof hosting is documented technique — Censys's research on tracking bulletproof hosting and abused RDP infrastructure, and Intel 471's writeup on a specific hosting provider's client relationships, both describe deliberate ASN-shifting to evade IP blocklists.{{< cite 13 >}} Silent Push's research on one hosting group's post-sanctions ASN migration is a concrete, named example of exactly this pattern — a real case, not a hypothetical, though it's one case rather than a general study of frequency across the threat landscape.{{< cite 14 >}}
{{< /callout >}}

### 13. Authentication Anomaly Baselines

*Per-user likelihood, not fleet-wide velocity rules*

Naive impossible-travel logic generates enough false positives from VPNs and mobile roaming that most teams tune it into uselessness. A 90-plus day per-user baseline asks a sharper question: not "is this new," but "how rare is this specifically for this person's own history."

```
for each user:
    build (country, ASN, device) categorical distribution, Laplace-smoothed, 90-day window
    for each new login: score = -log( P(observed_tuple | user_distribution) )
    flag logins in bottom percentile of likelihood, conditioned on travel-calendar exceptions
```

Two users logging in from a new country tomorrow are not the same event. For a frequent traveler whose baseline already contains a dozen countries, it's routine. For someone whose baseline contains one, it's genuinely rare. A shared distance/velocity rule can't distinguish these; a per-user likelihood model can, because it conditions on that specific person's own history rather than a fleet-wide threshold. The remaining confound — legitimate travel and VPN exceptions — is a {{< term def="When the distribution of inputs changes between training and deployment (or over time) in a way the model wasn't built to account for -- here, a person's genuinely changed travel pattern that a static historical baseline has no way to anticipate." label="covariate shift" >}}covariate shift{{< /term >}} problem the base model cannot solve on its own; it requires exogenous conditioning (a travel calendar, VPN exception list) layered on top, which functionally makes this a hierarchical rather than a flat per-user model.

{{< callout label="READING THE SOURCING" >}}
Multiple independent writeups converge here — Abnormal AI's impossible-travel research, ManageEngine's SIEM documentation, and WorkOS's Radar analysis all separately argue pure rule-based impossible travel is too noisy without behavioral baselining and device/IP reputation layered on top. Three identity-security vendors reaching the same conclusion independently is meaningfully stronger than any one alone, and it aligns with SANS guidance treating UEBA-style baselining as the modern replacement for static velocity checks, not merely a supplement to them.
{{< /callout >}}

### 14. Endpoint Coverage Gap Hunting

*Monitoring the reporting process itself as a point process*

A host that quietly stops sending meaningful telemetry while its sensor shows "connected" is a blind spot regardless of cause. You can only see the gap by knowing that host's own expected reporting cadence, then noticing a deviation from it.

```
for each host:
    expected = rolling_median(daily_event_volume, window=180)
    if actual_volume < 0.10 * expected for 3+ consecutive days:
        flag as coverage gap
    test observed inter-report gaps against expected point-process interarrival distribution
    cross-reference gap period against alerts immediately before/after
```

This is structurally the same object as Hunts 5 and 7 above: a {{< term def="A random process describing events occurring in time (or space) -- here, the sequence of telemetry reports from a host. Its expected inter-arrival distribution is exactly the thing to test observed gaps against for anomalous silence." label="point process" >}}point process{{< /term >}} whose inter-event timing you're modeling and testing for an anomalous gap, the same underlying mathematics as time-to-reactivation and time-to-trigger, just applied to the reporting pipeline instead of an account or an artifact. Naming that recurrence explicitly is worth more than treating these as three separate ad hoc heuristics, because it means one well-built duration-testing library covers all three hunts rather than three independent implementations.

{{< callout label="READING THE SOURCING" >}}
EDR tampering and telemetry blind spots are documented in academic literature — an empirical study of EDR blind spots against APT-style attack vectors is a peer-reviewed treatment, distinct from a vendor's marketing framing of the same idea.{{< cite 15 >}} LimaCharlie's operational approach to "detecting silent sensors" — comparing last-seen timestamps against expected reporting cadence — is precisely this hunt's method, described by a vendor building tooling around it: useful for the how, worth remembering it doubles as a sales pitch for that tooling.{{< cite 16 >}}
{{< /callout >}}

### 15. Long-Horizon TTP Recurrence (MITRE Mapping Drift)

*A multivariate control-chart problem dressed as a counting problem*

Any single alert mapped to a technique might not justify escalation alone. Three or four related techniques in the same kill-chain stage all spiking above their trailing baseline in the same month is a different claim entirely, and a per-technique univariate view will never surface it, because no individual technique in the cluster looks unusual by itself.

```
for each MITRE technique_id: maintain monthly count vector x_t across all techniques
compute trailing covariance-aware baseline (not per-technique moving average in isolation)
T2 = (x_t - mu)' * Sigma_inv * (x_t - mu)     # Hotelling's T-squared statistic
if T2 exceeds control limit AND 3+ techniques in same kill-chain stage contribute:
    flag as possible coordinated campaign build-up
```

"Current month > 2x trailing average, per technique" is a univariate rule applied independently across many correlated variables, and it discards exactly the information that makes a coordinated build-up detectable: correlation structure across techniques. {{< term def="A multivariate generalization of the t-test / control chart, accounting for correlations between multiple simultaneously-monitored variables -- the standard tool in statistical process control for detecting a joint deviation that no single variable's own control chart would flag." label="Hotelling's T-squared" >}}Hotelling's T²{{< /term >}} is the standard multivariate control-chart statistic for exactly this situation: a joint deviation across correlated variables that no individual variable's own control limit would catch, which is the actual rigorous version of "three or four techniques trending together," rather than an ad hoc conjunction of independent per-technique thresholds.

{{< callout label="READING THE SOURCING" >}}
Mapping detections to ATT&CK technique frequency over time is widely adopted practice for maturing a hunting program — the Alerting and Detection Strategies framework and MITRE's own Cyber Analytics Repository are both built around tracking technique coverage rather than isolated alerts, the standard-setting body's own framing.{{< cite 17 >}} Vectra's public research on correlating behaviors across hosts and mapping them to ATT&CK and NIST CSF describes this as the durable way to separate a coordinated campaign from routine noise — read with the usual discount for a vendor describing the value of the category of product it sells.{{< cite 18 >}}
{{< /callout >}}

## Four Recurring Structures

Read back across the fifteen, the actual mathematical surface area is much smaller than fifteen distinct techniques suggests. Nearly everything above reduces to one of four recurring structures, and recognizing which one you're building lets you reuse the same tooling and the same failure-mode intuition across hunts that look unrelated on the page.

1. **Duration / hazard modeling** — Hunts 5, 7, and 14. All three ask "how long until an expected event, and is this instance's timing anomalous." One survival-analysis library, three applications.
2. **Multiple-hypothesis-corrected anomaly scoring** — Hunts 2 and 9, and implicitly anything run per-host or per-user across a real fleet every day. Any hunt evaluated on a large population repeatedly needs false-discovery-rate control or its output volume swamps triage capacity regardless of how good the underlying signal is.
3. **Trend / regime-change detection over an aggregate series** — Hunts 3, 8, and 10. Robust slope-fitting plus a structural-break test, applied to bytes, entropy, or alert counts respectively.
4. **Diffusion / adoption-curve fitting** — Hunts 11 and 12. Both are, underneath, "is this population-level curve shaped like organic spread or like something pushed."

None of the fifteen needed inventing from scratch — each maps onto an existing, well-studied statistical structure. The actual engineering work is building four reusable primitives, not fifteen bespoke queries.

## Agentic Execution: Who's Actually Running the Loop

None of the above addresses who — or what — actually executes these hunts day to day, and that question has gotten sharper rather than more settled as agentic tooling has become standard infrastructure rather than a research curiosity. Worth treating on its own terms, since the risk profile changes qualitatively, not just quantitatively, once a hunt moves from "a scheduled query a human reviews" to "an agent that plans its own next query based on what it just found."

**The autonomy spectrum, stated precisely.** It's worth naming four distinct tiers rather than treating "AI-assisted" as one category:

- **Level 0 — deterministic scheduled query.** A cron job running fixed logic (most of the pseudocode above, as written). No model in the loop at inference time; all judgment was frozen in at authoring time.
- **Level 1 — single-shot classifier or explainer.** A model scores or explains pre-computed candidates in one call — the hunt-by-hunt AI angles implied throughout this document (summarize, explain, suggest a mapping) are all Level 1 by design. The model never queries the data store itself and never sees its own prior output as input to a further decision.
- **Level 2 — tool-using agent, {{< term def="An agent pattern (Yao et al., 2022) interleaving explicit reasoning steps with tool calls and their observed results, each feeding the next reasoning step -- the dominant pattern behind modern 'agentic' tool use, as opposed to a single-shot prompt-and-response." label="ReAct (Reason + Act)" >}}ReAct-style{{< /term >}} iteration.** The agent reasons, calls a tool (a query, an enrichment lookup), observes the result, and reasons again — genuinely investigating rather than scoring a fixed input. This is where dashboard-building tools generally sit once they move past templated alerting.
- **Level 3 — autonomous responder.** The agent can also act on the environment — isolate a host, disable an account, suppress an alert — without a human approving each step.

**The specific failure mode Level 2 introduces, and Level 1 structurally cannot.** A single-shot classifier is isolated by construction: it sees the input, produces an output, and that's the entire interaction. A multi-step agent is, by design, conditioned on everything it concluded in earlier steps of the same trace — and that is precisely the mechanism that makes early, wrong conclusions self-reinforcing. An agent that decides in step two "this looks like a benign backup job" can spend every subsequent tool call gathering evidence consistent with that framing rather than adversarially testing it, because nothing in a standard ReAct loop forces the later steps to treat the earlier reasoning as anything other than established context. This is confirmation bias implemented as an inference procedure, not a hypothetical edge case — it is the default behavior of an unconstrained multi-step agent, and it gets worse, not better, as the underlying model gets more fluent at constructing a coherent-sounding narrative around its own earlier framing.

The mitigation is not "use a smarter model." It's structural: grade the agent's *trace*, not just its final answer, and do so from a fresh context with no visibility into the reasoning that produced it — the same isolation discipline this site applies to a person grading a source document applies with more force to an agent grading its own multi-step investigation, precisely because the agent's self-narrative is the thing most likely to be internally consistent and evidentially hollow at the same time. A rotating adversarial pass — a second, independent agent instance whose only job is "does this trace's final claim actually follow from the tool outputs it collected, or does it follow from the framing established two steps in" — catches exactly the failure a single agent auditing its own work cannot, for the identical reason a person can't proofread their own overclaim by rereading it with the same assumptions that produced it.

**Memory poisoning across runs is the same failure, extended in time.** If an agent's findings get written back into a shared context or knowledge base that a later, separate agent run treats as ground truth, one early wrong conclusion becomes self-reinforcing not just within a trace but across the program's entire operational history — structurally identical to an unsourced claim propagating through successive citations until nobody can find the original observation behind it. Any agentic pipeline that accumulates its own memory across runs needs an explicit answer to "how does a wrong belief get corrected once it's in the shared context," and "the next run will probably notice" is not an answer, because the next run inherits the same contaminated prior the first run wrote.

**What this means concretely for the fifteen hunts above.** Score candidates at Level 1 — high leverage, low fabrication surface, because there's no multi-step self-conditioning to go wrong. Reserve Level 2 for narrow, naturally idempotent sub-tasks — WHOIS lookups, reputation enrichment, ASN ownership history — where iterative investigation adds real value and the tasks are closer to fact retrieval than to open-ended reasoning about ambiguous evidence. Do not run Level 3 against anything that reduces logging, isolation, or containment capability without a human approving the specific action, on the straightforward argument that an agent's own mistaken risk assessment can become the actual security incident, and an autonomous system that can both misjudge a threat and act on that misjudgment has no remaining check between the two.

## What This Is Actually For

None of these fifteen are a checklist. They're a menu you pick two or three items off of, and the selection criterion isn't "which is the most interesting attack pattern" — it's "which of these catches something my short-term alerting structurally cannot, badly enough that it's worth paying to retain the data for." A beacon with a 90-day signature and a dormant-account reactivation with a 60-day lookback are not equally worth building if your environment has never had an insider-risk incident and gets probed by C2 constantly. Read the fifteen, throw out the ones that don't match your actual threat model, and budget storage for what's left before writing a single production query.

The second thing worth carrying forward isn't a hunting technique at all — it's the habit this document tried to model in every "reading the sourcing" box, and it applies with more force, not less, the moment an agent is the one drafting your hunt logic. Fifteen technically plausible hunts and a wall of real citations is exactly what a capable model produces when tasked with researching this space. What generating the list cannot do is sort a framework's own structural definition from a vendor's case study from one peer-reviewed result standing alone — that sorting was never a question the generation step could answer, and it's still yours to do, every time, before anything gets wired into a production dashboard or handed to an agent with tool access.

*Draft. Voice, structure, and the glossary-tooltip mechanism above are all first attempts on this site's Academics section — flag anything unclear and we'll turn it into a proper teaching point rather than a hover tooltip bolted on after the fact.*

## References

<ol class="refs">
<li id="ref1">MITRE ATT&CK. "Application Layer Protocol" (T1071) &amp; DNS sub-technique (T1071.004). <a href="https://attack.mitre.org/techniques/T1071/">attack.mitre.org/techniques/T1071</a></li>
<li id="ref2">MITRE. "BZAR" — Zeek scripts mapped to ATT&CK. <a href="https://github.com/mitre-attack/bzar">github.com/mitre-attack/bzar</a></li>
<li id="ref3">SANS. "Run, Can't Hide: Real-Time Threat Hunting via Passive DNS." <a href="https://sans.org/webcasts/run-cant-hide-real-time-threat-hunting-passive-dns-102857">sans.org/webcasts/…-102857</a></li>
<li id="ref4">Sharma, A., Joshi, A., Finin, T. "Detecting Data Exfiltration by Integrating Information Across Layers." <em>IEEE IRI</em>, 2013. <a href="https://ebiquity.umbc.edu/paper/html/id/625">ebiquity.umbc.edu/paper/html/id/625</a></li>
<li id="ref5">MITRE ATT&CK. "System Binary Proxy Execution" (T1218). <a href="https://attack.mitre.org/techniques/T1218/">attack.mitre.org/techniques/T1218</a></li>
<li id="ref6">LOLBAS Project. <a href="https://lolbas-project.github.io/">lolbas-project.github.io</a></li>
<li id="ref7">AIMultiple. "UEBA Use Cases." <a href="https://research.aimultiple.com/ueba-use-cases">research.aimultiple.com/ueba-use-cases</a>; Sumo Logic. "UEBA SIEM Use Cases: Insider Threat." <a href="https://www.sumologic.com/blog/ueba-siem-use-cases-insider-threat.md">sumologic.com/blog/…</a></li>
<li id="ref8">Salesforce Engineering. "TLS Fingerprinting with JA3 and JA3S." <a href="https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967/">engineering.salesforce.com/…</a></li>
<li id="ref9">Carbon Black EDR documentation, TLS/JA3 fingerprinting. <a href="https://docs.vmware.com/en/VMware-Carbon-Black-EDR/7.8.0/vmw-cb-edr-ug/GUID-936FD1EB-3739-4A83-AFF8-AB10E661677C.html">docs.vmware.com/…</a></li>
<li id="ref10">MITRE ATT&CK. "Scheduled Task/Job" (T1053). <a href="https://attack.mitre.org/techniques/T1053/">attack.mitre.org/techniques/T1053</a></li>
<li id="ref11">Expel. "What are threat hunting frameworks?" <a href="https://expel.com/cyberspeak/what-are-threat-hunting-frameworks">expel.com/…</a>; TechTarget. "Threat hunting frameworks, techniques and methodologies." <a href="https://www.techtarget.com/cybersecurity/tip/Threat-hunting-frameworks-techniques-and-methodologies">techtarget.com/…</a></li>
<li id="ref12">Microsoft KQL hunting query examples. <a href="https://kqlsearch.com/">kqlsearch.com</a></li>
<li id="ref13">Censys. "Hiding in Plain Sight: Tracking Bulletproof Hosting and Abused RDP Infrastructure." <a href="https://censys.com/?p=4093">censys.com/?p=4093</a></li>
<li id="ref14">Silent Push. Aeza Group ASN migration research. <a href="https://www.silentpush.com/?p=13104">silentpush.com/?p=13104</a></li>
<li id="ref15">"An Empirical Study on Evading Endpoint Security." <em>arXiv:2108.10422</em>. <a href="https://arxiv.org/abs/2108.10422">arxiv.org/abs/2108.10422</a></li>
<li id="ref16">LimaCharlie. "Detecting Silent Sensors: Identifying EDR Telemetry Gaps." <a href="https://limacharlie.io/blog/detect-silent-sensors-edr-telemetry-gaps-with-limacharlie">limacharlie.io/…</a></li>
<li id="ref17">MITRE. "Cyber Analytics Repository." <a href="https://car.mitre.org/">car.mitre.org</a></li>
<li id="ref18">Vectra. Botnet/beaconing detection practitioner's guide. <a href="https://www.vectra.ai/topics/botnet-detection-techniques">vectra.ai/topics/botnet-detection-techniques</a></li>
</ol>

Sources named above without a link (RITA, Juniper Threat Labs, Elastic's ML detection, Plixer, Darktrace, Red Canary, Intel 471's general guidance and TA505 writeup, Microsoft Sentinel's dormant-account and DNS-tunneling patterns, Mandiant M-Trends, ManageEngine, cybersecuritynews.com's ANY.RUN coverage, SafeDNS, OPSWAT, Abnormal AI, WorkOS, general SANS identity guidance, Bitdefender, and Yao et al.'s ReAct paper) were referenced narratively in the source material without an accompanying URL, or are named for a well-known concept rather than a specific document. Naming them without a link is the honest version of citing them — inventing a URL to look more complete than the source material supports would be exactly the kind of fabrication this site's classification work exists to prevent, applied here even though nothing in this piece is tagged or graded.
