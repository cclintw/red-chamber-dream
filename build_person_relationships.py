#!/usr/bin/env python3
"""Copy minimal curated relationships into public output."""

from __future__ import annotations

import csv
import json
from pathlib import Path


SOURCE = Path("examples/relationships.csv")
OUTPUT_CSV = Path("public_output/relationships.csv")
OUTPUT_JSON = Path("public_output/relationships.json")
FIELDS = ["source", "target", "type", "label"]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing {SOURCE}")
    with SOURCE.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in FIELDS} for row in rows])
    OUTPUT_JSON.write_text(json.dumps({"relationships": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUTPUT_CSV}: {len(rows)} rows")
    print(f"wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
