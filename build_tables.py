#!/usr/bin/env python3
"""Build a minimal corpus layer from an example text.

This public script uses a compact demonstration schema. It is intended for
workflow testing and adaptation, not as a production schema definition.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


INPUT_TEXT = Path("examples/sample_text.txt")
OUTPUT_DIR = Path("public_output")
UNITS_CSV = OUTPUT_DIR / "corpus_units.csv"
TOKENS_CSV = OUTPUT_DIR / "tokens.csv"


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？；])", text)
    return [part.strip() for part in parts if part.strip()]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", text)


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not INPUT_TEXT.exists():
        raise SystemExit(f"missing {INPUT_TEXT}")

    paragraphs = [line.strip() for line in INPUT_TEXT.read_text(encoding="utf-8").splitlines() if line.strip()]
    unit_rows: list[dict[str, object]] = []
    token_rows: list[dict[str, object]] = []

    for paragraph_index, paragraph in enumerate(paragraphs, start=1):
        paragraph_id = f"u{paragraph_index:03d}"
        unit_rows.append(
            {
                "id": paragraph_id,
                "parent_id": "",
                "type": "paragraph",
                "order": paragraph_index,
                "text": paragraph,
            }
        )

        for sentence_index, sentence in enumerate(split_sentences(paragraph), start=1):
            sentence_id = f"{paragraph_id}s{sentence_index:02d}"
            unit_rows.append(
                {
                    "id": sentence_id,
                    "parent_id": paragraph_id,
                    "type": "sentence",
                    "order": sentence_index,
                    "text": sentence,
                }
            )
            for token_index, token in enumerate(tokenize(sentence), start=1):
                token_rows.append(
                    {
                        "unit_id": sentence_id,
                        "order": token_index,
                        "text": token,
                    }
                )

    write_csv(UNITS_CSV, unit_rows, ["id", "parent_id", "type", "order", "text"])
    write_csv(TOKENS_CSV, token_rows, ["unit_id", "order", "text"])
    print(f"wrote {UNITS_CSV}")
    print(f"wrote {TOKENS_CSV}")


if __name__ == "__main__":
    main()
