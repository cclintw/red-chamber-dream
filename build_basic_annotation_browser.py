#!/usr/bin/env python3
"""Create a minimal local annotation summary page."""

from __future__ import annotations

import csv
import html
from collections import Counter
from pathlib import Path


ANNOTATIONS_CSV = Path("public_output/annotations.csv")
ENTITIES_CSV = Path("examples/entities.csv")
OUTPUT = Path("public_output/annotation_summary.html")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    if not ANNOTATIONS_CSV.exists():
        raise SystemExit("run build_ner_tables.py first")
    entities = {row["id"]: row for row in read_csv(ENTITIES_CSV)}
    counts = Counter(row["entity_id"] for row in read_csv(ANNOTATIONS_CSV))
    rows = []
    for entity_id, count in counts.most_common():
        entity = entities.get(entity_id, {"name": entity_id, "type": ""})
        rows.append(
            "<tr>"
            f"<td>{html.escape(entity_id)}</td>"
            f"<td>{html.escape(entity['name'])}</td>"
            f"<td>{html.escape(entity.get('type', ''))}</td>"
            f"<td>{count}</td>"
            "</tr>"
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "<!doctype html><meta charset='utf-8'><title>Annotation Summary</title>"
        "<style>body{font-family:sans-serif;max-width:760px;margin:2rem auto}"
        "td,th{border-bottom:1px solid #ddd;padding:.4rem;text-align:left}</style>"
        "<h1>Annotation Summary</h1><table><tr><th>ID</th><th>Name</th><th>Type</th><th>Count</th></tr>"
        + "\n".join(rows)
        + "</table>",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
