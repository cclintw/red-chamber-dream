#!/usr/bin/env python3
import csv
import json
import shutil
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


SITE = Path("site")
DATA = SITE / "data"

CSV_ENCODING = "utf-8-sig"
BASIC_TYPES = {"PERSON", "PLACE", "GPE", "LOC", "BUILDING", "FAC", "TITLE_ROLE", "FLOWER"}
TYPE_ZH = {
    "PERSON": "人物",
    "PLACE": "地點",
    "GPE": "地點",
    "LOC": "地點",
    "BUILDING": "建築",
    "FAC": "建築",
    "TITLE_ROLE": "身份",
    "FLOWER": "花",
}


def read_csv(path: str) -> list[dict[str, str]]:
    with Path(path).open(encoding=CSV_ENCODING, newline="") as fh:
        return list(csv.DictReader(fh))


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sentence_offsets(sentences: list[dict[str, str]]) -> dict[str, int]:
    grouped = defaultdict(list)
    offsets = {}
    for sentence in sentences:
        grouped[sentence["paragraph_id"]].append(sentence)
    for _, rows in grouped.items():
        cursor = 0
        for row in sorted(rows, key=lambda r: int(r["sentence_number"])):
            offsets[row["sentence_id"]] = cursor
            cursor += len(row["text"])
    return offsets


def authority_maps() -> tuple[dict[str, dict[str, str]], dict[tuple[str, str], dict[str, str]]]:
    by_key = {}
    by_name = {}
    for row in read_csv("entity_authority.csv"):
        by_key[row["entity_key"]] = row
        by_name[(row["entity_type"], row["canonical_name"])] = row
        if row["entity_type"] == "PLACE":
            by_name[("GPE", row["canonical_name"])] = row
            by_name[("LOC", row["canonical_name"])] = row
        if row["entity_type"] == "BUILDING":
            by_name[("FAC", row["canonical_name"])] = row
    return by_key, by_name


def basic_entity_key(row: dict[str, str], by_name: dict[tuple[str, str], dict[str, str]]) -> tuple[str, str, str, str]:
    entity_key = row["entity_key"]
    canonical = row["canonical_name"]
    entity_type = row["entity_type"]
    if not entity_key:
        auth = by_name.get((entity_type, row["entity_text"]))
        if auth:
            entity_key = auth["entity_key"]
            canonical = auth["canonical_name"]
            entity_type = auth["entity_type"]
    if entity_type in {"PERSON", "PLACE", "GPE", "LOC", "BUILDING", "FAC", "FLOWER"} and not entity_key:
        return "", "", "", ""
    index_key = entity_key or f"{entity_type}:{row['entity_text']}"
    label = canonical or row["entity_text"]
    return index_key, label, entity_type, TYPE_ZH.get(entity_type, entity_type)


def build_ebook_json() -> None:
    chapters = read_csv("chapter.csv")
    paragraphs = read_csv("paragraph.csv")
    sentences = read_csv("sentence.csv")
    ner = read_csv("ner.csv")
    _, by_name = authority_maps()
    offsets = sentence_offsets(sentences)

    entities_by_paragraph = defaultdict(list)
    for row in ner:
        if row["entity_type"] not in BASIC_TYPES:
            continue
        index_key, label, entity_type, type_zh = basic_entity_key(row, by_name)
        if not index_key:
            continue
        start = offsets.get(row["sentence_id"])
        if start is None:
            continue
        entities_by_paragraph[row["paragraph_id"]].append(
            {
                "id": row["entity_id"],
                "key": index_key,
                "label": label,
                "type": entity_type,
                "type_zh": type_zh,
                "text": row["entity_text"],
                "start": start + int(row["char_start"]),
                "end": start + int(row["char_end"]),
            }
        )

    chapter_out = []
    paragraphs_by_chapter = defaultdict(list)
    for paragraph in paragraphs:
        ents = sorted(entities_by_paragraph.get(paragraph["paragraph_id"], []), key=lambda e: (e["start"], -(e["end"] - e["start"])))
        filtered = []
        last_end = -1
        for ent in ents:
            if ent["start"] < last_end:
                continue
            filtered.append(ent)
            last_end = ent["end"]
        paragraphs_by_chapter[paragraph["chapter_id"]].append(
            {
                "id": paragraph["paragraph_id"],
                "n": int(paragraph["paragraph_number"]),
                "text": paragraph["text"],
                "entities": filtered,
            }
        )
    for chapter in chapters:
        chapter_out.append(
            {
                "id": chapter["chapter_id"],
                "n": int(chapter["chapter_number"]),
                "title": chapter["chapter_title"],
                "paragraphs": paragraphs_by_chapter[chapter["chapter_id"]],
            }
        )
    write_json(DATA / "ebook.json", {"chapters": chapter_out})


def build_search_index() -> None:
    chapters = {row["chapter_id"]: row for row in read_csv("chapter.csv")}
    paragraphs = read_csv("paragraph.csv")
    docs = []
    for p in paragraphs:
        chapter = chapters[p["chapter_id"]]
        docs.append(
            {
                "id": p["paragraph_id"],
                "chapter_id": p["chapter_id"],
                "chapter_number": int(p["chapter_number"]),
                "chapter_title": chapter["chapter_title"],
                "paragraph_number": int(p["paragraph_number"]),
                "text": p["text"],
            }
        )
    write_json(DATA / "search_index.json", {"documents": docs})


def build_entity_indexes() -> None:
    shutil.copyfile("basic_entity_index.json", DATA / "basic_entity_index.json")
    ner = read_csv("ner.csv")
    chapter_counter = Counter()
    paragraph_index = defaultdict(list)
    for row in ner:
        key = row["entity_key"] or f"{row['entity_type']}:{row['entity_text']}"
        chapter_counter[(key, row["canonical_name"] or row["entity_text"], row["entity_type"], row["chapter_number"])] += 1
        paragraph_index[key].append(row["paragraph_id"])
    chapter_summary = [
        {
            "entity_key": key,
            "name": name,
            "entity_type": entity_type,
            "chapter_number": int(chapter),
            "count": count,
        }
        for (key, name, entity_type, chapter), count in sorted(chapter_counter.items(), key=lambda x: (x[0][0], int(x[0][3])))
    ]
    paragraph_summary = [
        {
            "entity_key": key,
            "paragraph_count": len(set(ids)),
            "paragraph_ids": sorted(set(ids)),
        }
        for key, ids in paragraph_index.items()
    ]
    write_json(DATA / "entity_chapter_summary.json", {"rows": chapter_summary})
    write_json(DATA / "entity_paragraph_index.json", {"rows": paragraph_summary})


def build_statistics_json() -> None:
    document = read_csv("document.csv")[0]
    chapters = read_csv("chapter.csv")
    paragraphs = read_csv("paragraph.csv")
    ner_summary = read_csv("ner_summary.csv")
    entity_occ = read_csv("entity_occurrence_summary.csv")
    motif_summary = read_csv("motif_summary.csv")
    motif_chapter = read_csv("motif_chapter_summary.csv")
    social_nodes = read_csv("person_social_nodes.csv")
    social_edges = read_csv("person_social_edges.csv")

    chapter_stats = []
    paragraphs_by_chapter = defaultdict(list)
    for paragraph in paragraphs:
        paragraphs_by_chapter[paragraph["chapter_id"]].append(paragraph)
    for chapter in chapters:
        ps = paragraphs_by_chapter[chapter["chapter_id"]]
        chapter_stats.append(
            {
                "chapter_id": chapter["chapter_id"],
                "chapter_number": int(chapter["chapter_number"]),
                "title": chapter["chapter_title"],
                "paragraph_count": len(ps),
                "char_count": sum(len(p["text"]) for p in ps),
            }
        )

    write_json(
        DATA / "statistics.json",
        {
            "document": document,
            "chapter_stats": chapter_stats,
            "ner_summary": ner_summary,
            "entity_occurrence_summary": entity_occ,
            "motif_summary": motif_summary,
            "motif_chapter_summary": motif_chapter,
            "person_social_top_nodes": social_nodes[:30],
            "person_social_top_edges": social_edges[:50],
        },
    )


def build_network_json() -> None:
    shutil.copyfile("person_social_network.json", DATA / "person_social_network.json")


def build_articles_json() -> None:
    articles = {
        "articles": [
            {
                "id": "article_placeholder_001",
                "title": "研究文章資料待建置",
                "author": "",
                "year": "",
                "tags": ["平台占位"],
                "abstract": "此區將用於整理紅樓夢研究文章、主題、人物與意象連結。",
                "links": [],
            }
        ]
    }
    write_json(DATA / "articles.json", articles)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    build_ebook_json()
    build_search_index()
    build_entity_indexes()
    build_statistics_json()
    build_network_json()
    build_articles_json()
    print(f"wrote platform data to {DATA}")


if __name__ == "__main__":
    main()
