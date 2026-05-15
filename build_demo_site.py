#!/usr/bin/env python3
"""Sync production site assets and mirror site data into the demo site.

The production preview/deploy target is ``site/``. The ``demo/`` directory is
kept as a file-openable and GitHub Pages-compatible mirror.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


SITE_DATA = Path("site/data")
DEMO_DATA = Path("demo/data")
TEMPLATE_ASSETS = Path("templates/demo-site/assets")
SITE_ASSETS = Path("site/assets")
DEMO_ASSETS = Path("demo/assets")
JSON_FILES = [
    "articles.json",
    "basic_entity_index.json",
    "ebook.json",
    "entity_chapter_summary.json",
    "entity_paragraph_index.json",
    "person_family_tree.json",
    "person_relationship_graph.json",
    "person_relationships.json",
    "person_social_network.json",
    "search_index.json",
    "statistics.json",
]


def write_json_wrapper(json_path: Path, js_path: Path, data_key: str) -> None:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    js_path.write_text(
        f'window.DEMO_JSON = window.DEMO_JSON || {{}};\n'
        f'window.DEMO_JSON["{data_key}"] = {payload};\n',
        encoding="utf-8",
    )


def sync_data() -> None:
    DEMO_DATA.mkdir(parents=True, exist_ok=True)
    for filename in JSON_FILES:
        src = SITE_DATA / filename
        if not src.exists():
            print(f"skip missing {src}")
            continue
        dst = DEMO_DATA / filename
        shutil.copyfile(src, dst)
        write_json_wrapper(dst, DEMO_DATA / f"{filename}.js", f"data/{filename}")
        print(f"synced {src} -> {dst} and {dst.name}.js")


def sync_assets() -> None:
    if not TEMPLATE_ASSETS.exists():
        return
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)
    DEMO_ASSETS.mkdir(parents=True, exist_ok=True)
    for src in TEMPLATE_ASSETS.glob("*.css"):
        site_dst = SITE_ASSETS / src.name
        shutil.copyfile(src, site_dst)
        print(f"synced {src} -> {site_dst}")
        dst = DEMO_ASSETS / src.name
        shutil.copyfile(src, dst)
        print(f"synced {src} -> {dst}")


def main() -> None:
    if not SITE_DATA.exists():
        raise SystemExit("site/data does not exist. Run python3 build_platform_site.py first.")
    sync_data()
    sync_assets()
    print("site assets and demo mirror ready")


if __name__ == "__main__":
    main()
