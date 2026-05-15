#!/usr/bin/env python3
"""Build person occurrence summaries from NER output."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


NER_CSV = Path("ner.csv")
PERSON_AUTHORITY_CSV = Path("person_authority.csv")
PERSON_OCCURRENCE_SUMMARY_CSV = Path("person_occurrence_summary.csv")

FIELDS = [
    "person_key",
    "canonical_name",
    "total_occurrences",
    "first_chapter",
    "last_chapter",
    "chapter_count",
    "paragraph_count",
    "sentence_count",
    "surface_forms",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fieldnames} for row in rows])


def main() -> None:
    people = {row["person_key"]: row for row in read_csv(PERSON_AUTHORITY_CSV)}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(NER_CSV):
        if row.get("entity_type") != "PERSON":
            continue
        key = row.get("entity_key", "")
        if key and key in people:
            grouped[key].append(row)

    rows = []
    for key, mentions in sorted(grouped.items()):
        chapters = sorted({int(row["chapter_number"]) for row in mentions if row.get("chapter_number")}, key=int)
        rows.append(
            {
                "person_key": key,
                "canonical_name": people[key]["canonical_name"],
                "total_occurrences": len(mentions),
                "first_chapter": chapters[0] if chapters else "",
                "last_chapter": chapters[-1] if chapters else "",
                "chapter_count": len(set(chapters)),
                "paragraph_count": len({row["paragraph_id"] for row in mentions}),
                "sentence_count": len({row["sentence_id"] for row in mentions}),
                "surface_forms": "|".join(sorted({row["entity_text"] for row in mentions})),
            }
        )

    rows.sort(key=lambda row: (-int(row["total_occurrences"]), row["canonical_name"]))
    write_csv(PERSON_OCCURRENCE_SUMMARY_CSV, FIELDS, rows)
    print(f"wrote {PERSON_OCCURRENCE_SUMMARY_CSV}: {len(rows)} rows")


if __name__ == "__main__":
    main()
