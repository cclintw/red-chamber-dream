# 紅樓夢知識圖譜

展示網站：[https://cclintw.github.io/red-chamber-dream/](https://cclintw.github.io/red-chamber-dream/)

《紅樓夢知識圖譜》是一個以《紅樓夢》為範例的數位人文研究平台。它不只是一個《紅樓夢》網站，而是一套可重用的 Digital Humanities workflow：從純文字文本出發，逐步建立章節、段落、句子、token、命名實體、意象標註、人物關係、共現網絡、SQLite 資料庫與可部署到 GitHub Pages 的展示網站。

本專案結合 NLP、規則標註、權威表校對、Knowledge Graph 與靜態網站發布流程，展示如何把章回小說轉換成可查詢、可分析、可視覺化、可重建的研究資料集。它同時保留演算法產物與人工校對空間，適合作為中文古典小說、文學社會網絡、語料標註、知識圖譜與數位策展的教學與研究範本。

## Project Overview

本 repo 的核心定位是「開源研究平台」而非單一網頁成品。它提供一個混合式工作流：先以 Python 腳本與 NLP 工具建立基礎語料表，再用權威表、別名表與規則表修正命名實體，最後把 CSV、SQLite 與 JSON 轉換為前端可用的靜態資料。

專案特別關注：

- Digital Humanities：將文學文本轉換為可重建、可引用、可檢查的研究資料。
- NLP：使用 CKIP、jieba 或 regex 建立斷詞、詞性與 NER 基礎。
- Knowledge Graph：建立人物、地點、建築、身份、意象與關係資料。
- Annotation：保留標註來源、offset、entity key、canonical name 與規則優先權。
- Hybrid Workflow：結合模型輸出、規則比對與人工整理，而非完全依賴自動化。
- GitHub Pages demo：以靜態網站展示全文閱讀、查詢、統計與圖譜視覺化。

## Live Demo

展示網站：

[https://cclintw.github.io/red-chamber-dream/](https://cclintw.github.io/red-chamber-dream/)

目前專案包含兩個網站版本：

- `site/`：一般靜態網站版本，透過 `fetch()` 讀取 `data/*.json`，建議用本機 server 或正式網站伺服器開啟。
- `demo/`：GitHub Pages 展示版網站，額外包含 `data/*.json.js`，可直接雙擊 `demo/index.html`，也可部署到 GitHub Pages。
- `templates/demo-site/`：展示網站版型規格與可重用 CSS。

## Research Goals

這個 repo 的目標不是把《紅樓夢》做成單一封閉資料庫，而是示範一套可移植的中文文本處理流程。使用者可以把 `red-chamber-dream.txt` 換成其他章回小說，例如《三國演義》，再依照同一套 workflow 重建語料表、標註表、人物網絡、SQLite 與展示網站。

本專案希望回答的問題包括：

- 古典小說如何從純文字轉換為結構化語料？
- 文學文本中的人物、地點、建築、身份與意象如何被標註與校對？
- 自動 NER、人工權威表與規則補強如何形成可解釋的 annotation pipeline？
- 人物共現網絡與人工語義關係如何同時存在於一個 knowledge graph？
- 研究資料如何以 CSV、SQLite、JSON 與 GitHub Pages 形式公開、重建與引用？

## Core Features

- 全文閱讀：章節清單、段落編號、文內標註、詞頻資訊。
- 查詢：支援精確字串與實體擴展查詢。
- NER：以 CKIP、權威表、別名表、規則表建立基本實體標註。
- Annotation pipeline：保留 char offset、token 對應、source、priority 與 confidence。
- 人物關係圖：整合人物共現與人工整理的親屬、婚姻、主僕、情感等關係。
- 共現圖：依段落建立人物、建築、地點、身份、花草等實體共現。
- 意象分析：以 motif 規則標註花、香、夢、淚、病等研究詞群。
- 統計資料：人物、NER 類型、意象、章回字數與段落統計。
- SQLite：可將主要 CSV 表匯入 `corpus.sqlite`，供查詢、API 或後續研究使用。
- GitHub Pages demo：展示站可部署為純靜態網站，不依賴後端服務。

## Core Workflow

本專案的核心流程如下：

```text
red-chamber-dream.txt
        |
        v
document / chapter / paragraph / sentence / token CSV
        |
        v
entity authority / alias / NER rules
        |
        v
NER candidates -> NER -> conflict and summary tables
        |
        v
motif annotations + person cooccurrence + semantic relationships
        |
        v
SQLite database + site/data JSON
        |
        v
site/ and demo/ static websites
```

簡化後的重建命令：

```bash
python3 build_all.py
```

若需要連同 NER seed tables 重新產生：

```bash
python3 build_all.py --with-seed
```

完整 pipeline、步驟 0~9、重跑腳本對照表與限制說明請見 [WORKFLOW.md](WORKFLOW.md)。

## Quick Start

建議使用 Python 3.10 以上。

安裝基本套件：

```bash
python3 -m pip install ckip-transformers jieba
```

若只想先建立章節、段落、句子與 token，可先安裝：

```bash
python3 -m pip install jieba
```

重建主要資料：

```bash
python3 build_all.py
```

只重建 CSV、JSON 與 demo，不建立 SQLite：

```bash
python3 build_all.py --skip-sqlite
```

建立網站資料：

```bash
python3 build_platform_site.py
python3 build_demo_site.py
```

預覽 `site/`：

```bash
python3 -m http.server 8766 --directory site
```

打開：

```text
http://127.0.0.1:8766/
```

預覽 `demo/`：

```bash
python3 -m http.server 8767 --directory demo
```

打開：

```text
http://127.0.0.1:8767/
```

`demo/index.html` 也可以直接用瀏覽器打開，因為它包含 `data/*.json.js` 作為 `file://` 預覽支援。

## Repository Structure

```text
.
├── red-chamber-dream.txt          # 原始文本
├── build_all.py                   # 一鍵重建主要資料流程
├── build_tables.py                # 建立 document/chapter/paragraph/sentence/token
├── build_ner_seed_tables.py        # 建立權威表、別名表、NER 規則表
├── build_ner_tables.py             # 建立 NER 候選、結果、衝突與摘要
├── build_motif_tables.py           # 建立 motif 標註與統計
├── build_person_social_network.py  # 建立人物共現網絡
├── build_person_relationships.py   # 建立人物語義關係
├── build_platform_site.py          # 建立 site/data/*.json
├── build_demo_site.py              # 同步 demo/data 並產生 demo/data/*.json.js
├── build_sqlite.py                 # 將主要 CSV 匯入 corpus.sqlite
├── *.csv                           # 語料表、NER 表、意象表、人物關係表
├── site/                           # 一般靜態網站
├── demo/                           # GitHub Pages 展示網站
├── templates/demo-site/            # demo 版型與 CSS 範本
├── WORKFLOW.md                     # 完整 pipeline 與重建流程
├── DATA_SCHEMA.md                  # CSV / SQLite / JSON 結構說明
└── CITATION.md                     # 學術引用與方法論引用規範
```

詳細 CSV、SQLite 與 JSON 欄位說明請見 [DATA_SCHEMA.md](DATA_SCHEMA.md)。

## Citation

若您在論文、研究計畫、教學、網站、軟體、資料庫、數位人文平台或衍生系統中使用、引用、改作或參考本專案的方法論、資料流程、表格設計、標註流程、知識圖譜架構、網站展示方式或程式碼，請註明來源。

建議引用格式：

```text
林春成. 紅樓夢知識圖譜：數位人文工作流與知識圖譜建構示範. GitHub repository, 2026.
https://github.com/cclintw/red-chamber-dream
```

BibTeX：

```bibtex
@misc{lin2026redchamberdream,
  author       = {Lin, Chance},
  title        = {紅樓夢知識圖譜：數位人文工作流與知識圖譜建構示範},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/cclintw/red-chamber-dream}
}
```

完整引用格式與方法論引用規範請見 [CITATION.md](CITATION.md)。

## Research Attribution

本專案屬於數位人文研究 workflow 示範平台。若引用、改作或延伸以下內容，請保留方法論來源說明：

- 從純文字到章節、段落、句子、token 的語料建構流程。
- 權威表、別名表與規則表結合的 NER 標註流程。
- 文學文本中的人物、地點、建築、身份、意象與共現分析。
- 人物關係圖、共現網絡與統計資料的產生方式。
- CSV、SQLite、JSON 與靜態網站之間的轉換流程。
- 可部署至 GitHub Pages 的數位人文展示網站架構。
- annotation pipeline、schema 設計、knowledge graph 設計與 hybrid workflow。

若您改作本專案，建議在 README、論文註腳、網站說明或專案文件中註明：

> 本專案部分方法、資料流程或系統設計參考自 Chance Lin 的「紅樓夢知識圖譜」專案。

本專案保留原創方法論與學術引用權利。程式碼授權不代表放棄研究方法、文件架構、schema 設計、標註流程與 knowledge graph workflow 的學術署名需求。

## License and Sources

本專案授權資訊請以 repository 中的正式授權檔案或 citation metadata 為準；目前 citation metadata 標示為 MIT。

本專案方法論、文件、資料流程與架構說明，引用時請依照本文「Citation」與 [CITATION.md](CITATION.md) 註明來源。

請依您使用的文本來源確認版權與授權狀態。若更換為其他文本，請確認該文本可公開使用、修改與散布。

## Documentation

- [WORKFLOW.md](WORKFLOW.md)：完整 pipeline、步驟 0~9、腳本用途、完整重建流程與重跑對照表。
- [DATA_SCHEMA.md](DATA_SCHEMA.md)：CSV、SQLite、JSON 欄位與資料結構說明。
- [CITATION.md](CITATION.md)：學術引用格式、Research Attribution 與方法論引用規範。
- [WEBPUBLISH.md](WEBPUBLISH.md)：既有網站生成與發布補充說明。
- [templates/demo-site/README.md](templates/demo-site/README.md)：展示網站版型規格。
