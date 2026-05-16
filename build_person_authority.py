#!/usr/bin/env python3
"""Extract a minimal person authority view from example entities."""

from __future__ import annotations

import csv
from pathlib import Path


ENTITIES_CSV = Path("examples/entities.csv")
OUTPUT = Path("public_output/persons.csv")


def main() -> None:
    with ENTITIES_CSV.open(encoding="utf-8", newline="") as fh:
        people = [row for row in csv.DictReader(fh) if row.get("type") == "person"]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "name", "aliases"])
        writer.writeheader()
        writer.writerows({"id": row["id"], "name": row["name"], "aliases": row.get("aliases", "")} for row in people)
    print(f"wrote {OUTPUT}: {len(people)} rows")


if __name__ == "__main__":
    main()
