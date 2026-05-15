#!/usr/bin/env python3
import csv
from collections import Counter, defaultdict
from pathlib import Path


SENTENCE_CSV = Path("sentence.csv")
TOKEN_CSV = Path("token.csv")
NER_CSV = Path("ner.csv")
MOTIF_RULE_CSV = Path("motif_rule.csv")
MOTIF_CSV = Path("motif.csv")
MOTIF_SUMMARY_CSV = Path("motif_summary.csv")
MOTIF_CHAPTER_SUMMARY_CSV = Path("motif_chapter_summary.csv")
PERSON_MOTIF_COOCCURRENCE_CSV = Path("person_motif_cooccurrence.csv")

DOC_ID = "hongloumeng"

MOTIF_RULE_ROWS = [
    ("玉", "motif_jade", "物象", "玉石", 80, "通靈寶玉、賈寶玉、玉石物件需依上下文判斷。"),
    ("通靈寶玉", "motif_jade", "物象", "玉石", 100, "核心象徵物。"),
    ("夢", "motif_dream", "夢幻", "夢", 90, "真幻、預示、太虛幻境相關。"),
    ("淚", "motif_tears", "情感身體", "眼淚", 90, "還淚神話與情感表現。"),
    ("哭", "motif_tears", "情感身體", "哭泣", 70, "情緒與身體反應。"),
    ("病", "motif_illness", "身體", "疾病", 85, "身體、命運、情感消耗。"),
    ("香", "motif_fragrance", "感官", "香氣", 75, "女性、空間、物件命名常見。"),
    ("紅", "motif_red", "顏色", "紅色", 80, "紅樓、女兒、繁華、情感色彩。"),
    ("白", "motif_white", "顏色", "白色", 75, "潔淨、喪亡、雪色等語境。"),
    ("青", "motif_green_blue", "顏色", "青色", 70, "服色、植物、空間色彩。"),
    ("綠", "motif_green", "顏色", "綠色", 70, "服色、植物、空間色彩。"),
    ("紫", "motif_purple", "顏色", "紫色", 70, "服色、身份、空間色彩。"),
    ("花", "motif_flower", "花木", "泛花", 65, "泛稱花，需注意高頻與歧義。"),
    ("海棠", "motif_haitang", "花木", "海棠", 95, "海棠社與女性才情相關。"),
    ("菊花", "motif_chrysanthemum", "花木", "菊花", 90, "詩社、季節、文人意象。"),
    ("芙蓉", "motif_hibiscus", "花木", "芙蓉", 90, "晴雯等相關意象。"),
    ("桃花", "motif_peach_blossom", "花木", "桃花", 85, ""),
    ("梅花", "motif_plum_blossom", "花木", "梅花", 85, ""),
    ("牡丹", "motif_peony", "花木", "牡丹", 85, ""),
    ("蓮", "motif_lotus", "花木", "蓮", 75, "單字可能與人名重疊。"),
    ("竹", "motif_bamboo", "花木", "竹", 75, "瀟湘館與清雅意象。"),
    ("柳", "motif_willow", "花木", "柳", 75, "春景、女性、離別意象。"),
    ("雪", "motif_snow", "自然", "雪", 85, "潔白、寒冷、詩社場景。"),
    ("月", "motif_moon", "自然", "月", 85, "夜、情感、詩性場景。"),
    ("風", "motif_wind", "自然", "風", 70, ""),
    ("雨", "motif_rain", "自然", "雨", 70, ""),
    ("詩", "motif_poetry", "文藝", "詩", 80, "詩社、才情、題詠。"),
    ("曲", "motif_song_drama", "文藝", "曲", 70, "戲曲、歌曲、曲文。"),
    ("書", "motif_book", "文藝", "書", 55, "高歧義，保守使用。"),
    ("酒", "motif_wine", "飲食", "酒", 70, "宴飲與情境。"),
    ("茶", "motif_tea", "飲食", "茶", 70, "日常、品味、空間交往。"),
    ("藥", "motif_medicine", "身體", "藥", 75, "疾病與身體治理。"),
    ("金", "motif_gold", "物象", "金", 60, "金玉、財富、命名歧義。"),
    ("石", "motif_stone", "物象", "石", 70, "石頭記、頑石神話。"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fieldnames} for row in rows])


def ensure_motif_rules() -> list[dict[str, str]]:
    if not MOTIF_RULE_CSV.exists():
        rows = [
            {
                "surface_text": surface,
                "motif_key": key,
                "motif_type": motif_type,
                "subtype": subtype,
                "priority": priority,
                "notes": notes,
            }
            for surface, key, motif_type, subtype, priority, notes in MOTIF_RULE_ROWS
        ]
        write_csv(
            MOTIF_RULE_CSV,
            ["surface_text", "motif_key", "motif_type", "subtype", "priority", "notes"],
            rows,
        )
    return read_csv(MOTIF_RULE_CSV)


def iter_occurrences(text: str, pattern: str) -> list[tuple[int, int]]:
    positions = []
    start = 0
    while pattern:
        idx = text.find(pattern, start)
        if idx == -1:
            return positions
        positions.append((idx, idx + len(pattern)))
        start = idx + 1
    return positions


def load_tokens_by_sentence() -> dict[str, list[dict[str, str]]]:
    grouped = defaultdict(list)
    for row in read_csv(TOKEN_CSV):
        grouped[row["sentence_id"]].append(row)
    return grouped


def align_tokens(row: dict[str, object], tokens_by_sentence: dict[str, list[dict[str, str]]]) -> None:
    tokens = tokens_by_sentence.get(str(row["sentence_id"]), [])
    start = int(row["char_start"])
    end = int(row["char_end"])
    covered = [token for token in tokens if int(token["char_start"]) < end and start < int(token["char_end"])]
    if not covered:
        row["start_token_id"] = ""
        row["end_token_id"] = ""
        row["start_token_number"] = ""
        row["end_token_number"] = ""
        return
    row["start_token_id"] = covered[0]["token_id"]
    row["end_token_id"] = covered[-1]["token_id"]
    row["start_token_number"] = covered[0]["token_number"]
    row["end_token_number"] = covered[-1]["token_number"]


def build_motifs(sentences: list[dict[str, str]], rules: list[dict[str, str]]) -> list[dict[str, object]]:
    sorted_rules = sorted(rules, key=lambda row: (-len(row["surface_text"]), -int(row["priority"] or 0)))
    rows = []
    motif_id = 0
    for sentence in sentences:
        text = sentence["text"]
        spans = []
        for rule in sorted_rules:
            for start, end in iter_occurrences(text, rule["surface_text"]):
                spans.append((start, end, rule))
        spans.sort(key=lambda item: (item[0], -(item[1] - item[0]), -int(item[2]["priority"] or 0)))
        last_end = -1
        for start, end, rule in spans:
            if start < last_end:
                continue
            motif_id += 1
            rows.append(
                {
                    "motif_id": f"{DOC_ID}_mo{motif_id:07d}",
                    "document_id": sentence["document_id"],
                    "chapter_id": sentence["chapter_id"],
                    "chapter_number": sentence["chapter_number"],
                    "paragraph_id": sentence["paragraph_id"],
                    "paragraph_number": sentence["paragraph_number"],
                    "sentence_id": sentence["sentence_id"],
                    "sentence_number": sentence["sentence_number"],
                    "surface_text": text[start:end],
                    "motif_key": rule["motif_key"],
                    "motif_type": rule["motif_type"],
                    "subtype": rule["subtype"],
                    "char_start": start,
                    "char_end": end,
                    "priority": rule["priority"],
                    "source": "motif_rule",
                    "notes": rule["notes"],
                }
            )
            last_end = end
    return rows


def build_summary(motifs: list[dict[str, object]]) -> list[dict[str, object]]:
    counter = Counter((row["motif_key"], row["motif_type"], row["subtype"]) for row in motifs)
    surfaces = defaultdict(set)
    for row in motifs:
        surfaces[(row["motif_key"], row["motif_type"], row["subtype"])].add(row["surface_text"])
    return [
        {
            "motif_key": key,
            "motif_type": motif_type,
            "subtype": subtype,
            "count": count,
            "surface_forms": "|".join(sorted(surfaces[(key, motif_type, subtype)])),
        }
        for (key, motif_type, subtype), count in sorted(counter.items())
    ]


def build_chapter_summary(motifs: list[dict[str, object]]) -> list[dict[str, object]]:
    counter = Counter((row["chapter_id"], row["chapter_number"], row["motif_key"], row["motif_type"], row["subtype"]) for row in motifs)
    return [
        {
            "chapter_id": chapter_id,
            "chapter_number": chapter_number,
            "motif_key": key,
            "motif_type": motif_type,
            "subtype": subtype,
            "count": count,
        }
        for (chapter_id, chapter_number, key, motif_type, subtype), count in sorted(
            counter.items(), key=lambda item: (int(item[0][1]), item[0][2])
        )
    ]


def build_person_motif_cooccurrence(motifs: list[dict[str, object]], ner_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    people_by_sentence = defaultdict(list)
    for row in ner_rows:
        if row["entity_type"] == "PERSON" and row["entity_key"]:
            people_by_sentence[row["sentence_id"]].append(row)
    counter = Counter()
    for motif in motifs:
        for person in people_by_sentence.get(str(motif["sentence_id"]), []):
            counter[(person["entity_key"], person["canonical_name"], motif["motif_key"], motif["motif_type"], motif["subtype"])] += 1
    return [
        {
            "entity_key": entity_key,
            "canonical_name": canonical_name,
            "motif_key": motif_key,
            "motif_type": motif_type,
            "subtype": subtype,
            "cooccurrence_count": count,
        }
        for (entity_key, canonical_name, motif_key, motif_type, subtype), count in sorted(
            counter.items(), key=lambda item: (-item[1], item[0][1], item[0][2])
        )
    ]


def main() -> None:
    rules = ensure_motif_rules()
    sentences = read_csv(SENTENCE_CSV)
    motifs = build_motifs(sentences, rules)
    tokens_by_sentence = load_tokens_by_sentence()
    for row in motifs:
        align_tokens(row, tokens_by_sentence)

    motif_fields = [
        "motif_id",
        "document_id",
        "chapter_id",
        "chapter_number",
        "paragraph_id",
        "paragraph_number",
        "sentence_id",
        "sentence_number",
        "surface_text",
        "motif_key",
        "motif_type",
        "subtype",
        "char_start",
        "char_end",
        "start_token_id",
        "end_token_id",
        "start_token_number",
        "end_token_number",
        "priority",
        "source",
        "notes",
    ]
    write_csv(MOTIF_CSV, motif_fields, motifs)
    write_csv(MOTIF_SUMMARY_CSV, ["motif_key", "motif_type", "subtype", "count", "surface_forms"], build_summary(motifs))
    write_csv(
        MOTIF_CHAPTER_SUMMARY_CSV,
        ["chapter_id", "chapter_number", "motif_key", "motif_type", "subtype", "count"],
        build_chapter_summary(motifs),
    )
    write_csv(
        PERSON_MOTIF_COOCCURRENCE_CSV,
        ["entity_key", "canonical_name", "motif_key", "motif_type", "subtype", "cooccurrence_count"],
        build_person_motif_cooccurrence(motifs, read_csv(NER_CSV)),
    )
    print(f"wrote {MOTIF_RULE_CSV}: {len(rules)} rows")
    print(f"wrote {MOTIF_CSV}: {len(motifs)} rows")
    print(f"wrote {MOTIF_SUMMARY_CSV}")
    print(f"wrote {MOTIF_CHAPTER_SUMMARY_CSV}")
    print(f"wrote {PERSON_MOTIF_COOCCURRENCE_CSV}")


if __name__ == "__main__":
    main()
