#!/usr/bin/env python3
"""Validate and copy the minimal entity authority example."""

from __future__ import annotations

import csv
from pathlib import Path


SOURCE = Path("examples/entities.csv")
OUTPUT = Path("public_output/entities.csv")
FIELDS = ["id", "name", "type", "aliases"]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing {SOURCE}")
    with SOURCE.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    missing = [field for field in FIELDS if rows and field not in rows[0]]
    if missing:
        raise SystemExit(f"{SOURCE} missing columns: {', '.join(missing)}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in FIELDS} for row in rows])
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
