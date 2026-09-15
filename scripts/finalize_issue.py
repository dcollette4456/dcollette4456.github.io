#!/usr/bin/env python3
"""
Last mechanical step of the draft-to-PR pipeline (see
docs/specs/Automation_Pipeline_Scope.md): branch, stage exactly this
issue's files, commit, and push. Opening the pull request itself is not
done here -- that's a GitHub API call, not a git operation, and in a
Claude Code session it goes through the GitHub MCP tools rather than a
shell script holding credentials. Run this, then open the PR.

Refuses to run if scripts/validate_data.py fails. A pipeline that can
reach this stage on broken data and still offer to open a PR would be
the shortcut this whole project exists to not take.

Usage:
  python3 scripts/finalize_issue.py --serial TI-YYYYMMDD-NNN
  python3 scripts/finalize_issue.py --serial TI-YYYYMMDD-NNN --dry-run
  python3 scripts/finalize_issue.py --serial TI-YYYYMMDD-NNN --branch custom-branch-name
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from prepare_regrade_test import find_article  # noqa: E402


def run(cmd, dry_run, check=True):
    printable = " ".join(f'"{c}"' if (" " in c or "\n" in c) else c for c in cmd)
    print(f"$ {printable}")
    if dry_run:
        return None
    return subprocess.run(cmd, cwd=ROOT, check=check, capture_output=True, text=True)


def collect_issue_files(serial, article_path):
    """Every file this issue's pipeline run touches or produces. Data
    files that are shared across issues (the registry, serials.json) are
    included too, since build_registry.py and allocate_serial.py rewrite
    them in place -- there's no per-issue copy to stage instead."""
    files = [article_path]

    citations = ROOT / "data" / "citations" / f"{serial}.json"
    if citations.exists():
        files.append(citations)

    ledger = ROOT / "data" / "ledger" / f"{serial}.json"
    if ledger.exists():
        files.append(ledger)

    drafts_dir = ROOT / "data" / "claim_drafts" / serial
    if drafts_dir.is_dir():
        files.extend(sorted(drafts_dir.glob("*.json")))

    manifest = ROOT / "data" / "evidence" / f"{serial}.manifest.json"
    if manifest.exists():
        files.append(manifest)

    registry = ROOT / "data" / "sources" / "registry.json"
    if registry.exists():
        files.append(registry)

    serials = ROOT / "data" / "serials.json"
    if serials.exists():
        files.append(serials)

    return files


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--serial", required=True)
    p.add_argument("--branch", default=None, help="Default: claude/issue-{serial-lowercase}")
    p.add_argument("--dry-run", action="store_true", help="Print what would run; no git commands executed")
    args = p.parse_args()

    serial = args.serial
    article_path = find_article(serial)
    ledger_path = ROOT / "data" / "ledger" / f"{serial}.json"
    if not ledger_path.exists():
        sys.exit(f"error: {ledger_path.relative_to(ROOT)} does not exist. Finalize runs after the "
                  f"ledger is written and the article is reconciled against it, not before.")

    print("Running scripts/validate_data.py...")
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_data.py")],
                             cwd=ROOT, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit("error: validate_data.py failed. Not staging a branch on broken data.")

    files = collect_issue_files(serial, article_path)
    print(f"\n{len(files)} file(s) for {serial}:")
    for f in files:
        print(f"  {f.relative_to(ROOT)}")

    branch = args.branch or f"claude/issue-{serial.lower()}"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    claim_count = len(ledger)
    disputed = sum(1 for c in ledger if c.get("disposition") == "disputed")

    print(f"\nBranch: {branch}")
    run(["git", "checkout", "-b", branch], args.dry_run)
    run(["git", "add"] + [str(f) for f in files], args.dry_run)

    commit_message = (
        f"Publish {serial}: {article_path.stem}\n\n"
        f"{claim_count} claim(s) graded"
        + (f", {disputed} disputed" if disputed else "")
        + ".\n\n"
        f"Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\n"
    )
    run(["git", "commit", "-m", commit_message], args.dry_run)
    run(["git", "push", "-u", "origin", branch], args.dry_run)

    if args.dry_run:
        print("\n[dry-run] no git commands were actually run.")
    else:
        print(f"\nPushed {branch}. Open the PR next -- that's a GitHub API call, done separately.")


if __name__ == "__main__":
    main()
