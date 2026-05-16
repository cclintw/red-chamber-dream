#!/usr/bin/env python3
"""Render a small annotated HTML reading view from minimal annotations."""

from __future__ import annotations

import csv
import html
from pathlib import Path


UNITS_CSV = Path("public_output/corpus_units.csv")
ANNOTATIONS_CSV = Path("public_output/annotations.csv")
ENTITIES_CSV = Path("examples/entities.csv")
OUTPUT = Path("public_output/annotated_text.html")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def annotate(text: str, annotations: list[dict[str, str]], names: dict[str, str]) -> str:
    output = []
    cursor = 0
    ordered = sorted(annotations, key=lambda row: int(row["start"]))
    for row in ordered:
        start = int(row["start"])
        end = int(row["end"])
        if start < cursor:
            continue
        output.append(html.escape(text[cursor:start]))
        label = html.escape(names.get(row["entity_id"], row["entity_id"]))
        surface = html.escape(text[start:end])
        output.append(f'<mark title="{label}">{surface}</mark>')
        cursor = end
    output.append(html.escape(text[cursor:]))
    return "".join(output)


def main() -> None:
    if not UNITS_CSV.exists() or not ANNOTATIONS_CSV.exists():
        raise SystemExit("run build_tables.py and build_ner_tables.py first")
    names = {row["id"]: row["name"] for row in read_csv(ENTITIES_CSV)}
    annotations_by_unit: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(ANNOTATIONS_CSV):
        annotations_by_unit.setdefault(row["unit_id"], []).append(row)

    body = []
    for unit in read_csv(UNITS_CSV):
        if unit["type"] != "sentence":
            continue
        body.append(f"<p>{annotate(unit['text'], annotations_by_unit.get(unit['id'], []), names)}</p>")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "<!doctype html><meta charset='utf-8'><title>Annotated Text</title>"
        "<style>body{font-family:serif;line-height:1.9;max-width:760px;margin:2rem auto}"
        "mark{background:#fff3bf;padding:0 .15em}</style>"
        + "\n".join(body),
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
