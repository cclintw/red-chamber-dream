#!/usr/bin/env python3
"""Build minimal motif annotations from example motif rules."""

from __future__ import annotations

import csv
from pathlib import Path


UNITS_CSV = Path("public_output/corpus_units.csv")
MOTIFS_CSV = Path("examples/motifs.csv")
OUTPUT = Path("public_output/motifs.csv")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    if not UNITS_CSV.exists():
        raise SystemExit("run build_tables.py first")
    units = [row for row in read_csv(UNITS_CSV) if row["type"] == "sentence"]
    motifs = read_csv(MOTIFS_CSV)
    rows: list[dict[str, object]] = []

    for unit in units:
        text = unit["text"]
        for motif in motifs:
            for term in [item.strip() for item in motif.get("terms", "").split("|") if item.strip()]:
                start = 0
                while True:
                    pos = text.find(term, start)
                    if pos < 0:
                        break
                    rows.append(
                        {
                            "unit_id": unit["id"],
                            "motif_id": motif["id"],
                            "start": pos,
                            "end": pos + len(term),
                            "term": term,
                        }
                    )
                    start = pos + len(term)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["unit_id", "motif_id", "start", "end", "term"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUTPUT}: {len(rows)} rows")


if __name__ == "__main__":
    main()
