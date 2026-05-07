#!/usr/bin/env python3
import csv
import html
import json
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


CHAPTER_CSV = Path("chapter.csv")
PARAGRAPH_CSV = Path("paragraph.csv")
SENTENCE_CSV = Path("sentence.csv")
NER_CSV = Path("ner.csv")

ANNOTATED_HTML = Path("annotated_paragraphs.html")
ANNOTATED_XML = Path("annotated_text.xml")
ANNOTATED_JSON = Path("annotated_paragraphs.json")

TYPE_CLASS = {
    "PERSON": "person",
    "BUILDING": "building",
    "PLACE": "place",
    "GPE": "place",
    "LOC": "place",
    "ROOM_SPACE": "space",
    "OBJECT": "object",
    "FLOWER": "flower",
    "PLANT": "plant",
    "COLOR": "color",
    "TITLE_ROLE": "role",
    "MOTIF": "motif",
    "TIME": "time",
    "DATE": "time",
    "FOOD": "food",
    "CLOTHING": "clothing",
    "MEDICINE": "medicine",
    "RELIGION_MYTH": "myth",
    "WORK_OF_ART": "work",
}

TYPE_ZH = {
    "PERSON": "人物",
    "BUILDING": "建築",
    "PLACE": "地點",
    "GPE": "地點",
    "LOC": "地點",
    "ROOM_SPACE": "空間",
    "OBJECT": "物件",
    "FLOWER": "花",
    "PLANT": "植物",
    "COLOR": "顏色",
    "TITLE_ROLE": "身份稱謂",
    "MOTIF": "意象",
    "TIME": "時間",
    "DATE": "時間",
    "FOOD": "飲食",
    "CLOTHING": "服飾",
    "MEDICINE": "藥物",
    "RELIGION_MYTH": "神佛仙道",
    "WORK_OF_ART": "作品",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def sentence_offsets_by_paragraph(sentences: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    offsets = {}
    grouped = defaultdict(list)
    for sentence in sentences:
        grouped[sentence["paragraph_id"]].append(sentence)

    for paragraph_id, rows in grouped.items():
        cursor = 0
        for row in sorted(rows, key=lambda r: int(r["sentence_number"])):
            offsets[row["sentence_id"]] = {"paragraph_start": cursor, "paragraph_end": cursor + len(row["text"])}
            cursor += len(row["text"])
    return offsets


def ner_by_paragraph(ner_rows: list[dict[str, str]], sentence_offsets: dict[str, dict[str, int]]) -> dict[str, list[dict[str, object]]]:
    grouped = defaultdict(list)
    for row in ner_rows:
        offsets = sentence_offsets.get(row["sentence_id"])
        if not offsets:
            continue
        paragraph_start = offsets["paragraph_start"] + int(row["char_start"])
        paragraph_end = offsets["paragraph_start"] + int(row["char_end"])
        item = dict(row)
        item["paragraph_char_start"] = paragraph_start
        item["paragraph_char_end"] = paragraph_end
        grouped[row["paragraph_id"]].append(item)

    for paragraph_id, rows in grouped.items():
        rows.sort(key=lambda r: (int(r["paragraph_char_start"]), -(int(r["paragraph_char_end"]) - int(r["paragraph_char_start"]))))
        filtered = []
        last_end = -1
        for row in rows:
            start = int(row["paragraph_char_start"])
            end = int(row["paragraph_char_end"])
            if start < last_end:
                continue
            filtered.append(row)
            last_end = end
        grouped[paragraph_id] = filtered
    return grouped


def attrs_html(row: dict[str, object]) -> str:
    entity_type = str(row["entity_type"])
    class_name = TYPE_CLASS.get(entity_type, "other")
    attrs = {
        "class": f"entity entity-{class_name}",
        "data-entity-id": row["entity_id"],
        "data-entity-type": entity_type,
        "data-entity-type-zh": TYPE_ZH.get(entity_type, entity_type),
        "data-subtype": row.get("subtype", ""),
        "data-entity-key": row.get("entity_key", ""),
        "data-canonical-name": row.get("canonical_name", ""),
        "data-source": row.get("source", ""),
        "data-confidence": row.get("confidence", ""),
        "data-sentence-id": row.get("sentence_id", ""),
        "data-start": row["paragraph_char_start"],
        "data-end": row["paragraph_char_end"],
        "data-offset-unit": "paragraph-char",
        "title": f"{TYPE_ZH.get(entity_type, entity_type)} {row.get('canonical_name') or row.get('entity_text')}",
    }
    return " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in attrs.items())


def render_marked_html(text: str, entities: list[dict[str, object]]) -> str:
    pieces = []
    cursor = 0
    for entity in entities:
        start = int(entity["paragraph_char_start"])
        end = int(entity["paragraph_char_end"])
        if start < cursor or end > len(text) or start >= end:
            continue
        pieces.append(html.escape(text[cursor:start]))
        pieces.append(f"<span {attrs_html(entity)}>{html.escape(text[start:end])}</span>")
        cursor = end
    pieces.append(html.escape(text[cursor:]))
    return "".join(pieces)


def attrs_xml(row: dict[str, object]) -> str:
    attrs = {
        "xml:id": row["entity_id"],
        "type": row["entity_type"],
        "subtype": row.get("subtype", ""),
        "ref": row.get("entity_key", ""),
        "canonical": row.get("canonical_name", ""),
        "source": row.get("source", ""),
        "confidence": row.get("confidence", ""),
        "sentence": row.get("sentence_id", ""),
        "start": row["paragraph_char_start"],
        "end": row["paragraph_char_end"],
        "offsetUnit": "paragraph-char",
    }
    return " ".join(f'{key}="{xml_escape(str(value))}"' for key, value in attrs.items() if value != "")


def render_marked_xml(text: str, entities: list[dict[str, object]]) -> str:
    pieces = []
    cursor = 0
    for entity in entities:
        start = int(entity["paragraph_char_start"])
        end = int(entity["paragraph_char_end"])
        if start < cursor or end > len(text) or start >= end:
            continue
        pieces.append(xml_escape(text[cursor:start]))
        pieces.append(f"<entity {attrs_xml(entity)}>{xml_escape(text[start:end])}</entity>")
        cursor = end
    pieces.append(xml_escape(text[cursor:]))
    return "".join(pieces)


def build_html(chapters: list[dict[str, str]], paragraphs: list[dict[str, str]], entities_by_paragraph: dict[str, list[dict[str, object]]]) -> str:
    chapter_map = {row["chapter_id"]: row for row in chapters}
    body = []
    current_chapter = None
    for paragraph in paragraphs:
        chapter_id = paragraph["chapter_id"]
        if chapter_id != current_chapter:
            if current_chapter is not None:
                body.append("</section>")
            chapter = chapter_map[chapter_id]
            body.append(
                f'<section class="chapter" data-chapter-id="{html.escape(chapter_id)}" data-chapter-number="{chapter["chapter_number"]}">'
                f'<h2>第 {chapter["chapter_number"]} 回 {html.escape(chapter["chapter_title"])}</h2>'
            )
            current_chapter = chapter_id

        marked = render_marked_html(paragraph["text"], entities_by_paragraph.get(paragraph["paragraph_id"], []))
        body.append(
            f'<p class="paragraph" data-document-id="{html.escape(paragraph["document_id"])}" '
            f'data-chapter-id="{html.escape(chapter_id)}" data-paragraph-id="{html.escape(paragraph["paragraph_id"])}" '
            f'data-paragraph-number="{paragraph["paragraph_number"]}">{marked}</p>'
        )
    if current_chapter is not None:
        body.append("</section>")

    legend = "".join(
        f'<span class="legend-item entity-{css}">{html.escape(label)}</span>'
        for css, label in [
            ("person", "人物"),
            ("building", "建築"),
            ("place", "地點"),
            ("space", "空間"),
            ("object", "物件"),
            ("flower", "花"),
            ("plant", "植物"),
            ("color", "顏色"),
            ("role", "身份稱謂"),
            ("motif", "意象"),
        ]
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>紅樓夢標記文本</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Noto Serif TC", "Songti TC", serif; line-height: 1.9; margin: 0; color: #1f2933; background: #fafafa; }}
header {{ position: sticky; top: 0; background: #ffffff; border-bottom: 1px solid #ddd; padding: 12px 24px; z-index: 2; }}
main {{ max-width: 980px; margin: 0 auto; padding: 24px; background: #fff; }}
h1 {{ font-size: 24px; margin: 0 0 8px; }}
h2 {{ font-size: 20px; margin: 32px 0 16px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb; }}
p {{ font-size: 18px; margin: 0 0 14px; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 8px; font-size: 14px; }}
.legend-item {{ padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0,0,0,.08); }}
.entity {{ padding: 0 2px; border-radius: 3px; cursor: help; }}
.entity-person {{ background: #fde2e2; }}
.entity-building {{ background: #dbeafe; }}
.entity-place {{ background: #d1fae5; }}
.entity-space {{ background: #e0e7ff; }}
.entity-object {{ background: #fef3c7; }}
.entity-flower {{ background: #fce7f3; }}
.entity-plant {{ background: #dcfce7; }}
.entity-color {{ background: #ede9fe; }}
.entity-role {{ background: #e5e7eb; }}
.entity-motif {{ background: #ffedd5; }}
.entity-time {{ background: #ccfbf1; }}
.entity-food {{ background: #fef9c3; }}
.entity-clothing {{ background: #f3e8ff; }}
.entity-myth {{ background: #cffafe; }}
.entity-work {{ background: #f5d0fe; }}
</style>
</head>
<body>
<header>
<h1>紅樓夢標記文本</h1>
<div class="legend">{legend}</div>
</header>
<main>
{chr(10).join(body)}
</main>
</body>
</html>
"""


def build_xml(chapters: list[dict[str, str]], paragraphs: list[dict[str, str]], entities_by_paragraph: dict[str, list[dict[str, object]]]) -> str:
    chapter_map = {row["chapter_id"]: row for row in chapters}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<text id="hongloumeng" title="紅樓夢">']
    current_chapter = None
    for paragraph in paragraphs:
        chapter_id = paragraph["chapter_id"]
        if chapter_id != current_chapter:
            if current_chapter is not None:
                lines.append("  </chapter>")
            chapter = chapter_map[chapter_id]
            lines.append(
                f'  <chapter xml:id="{xml_escape(chapter_id)}" n="{chapter["chapter_number"]}" title="{xml_escape(chapter["chapter_title"])}">'
            )
            current_chapter = chapter_id
        marked = render_marked_xml(paragraph["text"], entities_by_paragraph.get(paragraph["paragraph_id"], []))
        lines.append(
            f'    <p xml:id="{xml_escape(paragraph["paragraph_id"])}" n="{paragraph["paragraph_number"]}">{marked}</p>'
        )
    if current_chapter is not None:
        lines.append("  </chapter>")
    lines.append("</text>")
    return "\n".join(lines) + "\n"


def build_json(paragraphs: list[dict[str, str]], entities_by_paragraph: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    output = []
    for paragraph in paragraphs:
        entities = []
        for entity in entities_by_paragraph.get(paragraph["paragraph_id"], []):
            entities.append(
                {
                    "entity_id": entity["entity_id"],
                    "entity_text": entity["entity_text"],
                    "entity_type": entity["entity_type"],
                    "entity_type_zh": TYPE_ZH.get(str(entity["entity_type"]), str(entity["entity_type"])),
                    "subtype": entity.get("subtype", ""),
                    "entity_key": entity.get("entity_key", ""),
                    "canonical_name": entity.get("canonical_name", ""),
                    "source": entity.get("source", ""),
                    "confidence": entity.get("confidence", ""),
                    "paragraph_char_start": entity["paragraph_char_start"],
                    "paragraph_char_end": entity["paragraph_char_end"],
                    "sentence_id": entity["sentence_id"],
                }
            )
        output.append({**paragraph, "entities": entities})
    return output


def main() -> None:
    chapters = read_csv(CHAPTER_CSV)
    paragraphs = read_csv(PARAGRAPH_CSV)
    sentences = read_csv(SENTENCE_CSV)
    ner_rows = read_csv(NER_CSV)
    sentence_offsets = sentence_offsets_by_paragraph(sentences)
    entities_by_paragraph = ner_by_paragraph(ner_rows, sentence_offsets)

    ANNOTATED_HTML.write_text(build_html(chapters, paragraphs, entities_by_paragraph), encoding="utf-8")
    ANNOTATED_XML.write_text(build_xml(chapters, paragraphs, entities_by_paragraph), encoding="utf-8")
    ANNOTATED_JSON.write_text(
        json.dumps(build_json(paragraphs, entities_by_paragraph), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {ANNOTATED_HTML}")
    print(f"wrote {ANNOTATED_XML}")
    print(f"wrote {ANNOTATED_JSON}")


if __name__ == "__main__":
    main()
