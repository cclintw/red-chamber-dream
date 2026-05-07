#!/usr/bin/env python3
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path


CHAPTER_CSV = Path("chapter.csv")
PARAGRAPH_CSV = Path("paragraph.csv")
SENTENCE_CSV = Path("sentence.csv")
NER_CSV = Path("ner.csv")
AUTHORITY_CSV = Path("entity_authority.csv")

OUTPUT_HTML = Path("basic_annotated_browser.html")
OUTPUT_JSON = Path("basic_entity_index.json")
OUTPUT_MD = Path("basic_entity_summary.md")

BASIC_TYPES = {"PERSON", "PLACE", "GPE", "LOC", "BUILDING", "FAC", "TITLE_ROLE", "FLOWER"}
TYPE_CLASS = {
    "PERSON": "person",
    "PLACE": "place",
    "GPE": "place",
    "LOC": "place",
    "BUILDING": "building",
    "FAC": "building",
    "TITLE_ROLE": "role",
    "FLOWER": "flower",
}
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def authority_name_map() -> dict[tuple[str, str], dict[str, str]]:
    mapping = {}
    for row in read_csv(AUTHORITY_CSV):
        mapping[(row["entity_type"], row["canonical_name"])] = row
        if row["entity_type"] == "PLACE":
            for compatible_type in ["GPE", "LOC"]:
                mapping[(compatible_type, row["canonical_name"])] = row
        if row["entity_type"] == "BUILDING":
            mapping[("FAC", row["canonical_name"])] = row
    return mapping


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


def entity_index_key(row: dict[str, object]) -> str:
    if row.get("entity_key"):
        return str(row["entity_key"])
    return f'{row["entity_type"]}:{row["entity_text"]}'


def entity_label(row: dict[str, object]) -> str:
    return str(row.get("canonical_name") or row.get("entity_text") or "")


def prepare_entities(
    ner_rows: list[dict[str, str]],
    sentence_offsets: dict[str, dict[str, int]],
    authority_by_name: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    entities = []
    for row in ner_rows:
        if row["entity_type"] not in BASIC_TYPES:
            continue
        row = dict(row)
        if not row["entity_key"]:
            authority = authority_by_name.get((row["entity_type"], row["entity_text"]))
            if authority:
                row["entity_key"] = authority["entity_key"]
                row["canonical_name"] = authority["canonical_name"]
        if row["entity_type"] in {"PERSON", "PLACE", "GPE", "LOC", "BUILDING", "FAC", "FLOWER"} and not row["entity_key"]:
            continue
        offsets = sentence_offsets.get(row["sentence_id"])
        if not offsets:
            continue
        item = dict(row)
        item["paragraph_char_start"] = offsets["paragraph_start"] + int(row["char_start"])
        item["paragraph_char_end"] = offsets["paragraph_start"] + int(row["char_end"])
        item["index_key"] = entity_index_key(item)
        item["label"] = entity_label(item)
        item["type_zh"] = TYPE_ZH.get(row["entity_type"], row["entity_type"])
        entities.append(item)
    return entities


def group_entities_by_paragraph(entities: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped = defaultdict(list)
    for entity in entities:
        grouped[str(entity["paragraph_id"])].append(entity)
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


def build_entity_index(
    entities: list[dict[str, object]],
    paragraphs: list[dict[str, str]],
    chapters: list[dict[str, str]],
) -> dict[str, object]:
    paragraph_map = {row["paragraph_id"]: row for row in paragraphs}
    chapter_map = {row["chapter_id"]: row for row in chapters}
    grouped = defaultdict(list)
    by_paragraph = defaultdict(list)
    for entity in entities:
        grouped[str(entity["index_key"])].append(entity)
        by_paragraph[str(entity["paragraph_id"])].append(entity)

    index = {}
    for key, rows in grouped.items():
        sample = rows[0]
        paragraph_ids = []
        seen_paragraphs = set()
        for row in rows:
            pid = str(row["paragraph_id"])
            if pid not in seen_paragraphs:
                seen_paragraphs.add(pid)
                paragraph_ids.append(pid)

        paragraph_list = []
        for pid in paragraph_ids:
            paragraph = paragraph_map[pid]
            chapter = chapter_map[paragraph["chapter_id"]]
            paragraph_list.append(
                {
                    "chapter_number": int(paragraph["chapter_number"]),
                    "chapter_title": chapter["chapter_title"],
                    "paragraph_id": pid,
                    "paragraph_number": int(paragraph["paragraph_number"]),
                    "text": paragraph["text"],
                }
            )

        cooccurrence_counter = Counter()
        for pid in paragraph_ids:
            for other in by_paragraph[pid]:
                other_key = str(other["index_key"])
                if other_key == key:
                    continue
                cooccurrence_counter[other_key] += 1

        cooccurrences = []
        for other_key, count in cooccurrence_counter.most_common(30):
            other_sample = grouped[other_key][0]
            cooccurrences.append(
                {
                    "key": other_key,
                    "label": entity_label(other_sample),
                    "type": other_sample["entity_type"],
                    "type_zh": other_sample["type_zh"],
                    "count": count,
                }
            )

        index[key] = {
            "key": key,
            "label": entity_label(sample),
            "entity_type": sample["entity_type"],
            "entity_type_zh": sample["type_zh"],
            "entity_key": sample.get("entity_key", ""),
            "canonical_name": sample.get("canonical_name", ""),
            "frequency": len(rows),
            "paragraph_count": len(paragraph_ids),
            "surface_forms": sorted({str(row["entity_text"]) for row in rows}),
            "paragraphs": paragraph_list,
            "cooccurrences": cooccurrences,
        }
    return {
        "metadata": {
            "included_types": sorted(BASIC_TYPES),
            "entity_count": len(index),
            "occurrence_count": len(entities),
        },
        "entities": index,
    }


def attrs_html(row: dict[str, object]) -> str:
    entity_type = str(row["entity_type"])
    class_name = TYPE_CLASS.get(entity_type, "other")
    attrs = {
        "class": f"entity entity-{class_name}",
        "data-index-key": row["index_key"],
        "data-entity-id": row["entity_id"],
        "data-entity-type": entity_type,
        "data-entity-type-zh": row["type_zh"],
        "data-entity-key": row.get("entity_key", ""),
        "data-canonical-name": row.get("canonical_name", ""),
        "data-start": row["paragraph_char_start"],
        "data-end": row["paragraph_char_end"],
        "title": f'{row["type_zh"]} {entity_label(row)}',
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
        pieces.append(f"<button {attrs_html(entity)}>{html.escape(text[start:end])}</button>")
        cursor = end
    pieces.append(html.escape(text[cursor:]))
    return "".join(pieces)


def build_html(
    chapters: list[dict[str, str]],
    paragraphs: list[dict[str, str]],
    entities_by_paragraph: dict[str, list[dict[str, object]]],
    entity_index: dict[str, object],
) -> str:
    chapter_map = {row["chapter_id"]: row for row in chapters}
    chapter_nav = "\n".join(
        f'<a href="#chapter-{html.escape(row["chapter_id"])}" title="第 {row["chapter_number"]} 回 {html.escape(row["chapter_title"])}">'
        f'<span class="chapter-n">第 {row["chapter_number"]} 回</span><span class="chapter-title">{html.escape(row["chapter_title"])}</span></a>'
        for row in chapters
    )
    body = []
    current_chapter = None
    for paragraph in paragraphs:
        chapter_id = paragraph["chapter_id"]
        if chapter_id != current_chapter:
            if current_chapter is not None:
                body.append("</section>")
            chapter = chapter_map[chapter_id]
            body.append(
                f'<section class="chapter" id="chapter-{html.escape(chapter_id)}" data-chapter-id="{html.escape(chapter_id)}" data-chapter-number="{chapter["chapter_number"]}">'
                f'<h2>第 {chapter["chapter_number"]} 回 {html.escape(chapter["chapter_title"])}</h2>'
            )
            current_chapter = chapter_id
        marked = render_marked_html(paragraph["text"], entities_by_paragraph.get(paragraph["paragraph_id"], []))
        body.append(
            f'<p class="paragraph" id="{html.escape(paragraph["paragraph_id"])}" '
            f'data-chapter-number="{paragraph["chapter_number"]}" data-paragraph-number="{paragraph["paragraph_number"]}">{marked}</p>'
        )
    if current_chapter is not None:
        body.append("</section>")

    index_json = json.dumps(entity_index, ensure_ascii=False).replace("<", "\\u003c").replace("</script", "<\\/script")
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>紅樓夢基本實體標記瀏覽</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Noto Serif TC", "Songti TC", serif; line-height: 1.9; margin: 0; color: #1f2933; background: #f7f7f7; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 30px; }}
header {{ position: sticky; top: 0; background: #fff; border-bottom: 1px solid #ddd; padding: 10px 18px; z-index: 4; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
main {{ max-width: 980px; margin: 0 auto; padding: 24px 380px 24px 280px; background: #fff; min-height: 100vh; }}
h1 {{ font-size: 20px; margin: 0; }}
h2 {{ font-size: 20px; margin: 32px 0 16px; border-bottom: 1px solid #e5e7eb; }}
.chapter {{ scroll-margin-top: 30px; }}
.paragraph {{ scroll-margin-top: 30px; }}
p {{ font-size: 18px; margin: 0 0 14px; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 8px; font-size: 14px; }}
.legend span {{ padding: 2px 8px; border-radius: 4px; }}
.entity {{ border: 0; font: inherit; padding: 0 2px; border-radius: 3px; cursor: pointer; }}
.entity:hover {{ outline: 2px solid #111827; }}
.entity-person {{ background: #fde2e2; }}
.entity-building {{ background: #dbeafe; }}
.entity-place {{ background: #d1fae5; }}
.entity-role {{ background: #e5e7eb; }}
.entity-flower {{ background: #fce7f3; }}
#left-panel {{ position: fixed; left: 0; top: 57px; bottom: 0; width: 248px; overflow: auto; background: #fff; border-right: 1px solid #ddd; padding: 12px; z-index: 2; box-shadow: 4px 0 10px rgba(0,0,0,.03); transition: transform .18s ease; }}
#right-panel {{ position: fixed; right: 0; top: 57px; bottom: 0; width: 340px; overflow: auto; background: #fff; border-left: 1px solid #ddd; padding: 16px; box-shadow: -4px 0 10px rgba(0,0,0,.04); z-index: 2; transition: transform .18s ease; }}
.sidebar-title {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 10px; }}
.sidebar-title h3 {{ margin: 0; font-size: 18px; }}
.toggle {{ width: 30px; height: 30px; border: 1px solid #d1d5db; background: #fff; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 18px; line-height: 1; }}
#toggle-left-floating, #toggle-right-floating {{ position: fixed; top: 66px; z-index: 5; display: none; }}
#toggle-left-floating {{ left: 10px; }}
#toggle-right-floating {{ right: 10px; }}
body.left-collapsed #left-panel {{ transform: translateX(-100%); }}
body.left-collapsed main {{ padding-left: 40px; }}
body.left-collapsed #toggle-left-floating {{ display: inline-flex; }}
body.right-collapsed #right-panel {{ transform: translateX(100%); }}
body.right-collapsed main {{ padding-right: 40px; }}
body.right-collapsed #toggle-right-floating {{ display: inline-flex; }}
.chapter-list {{ display: flex; flex-direction: column; gap: 2px; }}
.chapter-list a {{ color: #1f2933; text-decoration: none; border-radius: 5px; padding: 5px 6px; display: grid; grid-template-columns: 58px minmax(0, 1fr); gap: 6px; align-items: center; }}
.chapter-list a:hover {{ background: #f3f4f6; }}
.chapter-n {{ font-size: 12px; color: #6b7280; white-space: nowrap; }}
.chapter-title {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 14px; }}
#panel h3 {{ margin: 0 0 8px; font-size: 20px; }}
#right-panel h3 {{ margin: 0 0 8px; font-size: 20px; }}
#right-panel .meta {{ color: #4b5563; font-size: 14px; margin-bottom: 12px; }}
#right-panel ol {{ padding-left: 22px; }}
#right-panel li {{ margin-bottom: 8px; font-size: 14px; line-height: 1.55; }}
.paragraph-preview {{ display: block; max-width: 286px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.co button {{ margin: 0 6px 6px 0; border: 1px solid #ddd; background: #fafafa; border-radius: 4px; padding: 2px 6px; cursor: pointer; }}
input[type="search"] {{ font-size: 15px; padding: 6px 8px; width: 100%; box-sizing: border-box; margin-bottom: 12px; }}
@media (max-width: 1000px) {{ main {{ padding: 24px; }} #left-panel, #right-panel {{ position: static; width: auto; transform: none !important; border-left: 0; border-right: 0; border-top: 1px solid #ddd; }} #toggle-left-floating, #toggle-right-floating, .toggle {{ display: none !important; }} }}
</style>
</head>
<body>
<header>
<h1>紅樓夢基本實體標記</h1>
<div class="legend">
<span class="entity-person">人物</span>
<span class="entity-place">地點</span>
<span class="entity-building">建築</span>
<span class="entity-role">身份</span>
<span class="entity-flower">花</span>
</div>
</header>
<button id="toggle-left-floating" class="toggle" title="展開章節">☰</button>
<button id="toggle-right-floating" class="toggle" title="展開資訊">◀</button>
<aside id="left-panel">
  <div class="sidebar-title"><h3>章節</h3><button id="toggle-left" class="toggle" title="收合章節">☰</button></div>
  <nav class="chapter-list">{chapter_nav}</nav>
</aside>
<aside id="right-panel">
  <div class="sidebar-title"><h3>實體資訊</h3><button id="toggle-right" class="toggle" title="收合資訊">▶</button></div>
  <input id="search" type="search" placeholder="搜尋人物、地點、身份、花">
  <div id="entity-detail"><h3>點選標記</h3><div class="meta">點擊原文中的標記，可查看詞頻、段落與共現。</div></div>
</aside>
<main>
{chr(10).join(body)}
</main>
<script id="entity-index" type="application/json">{index_json}</script>
<script>
const INDEX = JSON.parse(document.getElementById('entity-index').textContent).entities;
const detail = document.getElementById('entity-detail');
function escapeHtml(s) {{
  return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
}}
function firstSentence(text) {{
  const match = String(text).match(/^.*?[。！？；：]/);
  return match ? match[0] : String(text);
}}
function showEntity(key) {{
  const item = INDEX[key];
  if (!item) return;
  document.body.classList.remove('right-collapsed');
  const paragraphs = item.paragraphs.slice(0, 80);
  detail.innerHTML = `
    <h3>${{escapeHtml(item.label)}}</h3>
    <div class="meta">${{escapeHtml(item.entity_type_zh)}}｜出現 ${{item.frequency}} 次｜段落 ${{item.paragraph_count}} 段</div>
    <div class="meta">表記：${{escapeHtml(item.surface_forms.join('、'))}}</div>
    <h4>共現</h4>
    <div class="co">${{item.cooccurrences.slice(0, 20).map(c => `<button data-key="${{escapeHtml(c.key)}}">${{escapeHtml(c.label)}}(${{c.count}})</button>`).join('')}}</div>
    <h4>段落</h4>
    <ol>${{paragraphs.map(p => `<li><a href="#${{escapeHtml(p.paragraph_id)}}">第${{p.chapter_number}}回 第${{p.paragraph_number}}段</a><span class="paragraph-preview" title="${{escapeHtml(firstSentence(p.text))}}">${{escapeHtml(firstSentence(p.text))}}</span></li>`).join('')}}</ol>
  `;
}}
document.addEventListener('click', event => {{
  const entityButton = event.target.closest('.entity');
  if (entityButton) showEntity(entityButton.dataset.indexKey);
  const coButton = event.target.closest('.co button');
  if (coButton) showEntity(coButton.dataset.key);
}});
document.getElementById('search').addEventListener('input', event => {{
  const q = event.target.value.trim();
  if (!q) return;
  const found = Object.values(INDEX).find(item => item.label.includes(q) || item.surface_forms.some(s => s.includes(q)));
  if (found) showEntity(found.key);
}});
document.getElementById('toggle-left').addEventListener('click', () => document.body.classList.add('left-collapsed'));
document.getElementById('toggle-left-floating').addEventListener('click', () => document.body.classList.remove('left-collapsed'));
document.getElementById('toggle-right').addEventListener('click', () => document.body.classList.add('right-collapsed'));
document.getElementById('toggle-right-floating').addEventListener('click', () => document.body.classList.remove('right-collapsed'));
</script>
</body>
</html>
"""


def build_summary_md(entity_index: dict[str, object]) -> str:
    entities = sorted(entity_index["entities"].values(), key=lambda item: item["frequency"], reverse=True)
    lines = ["# Basic Entity Summary", "", f"- entity_count: {entity_index['metadata']['entity_count']}", f"- occurrence_count: {entity_index['metadata']['occurrence_count']}", "", "## Top Entities", ""]
    lines.append("|名稱|類型|出現次數|段落數|表記|")
    lines.append("|---|---:|---:|---:|---|")
    for item in entities[:100]:
        lines.append(
            f"|{item['label']}|{item['entity_type_zh']}|{item['frequency']}|{item['paragraph_count']}|{'、'.join(item['surface_forms'][:8])}|"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    chapters = read_csv(CHAPTER_CSV)
    paragraphs = read_csv(PARAGRAPH_CSV)
    sentences = read_csv(SENTENCE_CSV)
    ner_rows = read_csv(NER_CSV)
    offsets = sentence_offsets_by_paragraph(sentences)
    entities = prepare_entities(ner_rows, offsets, authority_name_map())
    entities_by_paragraph = group_entities_by_paragraph(entities)
    entity_index = build_entity_index(entities, paragraphs, chapters)

    OUTPUT_JSON.write_text(json.dumps(entity_index, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(chapters, paragraphs, entities_by_paragraph, entity_index), encoding="utf-8")
    OUTPUT_MD.write_text(build_summary_md(entity_index), encoding="utf-8")
    print(f"wrote {OUTPUT_HTML}")
    print(f"wrote {OUTPUT_JSON}")
    print(f"wrote {OUTPUT_MD}")
    print(f"entities: {entity_index['metadata']['entity_count']}")
    print(f"occurrences: {entity_index['metadata']['occurrence_count']}")


if __name__ == "__main__":
    main()
