#!/usr/bin/env python3
"""Build person authority and relationship support tables.

This script keeps person authority data separate from NER occurrence data.
It uses the Wikipedia-derived character list as a candidate source, preserves
existing manually curated person keys where possible, and synchronizes PERSON
rows back into the generic entity authority/alias tables used by NER.
"""

from __future__ import annotations

import csv
import re
from collections import OrderedDict
from pathlib import Path


WIKI_PERSON_CSV = Path("red_chamber_dream_wikipedia_characters.csv")
ENTITY_AUTHORITY_CSV = Path("entity_authority.csv")
ENTITY_ALIAS_CSV = Path("entity_alias.csv")
PERSON_AUTHORITY_CSV = Path("person_authority.csv")
PERSON_ALIAS_CSV = Path("person_alias.csv")
PERSON_RELATIONSHIP_CSV = Path("person_relationship.csv")
PERSON_SEMANTIC_RELATIONSHIP_CSV = Path("person_semantic_relationship.csv")
PERSON_KINSHIP_CSV = Path("person_kinship.csv")
PERSON_MARRIAGE_CSV = Path("person_marriage.csv")
PERSON_SERVICE_RELATION_CSV = Path("person_service_relation.csv")

WIKI_SOURCE_URL = "https://zh.wikipedia.org/zh-tw/红楼梦角色列表"

PERSON_AUTHORITY_FIELDS = [
    "person_key",
    "canonical_name",
    "display_name",
    "person_type",
    "gender",
    "family_group",
    "household",
    "residence",
    "residence_detail",
    "generation",
    "role_category",
    "description",
    "source",
    "source_note",
    "review_status",
    "notes",
]

PERSON_ALIAS_FIELDS = [
    "alias",
    "person_key",
    "alias_type",
    "priority",
    "source",
    "review_status",
    "notes",
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


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def codepoint_key(name: str) -> str:
    parts = [f"{ord(char):x}" for char in name if not char.isspace()]
    return "person_u" + "_".join(parts)


def load_existing_people() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    authority = read_csv(ENTITY_AUTHORITY_CSV)
    people = {
        row["entity_key"]: row
        for row in authority
        if row.get("entity_type") == "PERSON" and row.get("entity_key")
    }
    name_to_key = {row["canonical_name"]: key for key, row in people.items()}
    for row in read_csv(ENTITY_ALIAS_CSV):
        key = row.get("entity_key", "")
        if key in people and row.get("alias"):
            name_to_key[row["alias"]] = key
    return people, name_to_key


def infer_person_type(category: str, existing_subtype: str) -> str:
    if existing_subtype:
        return existing_subtype
    if category in {"賈家", "史家", "王家", "薛家"}:
        return "family_member"
    if category == "丫鬟":
        return "maid"
    if category == "小廝及僕人":
        return "servant"
    if category == "十二官":
        return "performer"
    if category == "其他主要人物":
        return "major_character"
    if category.startswith("其他次要人物"):
        return "minor_character"
    return "character"


def infer_gender(name: str, category: str, description: str) -> str:
    text = f"{name} {category} {description}"
    if category in {"丫鬟", "十二官"}:
        return "female"
    if any(mark in text for mark in ["夫人", "姨媽", "姨娘", "妾", "妻", "女", "姑娘", "小姐", "母", "姊", "妹"]):
        return "female"
    if any(mark in text for mark in ["公", "爺", "父", "子", "兄", "弟", "和尚", "道人", "小廝"]):
        return "male"
    return "unknown"


def infer_role_category(category: str, description: str) -> str:
    text = f"{category} {description}"
    if category == "丫鬟" or "丫鬟" in text:
        return "maid"
    if category == "小廝及僕人" or any(mark in text for mark in ["小廝", "僕", "管家", "陪房", "婆子"]):
        return "servant"
    if category == "十二官" or "戲子" in text:
        return "performer"
    if any(mark in text for mark in ["妾", "姨娘"]):
        return "concubine"
    if any(mark in text for mark in ["官", "御史", "知府", "太守", "尚書", "統制"]):
        return "official"
    if any(mark in text for mark in ["僧", "和尚", "尼姑", "道士", "道人"]):
        return "religious"
    if category in {"賈家", "史家", "王家", "薛家"}:
        return "family_member"
    return "character"


def family_group(category: str, name: str, description: str) -> str:
    if category in {"賈家", "史家", "王家", "薛家"}:
        return category
    text = f"{name} {description}"
    if name.startswith("林") or "林如海" in text or "林黛玉" in text:
        return "林家"
    if name.startswith("甄") or "甄士隱" in text or "甄英蓮" in text:
        return "甄家"
    if name.startswith("尤") or "尤氏" in text:
        return "尤家"
    return ""


RONGGUOFU_NAMES = {
    "賈母", "賈代善", "賈代儒", "賈赦", "邢夫人", "賈政", "王夫人", "趙姨娘", "賈敏",
    "賈璉", "王熙鳳", "巧姐", "賈珠", "李紈", "賈寶玉", "賈元春", "賈探春", "賈迎春",
    "賈環", "賈蘭", "襲人", "晴雯", "麝月", "秋紋", "紫鵑", "雪雁", "平兒", "鴛鴦",
    "司棋", "侍書", "金釧", "玉釧", "周瑞家的", "賴大",
}

NINGGUOFU_NAMES = {"賈演", "賈代化", "賈敬", "賈珍", "尤氏", "賈蓉", "秦可卿", "賈惜春", "入畫"}


def infer_household(name: str, description: str) -> str:
    if name in NINGGUOFU_NAMES or "寧國府" in description or "寧府" in description:
        return "寧國府"
    if name in RONGGUOFU_NAMES or "榮國府" in description or "榮府" in description:
        return "榮國府"
    return ""


def extract_variant_aliases(notes: str) -> list[str]:
    aliases: list[str] = []
    for match in re.findall(r"[也又]作[「『](.*?)[」』]", notes or ""):
        aliases.extend(part.strip() for part in re.split(r"[、,，/]", match) if part.strip())
    for match in re.findall(r"原名[「『]?([^，。、；;「」『』 ]+)", notes or ""):
        aliases.append(match.strip())
    return aliases


def build_person_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    existing_people, name_to_key = load_existing_people()
    wiki_rows = read_csv(WIKI_PERSON_CSV)
    people: OrderedDict[str, dict[str, object]] = OrderedDict()
    wiki_aliases: list[dict[str, object]] = []

    for row in wiki_rows:
        source_name = clean_text(row.get("姓名", ""))
        if not source_name:
            continue
        description = clean_text(row.get("人物簡介", ""))
        category = clean_text(row.get("家族", ""))
        notes = clean_text(row.get("備註", ""))
        key = name_to_key.get(source_name) or codepoint_key(source_name)
        existing = existing_people.get(key, {})
        canonical_name = existing.get("canonical_name") or source_name
        person_type = infer_person_type(category, existing.get("subtype", ""))

        if key not in people:
            people[key] = {
                "person_key": key,
                "canonical_name": canonical_name,
                "display_name": existing.get("display_name") or "",
                "person_type": person_type,
                "gender": infer_gender(source_name, category, description),
                "family_group": family_group(category, source_name, description),
                "household": infer_household(source_name, description),
                "residence": existing.get("residence") or "",
                "residence_detail": existing.get("residence_detail") or "",
                "generation": "",
                "role_category": infer_role_category(category, description),
                "description": existing.get("description") or description,
                "source": "wikipedia_character_list",
                "source_note": f"source_group={category}",
                "review_status": "unreviewed",
                "notes": notes,
            }
        else:
            current = people[key]
            if description and description not in str(current.get("description", "")):
                current["description"] = f"{current.get('description', '')} / {description}".strip(" /")
            if notes and notes not in str(current.get("notes", "")):
                current["notes"] = f"{current.get('notes', '')} / {notes}".strip(" /")

        wiki_aliases.append(
            {
                "alias": source_name,
                "person_key": key,
                "alias_type": "source_name" if source_name != canonical_name else "full_name",
                "priority": 100,
                "source": "wikipedia_character_list",
                "review_status": "unreviewed",
                "notes": notes,
            }
        )
        for alias in extract_variant_aliases(notes):
            wiki_aliases.append(
                {
                    "alias": alias,
                    "person_key": key,
                    "alias_type": "variant_name",
                    "priority": 95,
                    "source": "wikipedia_character_list",
                    "review_status": "unreviewed",
                    "notes": notes,
                }
            )

    for key, row in existing_people.items():
        if key in people:
            continue
        people[key] = {
            "person_key": key,
            "canonical_name": row["canonical_name"],
            "person_type": row.get("subtype", "") or "character",
            "gender": "unknown",
            "family_group": "",
            "household": "",
            "residence": row.get("residence", ""),
            "residence_detail": row.get("residence_detail", ""),
            "generation": "",
            "role_category": row.get("subtype", "") or "character",
            "description": row.get("description", ""),
            "source": "entity_authority_legacy",
            "source_note": "",
            "review_status": "reviewed",
            "notes": "",
        }

    aliases = build_person_aliases(people, wiki_aliases)
    return list(people.values()), aliases


def build_person_aliases(
    people: OrderedDict[str, dict[str, object]],
    wiki_aliases: list[dict[str, object]],
) -> list[dict[str, object]]:
    alias_rows: OrderedDict[tuple[str, str], dict[str, object]] = OrderedDict()

    def add(row: dict[str, object]) -> None:
        alias = clean_text(str(row.get("alias", "")))
        key = clean_text(str(row.get("person_key", "")))
        if not alias or not key:
            return
        item = {field: row.get(field, "") for field in PERSON_ALIAS_FIELDS}
        item["alias"] = alias
        item["person_key"] = key
        alias_rows[(key, alias)] = item

    for person in people.values():
        add(
            {
                "alias": person["canonical_name"],
                "person_key": person["person_key"],
                "alias_type": "full_name",
                "priority": 100,
                "source": "person_authority",
                "review_status": person["review_status"],
                "notes": "",
            }
        )

    person_keys = set(people)
    for row in read_csv(ENTITY_ALIAS_CSV):
        key = row.get("entity_key", "")
        if key not in person_keys:
            continue
        add(
            {
                "alias": row.get("alias", ""),
                "person_key": key,
                "alias_type": row.get("alias_type", ""),
                "priority": row.get("priority", ""),
                "source": "entity_alias_legacy",
                "review_status": "reviewed",
                "notes": row.get("notes", ""),
            }
        )

    for row in wiki_aliases:
        add(row)

    return list(alias_rows.values())


def sync_entity_tables(people: list[dict[str, object]], aliases: list[dict[str, object]]) -> None:
    non_person = [
        row
        for row in read_csv(ENTITY_AUTHORITY_CSV)
        if row.get("entity_type") != "PERSON"
    ]
    person_rows = [
        {
            "entity_key": row["person_key"],
            "canonical_name": row["canonical_name"],
            "entity_type": "PERSON",
            "subtype": row["person_type"],
            "description": row["description"],
        }
        for row in people
    ]
    write_csv(
        ENTITY_AUTHORITY_CSV,
        ["entity_key", "canonical_name", "entity_type", "subtype", "description"],
        person_rows + non_person,
    )

    entity_alias_rows = [
        {
            "alias": row["alias"],
            "entity_key": row["person_key"],
            "alias_type": row["alias_type"],
            "priority": row["priority"],
            "notes": row["notes"],
        }
        for row in aliases
    ]
    write_csv(ENTITY_ALIAS_CSV, ["alias", "entity_key", "alias_type", "priority", "notes"], entity_alias_rows)


def convert_relationships() -> None:
    rows = read_csv(PERSON_RELATIONSHIP_CSV)
    semantic_rows = []
    kinship_rows = []
    marriage_rows = []
    service_rows = []

    for row in rows:
        semantic = {
            "relation_id": row.get("relation_id", ""),
            "source_person_key": row.get("source", ""),
            "target_person_key": row.get("target", ""),
            "source_name": row.get("source_name", ""),
            "target_name": row.get("target_name", ""),
            "relation_type": row.get("relation_type", ""),
            "relation_label": row.get("relation_label", ""),
            "direction": row.get("direction", ""),
            "confidence": row.get("confidence", ""),
            "source_method": row.get("source_method", ""),
            "source_text": "",
            "notes": row.get("note", ""),
            "review_status": "seed",
        }
        semantic_rows.append(semantic)

        relation_type = row.get("relation_type", "")
        if relation_type == "kin":
            kinship_rows.append(
                {
                    "kinship_id": row.get("relation_id", ""),
                    "source_person_key": row.get("source", ""),
                    "target_person_key": row.get("target", ""),
                    "source_name": row.get("source_name", ""),
                    "target_name": row.get("target_name", ""),
                    "kinship_type": row.get("relation_label", ""),
                    "direction": row.get("direction", ""),
                    "confidence": row.get("confidence", ""),
                    "source_method": row.get("source_method", ""),
                    "notes": row.get("note", ""),
                    "review_status": "seed",
                }
            )
        elif relation_type == "marriage":
            marriage_rows.append(
                {
                    "marriage_id": row.get("relation_id", ""),
                    "partner_a": row.get("source", ""),
                    "partner_b": row.get("target", ""),
                    "partner_a_name": row.get("source_name", ""),
                    "partner_b_name": row.get("target_name", ""),
                    "marriage_type": row.get("relation_label", ""),
                    "confidence": row.get("confidence", ""),
                    "source_method": row.get("source_method", ""),
                    "notes": row.get("note", ""),
                    "review_status": "seed",
                }
            )
        elif relation_type == "servant":
            service_rows.append(
                {
                    "service_id": row.get("relation_id", ""),
                    "master_key": row.get("source", ""),
                    "servant_key": row.get("target", ""),
                    "master_name": row.get("source_name", ""),
                    "servant_name": row.get("target_name", ""),
                    "service_type": row.get("relation_label", ""),
                    "household": "",
                    "confidence": row.get("confidence", ""),
                    "source_method": row.get("source_method", ""),
                    "notes": row.get("note", ""),
                    "review_status": "seed",
                }
            )

    write_csv(
        PERSON_SEMANTIC_RELATIONSHIP_CSV,
        [
            "relation_id",
            "source_person_key",
            "target_person_key",
            "source_name",
            "target_name",
            "relation_type",
            "relation_label",
            "direction",
            "confidence",
            "source_method",
            "source_text",
            "notes",
            "review_status",
        ],
        semantic_rows,
    )
    write_csv(
        PERSON_KINSHIP_CSV,
        [
            "kinship_id",
            "source_person_key",
            "target_person_key",
            "source_name",
            "target_name",
            "kinship_type",
            "direction",
            "confidence",
            "source_method",
            "notes",
            "review_status",
        ],
        kinship_rows,
    )
    write_csv(
        PERSON_MARRIAGE_CSV,
        [
            "marriage_id",
            "partner_a",
            "partner_b",
            "partner_a_name",
            "partner_b_name",
            "marriage_type",
            "confidence",
            "source_method",
            "notes",
            "review_status",
        ],
        marriage_rows,
    )
    write_csv(
        PERSON_SERVICE_RELATION_CSV,
        [
            "service_id",
            "master_key",
            "servant_key",
            "master_name",
            "servant_name",
            "service_type",
            "household",
            "confidence",
            "source_method",
            "notes",
            "review_status",
        ],
        service_rows,
    )


def main() -> None:
    people, aliases = build_person_rows()
    write_csv(PERSON_AUTHORITY_CSV, PERSON_AUTHORITY_FIELDS, people)
    write_csv(PERSON_ALIAS_CSV, PERSON_ALIAS_FIELDS, aliases)
    sync_entity_tables(people, aliases)
    convert_relationships()
    print(f"wrote {PERSON_AUTHORITY_CSV}: {len(people)} rows")
    print(f"wrote {PERSON_ALIAS_CSV}: {len(aliases)} rows")
    print(f"synced {ENTITY_AUTHORITY_CSV} and {ENTITY_ALIAS_CSV}")
    print(f"wrote {PERSON_SEMANTIC_RELATIONSHIP_CSV}")
    print(f"wrote {PERSON_KINSHIP_CSV}, {PERSON_MARRIAGE_CSV}, {PERSON_SERVICE_RELATION_CSV}")


if __name__ == "__main__":
    main()
