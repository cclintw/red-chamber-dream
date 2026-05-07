#!/usr/bin/env python3
"""Build first-pass semantic person relationships for the platform graph.

The co-occurrence network is derived from NER statistics. This file keeps
curated semantic relationships separate so they can be reviewed and revised.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SITE_DATA = ROOT / "site" / "data"


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


def main() -> None:
    nodes = read_nodes()
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

    print(f"wrote {len(rows)} relationships")
    print(f"skipped {len(skipped)} relationships with missing nodes")


if __name__ == "__main__":
    main()
