#!/usr/bin/env python3
"""Build first-pass semantic person relationships for the platform graph.

The co-occurrence network is derived from NER statistics. This file keeps
curated semantic relationships separate so they can be reviewed and revised.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SITE_DATA = ROOT / "site" / "data"
KEY_FIELDS = {
    "person": "person_key",
    "kinship": "kinship_id",
    "marriage": "marriage_id",
    "service": "service_id",
}
TREE_FAMILY_ORDER = ["賈家", "史家", "王家", "薛家", "林家", "甄家", "尤家", "其他"]
CORE_MARRIAGE_FAMILIES = {"賈家", "史家", "王家", "薛家"}
MATERNAL_OVERRIDES = {
    "賈元春": "王夫人",
    "賈珠": "王夫人",
    "賈寶玉": "王夫人",
    "賈探春": "趙姨娘",
    "賈環": "趙姨娘",
}
PATERNAL_OVERRIDES = {
    "賈敏": "賈代善",
}
AFFINAL_EXTENSION_RELATIONS = [
    ("秦可卿", "秦業", "秦可卿父"),
    ("秦可卿", "秦鍾", "秦可卿弟"),
    ("秦鍾", "智能", "秦鍾戀人"),
]
FAMILY_STRENGTH = 60
RELATION_STRENGTH = {
    "kin": 100,
    "marriage": 96,
    "servant": 88,
    "romance": 74,
    "ally": 68,
    "conflict": 64,
    "rival": 58,
}


RELATIONS = [
    # source, target, type, label, direction, confidence, note
    ("person_jia_baoyu", "person_jia_zheng", "kin", "父子", "undirected", 0.95, "賈政為賈寶玉之父。"),
    ("person_jia_baoyu", "person_wang_furen", "kin", "母子", "undirected", 0.95, "王夫人為賈寶玉之母。"),
    ("person_jia_baoyu", "person_jia_mu", "kin", "祖孫", "undirected", 0.95, "賈母為賈寶玉祖母。"),
    ("person_lin_daiyu", "person_lin_ruhai", "kin", "父女", "undirected", 0.95, "林如海為林黛玉之父。"),
    ("person_lin_daiyu", "person_jia_mu", "kin", "外祖孫", "undirected", 0.95, "林黛玉為賈母外孫女。"),
    ("person_xue_baochai", "person_xue_yima", "kin", "母女", "undirected", 0.95, "薛姨媽為薛寶釵之母。"),
    ("person_jia_lian", "person_jia_she", "kin", "父子", "undirected", 0.95, "賈赦為賈璉之父。"),
    ("person_jia_yingchun", "person_jia_she", "kin", "父女", "undirected", 0.9, "賈迎春為賈赦之女。"),
    ("person_jia_tanchun", "person_jia_zheng", "kin", "父女", "undirected", 0.95, "賈探春為賈政庶女。"),
    ("person_jia_tanchun", "person_zhao_yiniang", "kin", "母女", "undirected", 0.95, "趙姨娘為賈探春生母。"),
    ("person_jia_huan", "person_jia_zheng", "kin", "父子", "undirected", 0.95, "賈環為賈政庶子。"),
    ("person_jia_huan", "person_zhao_yiniang", "kin", "母子", "undirected", 0.95, "趙姨娘為賈環生母。"),
    ("person_jia_zhen", "person_jia_rong", "kin", "父子", "undirected", 0.95, "賈珍為賈蓉之父。"),
    ("person_jia_zhen", "person_jia_xichun", "kin", "兄妹", "undirected", 0.9, "賈惜春為寧府賈珍之妹。"),
    ("person_li_wan", "person_jia_lan", "kin", "母子", "undirected", 0.95, "李紈為賈蘭之母。"),
    ("person_jia_baoyu", "person_jia_huan", "kin", "兄弟", "undirected", 0.85, "同父異母兄弟。"),
    ("person_jia_yuanchun", "person_jia_baoyu", "kin", "姊弟", "undirected", 0.9, "賈元春為賈寶玉之姊。"),
    ("person_jia_tanchun", "person_jia_baoyu", "kin", "兄妹", "undirected", 0.85, "同父異母兄妹。"),
    ("person_jia_yingchun", "person_jia_tanchun", "kin", "姊妹", "undirected", 0.75, "賈府姊妹序列關係。"),
    ("person_jia_tanchun", "person_jia_xichun", "kin", "姊妹", "undirected", 0.75, "賈府姊妹序列關係。"),
    ("person_you_shi", "person_you_erjie", "kin", "姊妹/姻親", "undirected", 0.75, "尤氏與尤二姐為尤氏姐妹關係系統。"),
    ("person_you_shi", "person_you_sanjie", "kin", "姊妹/姻親", "undirected", 0.75, "尤氏與尤三姐為尤氏姐妹關係系統。"),
    ("person_you_erjie", "person_you_sanjie", "kin", "姊妹", "undirected", 0.9, "尤二姐、尤三姐為姐妹。"),
    ("person_zhen_shiyin", "person_xiangling", "kin", "父女", "undirected", 0.9, "香菱原名甄英蓮，甄士隱之女。"),

    ("person_jia_lian", "person_wang_xifeng", "marriage", "夫妻", "undirected", 0.95, "王熙鳳為賈璉之妻。"),
    ("person_jia_rong", "person_qin_keqing", "marriage", "夫妻", "undirected", 0.95, "秦可卿為賈蓉之妻。"),
    ("person_jia_zhen", "person_you_shi", "marriage", "夫妻", "undirected", 0.95, "尤氏為賈珍之妻。"),
    ("person_jia_baoyu", "person_xue_baochai", "marriage", "婚配", "undirected", 0.85, "金玉良緣與後文婚配線。"),
    ("person_jia_lian", "person_you_erjie", "marriage", "妾/婚配", "undirected", 0.8, "尤二姐與賈璉婚配線。"),
    ("person_xue_pan", "person_xiangling", "marriage", "妾", "undirected", 0.75, "香菱為薛蟠妾；薛蟠未在目前 48 節點中時會略過。"),
    ("person_jia_zheng", "person_zhao_yiniang", "marriage", "妾", "undirected", 0.9, "趙姨娘為賈政妾。"),

    ("person_jia_baoyu", "person_lin_daiyu", "romance", "情感", "undirected", 0.9, "木石前盟與寶黛情感線。"),
    ("person_jia_baoyu", "person_xiren", "romance", "親密/准妾", "undirected", 0.65, "襲人與寶玉有親密及准妾線索。"),
    ("person_jia_baoyu", "person_qingwen", "romance", "親近/情感", "undirected", 0.55, "晴雯與寶玉為親近情感線，需後續校對。"),

    ("person_jia_baoyu", "person_xiren", "servant", "主僕", "directed", 0.95, "襲人為寶玉身邊丫鬟。"),
    ("person_jia_baoyu", "person_qingwen", "servant", "主僕", "directed", 0.95, "晴雯為寶玉身邊丫鬟。"),
    ("person_jia_baoyu", "person_she_yue", "servant", "主僕", "directed", 0.95, "麝月為寶玉身邊丫鬟。"),
    ("person_jia_baoyu", "person_qiuwen", "servant", "主僕", "directed", 0.9, "秋紋為寶玉身邊丫鬟。"),
    ("person_lin_daiyu", "person_zijuan", "servant", "主僕", "directed", 0.95, "紫鵑為林黛玉丫鬟。"),
    ("person_lin_daiyu", "person_xueyan", "servant", "主僕", "directed", 0.95, "雪雁為林黛玉丫鬟。"),
    ("person_xue_baochai", "person_ying_er", "servant", "主僕", "directed", 0.95, "鶯兒為薛寶釵丫鬟。"),
    ("person_wang_xifeng", "person_ping_er", "servant", "主僕/陪房", "directed", 0.95, "平兒為王熙鳳陪房丫鬟。"),
    ("person_jia_mu", "person_yuanyang", "servant", "主僕", "directed", 0.95, "鴛鴦為賈母身邊丫鬟。"),
    ("person_jia_yingchun", "person_siqi", "servant", "主僕", "directed", 0.9, "司棋為迎春丫鬟。"),
    ("person_jia_tanchun", "person_shishu", "servant", "主僕", "directed", 0.9, "侍書為探春丫鬟。"),
    ("person_jia_xichun", "person_ruhua", "servant", "主僕", "directed", 0.9, "入畫為惜春丫鬟。"),
    ("person_wang_furen", "person_jinchuan", "servant", "主僕", "directed", 0.9, "金釧為王夫人丫鬟。"),
    ("person_wang_furen", "person_yuchuan", "servant", "主僕", "directed", 0.9, "玉釧為王夫人丫鬟。"),
    ("person_wang_furen", "person_zhou_rui_jia", "servant", "陪房/僕役", "directed", 0.85, "周瑞家的為王夫人陪房。"),
    ("person_jia_mu", "person_lai_da", "servant", "僕役/管家", "directed", 0.75, "賴大為賈府管家，暫連賈母代表家族權力中心。"),

    ("person_jia_baoyu", "person_qin_zhong", "ally", "友誼", "undirected", 0.8, "秦鐘未在目前 48 節點中時會略過。"),
    ("person_jia_baoyu", "person_miaoyu", "ally", "詩文/清談", "undirected", 0.55, "寶玉與妙玉的清談、品茶關係，需後續校對。"),
    ("person_lin_daiyu", "person_shi_xiangyun", "ally", "詩社/姊妹", "undirected", 0.7, "大觀園詩社與姊妹互動。"),
    ("person_xue_baochai", "person_shi_xiangyun", "ally", "詩社/姊妹", "undirected", 0.7, "大觀園詩社與姊妹互動。"),
    ("person_li_wan", "person_jia_tanchun", "ally", "理家/詩社", "undirected", 0.7, "李紈與探春在詩社、理家中同場。"),

    ("person_jia_baoyu", "person_jia_zheng", "conflict", "父子衝突", "undirected", 0.75, "教養、功名與情性衝突。"),
    ("person_lin_daiyu", "person_xue_baochai", "rival", "情感/詮釋張力", "undirected", 0.65, "寶黛釵三角詮釋張力，需作為分析類關係看待。"),
    ("person_wang_xifeng", "person_you_erjie", "conflict", "婚姻衝突", "undirected", 0.8, "王熙鳳與尤二姐的婚姻權力衝突。"),
    ("person_wang_xifeng", "person_zhao_yiniang", "conflict", "府內權力衝突", "undirected", 0.55, "府內權力與家務衝突線，需後續校對。"),
]


def read_nodes() -> dict[str, dict]:
    with (SITE_DATA / "person_social_network.json").open(encoding="utf-8") as f:
        data = json.load(f)
    return {row["id"]: row for row in data["nodes"]}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_authority() -> dict[str, dict]:
    return {row["person_key"]: row for row in read_csv(ROOT / "person_authority.csv")}


def family_of(node: dict) -> str:
    return node.get("family_group") or "其他"


def is_distant_kin(node: dict) -> bool:
    text = " ".join([node.get("description", ""), node.get("notes", ""), node.get("source_note", "")])
    return bool(re.search(r"遠房宗族|遠方親族|遠房親族|宗族遠親", text))


def display_name_of(node: dict) -> str:
    return node.get("display_name") or node.get("canonical_name") or ""


def birth_family_of(node: dict) -> str:
    text = " ".join([node.get("description", ""), node.get("notes", ""), node.get("source_note", "")])
    match = re.search(r"出身([一-龥]{1,4}家)", text)
    if match:
        return match.group(1)
    return ""


def build_graph(nodes: dict[str, dict], relationships: list[dict]) -> dict:
    graph_nodes: dict[str, dict] = {}
    graph_links = []
    families = sorted({family_of(node) for node in nodes.values()})

    for family in families:
        graph_nodes[f"family_{family}"] = {
            "id": f"family_{family}",
            "name": family,
            "type": "FAMILY",
            "family": family,
            "subtype": "family",
            "frequency": 0,
            "paragraph_count": None,
            "weighted_degree": 0,
        }

    for person_id, node in nodes.items():
        family = family_of(node)
        graph_nodes[person_id] = {**node, "family": family}
        graph_links.append(
            {
                "id": f"family:{person_id}",
                "source": f"family_{family}",
                "target": person_id,
                "source_name": family,
                "target_name": node["name"],
                "relation_type": "family",
                "relation_label": "家族成員",
                "direction": "undirected",
                "weight": FAMILY_STRENGTH,
                "confidence": None,
                "source_method": "person_authority_family_group",
            }
        )

    for rel in relationships:
        weight = RELATION_STRENGTH.get(
            rel["relation_type"],
            max(40, round(float(rel.get("confidence") or 0.5) * 90)),
        )
        graph_links.append(
            {
                **rel,
                "id": f"semantic:{rel['relation_id']}",
                "weight": weight,
            }
        )

    return {
        "metadata": {
            "graph_type": "person_relationship_graph",
            "description": "Curated semantic person relationships plus family membership nodes.",
            "person_node_count": len(nodes),
            "family_node_count": len(families),
            "semantic_relationship_count": len(relationships),
            "family_membership_count": len(nodes),
        },
        "nodes": list(graph_nodes.values()),
        "links": graph_links,
    }


def normalized_names(authority: dict[str, dict]) -> dict[str, str]:
    names = {}
    for key, row in authority.items():
        names[row["canonical_name"]] = key
    for row in read_csv(ROOT / "person_alias.csv"):
        person_key = row.get("person_key")
        alias = row.get("alias")
        if person_key in authority and alias:
            names.setdefault(alias, person_key)
    return names


def split_names(value: str) -> list[str]:
    if not value:
        return []
    value = re.sub(r"[（）()「」『』]", "", value)
    parts = re.split(r"[、,，/／；;與和及]", value)
    return [part.strip() for part in parts if part.strip()]


def relation_targets(text: str, labels: list[str]) -> list[str]:
    names: list[str] = []
    for label in labels:
        pattern = rf"{label}\s*[:：]\s*([^。；;]+?)(?=\s*[妻夫妾子女孫母父]\s*[:：]|[。；;]|$)"
        for match in re.finditer(pattern, text):
            names.extend(split_names(match.group(1)))
    return names


def parent_names_from_text(text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"([^，。；;、]+?)之[男女]?[子女]", text):
        names.extend(split_names(match.group(1)))
    for match in re.finditer(r"([一-龥]{2,4}?)[長次庶]?[子女]", text):
        names.append(match.group(1).strip())
    return names


def add_parent_child(parent_child: dict[str, set[str]], parent: str, child: str) -> None:
    if parent and child and parent != child:
        parent_child[parent].add(child)


def add_pair(relations: dict[str, list[dict]], left: str, right: str, rel_type: str, label: str) -> None:
    if not left or not right or left == right:
        return
    item = {"person_key": right, "type": rel_type, "label": label}
    if item not in relations[left]:
        relations[left].append(item)


def add_side_child(
    side_children: dict[str, list[dict]],
    anchor: str,
    child: str,
    label: str,
    side_type: str = "kin",
    affinal_anchor: str = "",
) -> None:
    if not anchor or not child or anchor == child:
        return
    item = {"person_key": child, "label": label, "side_type": side_type, "affinal_anchor": affinal_anchor}
    if item not in side_children[anchor]:
        side_children[anchor].append(item)


def reciprocal_marriage_label(label: str) -> str:
    if "妾" in label:
        return "夫"
    if "妻" in label:
        return "夫"
    if "夫" in label:
        return "妻"
    if label == "夫妻":
        return "夫"
    return label


def forward_marriage_label(label: str) -> str:
    if label == "夫妻":
        return "妻"
    return label


def build_family_tree(authority: dict[str, dict]) -> dict:
    name_to_key = normalized_names(authority)
    parent_child: dict[str, set[str]] = defaultdict(set)
    side_children: dict[str, list[dict]] = defaultdict(list)
    side_child_candidates: list[dict] = []
    spouses: dict[str, list[dict]] = defaultdict(list)
    services: dict[str, list[dict]] = defaultdict(list)
    side_relations: dict[str, list[dict]] = defaultdict(list)

    for row in authority.values():
        key = row["person_key"]
        text = " ".join([row.get("description", ""), row.get("notes", "")])
        for name in relation_targets(text, ["子"]):
            add_parent_child(parent_child, key, name_to_key.get(name, ""))
        for name in relation_targets(text, ["女"]):
            add_parent_child(parent_child, key, name_to_key.get(name, ""))
        for label in ["妻", "夫", "妾"]:
            for name in relation_targets(text, [label]):
                target = name_to_key.get(name, "")
                add_pair(spouses, key, target, "marriage", label)
                add_pair(spouses, target, key, "marriage", reciprocal_marriage_label(label))
        for match in re.finditer(r"([一-龥]{2,5}?)之(妻|夫|妾)", text):
            target = name_to_key.get(match.group(1), "")
            label = match.group(2)
            add_pair(spouses, target, key, "marriage", label)
            add_pair(spouses, key, target, "marriage", reciprocal_marriage_label(label))
        for label in ["母", "父"]:
            for name in relation_targets(text, [label]):
                add_parent_child(parent_child, name_to_key.get(name, ""), key)
        for name in parent_names_from_text(text):
            add_parent_child(parent_child, name_to_key.get(name, ""), key)
        for match in re.finditer(r"([一-龥]{2,5}?)(?:之|的)?(內?侄女|內?侄子|內?侄)", text):
            anchor = name_to_key.get(match.group(1), "")
            label = match.group(2).removeprefix("內")
            if label == "侄":
                label = "侄女" if (row.get("gender") or "").lower() == "female" and "小廝" not in text else "侄子"
            side_child_candidates.append(
                {
                    "anchor": anchor,
                    "anchor_name": match.group(1),
                    "child": key,
                    "label": label,
                }
            )

    for row in read_csv(ROOT / "person_kinship.csv"):
        source = row["source_person_key"]
        target = row["target_person_key"]
        kinship_type = row["kinship_type"]
        if kinship_type in {"父子", "父女", "母子", "母女"}:
            source_name = row["source_name"]
            target_name = row["target_name"]
            notes = row.get("notes", "")
            if re.search(rf"{re.escape(source_name)}為{re.escape(target_name)}之[父母]", notes):
                add_parent_child(parent_child, source, target)
            elif re.search(rf"{re.escape(target_name)}為{re.escape(source_name)}之[父母]", notes):
                add_parent_child(parent_child, target, source)
            else:
                add_parent_child(parent_child, target, source)
        elif kinship_type in {"祖孫", "外祖孫"}:
            add_pair(side_relations, source, target, "kinship", kinship_type)
            add_pair(side_relations, target, source, "kinship", kinship_type)
        else:
            add_pair(side_relations, source, target, "kinship", kinship_type)
            add_pair(side_relations, target, source, "kinship", kinship_type)

    for row in read_csv(ROOT / "person_marriage.csv"):
        left = row["partner_a"]
        right = row["partner_b"]
        label = row["marriage_type"]
        add_pair(spouses, left, right, "marriage", forward_marriage_label(label))
        add_pair(spouses, right, left, "marriage", reciprocal_marriage_label(label))

    marriage_family_anchor: dict[str, str] = {}
    for person, items in spouses.items():
        for item in items:
            partner = item["person_key"]
            if person not in authority or partner not in authority:
                continue
            person_family = family_of(authority[person])
            partner_family = family_of(authority[partner])
            if person_family in CORE_MARRIAGE_FAMILIES and partner_family not in CORE_MARRIAGE_FAMILIES:
                marriage_family_anchor[partner] = person

    for item in side_child_candidates:
        anchor = item["anchor"]
        child = item["child"]
        if anchor not in authority or child not in authority:
            continue
        if family_of(authority[anchor]) in CORE_MARRIAGE_FAMILIES:
            add_side_child(side_children, anchor, child, item["label"], "kin")
        elif anchor in marriage_family_anchor:
            anchor_name = display_name_of(authority[anchor])
            add_side_child(
                side_children,
                marriage_family_anchor[anchor],
                child,
                f"{anchor_name}{item['label']}",
                "affinal",
                anchor,
            )

    for anchor_name, relative_name, label in AFFINAL_EXTENSION_RELATIONS:
        anchor = name_to_key.get(anchor_name, "")
        add_side_child(
            side_children,
            marriage_family_anchor.get(anchor, anchor),
            name_to_key.get(relative_name, ""),
            label,
            "affinal",
            anchor if anchor in marriage_family_anchor else "",
        )

    for row in read_csv(ROOT / "person_service_relation.csv"):
        master = row["master_key"]
        servant = row["servant_key"]
        if master in authority and servant in authority:
            services[master].append(
                {
                    "person_key": servant,
                    "name": display_name_of(authority[servant]),
                    "label": row["service_type"],
                    "family": authority[servant].get("family_group") or "其他",
                    "household": row.get("household") or authority[servant].get("household"),
                    "residence": authority[servant].get("residence") or "",
                    "residence_detail": authority[servant].get("residence_detail") or "",
                }
            )

    for child_name, parent_name in PATERNAL_OVERRIDES.items():
        add_parent_child(parent_child, name_to_key.get(parent_name, ""), name_to_key.get(child_name, ""))

    child_to_parents: dict[str, set[str]] = defaultdict(set)
    for parent, children in parent_child.items():
        for child in children:
            child_to_parents[child].add(parent)
    side_child_to_anchor: dict[str, str] = {}
    side_child_labels: dict[str, str] = {}
    side_child_types: dict[str, str] = {}
    side_child_affinal_anchors: dict[str, str] = {}
    for anchor, children in side_children.items():
        for item in children:
            side_child_to_anchor[item["person_key"]] = anchor
            side_child_labels[item["person_key"]] = item["label"]
            side_child_types[item["person_key"]] = item.get("side_type") or "kin"
            if item.get("affinal_anchor"):
                side_child_affinal_anchors[item["person_key"]] = item["affinal_anchor"]

    generation_cache: dict[str, int] = {}

    def generation(key: str, stack: set[str] | None = None) -> int:
        if key in generation_cache:
            return generation_cache[key]
        stack = set() if stack is None else stack
        if key in stack:
            generation_cache[key] = 1
            return 1
        stack.add(key)
        if child_to_parents.get(key):
            generation_cache[key] = 1 + max(generation(parent, stack) for parent in child_to_parents[key])
        elif key in side_child_to_anchor:
            generation_cache[key] = generation(side_child_to_anchor[key], stack) + 1
        else:
            generation_cache[key] = 1
        stack.remove(key)
        return generation_cache[key]

    def person_node(key: str, seen: set[str] | None = None, context_family: str | None = None) -> dict:
        seen = set() if seen is None else seen
        row = authority[key]
        family = family_of(row)
        birth_family = birth_family_of(row)
        is_birth_family_context = bool(context_family and birth_family == context_family and family != context_family)
        is_affinal_relative = side_child_types.get(key) == "affinal"
        gen = generation(key)
        children = []
        if key not in seen and not is_birth_family_context:
            next_seen = {*seen, key}
            if not is_affinal_relative:
                children = [
                    person_node(child, next_seen, family)
                    for child in sorted(parent_child.get(key, []), key=person_order)
                    if child in authority and should_attach_child_to_parent(key, child)
                ]
                children.extend(
                    person_node(item["person_key"], next_seen, family)
                    for item in sorted(side_children.get(key, []), key=lambda item: person_order(item["person_key"]))
                    if item["person_key"] in authority
                )
            else:
                children.extend(
                    person_node(item["person_key"], next_seen, family)
                    for item in sorted(side_children.get(key, []), key=lambda item: person_order(item["person_key"]))
                    if item["person_key"] in authority
                )
        spouse_items = [
            {
                "person_key": item["person_key"],
                "name": display_name_of(authority[item["person_key"]]),
                "label": item["label"],
                "family": family_of(authority[item["person_key"]]),
                "birth_family": birth_family_of(authority[item["person_key"]]),
                "household": authority[item["person_key"]].get("household"),
                "residence": authority[item["person_key"]].get("residence") or "",
                "residence_detail": authority[item["person_key"]].get("residence_detail") or "",
            }
            for item in spouses.get(key, [])
            if item["person_key"] in authority
        ]
        relation_items = [
            {
                "person_key": item["person_key"],
                "name": display_name_of(authority[item["person_key"]]),
                "label": item["label"],
            }
            for item in side_relations.get(key, [])
            if item["person_key"] in authority
        ]
        parent_items = [
            {
                "person_key": parent,
                "name": display_name_of(authority[parent]),
                "family": family_of(authority[parent]),
                "birth_family": birth_family_of(authority[parent]),
            }
            for parent in sorted(child_to_parents.get(key, set()), key=person_order)
            if parent in authority
        ]
        override_mother = name_to_key.get(MATERNAL_OVERRIDES.get(row["canonical_name"], ""))
        if override_mother and override_mother not in {item["person_key"] for item in parent_items}:
            parent_items.append(
                {
                    "person_key": override_mother,
                    "name": display_name_of(authority[override_mother]),
                    "family": family_of(authority[override_mother]),
                    "birth_family": birth_family_of(authority[override_mother]),
                }
            )
        return {
            "person_key": key,
            "name": display_name_of(row),
            "canonical_name": row["canonical_name"],
            "gender": row.get("gender") or "unknown",
            "family": family,
            "birth_family": birth_family,
            "context_family": context_family or family,
            "household": row.get("household") or "未標定",
            "residence": row.get("residence") or "",
            "residence_detail": row.get("residence_detail") or "",
            "generation": gen,
            "generation_label": f"第{gen}代",
            "side_label": side_child_labels.get(key, ""),
            "side_type": side_child_types.get(key, ""),
            "affinal_anchor_key": side_child_affinal_anchors.get(key, ""),
            "role_category": row.get("role_category") or "",
            "description": row.get("description") or "",
            "notes": row.get("notes") or "",
            "spouses": spouse_items,
            "parents": parent_items,
            "services": services.get(key, []),
            "side_relations": relation_items,
            "children": children,
        }

    def should_attach_child_to_parent(parent: str, child: str) -> bool:
        parent_row = authority[parent]
        if (parent_row.get("gender") or "").lower() != "female":
            return True
        parent_family = parent_row.get("family_group") or "其他"
        child_family = authority[child].get("family_group") or "其他"
        other_parents = [
            other
            for other in child_to_parents.get(child, set())
            if other != parent and other in authority
        ]
        if not other_parents:
            return True
        return not any(
            (authority[other].get("family_group") or "其他") == child_family
            and child_family != parent_family
            for other in other_parents
        )

    def descendant_count(key: str, seen: set[str] | None = None) -> int:
        seen = set() if seen is None else seen
        if key in seen:
            return 0
        next_seen = {*seen, key}
        lineage_count = sum(1 + descendant_count(child, next_seen) for child in parent_child.get(key, set()) if child in authority)
        side_count = sum(
            1 + descendant_count(item["person_key"], next_seen)
            for item in side_children.get(key, [])
            if item["person_key"] in authority
        )
        return lineage_count + side_count

    def birth_order(row: dict) -> int:
        text = " ".join([row.get("description", ""), row.get("notes", "")])
        name = row.get("canonical_name", "")
        explicit = {
            "賈演": 1,
            "賈源": 2,
        }
        if name in explicit:
            return explicit[name]
        markers = [
            ("長子", 1),
            ("長女", 1),
            ("次子", 2),
            ("次女", 2),
            ("三子", 3),
            ("三女", 3),
            ("庶子", 20),
            ("庶女", 20),
        ]
        for marker, value in markers:
            if marker in text:
                return value
        return 50

    def person_order(key: str) -> tuple:
        row = authority[key]
        return (generation(key), birth_order(row), row["canonical_name"])

    core_embedded_keys: set[str] = set()
    for person, items in spouses.items():
        if person not in authority:
            continue
        for item in items:
            partner = item["person_key"]
            if partner not in authority:
                continue
            if family_of(authority[person]) in CORE_MARRIAGE_FAMILIES and family_of(authority[partner]) not in CORE_MARRIAGE_FAMILIES:
                core_embedded_keys.add(partner)
    for master, items in services.items():
        if master in authority and family_of(authority[master]) in CORE_MARRIAGE_FAMILIES:
            core_embedded_keys.update(item["person_key"] for item in items if item["person_key"] in authority)
    changed = True
    while changed:
        changed = False
        for child, anchor in side_child_to_anchor.items():
            if anchor in authority and (family_of(authority[anchor]) in CORE_MARRIAGE_FAMILIES or anchor in core_embedded_keys):
                if child not in core_embedded_keys:
                    core_embedded_keys.add(child)
                    changed = True

    families = []
    for family in TREE_FAMILY_ORDER:
        members = [
            key
            for key, row in authority.items()
            if (
                (family == "其他" and is_distant_kin(row))
                or family_of(row) == family
                or birth_family_of(row) == family
            )
        ]
        if not members:
            continue
        roots = []
        for key in members:
            row = authority[key]
            if family != "其他" and is_distant_kin(row):
                continue
            if family == "其他" and key in core_embedded_keys and not is_distant_kin(row):
                continue
            if family != "其他" and birth_family_of(row) == family and family_of(row) != family:
                roots.append(key)
                continue
            if any(parent in members for parent in child_to_parents.get(key, set())):
                continue
            if key in side_child_to_anchor:
                continue
            roots.append(key)
        roots = sorted(roots, key=lambda key: (generation(key), birth_order(authority[key]), -descendant_count(key), authority[key]["canonical_name"]))
        families.append(
            {
                "family": family,
                "member_count": len(members),
                "roots": [person_node(key, context_family=family) for key in roots],
                "unplaced": [],
            }
        )

    return {
        "metadata": {
            "graph_type": "person_family_tree",
            "description": "Family-block organization chart derived from person authority, kinship, marriage, and service relation tables.",
            "family_count": len(families),
            "person_count": len(authority),
        },
        "families": families,
    }


def main() -> None:
    nodes = read_nodes()
    authority = read_authority()
    rows = []
    skipped = []
    for idx, rel in enumerate(RELATIONS, start=1):
        source, target, rel_type, label, direction, confidence, note = rel
        if source not in nodes or target not in nodes:
            skipped.append(
                {
                    "source": source,
                    "target": target,
                    "relation_type": rel_type,
                    "label": label,
                    "reason": "missing_node",
                }
            )
            continue
        rows.append(
            {
                "relation_id": f"hongloumeng_pr{idx:04d}",
                "source": source,
                "target": target,
                "source_name": nodes[source]["name"],
                "target_name": nodes[target]["name"],
                "relation_type": rel_type,
                "relation_label": label,
                "direction": direction,
                "confidence": confidence,
                "source_method": "seed_manual_v1",
                "note": note,
            }
        )

    fieldnames = [
        "relation_id",
        "source",
        "target",
        "source_name",
        "target_name",
        "relation_type",
        "relation_label",
        "direction",
        "confidence",
        "source_method",
        "note",
    ]
    with (ROOT / "person_relationship.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with (SITE_DATA / "person_relationships.json").open("w", encoding="utf-8") as f:
        json.dump({"relationships": rows, "skipped": skipped}, f, ensure_ascii=False, indent=2)

    graph = build_graph(nodes, rows)
    with (SITE_DATA / "person_relationship_graph.json").open("w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    family_tree = build_family_tree(authority)
    with (SITE_DATA / "person_family_tree.json").open("w", encoding="utf-8") as f:
        json.dump(family_tree, f, ensure_ascii=False, indent=2)

    print(f"wrote {len(rows)} relationships")
    print(f"wrote {len(graph['nodes'])} relationship graph nodes")
    print(f"wrote {len(graph['links'])} relationship graph links")
    print(f"wrote {family_tree['metadata']['person_count']} family tree persons")
    print(f"skipped {len(skipped)} relationships with missing nodes")


if __name__ == "__main__":
    main()
