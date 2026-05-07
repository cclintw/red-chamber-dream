#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


NER_CSV = Path("ner.csv")
ENTITY_AUTHORITY_CSV = Path("entity_authority.csv")

PERSON_NODE_CSV = Path("person_social_nodes.csv")
PERSON_EDGE_CSV = Path("person_social_edges.csv")
PERSON_NETWORK_JSON = Path("person_social_network.json")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fieldnames} for row in rows])


def load_person_authority() -> dict[str, dict[str, str]]:
    return {
        row["entity_key"]: row
        for row in read_csv(ENTITY_AUTHORITY_CSV)
        if row["entity_type"] == "PERSON"
    }


def person_mentions() -> list[dict[str, str]]:
    people = load_person_authority()
    mentions = []
    for row in read_csv(NER_CSV):
        if row["entity_type"] != "PERSON":
            continue
        if not row["entity_key"] or row["entity_key"] not in people:
            continue
        mentions.append(row)
    return mentions


def build_nodes(mentions: list[dict[str, str]], people: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    by_person = defaultdict(list)
    for row in mentions:
        by_person[row["entity_key"]].append(row)

    nodes = []
    for key, rows in sorted(by_person.items()):
        authority = people[key]
        chapter_set = {row["chapter_id"] for row in rows}
        paragraph_set = {row["paragraph_id"] for row in rows}
        sentence_set = {row["sentence_id"] for row in rows}
        surface_counter = Counter(row["entity_text"] for row in rows)
        nodes.append(
            {
                "id": key,
                "name": authority["canonical_name"],
                "type": "PERSON",
                "subtype": authority["subtype"],
                "frequency": len(rows),
                "chapter_count": len(chapter_set),
                "paragraph_count": len(paragraph_set),
                "sentence_count": len(sentence_set),
                "surface_forms": "|".join(surface for surface, _ in surface_counter.most_common()),
                "degree": 0,
                "weighted_degree": 0,
            }
        )
    return nodes


def unique_people_by_scope(mentions: list[dict[str, str]], scope: str) -> dict[str, set[str]]:
    grouped = defaultdict(set)
    for row in mentions:
        grouped[row[scope]].add(row["entity_key"])
    return grouped


def build_edges(mentions: list[dict[str, str]], people: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    paragraph_groups = unique_people_by_scope(mentions, "paragraph_id")
    sentence_groups = unique_people_by_scope(mentions, "sentence_id")

    paragraph_counter = Counter()
    sentence_counter = Counter()
    chapter_counter = defaultdict(set)
    paragraph_examples = defaultdict(list)

    paragraph_chapters = {}
    paragraph_numbers = {}
    for row in mentions:
        paragraph_chapters[row["paragraph_id"]] = row["chapter_number"]
        paragraph_numbers[row["paragraph_id"]] = row["paragraph_number"]

    for paragraph_id, person_set in paragraph_groups.items():
        for source, target in combinations(sorted(person_set), 2):
            edge = (source, target)
            paragraph_counter[edge] += 1
            chapter_counter[edge].add(paragraph_chapters.get(paragraph_id, ""))
            if len(paragraph_examples[edge]) < 5:
                paragraph_examples[edge].append(
                    f"ch{paragraph_chapters.get(paragraph_id, '')}:p{paragraph_numbers.get(paragraph_id, '')}:{paragraph_id}"
                )

    for _, person_set in sentence_groups.items():
        for source, target in combinations(sorted(person_set), 2):
            sentence_counter[(source, target)] += 1

    edges = []
    for idx, ((source, target), paragraph_weight) in enumerate(paragraph_counter.most_common(), start=1):
        sentence_weight = sentence_counter.get((source, target), 0)
        edges.append(
            {
                "edge_id": f"person_edge_{idx:06d}",
                "source": source,
                "source_name": people[source]["canonical_name"],
                "target": target,
                "target_name": people[target]["canonical_name"],
                "relation_type": "co_occurrence",
                "scope": "paragraph",
                "weight": paragraph_weight,
                "shared_paragraph_count": paragraph_weight,
                "shared_sentence_count": sentence_weight,
                "chapter_count": len({chapter for chapter in chapter_counter[(source, target)] if chapter}),
                "chapters": "|".join(sorted({chapter for chapter in chapter_counter[(source, target)] if chapter}, key=int)),
                "examples": "|".join(paragraph_examples[(source, target)]),
            }
        )
    return edges


def add_degree_metrics(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> None:
    node_by_id = {node["id"]: node for node in nodes}
    neighbors = defaultdict(set)
    weighted = Counter()
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        weight = int(edge["weight"])
        neighbors[source].add(target)
        neighbors[target].add(source)
        weighted[source] += weight
        weighted[target] += weight
    for node in nodes:
        node["degree"] = len(neighbors[node["id"]])
        node["weighted_degree"] = weighted[node["id"]]


def build_graph_json(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> dict[str, object]:
    return {
        "metadata": {
            "network_type": "person_social_network",
            "node_type": "PERSON",
            "edge_relation": "co_occurrence",
            "edge_scope": "paragraph",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "note": "Edges represent paragraph-level co-occurrence, not confirmed kinship/romance/servitude semantics.",
        },
        "nodes": [
            {
                "id": node["id"],
                "name": node["name"],
                "type": node["type"],
                "subtype": node["subtype"],
                "frequency": node["frequency"],
                "chapter_count": node["chapter_count"],
                "paragraph_count": node["paragraph_count"],
                "degree": node["degree"],
                "weighted_degree": node["weighted_degree"],
            }
            for node in nodes
        ],
        "links": [
            {
                "source": edge["source"],
                "target": edge["target"],
                "source_name": edge["source_name"],
                "target_name": edge["target_name"],
                "relation_type": edge["relation_type"],
                "weight": edge["weight"],
                "shared_paragraph_count": edge["shared_paragraph_count"],
                "shared_sentence_count": edge["shared_sentence_count"],
                "chapter_count": edge["chapter_count"],
            }
            for edge in edges
        ],
    }


def main() -> None:
    people = load_person_authority()
    mentions = person_mentions()
    nodes = build_nodes(mentions, people)
    edges = build_edges(mentions, people)
    add_degree_metrics(nodes, edges)
    nodes.sort(key=lambda row: (-int(row["weighted_degree"]), -int(row["frequency"]), row["name"]))

    write_csv(
        PERSON_NODE_CSV,
        [
            "id",
            "name",
            "type",
            "subtype",
            "frequency",
            "chapter_count",
            "paragraph_count",
            "sentence_count",
            "degree",
            "weighted_degree",
            "surface_forms",
        ],
        nodes,
    )
    write_csv(
        PERSON_EDGE_CSV,
        [
            "edge_id",
            "source",
            "source_name",
            "target",
            "target_name",
            "relation_type",
            "scope",
            "weight",
            "shared_paragraph_count",
            "shared_sentence_count",
            "chapter_count",
            "chapters",
            "examples",
        ],
        edges,
    )
    PERSON_NETWORK_JSON.write_text(json.dumps(build_graph_json(nodes, edges), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {PERSON_NODE_CSV}: {len(nodes)} rows")
    print(f"wrote {PERSON_EDGE_CSV}: {len(edges)} rows")
    print(f"wrote {PERSON_NETWORK_JSON}")


if __name__ == "__main__":
    main()
