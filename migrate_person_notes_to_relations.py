#!/usr/bin/env python3
"""Migrate structured person notes into normalized relationship tables."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REL_LABELS = ["父", "母", "夫", "妻", "妾", "子", "女", "孫"]
REL_PATTERN = re.compile(
    rf"(?:(?<=^)|(?<=[\s，,；;、]))(?P<label>{'|'.join(REL_LABELS)})\s*[:：]?\s*"
    rf"(?P<value>.*?)(?=(?:[\s，,；;、](?:{'|'.join(REL_LABELS)})\s*[:：]?)|$)"
)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def authority_index(rows: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
    by_key = {row["person_key"]: row for row in rows}
    names: dict[str, str] = {}
    for row in rows:
        names[row["canonical_name"]] = row["person_key"]
    for row in read_csv(ROOT / "person_alias.csv"):
        key = row.get("person_key", "")
        alias = row.get("alias", "")
        if key in by_key and alias:
            names.setdefault(alias, key)
    return by_key, names


def split_names(value: str) -> list[str]:
    value = re.sub(r"[（）()「」『』]", "", value)
    value = value.replace("及", "、").replace("與", "、").replace("和", "、")
    parts = re.split(r"[、,，/／；; ]+", value)
    return [part.strip() for part in parts if part.strip()]


def resolve_name(name: str, names: dict[str, str]) -> str:
    if name in names:
        return names[name]
    if name == "趙":
        name = "趙姨娘"
    if name in names:
        return names[name]
    matches = sorted(
        (candidate for candidate in names if candidate and (candidate in name or name in candidate)),
        key=len,
        reverse=True,
    )
    return names[matches[0]] if matches else ""


def note_relations(note: str) -> list[tuple[str, list[str], str]]:
    relations = []
    for match in REL_PATTERN.finditer(note or ""):
        value = match.group("value").strip(" ，,、；;")
        if not value:
            continue
        relations.append((match.group("label"), split_names(value), match.group(0)))
    return relations


def child_kinship(parent: dict, child: dict, child_label: str) -> str:
    parent_gender = parent.get("gender")
    child_gender = "male" if child_label == "子" else "female" if child_label == "女" else child.get("gender")
    if parent_gender == "mother" or parent_gender == "female":
        return "母女" if child_gender == "female" else "母子"
    return "父女" if child_gender == "female" else "父子"


def parent_kinship(parent: dict, child: dict, label: str) -> str:
    if label == "母":
        return "母女" if child.get("gender") == "female" else "母子"
    return "父女" if child.get("gender") == "female" else "父子"


def add_kinship(
    rows: list[dict],
    existing: set[tuple[str, str, str]],
    child: dict,
    parent: dict,
    kinship_type: str,
    note: str,
) -> None:
    key = (child["person_key"], parent["person_key"], kinship_type)
    if key in existing:
        return
    existing.add(key)
    parent_role = "母" if kinship_type.startswith("母") else "父" if kinship_type.startswith("父") else "祖輩"
    rows.append(
        {
            "kinship_id": f"hongloumeng_mig_kin{len([r for r in rows if r['kinship_id'].startswith('hongloumeng_mig_kin')]) + 1:04d}",
            "source_person_key": child["person_key"],
            "target_person_key": parent["person_key"],
            "source_name": child["canonical_name"],
            "target_name": parent["canonical_name"],
            "kinship_type": kinship_type,
            "direction": "undirected",
            "confidence": "0.9",
            "source_method": "migrated_person_authority_notes",
            "notes": note.replace("父母輩", parent_role),
            "review_status": "migrated",
        }
    )


def add_marriage(
    rows: list[dict],
    existing: set[frozenset[str]],
    partner_a: dict,
    partner_b: dict,
    marriage_type: str,
    note: str,
) -> None:
    key = frozenset([partner_a["person_key"], partner_b["person_key"]])
    if key in existing:
        return
    existing.add(key)
    rows.append(
        {
            "marriage_id": f"hongloumeng_mig_mar{len([r for r in rows if r['marriage_id'].startswith('hongloumeng_mig_mar')]) + 1:04d}",
            "partner_a": partner_a["person_key"],
            "partner_b": partner_b["person_key"],
            "partner_a_name": partner_a["canonical_name"],
            "partner_b_name": partner_b["canonical_name"],
            "marriage_type": marriage_type,
            "confidence": "0.9",
            "source_method": "migrated_person_authority_notes",
            "notes": note,
            "review_status": "migrated",
        }
    )


def cleaned_note(note: str) -> str:
    cleaned = note or ""
    for _, _, raw in note_relations(cleaned):
        cleaned = cleaned.replace(raw, "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ，,、；;")


def main() -> None:
    authority = read_csv(ROOT / "person_authority.csv")
    by_key, names = authority_index(authority)
    kinship = read_csv(ROOT / "person_kinship.csv")
    marriage = read_csv(ROOT / "person_marriage.csv")
    unresolved: list[dict] = []

    existing_kin = {
        (row["source_person_key"], row["target_person_key"], row["kinship_type"])
        for row in kinship
    }
    existing_marriage = {
        frozenset([row["partner_a"], row["partner_b"]])
        for row in marriage
    }

    for row in authority:
        person = by_key[row["person_key"]]
        for label, candidates, raw in note_relations(row.get("notes", "")):
            for candidate in candidates:
                target_key = resolve_name(candidate, names)
                if not target_key:
                    unresolved.append(
                        {
                            "person_key": row["person_key"],
                            "person_name": row["canonical_name"],
                            "relation_label": label,
                            "unresolved_name": candidate,
                            "source_note": raw,
                        }
                    )
                    continue
                target = by_key[target_key]
                if label in {"父", "母"}:
                    add_kinship(
                        kinship,
                        existing_kin,
                        person,
                        target,
                        parent_kinship(target, person, label),
                        f"{target['canonical_name']}為{person['canonical_name']}之{label}。",
                    )
                elif label in {"子", "女"}:
                    add_kinship(
                        kinship,
                        existing_kin,
                        target,
                        person,
                        child_kinship(person, target, label),
                        f"{person['canonical_name']}為{target['canonical_name']}之父母輩。",
                    )
                elif label == "孫":
                    add_kinship(
                        kinship,
                        existing_kin,
                        target,
                        person,
                        "祖孫",
                        f"{target['canonical_name']}為{person['canonical_name']}之孫輩。",
                    )
                elif label == "夫":
                    add_marriage(marriage, existing_marriage, target, person, "夫妻", f"{target['canonical_name']}為{person['canonical_name']}之夫。")
                elif label == "妻":
                    add_marriage(marriage, existing_marriage, person, target, "夫妻", f"{target['canonical_name']}為{person['canonical_name']}之妻。")
                elif label == "妾":
                    add_marriage(marriage, existing_marriage, person, target, "妾", f"{target['canonical_name']}為{person['canonical_name']}之妾。")
        row["notes"] = cleaned_note(row.get("notes", ""))

    write_csv(ROOT / "person_authority.csv", authority, list(authority[0].keys()))
    write_csv(ROOT / "person_kinship.csv", kinship, list(kinship[0].keys()))
    write_csv(ROOT / "person_marriage.csv", marriage, list(marriage[0].keys()))
    write_csv(
        ROOT / "person_relationship_migration_unresolved.csv",
        unresolved,
        ["person_key", "person_name", "relation_label", "unresolved_name", "source_note"],
    )
    print(f"wrote {len(kinship)} kinship rows")
    print(f"wrote {len(marriage)} marriage rows")
    print(f"wrote {len(unresolved)} unresolved migrated names")


if __name__ == "__main__":
    main()
