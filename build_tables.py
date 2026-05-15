#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path


SOURCE = Path("red-chamber-dream.txt")
DOCUMENT_CSV = Path("document.csv")
CHAPTER_CSV = Path("chapter.csv")
PARAGRAPH_CSV = Path("paragraph.csv")
SENTENCE_CSV = Path("sentence.csv")
TOKEN_CSV = Path("token.csv")
LOCAL_DEPS = Path(".deps")
CKIP_MODEL = "albert-tiny"

if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS.resolve()))

try:
    from ckip_transformers.nlp import CkipPosTagger, CkipWordSegmenter
except ImportError:
    CkipWordSegmenter = None
    CkipPosTagger = None

if CkipWordSegmenter and CkipPosTagger:
    jieba = None
    pseg = None
else:
    try:
        import jieba
        import jieba.posseg as pseg

        jieba.setLogLevel(20)
    except ImportError:
        jieba = None
        pseg = None

DOC_ID = "hongloumeng"
CHAPTER_RE = re.compile(r"^第([一二三四五六七八九十百〇零0-9]+)回\s*(.*)$")
SENTENCE_END_RE = re.compile(r".+?[。！？；：]+[」』”’）】》]*|.+$")
FALLBACK_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z0-9]+|[^\s]")
PUNCT_RE = re.compile(r"^[\W_]+$", re.UNICODE)
CN_DIGITS = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}


def chinese_number_to_int(value: str) -> int:
    if value.isdigit():
        return int(value)
    total = 0
    section = 0
    number = 0
    for char in value:
        if char in CN_DIGITS:
            number = CN_DIGITS[char]
        elif char == "十":
            section += (number or 1) * 10
            number = 0
        elif char == "百":
            section += (number or 1) * 100
            number = 0
        else:
            raise ValueError(f"Unknown Chinese numeral: {value}")
    total += section + number
    return total


def clean_text(value: str) -> str:
    return value.strip().replace("\u3000", " ")


def split_sentences(text: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_END_RE.finditer(text) if match.group(0).strip()]


def token_type(token: str) -> str:
    if token.isdigit():
        return "number"
    if re.fullmatch(r"[A-Za-z0-9]+", token):
        return "latin"
    if PUNCT_RE.fullmatch(token) and not re.search(r"[\u4e00-\u9fff]", token):
        return "punct"
    return "word"


def add_token_offsets(text: str, tagged_tokens: list[tuple[str, str]], method: str) -> list[dict[str, str | int]]:
    tokens = []
    cursor = 0
    for word, pos in tagged_tokens:
        start = text.find(word, cursor)
        if start == -1:
            start = cursor
        end = start + len(word)
        tokens.append(
            {
                "token_text": word,
                "char_start": start,
                "char_end": end,
                "pos": pos,
                "token_type": token_type(word),
                "tokenizer": method,
            }
        )
        cursor = end
    return tokens


def tokenize_sentence(text: str) -> list[dict[str, str | int]]:
    if pseg:
        raw_tokens = [(word, flag) for word, flag in pseg.cut(text, HMM=True) if word.strip()]
        method = "jieba"
    else:
        raw_tokens = [(match.group(0), "") for match in FALLBACK_TOKEN_RE.finditer(text)]
        method = "regex"

    return add_token_offsets(text, raw_tokens, method)


def tokenize_sentences(sentence_rows: list[dict[str, str | int]]) -> list[list[dict[str, str | int]]]:
    sentence_texts = [str(row["text"]) for row in sentence_rows]
    if CkipWordSegmenter and CkipPosTagger:
        ws_driver = CkipWordSegmenter(model=CKIP_MODEL, device=-1)
        pos_driver = CkipPosTagger(model=CKIP_MODEL, device=-1)
        word_rows = ws_driver(sentence_texts, use_delim=False, batch_size=128)
        pos_rows = pos_driver(word_rows, use_delim=False, batch_size=128)
        return [
            add_token_offsets(text, list(zip(words, poses)), f"ckip-{CKIP_MODEL}")
            for text, words, poses in zip(sentence_texts, word_rows, pos_rows)
        ]

    return [tokenize_sentence(text) for text in sentence_texts]


def main() -> None:
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    chapters = []
    current = None

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        match = CHAPTER_RE.match(line)
        if match:
            if current:
                current["end_line"] = line_no - 1
                chapters.append(current)
            number = chinese_number_to_int(match.group(1))
            current = {
                "chapter_id": f"{DOC_ID}_ch{number:03d}",
                "chapter_number": number,
                "chapter_title": clean_text(match.group(2)),
                "start_line": line_no,
                "end_line": line_no,
                "paragraphs": [],
            }
            continue

        if current and line:
            current["paragraphs"].append(
                {
                    "line_no": line_no,
                    "text": raw_line.strip(),
                }
            )

    if current:
        current["end_line"] = len(lines)
        chapters.append(current)

    chapter_numbers = [chapter["chapter_number"] for chapter in chapters]
    expected = list(range(1, 121))
    if chapter_numbers != expected:
        raise ValueError(f"Expected chapters 1-120, got {chapter_numbers}")

    paragraph_rows = []
    sentence_rows = []
    global_paragraph_id = 0
    global_sentence_id = 0
    for chapter in chapters:
        for local_index, paragraph in enumerate(chapter["paragraphs"], start=1):
            global_paragraph_id += 1
            paragraph_id = f"{DOC_ID}_p{global_paragraph_id:05d}"
            sentences = split_sentences(paragraph["text"])
            paragraph_rows.append(
                {
                    "document_id": DOC_ID,
                    "chapter_id": chapter["chapter_id"],
                    "chapter_number": chapter["chapter_number"],
                    "paragraph_id": paragraph_id,
                    "paragraph_number": local_index,
                    "line_no": paragraph["line_no"],
                    "sentence_count": len(sentences),
                    "text": paragraph["text"],
                }
            )
            for sentence_index, sentence in enumerate(sentences, start=1):
                global_sentence_id += 1
                sentence_rows.append(
                    {
                        "document_id": DOC_ID,
                        "chapter_id": chapter["chapter_id"],
                        "chapter_number": chapter["chapter_number"],
                        "paragraph_id": paragraph_id,
                        "paragraph_number": local_index,
                        "sentence_id": f"{DOC_ID}_s{global_sentence_id:06d}",
                        "sentence_number": sentence_index,
                        "line_no": paragraph["line_no"],
                        "text": sentence,
                    }
                )

    token_rows = []
    global_token_id = 0
    tokenized_sentences = tokenize_sentences(sentence_rows)
    for sentence_row, sentence_tokens in zip(sentence_rows, tokenized_sentences):
        for token_index, token in enumerate(sentence_tokens, start=1):
            global_token_id += 1
            token_rows.append(
                {
                    "document_id": sentence_row["document_id"],
                    "chapter_id": sentence_row["chapter_id"],
                    "chapter_number": sentence_row["chapter_number"],
                    "paragraph_id": sentence_row["paragraph_id"],
                    "paragraph_number": sentence_row["paragraph_number"],
                    "sentence_id": sentence_row["sentence_id"],
                    "sentence_number": sentence_row["sentence_number"],
                    "token_id": f"{DOC_ID}_t{global_token_id:07d}",
                    "token_number": token_index,
                    "char_start": token["char_start"],
                    "char_end": token["char_end"],
                    "token_text": token["token_text"],
                    "pos": token["pos"],
                    "token_type": token["token_type"],
                    "tokenizer": token["tokenizer"],
                }
            )

    with DOCUMENT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "document_id",
                "title",
                "author",
                "source_file",
                "language",
                "total_chapters",
                "total_paragraphs",
                "total_sentences",
                "total_tokens",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "document_id": DOC_ID,
                "title": "紅樓夢",
                "author": "曹雪芹、高鶚",
                "source_file": SOURCE.name,
                "language": "zh-Hant",
                "total_chapters": len(chapters),
                "total_paragraphs": len(paragraph_rows),
                "total_sentences": len(sentence_rows),
                "total_tokens": len(token_rows),
            }
        )

    with CHAPTER_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "document_id",
                "chapter_id",
                "chapter_number",
                "chapter_title",
                "start_line",
                "end_line",
                "paragraph_count",
            ],
        )
        writer.writeheader()
        for chapter in chapters:
            writer.writerow(
                {
                    "document_id": DOC_ID,
                    "chapter_id": chapter["chapter_id"],
                    "chapter_number": chapter["chapter_number"],
                    "chapter_title": chapter["chapter_title"],
                    "start_line": chapter["start_line"],
                    "end_line": chapter["end_line"],
                    "paragraph_count": len(chapter["paragraphs"]),
                }
            )

    with PARAGRAPH_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "document_id",
                "chapter_id",
                "chapter_number",
                "paragraph_id",
                "paragraph_number",
                "line_no",
                "sentence_count",
                "text",
            ],
        )
        writer.writeheader()
        writer.writerows(paragraph_rows)

    with SENTENCE_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "document_id",
                "chapter_id",
                "chapter_number",
                "paragraph_id",
                "paragraph_number",
                "sentence_id",
                "sentence_number",
                "line_no",
                "text",
            ],
        )
        writer.writeheader()
        writer.writerows(sentence_rows)

    with TOKEN_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "document_id",
                "chapter_id",
                "chapter_number",
                "paragraph_id",
                "paragraph_number",
                "sentence_id",
                "sentence_number",
                "token_id",
                "token_number",
                "char_start",
                "char_end",
                "token_text",
                "pos",
                "token_type",
                "tokenizer",
            ],
        )
        writer.writeheader()
        writer.writerows(token_rows)

    print(f"wrote {DOCUMENT_CSV}: 1 row")
    print(f"wrote {CHAPTER_CSV}: {len(chapters)} rows")
    print(f"wrote {PARAGRAPH_CSV}: {len(paragraph_rows)} rows")
    print(f"wrote {SENTENCE_CSV}: {len(sentence_rows)} rows")
    print(f"wrote {TOKEN_CSV}: {len(token_rows)} rows")


if __name__ == "__main__":
    main()
