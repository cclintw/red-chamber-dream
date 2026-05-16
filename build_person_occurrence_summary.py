#!/usr/bin/env python3
"""Summarize minimal person mentions."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ANNOTATIONS_CSV = Path("public_output/annotations.csv")
PERSONS_CSV = Path("public_output/persons.csv")
OUTPUT = Path("public_output/person_occurrences.csv")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    if not ANNOTATIONS_CSV.exists():
        raise SystemExit("run build_ner_tables.py first")
    if not PERSONS_CSV.exists():
        raise SystemExit("run build_person_authority.py first")
    names = {row["id"]: row["name"] for row in read_csv(PERSONS_CSV)}
    counts = Counter(row["entity_id"] for row in read_csv(ANNOTATIONS_CSV) if row["entity_id"] in names)
    rows = [{"id": key, "name": names[key], "count": count} for key, count in sorted(counts.items())]
    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "name", "count"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUTPUT}: {len(rows)} rows")


if __name__ == "__main__":
    main()
