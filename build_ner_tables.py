#!/usr/bin/env python3
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


LOCAL_DEPS = Path(".deps")
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS.resolve()))

from ckip_transformers.nlp import CkipNerChunker


SENTENCE_CSV = Path("sentence.csv")
TOKEN_CSV = Path("token.csv")
AUTHORITY_CSV = Path("entity_authority.csv")
ALIAS_CSV = Path("entity_alias.csv")
RULE_CSV = Path("ner_rule.csv")

NER_CANDIDATE_CSV = Path("ner_candidate.csv")
NER_CSV = Path("ner.csv")
NER_CONFLICT_CSV = Path("ner_conflict.csv")
NER_SUMMARY_CSV = Path("ner_summary.csv")
ENTITY_OCCURRENCE_SUMMARY_CSV = Path("entity_occurrence_summary.csv")

DOC_ID = "hongloumeng"
CKIP_MODEL = "albert-tiny"
CKIP_SOURCE = f"ckip-{CKIP_MODEL}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fieldnames} for row in rows])


def load_authority() -> dict[str, dict[str, str]]:
    return {row["entity_key"]: row for row in read_csv(AUTHORITY_CSV)}


def candidate_inputs_are_current() -> bool:
    if not NER_CANDIDATE_CSV.exists():
        return False
    input_paths = [SENTENCE_CSV, TOKEN_CSV, AUTHORITY_CSV, ALIAS_CSV, RULE_CSV]
    candidate_mtime = NER_CANDIDATE_CSV.stat().st_mtime
    return all(path.exists() and path.stat().st_mtime <= candidate_mtime for path in input_paths)


def sentence_metadata(row: dict[str, str]) -> dict[str, str]:
    return {
        "document_id": row["document_id"],
        "chapter_id": row["chapter_id"],
        "chapter_number": row["chapter_number"],
        "paragraph_id": row["paragraph_id"],
        "paragraph_number": row["paragraph_number"],
        "sentence_id": row["sentence_id"],
        "sentence_number": row["sentence_number"],
    }


def add_authority_fields(candidate: dict[str, object], authority: dict[str, dict[str, str]]) -> None:
    key = str(candidate.get("entity_key") or "")
    auth = authority.get(key, {})
    if key and auth:
        candidate["canonical_name"] = auth["canonical_name"]
        candidate["entity_type"] = auth["entity_type"]
        candidate["subtype"] = auth["subtype"]
    else:
        candidate.setdefault("canonical_name", "")
        candidate.setdefault("subtype", "")


def iter_occurrences(text: str, pattern: str) -> list[tuple[int, int]]:
    if not pattern:
        return []
    positions = []
    start = 0
    while True:
        idx = text.find(pattern, start)
        if idx == -1:
            return positions
        positions.append((idx, idx + len(pattern)))
        start = idx + 1


def build_alias_candidates(
    sentence_rows: list[dict[str, str]],
    aliases: list[dict[str, str]],
    authority: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    candidates = []
    sorted_aliases = sorted(aliases, key=lambda row: (-len(row["alias"]), -int(row["priority"] or 0), row["alias"]))
    for row in sentence_rows:
        text = row["text"]
        meta = sentence_metadata(row)
        for alias in sorted_aliases:
            for start, end in iter_occurrences(text, alias["alias"]):
                candidate = {
                    **meta,
                    "entity_text": alias["alias"],
                    "entity_type": "PERSON",
                    "subtype": "",
                    "entity_key": alias["entity_key"],
                    "canonical_name": "",
                    "char_start": start,
                    "char_end": end,
                    "source": "alias",
                    "priority": int(alias["priority"] or 0),
                    "confidence": "0.95",
                    "rule_or_alias": alias["alias"],
                }
                add_authority_fields(candidate, authority)
                candidates.append(candidate)
    return candidates


def build_rule_candidates(
    sentence_rows: list[dict[str, str]],
    rules: list[dict[str, str]],
    authority: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    candidates = []
    sorted_rules = sorted(rules, key=lambda row: (-len(row["pattern"]), -int(row["priority"] or 0), row["pattern"]))
    for row in sentence_rows:
        text = row["text"]
        meta = sentence_metadata(row)
        for rule in sorted_rules:
            if rule["match_type"] != "exact":
                continue
            for start, end in iter_occurrences(text, rule["pattern"]):
                candidate = {
                    **meta,
                    "entity_text": rule["pattern"],
                    "entity_type": rule["entity_type"],
                    "subtype": rule["subtype"],
                    "entity_key": rule["entity_key"],
                    "canonical_name": "",
                    "char_start": start,
                    "char_end": end,
                    "source": "rule",
                    "priority": int(rule["priority"] or 0),
                    "confidence": "0.90" if int(rule["priority"] or 0) >= 70 else "0.65",
                    "rule_or_alias": rule["pattern"],
                }
                add_authority_fields(candidate, authority)
                candidates.append(candidate)
    return candidates


def build_ckip_candidates(
    sentence_rows: list[dict[str, str]],
    authority: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    ner = CkipNerChunker(model=CKIP_MODEL, device=-1)
    texts = [row["text"] for row in sentence_rows]
    outputs = ner(texts, use_delim=False, batch_size=128)
    candidates = []
    for row, entities in zip(sentence_rows, outputs):
        meta = sentence_metadata(row)
        for entity in entities:
            start, end = entity.idx
            candidate = {
                **meta,
                "entity_text": entity.word,
                "entity_type": entity.ner,
                "subtype": "",
                "entity_key": "",
                "canonical_name": "",
                "char_start": start,
                "char_end": end,
                "source": CKIP_SOURCE,
                "priority": 50,
                "confidence": "0.70",
                "rule_or_alias": "",
            }
            add_authority_fields(candidate, authority)
            candidates.append(candidate)
    return candidates


def score_candidate(row: dict[str, object]) -> tuple[int, int, int]:
    source = str(row["source"])
    priority = int(row["priority"])
    length = int(row["char_end"]) - int(row["char_start"])
    source_score = {"alias": 3, "rule": 2, CKIP_SOURCE: 1}.get(source, 0)
    if row.get("entity_key"):
        source_score += 2
    return (priority, length, source_score)


def overlaps(a: dict[str, object], b: dict[str, object]) -> bool:
    if a["sentence_id"] != b["sentence_id"]:
        return False
    return int(a["char_start"]) < int(b["char_end"]) and int(b["char_start"]) < int(a["char_end"])


def merge_candidates(candidates: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_sentence: dict[str, list[dict[str, object]]] = defaultdict(list)
    for candidate in candidates:
        by_sentence[str(candidate["sentence_id"])].append(candidate)

    merged = []
    conflicts = []
    for sentence_id, rows in by_sentence.items():
        rows = sorted(rows, key=lambda row: (int(row["char_start"]), -int(row["char_end"]), -int(row["priority"])))
        used = [False] * len(rows)
        for i, row in enumerate(rows):
            if used[i]:
                continue
            group = [row]
            used[i] = True
            for j in range(i + 1, len(rows)):
                if not used[j] and overlaps(row, rows[j]):
                    group.append(rows[j])
                    used[j] = True

            unique_choices = {(g.get("entity_key") or "", g["entity_type"], g.get("subtype") or "") for g in group}
            best = sorted(group, key=score_candidate, reverse=True)[0].copy()
            sources = sorted({str(g["source"]) for g in group})
            if len(sources) > 1:
                if "alias" in sources and CKIP_SOURCE in sources:
                    best["source"] = f"{CKIP_SOURCE}+alias"
                elif "rule" in sources and CKIP_SOURCE in sources:
                    best["source"] = f"{CKIP_SOURCE}+rule"
                else:
                    best["source"] = "+".join(sources)
            best["merged_candidate_count"] = len(group)
            merged.append(best)

            if len(unique_choices) > 1:
                conflicts.append(
                    {
                        "sentence_id": sentence_id,
                        "text": best["entity_text"],
                        "char_start": best["char_start"],
                        "char_end": best["char_end"],
                        "candidate_entity_keys": "|".join(sorted({str(g.get("entity_key") or "") for g in group})),
                        "candidate_types": "|".join(sorted({str(g["entity_type"]) for g in group})),
                        "candidate_sources": "|".join(sources),
                        "reason": "overlapping_candidates",
                        "suggested_resolution": best.get("entity_key") or best.get("entity_type") or "",
                    }
                )
    return merged, conflicts


def load_tokens_by_sentence() -> dict[str, list[dict[str, str]]]:
    by_sentence: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(TOKEN_CSV):
        by_sentence[row["sentence_id"]].append(row)
    return by_sentence


def align_tokens(row: dict[str, object], tokens_by_sentence: dict[str, list[dict[str, str]]]) -> None:
    tokens = tokens_by_sentence.get(str(row["sentence_id"]), [])
    start = int(row["char_start"])
    end = int(row["char_end"])
    covered = [
        token
        for token in tokens
        if int(token["char_start"]) < end and start < int(token["char_end"])
    ]
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


def add_ids(rows: list[dict[str, object]], id_field: str, prefix: str) -> None:
    for idx, row in enumerate(rows, start=1):
        row[id_field] = f"{DOC_ID}_{prefix}{idx:07d}"


def add_entity_numbers(rows: list[dict[str, object]]) -> None:
    counters: dict[str, int] = defaultdict(int)
    for row in sorted(rows, key=lambda r: (str(r["sentence_id"]), int(r["char_start"]), int(r["char_end"]))):
        sid = str(row["sentence_id"])
        counters[sid] += 1
        row["entity_number"] = counters[sid]


def build_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["entity_type"]), str(row.get("subtype") or ""), str(row["source"]))].append(row)
    summary = []
    for (entity_type, subtype, source), group in sorted(grouped.items()):
        summary.append(
            {
                "entity_type": entity_type,
                "subtype": subtype,
                "source": source,
                "count": len(group),
                "unique_surface_count": len({str(row["entity_text"]) for row in group}),
                "unique_entity_count": len({str(row.get("entity_key") or row["entity_text"]) for row in group}),
            }
        )
    return summary


def build_entity_occurrence_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = str(row.get("entity_key") or "")
        if key:
            grouped[key].append(row)

    summary = []
    for key, group in sorted(grouped.items()):
        chapters = sorted({int(row["chapter_number"]) for row in group})
        sample = group[0]
        summary.append(
            {
                "entity_key": key,
                "canonical_name": sample.get("canonical_name") or "",
                "entity_type": sample.get("entity_type") or "",
                "subtype": sample.get("subtype") or "",
                "total_occurrences": len(group),
                "first_chapter": chapters[0],
                "last_chapter": chapters[-1],
                "chapter_count": len(chapters),
                "surface_forms": "|".join(sorted({str(row["entity_text"]) for row in group})),
            }
        )
    return summary


def main() -> None:
    authority = load_authority()
    sentences = read_csv(SENTENCE_CSV)
    aliases = read_csv(ALIAS_CSV)
    rules = read_csv(RULE_CSV)

    candidate_fields = [
        "candidate_id",
        "document_id",
        "chapter_id",
        "chapter_number",
        "paragraph_id",
        "paragraph_number",
        "sentence_id",
        "sentence_number",
        "entity_text",
        "entity_type",
        "subtype",
        "entity_key",
        "canonical_name",
        "char_start",
        "char_end",
        "source",
        "priority",
        "confidence",
        "rule_or_alias",
    ]
    if candidate_inputs_are_current():
        candidates = read_csv(NER_CANDIDATE_CSV)
    else:
        candidates = []
        candidates.extend(build_ckip_candidates(sentences, authority))
        candidates.extend(build_alias_candidates(sentences, aliases, authority))
        candidates.extend(build_rule_candidates(sentences, rules, authority))

        add_ids(candidates, "candidate_id", "nc")
        write_csv(NER_CANDIDATE_CSV, candidate_fields, candidates)

    merged, conflicts = merge_candidates(candidates)
    add_ids(merged, "entity_id", "ne")
    add_entity_numbers(merged)
    tokens_by_sentence = load_tokens_by_sentence()
    for row in merged:
        align_tokens(row, tokens_by_sentence)

    ner_fields = [
        "entity_id",
        "document_id",
        "chapter_id",
        "chapter_number",
        "paragraph_id",
        "paragraph_number",
        "sentence_id",
        "sentence_number",
        "entity_number",
        "entity_text",
        "entity_type",
        "subtype",
        "entity_key",
        "canonical_name",
        "char_start",
        "char_end",
        "start_token_id",
        "end_token_id",
        "start_token_number",
        "end_token_number",
        "source",
        "priority",
        "confidence",
        "merged_candidate_count",
    ]
    write_csv(NER_CSV, ner_fields, merged)

    add_ids(conflicts, "conflict_id", "ncf")
    conflict_fields = [
        "conflict_id",
        "sentence_id",
        "text",
        "char_start",
        "char_end",
        "candidate_entity_keys",
        "candidate_types",
        "candidate_sources",
        "reason",
        "suggested_resolution",
    ]
    write_csv(NER_CONFLICT_CSV, conflict_fields, conflicts)

    summary = build_summary(merged)
    write_csv(
        NER_SUMMARY_CSV,
        ["entity_type", "subtype", "source", "count", "unique_surface_count", "unique_entity_count"],
        summary,
    )

    occurrence_summary = build_entity_occurrence_summary(merged)
    write_csv(
        ENTITY_OCCURRENCE_SUMMARY_CSV,
        [
            "entity_key",
            "canonical_name",
            "entity_type",
            "subtype",
            "total_occurrences",
            "first_chapter",
            "last_chapter",
            "chapter_count",
            "surface_forms",
        ],
        occurrence_summary,
    )

    print(f"wrote {NER_CANDIDATE_CSV}: {len(candidates)} rows")
    print(f"wrote {NER_CSV}: {len(merged)} rows")
    print(f"wrote {NER_CONFLICT_CSV}: {len(conflicts)} rows")
    print(f"wrote {NER_SUMMARY_CSV}: {len(summary)} rows")
    print(f"wrote {ENTITY_OCCURRENCE_SUMMARY_CSV}: {len(occurrence_summary)} rows")


if __name__ == "__main__":
    main()
