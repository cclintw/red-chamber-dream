#!/usr/bin/env python3
"""Run the project rebuild pipeline in order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_STEPS = [
    "build_tables.py",
    "build_ner_tables.py",
    "build_motif_tables.py",
    "build_person_social_network.py",
    "build_platform_site.py",
    "build_person_relationships.py",
    "build_demo_site.py",
    "build_sqlite.py",
]

SEED_STEP = "build_ner_seed_tables.py"


def run_script(script: str) -> None:
    if not Path(script).exists():
        raise SystemExit(f"missing script: {script}")
    print(f"\n==> python3 {script}", flush=True)
    subprocess.run([sys.executable, script], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild corpus CSV, JSON, demo data, and SQLite outputs.")
    parser.add_argument(
        "--with-seed",
        action="store_true",
        help="also run build_ner_seed_tables.py before NER. This may overwrite manually curated authority/alias/rule tables.",
    )
    parser.add_argument(
        "--skip-sqlite",
        action="store_true",
        help="skip build_sqlite.py",
    )
    parser.add_argument(
        "--skip-demo",
        action="store_true",
        help="skip build_demo_site.py",
    )
    args = parser.parse_args()

    steps = list(DEFAULT_STEPS)
    if args.with_seed:
        steps.insert(1, SEED_STEP)
    if args.skip_sqlite:
        steps = [step for step in steps if step != "build_sqlite.py"]
    if args.skip_demo:
        steps = [step for step in steps if step != "build_demo_site.py"]

    for step in steps:
        run_script(step)
    print("\nrebuild complete")


if __name__ == "__main__":
    main()
