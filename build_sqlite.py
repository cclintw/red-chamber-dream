#!/usr/bin/env python3
"""Import project CSV tables into a SQLite database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


DB_PATH = Path("corpus.sqlite")
CSV_ENCODING = "utf-8-sig"

TABLES = [
    ("document", Path("document.csv")),
    ("chapter", Path("chapter.csv")),
    ("paragraph", Path("paragraph.csv")),
    ("sentence", Path("sentence.csv")),
    ("token", Path("token.csv")),
    ("entity_authority", Path("entity_authority.csv")),
    ("entity_alias", Path("entity_alias.csv")),
    ("ner_rule", Path("ner_rule.csv")),
    ("ner_candidate", Path("ner_candidate.csv")),
    ("ner", Path("ner.csv")),
    ("ner_conflict", Path("ner_conflict.csv")),
    ("ner_summary", Path("ner_summary.csv")),
    ("entity_occurrence_summary", Path("entity_occurrence_summary.csv")),
    ("motif_rule", Path("motif_rule.csv")),
    ("motif", Path("motif.csv")),
    ("motif_summary", Path("motif_summary.csv")),
    ("motif_chapter_summary", Path("motif_chapter_summary.csv")),
    ("person_motif_cooccurrence", Path("person_motif_cooccurrence.csv")),
    ("person_social_nodes", Path("person_social_nodes.csv")),
    ("person_social_edges", Path("person_social_edges.csv")),
    ("person_relationship", Path("person_relationship.csv")),
]

INDEXES = [
    ("chapter", "chapter_id"),
    ("paragraph", "paragraph_id"),
    ("paragraph", "chapter_id"),
    ("sentence", "sentence_id"),
    ("sentence", "paragraph_id"),
    ("token", "sentence_id"),
    ("token", "token_text"),
    ("ner", "entity_key"),
    ("ner", "canonical_name"),
    ("ner", "paragraph_id"),
    ("ner", "sentence_id"),
    ("motif", "motif_key"),
    ("motif", "paragraph_id"),
    ("person_social_edges", "source"),
    ("person_social_edges", "target"),
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding=CSV_ENCODING, newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def quote_name(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def import_table(conn: sqlite3.Connection, table: str, path: Path) -> None:
    if not path.exists():
        print(f"skip missing {path}")
        return
    fields, rows = read_csv(path)
    if not fields:
        print(f"skip empty {path}")
        return

    q_table = quote_name(table)
    columns = ", ".join(f"{quote_name(field)} TEXT" for field in fields)
    conn.execute(f"DROP TABLE IF EXISTS {q_table}")
    conn.execute(f"CREATE TABLE {q_table} ({columns})")

    placeholders = ", ".join("?" for _ in fields)
    column_names = ", ".join(quote_name(field) for field in fields)
    conn.executemany(
        f"INSERT INTO {q_table} ({column_names}) VALUES ({placeholders})",
        [[row.get(field, "") for field in fields] for row in rows],
    )
    print(f"imported {path} -> {table}: {len(rows)} rows")


def create_indexes(conn: sqlite3.Connection) -> None:
    existing = {
        row[0]: {col[1] for col in conn.execute(f"PRAGMA table_info({quote_name(row[0])})")}
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    for table, column in INDEXES:
        if column not in existing.get(table, set()):
            continue
        index_name = f"idx_{table}_{column}"
        conn.execute(
            f"CREATE INDEX IF NOT EXISTS {quote_name(index_name)} "
            f"ON {quote_name(table)} ({quote_name(column)})"
        )


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        for table, path in TABLES:
            import_table(conn, table, path)
        create_indexes(conn)
        conn.commit()
    print(f"wrote {DB_PATH}")


if __name__ == "__main__":
    main()
