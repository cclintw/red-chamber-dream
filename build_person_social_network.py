#!/usr/bin/env python3
"""Build a minimal co-occurrence network from sentence-level annotations."""

from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ANNOTATIONS_CSV = Path("public_output/annotations.csv")
PERSONS_CSV = Path("public_output/persons.csv")
EDGES_CSV = Path("public_output/network_edges.csv")
GRAPH_JSON = Path("public_output/network.json")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    if not ANNOTATIONS_CSV.exists() or not PERSONS_CSV.exists():
        raise SystemExit("run build_ner_tables.py and build_person_authority.py first")
    person_names = {row["id"]: row["name"] for row in read_csv(PERSONS_CSV)}
    by_unit: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(ANNOTATIONS_CSV):
        if row["entity_id"] in person_names:
            by_unit[row["unit_id"]].add(row["entity_id"])

    weights: Counter[tuple[str, str]] = Counter()
    for ids in by_unit.values():
        for source, target in itertools.combinations(sorted(ids), 2):
            weights[(source, target)] += 1

    edge_rows = [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in sorted(weights.items())
    ]
    with EDGES_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["source", "target", "weight"])
        writer.writeheader()
        writer.writerows(edge_rows)

    graph = {
        "nodes": [{"id": key, "label": value} for key, value in person_names.items()],
        "edges": edge_rows,
    }
    GRAPH_JSON.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {EDGES_CSV}: {len(edge_rows)} rows")
    print(f"wrote {GRAPH_JSON}")


if __name__ == "__main__":
    main()
