#!/usr/bin/env python3
"""Create the research/ working tree used by the rigorous-method-improvement skill.

Usage:
    python scripts/init_research.py research/ [--evaluator path [path ...]]

Creates the folder layout, writes stub files from the templates, writes STATUS.md,
and records a SHA-256 for every evaluator file named so that later audits can prove
the metric code was never touched. Safe to re-run: existing files are left alone.
"""
import argparse
import hashlib
import pathlib
import sys
from datetime import datetime, timezone

TREE = [
    "03_experiments",
    "04_ablation",
    "06_review",
    "07_audit",
]

SETUP = """# Setup

## Problem
- Source paper / repo:
- Task in one sentence:
- Primary metric(s) and direction:
- Secondary metrics:
- Datasets / splits used by the paper:

## Subset (for fast iteration)
- Definition:
- Why it is representative:
- Wall-clock per run:

## Baseline reproduction
| Setting | Paper | Reproduced (subset) | Reproduced (full) |
|---|---|---|---|
| | | | |
- Tolerance accepted and why:
- Discrepancies and their likely cause:

## Noise floor
- ε_abs (absolute floor on primary metric):
- k (multiplier on seed σ; default 1):
- Min seeds on subset (default 3):

## Frozen evaluator
{hashes}
- Rule: these files are never edited; any metric change is a specification violation.

## Decisions taken without asking
-
"""

STATUS = """# STATUS

- Updated (UTC): {ts}
- Current stage: 0 Setup
- Budget remaining: see SKILL.md defaults (edit as you spend)
- Last verdict: none
- Sham status: not run
- Stop reason: none
- Next action: reproduce baseline on subset; freeze evaluator
"""

STUBS = {
    "01_limitations.md": (
        "# Limitations of the baseline method\n\n"
        "<!-- one entry per limitation: flaw / why it limits / opportunity -->\n"
    ),
    "02_ideas.md": "# Seed ideas\n\n<!-- one idea card per idea; rank by novelty -->\n",
    "04_ablation/plans.md": (
        "# Ablation plans\n\n"
        "| # | Ablated component | Variant(s) | Held identical | Expected if component is real |\n"
        "|---|---|---|---|---|\n"
    ),
    "04_ablation/redesign.md": (
        "# Redesign from ablation\n\n"
        "| # | Ablation finding | Redesign |\n"
        "|---|---|---|\n"
    ),
    "05_draft.md": (
        "# <Title>\n\n## Abstract\n\n## 1 Introduction\n\n"
        "## 2 Method\n\n## 3 Experiments\n\n## 4 Conclusion and limitations\n"
    ),
    "07_audit/references.md": (
        "# Reference verification\n\n"
        "| Citation key | Title found | Where verified | Supports the claim? |\n"
        "|---|---|---|---|\n"
    ),
}


def _stub(text: str) -> str:
    return text.replace("\\n", "\n") if False else bytes(text, "utf-8").decode("unicode_escape")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", help="directory to create, e.g. research/")
    p.add_argument("--evaluator", nargs="*", default=[], help="metric/evaluation files to hash and freeze")
    args = p.parse_args(argv)

    root = pathlib.Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    for d in TREE:
        (root / d).mkdir(parents=True, exist_ok=True)

    hashes = []
    for ev in args.evaluator:
        ev_path = pathlib.Path(ev)
        if not ev_path.is_file():
            print(f"warning: evaluator file not found: {ev}", file=sys.stderr)
            continue
        hashes.append(f"- {ev_path} sha256 {sha256(ev_path)}")
    hashes_block = "\n".join(hashes) if hashes else "- Files: <path> sha256 <hash>"

    setup = root / "00_setup.md"
    if not setup.exists():
        setup.write_text(SETUP.format(hashes=hashes_block), encoding="utf-8")
    elif hashes:
        with setup.open("a", encoding="utf-8") as f:
            f.write("\n## Frozen evaluator (added)\n" + hashes_block + "\n")

    status = root / "STATUS.md"
    if not status.exists():
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        status.write_text(STATUS.format(ts=ts), encoding="utf-8")

    for rel, content in STUBS.items():
        path = root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_stub(content), encoding="utf-8")

    print(f"research tree ready at {root}/")
    if hashes:
        print("frozen evaluator hashes recorded in 00_setup.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
