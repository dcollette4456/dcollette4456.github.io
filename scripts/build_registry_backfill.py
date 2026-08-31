#!/usr/bin/env python3
"""
One-time backfill: register every source cited across the published issues,
in the backfill pool, with an admission record. Per CLAUDECODEBRIEF §9.

This does NOT fetch any URL and does NOT mint claims. It registers sources
so classification spec §21 admission (including the impersonation
near-match check) runs against them, per the brief's explicit instruction
to do registry + admission first and evidence capture as a separate pass.

`origin` is set only where the ccTLD or the publisher is unambiguous
(a US federal agency, a .co.kr/.or.kr/.co.uk domain). Everywhere else it
is left absent rather than guessed, per the brief's "never invent a
value" rule -- company headquarters for a mid-size vendor blog is not
something this script can respectably claim to know.

Run with: python3 scripts/build_registry_backfill.py
Writes data/sources/registry.json. Idempotent: re-running recomputes the
whole file from this source table rather than appending.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

# (url, canonical_name, type, origin_or_None, cited_in_serial)
CITATIONS = [
    ("https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a", "CISA Cybersecurity Advisories", "GOV", "US", "TI-20260811-001"),
    ("https://www.extrahop.com/blog/aoa-iranian-affiliated-actors-target-u-s-critical-infrastructure-through-plcs", "ExtraHop", "VND", "US", "TI-20260811-001"),
    ("https://www.kelacyber.com/blog/irans-apts-and-the-us-enterprise-in-2026-muddywater/", "KELA Intelligence", "VND", None, "TI-20260811-001"),
    ("https://www.washingtonpost.com/national-security/2026/07/30/us-spy-agencies-suspect-iran-launched-cyberattack-minnesota-water-facilities/", "The Washington Post", "MED", "US", "TI-20260811-001"),
    ("https://www.rescana.com/post/rustywater-iranian-muddywater-apt-targets-israeli-government-and-infrastructure-with-advanced-rust", "Rescana", "VND", None, "TI-20260811-001"),
    ("https://www.safebreach.com/blog/cisa-aa26-097a-iranian-plc-exploitation-safebreach-coverage/", "SafeBreach", "VND", "US", "TI-20260811-001"),
    ("https://socradar.io/blog/iranian-hackers-plc-us-critical-infrastructure/", "SOCRadar", "VND", None, "TI-20260811-001"),
    ("https://www.techtimes.com/articles/321335/20260723/iranian-hackers-infiltrate-siemens-schneider-plcs-blinding-operators-fake-readings.htm", "Tech Times", "MED", "US", "TI-20260811-001"),
    ("https://www.trellix.com/blogs/research/the-iranian-cyber-capability-2026/", "Trellix", "VND", "US", "TI-20260811-001"),

    ("https://www.bleepingcomputer.com/news/security/lazarus-hackers-exploited-windows-zero-day-to-target-defense-firms/", "BleepingComputer", "MED", "US", "TI-20260822-002"),
    ("https://www.cryptopolitan.com/did-north-korea-hackers-attack-arrayref/", "Cryptopolitan", "MED", None, "TI-20260822-002"),
    ("https://cypro.co.uk/insights/cyber-bulletins/windows-ancillary-function-0-day-cisa-confirms-exploited-flaw/", "CyPro", "VND", "UK", "TI-20260822-002"),
    ("https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/", "Rust Security Response Team", "NPO", "US", "TI-20260822-002"),
    ("https://www.infosecurity-magazine.com/news/north-korean-rust-supply-chain/", "Infosecurity Magazine", "MED", "UK", "TI-20260822-002"),
    ("https://www.wiz.io/blog/rust-supply-chain-attack-on-arrayref-significant-overlap-with-dprk-campaigns", "Wiz", "VND", "US", "TI-20260822-002"),
    ("https://radar.offseq.com/threat/rust-supply-chain-attack-linked-to-north-korean-hackers-0ce7936d030d6a11", "OffSeq Threat Radar", "VND", None, "TI-20260822-002"),
    ("https://rewterz.com/threat-advisory/windows-afd-sys-zero-day-exploited-by-lazarus-active-iocs", "Rewterz", "VND", None, "TI-20260822-002"),
    ("https://www.securityweek.com/rust-supply-chain-attack-linked-to-north-korean-hackers/", "SecurityWeek", "MED", "US", "TI-20260822-002"),
    ("https://thehackernews.com/2026/08/rust-supply-chain-attack-puts-build.html", "The Hacker News", "MED", None, "TI-20260822-002"),
    ("https://thehackernews.com/2026/08/lazarus-exploits-windows-zero-day-to.html", "The Hacker News", "MED", None, "TI-20260822-002"),

    ("https://socradar.io/blog/doublecup-clickfix-loader-devicemanager-rats/", "SOCRadar", "VND", None, "TI-20260830-002"),
    ("https://www.bleepingcomputer.com/news/security/new-doublecup-clickfix-service-hides-malware-in-browser-cache-images/", "BleepingComputer", "MED", "US", "TI-20260830-002"),
    ("https://thehackernews.com/2026/08/doublecup-uses-clickfix-and-cached-pngs.html", "The Hacker News", "MED", None, "TI-20260830-002"),
    ("https://securityboulevard.com/2025/10/threat-actors-weaponizing-open-source-adaptixc2-tied-to-russian-underworld/", "Security Boulevard", "MED", "US", "TI-20260830-002"),

    ("https://asec.ahnlab.com/en/94696/", "AhnLab ASEC", "VND", "KR", "TI-20260809-001"),
    ("https://www.aljazeera.com/economy/2026/8/10/north-koreas-hackers-using-ai-for-attacks-cybersecurity-firm-says", "Al Jazeera", "MED", "QA", "TI-20260809-001"),
    ("https://www.enki.co.kr", "Enki White Hat", "VND", "KR", "TI-20260809-001"),
    ("https://www.genians.co.kr/en/blog/threat_intelligence/kimsuky_ai_llm", "Genians Security Center", "VND", "KR", "TI-20260809-001"),
    ("https://www.insurancejournal.com/news/international/2026/07/23/878763.htm", "Insurance Journal", "MED", "US", "TI-20260809-001"),
    ("https://www.boho.or.kr/kr/bbs/view.do", "Korea Internet & Security Agency (KISA) joint advisory", "GOV", "KR", "TI-20260809-001"),
    ("https://www.fortinet.com/blog/threat-research/dprk-related-campaigns-with-lnk-and-github-c2", "Fortinet / FortiGuard Labs", "VND", "US", "TI-20260809-001"),
    ("https://attack.mitre.org/groups/G0094/", "MITRE ATT&CK", "TEC", "US", "TI-20260809-001"),
    ("https://www.nknews.org/2026/08/crypto-exchange-sues-north-korean-government-and-hackers-over-1-5b-heist/", "NK News", "MED", None, "TI-20260809-001"),
    ("https://s2w.medium.com/detailed-analysis-of-signbt-malware-cluster-504fc3ab4ecf", "S2W Talon", "VND", "KR", "TI-20260809-001"),
    ("https://securityaffairs.com/196417/apt/south-korea-warns-of-state-backed-watering-hole-attacks.html", "Security Affairs", "MED", None, "TI-20260809-001"),
    ("https://www.techtimes.com/articles/323486/20260807/north-korean-hackers-infected-themselves-exposing-1640-company-breach-researcher.htm", "Tech Times", "MED", "US", "TI-20260809-001"),
    ("https://therecord.media/south-korea-cyberattack-foreign-ministry", "The Record (Recorded Future News)", "MED", "US", "TI-20260809-001"),
    ("https://therecord.media/kimsuky-north-korea-espionage-groupware-companies", "The Record (Recorded Future News)", "MED", "US", "TI-20260809-001"),
    ("https://therecord.media/north-korea-hackers-ransomware", "The Record (Recorded Future News)", "MED", "US", "TI-20260809-001"),

    ("https://adversa.ai/blog/cryptographic-context-injection-grok-data-theft/", "Adversa AI", "VND", None, "IW-20260826-001"),
    ("https://www.bleepingcomputer.com/news/security/meta-ai-model-hacked-a-company-during-misconfigured-cyber-test/", "BleepingComputer", "MED", "US", "IW-20260826-001"),
    ("https://www.bleepingcomputer.com/news/security/hackers-poison-arrayref-rust-crate-to-push-infostealer-malware/", "BleepingComputer", "MED", "US", "IW-20260826-001"),
    ("https://betanews.com/article/meta-muse-spark-1-1-security-breach/", "BetaNews", "MED", "US", "IW-20260826-001"),
    ("https://cybermagazine.com/news/hugging-face-breach-how-openai-agents-planned-the-attack", "Cyber Magazine", "MED", "UK", "IW-20260826-001"),
    ("https://www.cbsnews.com/news/meta-says-ai-model-breached-third-party-company/", "CBS News", "MED", "US", "IW-20260826-001"),
    ("https://www.cybersecuritydive.com/news/openai-hugging-face-hack-ai-models-black-hat/827167/", "Cybersecurity Dive", "MED", "US", "IW-20260826-001"),
    ("https://dataconomy.com/2026/08/21/xais-grok-chat-agent-vulnerable-to-cryptographic-context/", "Dataconomy", "MED", None, "IW-20260826-001"),
    ("https://explainx.ai/blog/openai-agent-swarm-message-board-black-hat-security-incident-august-2026", "explainx.ai", "VND", None, "IW-20260826-001"),
    ("https://explainx.ai/blog/grok-cryptographic-context-injection-attack-august-2026", "explainx.ai", "VND", None, "IW-20260826-001"),
    ("https://forkast.news/openais-evaluation-agents-built-a-secret-message-board-exploited-zero-days-and-breached-hugging-face-from-the-inside", "Forkast", "MED", "HK", "IW-20260826-001"),
    ("https://www.iansresearch.com/resources/all-blogs/post/security-blog/2026/08/06/black-hat--inside-the-openai-hugging-face-breach", "IANS Research", "VND", "US", "IW-20260826-001"),
    ("https://groundlevel-ai.com/p/openai-gives-first-detailed-debrief", "Ground Level", "MED", None, "IW-20260826-001"),
    ("https://thehackernews.com/2026/08/new-cryptographic-context-injection.html", "The Hacker News", "MED", None, "IW-20260826-001"),
    ("https://thehackernews.com/2026/08/rust-supply-chain-attack-puts-build.html", "The Hacker News", "MED", None, "IW-20260826-001"),
    ("https://blog.invidelabs.com/rust-arrayref-supply-chain-attack/", "Invide Labs", "VND", None, "IW-20260826-001"),
    ("https://benarent.co.uk/talks/black-hat-usa-2026/openai-hugging-face-incident", "Ben Arent", "IND", None, "IW-20260826-001"),
    ("https://www.nextgov.com/artificial-intelligence/2026/08/openai-agents-rebuilt-internal-message-board-lead-hugging-face-breach/415240/", "Nextgov/FCW", "MED", "US", "IW-20260826-001"),
    ("https://safedep.io/arrayref-proc-macro1-rust-build-time-malware", "safedep.io", "VND", None, "IW-20260826-001"),
    ("https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/", "Rust Security Response Team", "NPO", "US", "IW-20260826-001"),
    ("https://semgrep.dev/blog/2026/rust-crates-arrayref-append-only-vec-compromised-proc-macro1", "Semgrep", "VND", "US", "IW-20260826-001"),
    ("https://securityaffairs.com/197717/hacking/zero-click-grok-chat-history-theft-adversa-ai-demonstrates-cryptographic-context-injection.html", "Security Affairs", "MED", None, "IW-20260826-001"),
    ("https://www.securityweek.com/encrypted-prompts-bypass-ai-safety-guardrails-in-grok-and-gemini/", "SecurityWeek", "MED", "US", "IW-20260826-001"),
    ("https://www.scworld.com/news/black-hat-2026-openai-reveals-agents-planned-collective-attacks-via-secret-message-board", "SC World", "MED", "US", "IW-20260826-001"),
    ("https://sofx.com/grok-decrypts-hidden-attack-payload-and-leaks-user-data-to-attacker-servers", "SOFX", "MED", None, "IW-20260826-001"),
    ("https://cryptorank.io/news/feed/0a824-grok-leaks-chats-encrypted-webpage", "CryptoRank", "MED", None, "IW-20260826-001"),
    ("https://sqmagazine.co.uk/meta-ai-model-breached-company-irregular-test/", "SQ Magazine", "MED", "UK", "IW-20260826-001"),
    ("https://www.stepsecurity.io/blog/arrayref-rust-crate-supply-chain-attack", "StepSecurity", "VND", None, "IW-20260826-001"),
    ("https://www.theinformation.com/articles/meta-ai-model-hacked-another-company-cybersecurity-testing", "The Information", "MED", "US", "IW-20260826-001"),
    ("https://www.theregister.com/security/2026/08/06/openai-reveals-its-rogue-agent-swarm-went-a-little-bit-borg-ahead-of-hugging-face-hack/", "The Register", "MED", "UK", "IW-20260826-001"),
    ("https://www.theregister.com/ai-and-ml/2026/08/20/grok-chat-duped-into-swallowing-injected-instructions/", "The Register", "MED", "UK", "IW-20260826-001"),
    ("https://www.theregister.com/security/2026/08/21/hackers-poison-popular-rust-crates-to-steal-developers-credentials/", "The Register", "MED", "UK", "IW-20260826-001"),
    ("https://tuxcare.com/blog/rust-attack-arrayref", "TuxCare", "VND", None, "IW-20260826-001"),
    ("https://www.wiz.io/blog/rust-supply-chain-attack-on-arrayref-significant-overlap-with-dprk-campaigns", "Wiz", "VND", "US", "IW-20260826-001"),

    ("https://www.huntress.com/blog/n-able-vulnerability-exploitation", "Huntress", "VND", "US", "TI-20260817-001"),
    ("https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "CISA Known Exploited Vulnerabilities (KEV) Catalog", "TEC", "US", "TI-20260817-001"),
    ("https://www.fortinet.com/blog/threat-research/quickfox-supply-chain-attack-used-to-deploy-fdmtp-implant", "Fortinet / FortiGuard Labs", "VND", "US", "TI-20260817-001"),
    ("https://www.darktrace.com/blog/chinese-apt-campaign-targets-entities-with-updated-fdmtp-backdoor", "Darktrace", "VND", "UK", "TI-20260817-001"),
    ("https://www.govinfosecurity.com/china-linked-hackers-exploit-n-able-flaw-in-ransomware-attacks-a-32506", "GovInfoSecurity", "MED", "US", "TI-20260817-001"),
    ("https://thehackernews.com/2026/08/quickfox-supply-chain-attack-delivers.html", "The Hacker News", "MED", None, "TI-20260817-001"),
    ("https://attack.mitre.org/groups/G0129/", "MITRE ATT&CK", "TEC", "US", "TI-20260817-001"),
    ("https://thehackernews.com/2026/08/china-linked-hackers-deploy-new.html", "The Hacker News", "MED", None, "TI-20260817-001"),

    ("https://thehackernews.com/2026/08/sandworm-linked-uac-0145-uses-fake-job.html", "The Hacker News", "MED", None, "TI-20260822-001"),
    ("https://therecord.media/russian-military-hackers-pose-as-recruiters-ukraine-it-workers", "The Record (Recorded Future News)", "MED", "US", "TI-20260822-001"),
    ("https://www.microsoft.com/en-us/security/blog/2026/07/31/captivecrunch-midnight-blizzard-targets-travelers-worldwide-for-malware-delivery-and-credential-theft/", "Microsoft Threat Intelligence", "VND", "US", "TI-20260822-001"),
    ("https://reliaquest.com/blog/threat-spotlight-dns-poisoning-tactics-expand-to-hospitality/", "ReliaQuest", "VND", "US", "TI-20260822-001"),

    ("https://www.bleepingcomputer.com/news/security/ransomware-gang-abuses-microsoft-teams-relays-to-hide-malicious-traffic/", "BleepingComputer", "MED", "US", "TI-20260830-001"),
    ("https://www.bleepingcomputer.com/news/security/fake-it-support-calls-on-microsoft-teams-push-etherrat-malware/", "BleepingComputer", "MED", "US", "TI-20260830-001"),
    ("https://www.bleepingcomputer.com/news/security/microsoft-teams-vishing-attacks-lead-to-chaos-ransomware-attacks/", "BleepingComputer", "MED", "US", "TI-20260830-001"),
    ("https://www.microsoft.com/en-us/security/blog/2024/05/15/threat-actors-misusing-quick-assist-in-social-engineering-attacks-leading-to-ransomware/", "Microsoft Threat Intelligence", "VND", "US", "TI-20260830-001"),
    ("https://www.rapid7.com/blog/post/tr-muddying-tracks-state-sponsored-shadow-behind-chaos-ransomware/", "Rapid7", "VND", "US", "TI-20260830-001"),
    ("https://www.securityweek.com/iranian-apt-intrusion-masquerades-as-chaos-ransomware-attack/", "SecurityWeek", "MED", "US", "TI-20260830-001"),
    ("https://www.sophos.com/en-us/blog/chaos-in-teams-vishing", "Sophos", "VND", "UK", "TI-20260830-001"),
    ("https://thehackernews.com/2026/05/muddywater-uses-microsoft-teams-to.html", "The Hacker News", "MED", None, "TI-20260830-001"),
]


def canonical_domain(url):
    netloc = urlparse(url).netloc.lower()
    return re.sub(r"^www\.", "", netloc)


def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]


def impersonation_check(domain, existing_domains):
    """Near-match: small edit distance, or same registrable name differing
    only by TLD or a hyphen. Classification spec §21."""
    hits = []
    stem = re.sub(r"\.(com|net|org|io|ai|dev|co|media|news)$", "", domain)
    for other in existing_domains:
        if other == domain:
            continue
        other_stem = re.sub(r"\.(com|net|org|io|ai|dev|co|media|news)$", "", other)
        dist = levenshtein(domain, other)
        if dist <= 2 or stem.replace("-", "") == other_stem.replace("-", ""):
            hits.append(other)
    return hits


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    # group citations by canonical_domain, keeping distinct (domain, canonical_name)
    # pairs separate where one publisher runs two genuinely different
    # source types under one domain (cisa.gov: advisories are GOV, the KEV
    # catalog is TEC -- classification spec §3's own worked example).
    grouped = {}
    order = []
    for url, name, type_, origin, serial in CITATIONS:
        key = (canonical_domain(url), name)
        if key not in grouped:
            grouped[key] = {
                "canonical_name": name,
                "canonical_domain": key[0],
                "type": type_,
                "origin": origin,
                "first_seen_url": url,
                "cited_in": [],
            }
            order.append(key)
        entry = grouped[key]
        if serial not in entry["cited_in"]:
            entry["cited_in"].append(serial)

    registered_domains = []
    registry = []
    held_for_review = []

    for i, key in enumerate(order, start=1):
        g = grouped[key]
        source_id = f"SRC-{i:04d}"
        near_matches = impersonation_check(g["canonical_domain"], registered_domains)
        registered_domains.append(g["canonical_domain"])

        review_flag = "held_impersonation" if near_matches else "first_citation"
        impersonation_note = (
            f"near-match against {', '.join(near_matches)}: held for review"
            if near_matches else
            "no near-match against registry canonical domains"
        )
        if near_matches:
            held_for_review.append((source_id, g["canonical_name"], near_matches))

        entry = {
            "source_id": source_id,
            "canonical_name": g["canonical_name"],
            "canonical_domain": g["canonical_domain"],
            "type": g["type"],
            "language": "en",
            "synthetic": False,
            "cited_in": sorted(g["cited_in"]),
            "admission": {
                "first_seen_url": g["first_seen_url"],
                "admitted": now,
                "assigned_type": g["type"],
                "type_basis": (
                    "assigned from publisher name and domain as cited in the issue's "
                    "References list; not yet verified against a fetched about/masthead "
                    "page (backfill admission, pre-fetch pass, CLAUDECODEBRIEF §9)"
                ),
                "domain_age_days": None,
                "impersonation_check": impersonation_note,
                "review_flag": review_flag,
                "reviewed": False,
            },
            "live": {
                "unique_claims": 0,
                "citations": 0,
                "distribution": {},
                "record_status": "insufficient",
            },
            "backfill": {
                "unique_claims": 0,
                "citations": 0,
                "distribution": {},
                "record_status": "insufficient",
                "from_issues": sorted(g["cited_in"]),
            },
        }
        if g["origin"]:
            entry["origin"] = g["origin"]
        registry.append(entry)

    out_path = ROOT / "data" / "sources" / "registry.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"wrote {len(registry)} registry entries to {out_path.relative_to(ROOT)}")
    if held_for_review:
        print(f"\n{len(held_for_review)} entries HELD for impersonation review (publication block):")
        for source_id, name, matches in held_for_review:
            print(f"  - {source_id} {name!r} near-matches: {matches}")
    else:
        print("no entries held for impersonation review")


if __name__ == "__main__":
    main()
