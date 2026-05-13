# Workflow

本文件保存《紅樓夢知識圖譜》的完整 pipeline、步驟 0~9、各 `build_*.py` 腳本用途、完整重建流程、常見問題與重跑對照表。README 僅保留首頁導覽；操作細節集中於此。

## Workflow Overview

本專案是一套可重建的中文古典小說數位人文 workflow。它從純文字文本開始，建立語料層、標註層、關係層、資料庫層與展示層：

```text
raw text
  -> document / chapter / paragraph / sentence / token
  -> entity authority / alias / NER rules
  -> NER candidates / NER / conflicts / summaries
  -> motif annotations
  -> person social network / semantic relationships
  -> SQLite
  -> site JSON
  -> demo JSON and JSONP-style JS
```

目前流程以《紅樓夢》為預設，但設計上可遷移到其他章回小說。更換文本時，最重要的是重新整理文本 metadata、章回規則、NER 權威表、別名表、規則表、motif 規則與人物語義關係。

## Environment

建議使用 Python 3.10 以上。

本專案可使用 CKIP 斷詞與 NER。若未安裝 CKIP，`build_tables.py` 會退回 `jieba` 或簡單 regex 斷詞；但 `build_ner_tables.py` 目前需要 `ckip-transformers`。

建議安裝：

```bash
python3 -m pip install ckip-transformers jieba
```

如果只想先建立章節、段落、句子、token，可先執行：

```bash
python3 -m pip install jieba
```

## Script Index

| 腳本 | 用途 | 主要輸出 |
| --- | --- | --- |
| `build_all.py` | 依序執行主要重建流程 | CSV、JSON、demo data、SQLite |
| `build_tables.py` | 建立文獻、章節、段落、句子、token 表 | `document.csv`、`chapter.csv`、`paragraph.csv`、`sentence.csv`、`token.csv` |
| `build_ner_seed_tables.py` | 建立第一版權威表、別名表、NER 規則表 | `entity_authority.csv`、`entity_alias.csv`、`ner_rule.csv` |
| `build_ner_tables.py` | 整合 CKIP NER、別名表與規則表 | `ner_candidate.csv`、`ner.csv`、`ner_conflict.csv`、`ner_summary.csv` |
| `build_annotated_texts.py` | 產生 HTML/XML/JSON 標註文本 | `annotated_paragraphs.html`、`annotated_text.xml`、`annotated_paragraphs.json` |
| `build_motif_tables.py` | 建立意象與 motif 統計 | `motif.csv`、`motif_summary.csv`、`motif_chapter_summary.csv` |
| `build_person_social_network.py` | 建立人物共現網絡 | `person_social_nodes.csv`、`person_social_edges.csv`、`person_social_network.json` |
| `build_person_relationships.py` | 建立人物語義關係 | `person_relationship.csv`、`site/data/person_relationships.json` |
| `build_platform_site.py` | 建立網站所需 JSON | `site/data/*.json` |
| `build_demo_site.py` | 同步 demo data 並產生 `*.json.js` | `demo/data/*.json`、`demo/data/*.json.js` |
| `build_sqlite.py` | 將主要 CSV 匯入 SQLite | `corpus.sqlite` |
| `build_basic_annotation_browser.py` | 建立基礎標註瀏覽資料 | `basic_entity_index.json`、`basic_entity_summary.md` |

## Step 0: Prepare Project and Text

目的：建立專案資料夾，放入原始文本，確認文本是 UTF-8。

操作指令範例：

```text
請檢查專案資料夾，讀取其中的 txt 檔，判斷是否為章回小說，並告訴我章回標題格式。
```

使用工具：

- shell：`ls`、`rg --files`、`sed`、`head`
- Python：必要時讀取文字檔、檢查編碼與行數

輸入檔：

- `red-chamber-dream.txt`

注意事項：

- 目前腳本預設檔名是 `red-chamber-dream.txt`。
- 章回標題預設要符合 `第X回 標題`。
- 每個非空白行會被視為一個段落。

常見問題：

- 如果章回標題不是 `第X回`，需要修改 `build_tables.py` 的 `CHAPTER_RE`。
- 如果文本是簡體或有特殊標點，可能需要先正規化。

## Step 1: Build Corpus Tables

目的：把純文字文本轉成語料層基本資料表。

操作指令範例：

```text
請讀取 red-chamber-dream.txt，自動判斷章節，建立 document.csv、chapter.csv、paragraph.csv、sentence.csv、token.csv。
```

使用工具：

- Python 腳本：`build_tables.py`
- CKIP：若已安裝 `ckip-transformers`，使用 CKIP WS/POS
- jieba：若 CKIP 不可用，退回 jieba
- regex：若 jieba 也不可用，退回簡單正則切 token

執行：

```bash
python3 build_tables.py
```

產生檔案：

- `document.csv`
- `chapter.csv`
- `paragraph.csv`
- `sentence.csv`
- `token.csv`

常見問題：

- `Expected chapters 1-120` 錯誤：章回數與腳本預期不符，請修改 `expected = list(range(...))`。
- CKIP 下載模型失敗：先確認網路，或改用 jieba 建立初版 token。
- token 位置錯誤：通常是斷詞結果與原文 offset 對不齊，需要檢查標點或空白正規化。

## Step 2: Build NER Seed Tables

目的：先建立可校對的語意基礎，不直接相信模型輸出。

操作指令範例：

```text
請先依紅樓夢建立 NER 權威表、別名表、規則表，讓我可以人工校對，再用這些表重建 NER。
```

使用工具：

- Python 腳本：`build_ner_seed_tables.py`
- 人工整理規則：人物、建築、地點、身份、花草等

執行：

```bash
python3 build_ner_seed_tables.py
```

產生檔案：

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`

建議校對重點：

- `entity_authority.csv`：標準名稱、類型、entity_key 是否正確。
- `entity_alias.csv`：別名是否過度擴張，例如「怡紅」不能直接等同「怡紅公子」或「怡紅院」。
- `ner_rule.csv`：建築、地點、身份、花草是否需要規則補強。

常見問題：

- 中文與 key 混在一起不易校對：可另產生中文校對版 CSV。
- 同一字串多義：例如「寶玉」可能是人，也可能是物，需用規則或人工判斷。

## Step 3: Build NER Candidates and Final NER

目的：整合 CKIP NER、別名表與規則表，產生可分析的命名實體表。

操作指令範例：

```text
請使用 CKIP、entity_authority.csv、entity_alias.csv、ner_rule.csv 重建 ner.csv，並輸出 ner_candidate.csv、ner_conflict.csv、ner_summary.csv。
```

使用工具：

- Python 腳本：`build_ner_tables.py`
- CKIP NER：`CkipNerChunker`
- 規則比對：exact match
- 候選合併：依 priority、長度、source 分數處理重疊

執行：

```bash
python3 build_ner_tables.py
```

產生檔案：

- `ner_candidate.csv`
- `ner.csv`
- `ner_conflict.csv`
- `ner_summary.csv`
- `entity_occurrence_summary.csv`

常見問題：

- CKIP 把建築判成 ORG/FAC：可用 `ner_rule.csv` 修正。
- 人名被判成地名：提高 alias/rule priority。
- `ner_conflict.csv` 很多：先處理高頻人物與核心地點，不必一次校完。

## Step 4: Build Annotated Text Outputs

目的：讓標註可以回到原文，用於檢查與展示。

操作指令範例：

```text
請依 ner.csv 產生 HTML 與 XML 標註文本，標註要保留 entity_key、type、start、end 與來源。
```

使用工具：

- Python 腳本：`build_annotated_texts.py`
- 來源表：`chapter.csv`、`paragraph.csv`、`sentence.csv`、`ner.csv`

執行：

```bash
python3 build_annotated_texts.py
```

產生檔案：

- `annotated_paragraphs.html`
- `annotated_text.xml`
- `annotated_paragraphs.json`

注意：這些是大型產物，目前 `.gitignore` 預設不提交。若要發布標註文本，可另建 release 或資料下載包。

## Step 5: Build Motif Tables

目的：標註花、香、夢、淚、病等具有研究意義的詞群。

操作指令範例：

```text
請依 motif_rule.csv 建立 motif.csv、motif_summary.csv、motif_chapter_summary.csv，並統計人物與意象共現。
```

使用工具：

- Python 腳本：`build_motif_tables.py`
- 規則表：`motif_rule.csv`
- 來源表：`sentence.csv`、`token.csv`、`ner.csv`

執行：

```bash
python3 build_motif_tables.py
```

產生檔案：

- `motif.csv`
- `motif_summary.csv`
- `motif_chapter_summary.csv`
- `person_motif_cooccurrence.csv`

常見問題：

- motif 太寬：例如「夢」可能是一般詞，也可能是敘事層夢境。
- 新文本要重寫 `motif_rule.csv`，不能直接套用紅樓夢規則。

## Step 6: Build Person Cooccurrence Network

目的：由 NER 結果建立人物節點與人物共現邊。

操作指令範例：

```text
請依 ner.csv 建立人物社會網絡，輸出 person_social_nodes.csv、person_social_edges.csv、person_social_network.json。
```

使用工具：

- Python 腳本：`build_person_social_network.py`
- 來源表：`ner.csv`、`entity_authority.csv`
- 演算法：以段落為共現單位，統計人物同段出現次數

執行：

```bash
python3 build_person_social_network.py
```

產生檔案：

- `person_social_nodes.csv`
- `person_social_edges.csv`
- `person_social_network.json`

常見問題：

- 共現不是語義關係：同段出現不等於親屬或情感關係。
- 節點太多：前端可設定節點上限與權重門檻。

## Step 7: Build Semantic Person Relationships

目的：補上親屬、婚姻、主僕、情感、衝突等人工語義關係。

操作指令範例：

```text
請依人物權威表與人物網絡，建立第一版 person_relationship.csv，類型包含親屬、婚姻、主僕、情感、衝突，並產生網站用 JSON。
```

使用工具：

- Python 腳本：`build_person_relationships.py`
- 來源資料：`site/data/person_social_network.json`
- 人工整理的 `RELATIONS`

執行：

```bash
python3 build_person_relationships.py
```

產生檔案：

- `person_relationship.csv`
- `site/data/person_relationships.json`

常見問題：

- 目前此腳本是紅樓夢專用。
- 若換文本，應把 `RELATIONS` 改成外部 CSV，避免每次改 Python。

## Step 8: Build SQLite Database

目的：把主要 CSV 統一匯入 SQLite，方便後續查詢、API 或正式網站使用。

操作指令範例：

```text
請把目前所有主要 CSV 匯入 SQLite，建立 corpus.sqlite，並建立常用查詢索引。
```

使用工具：

- Python 腳本：`build_sqlite.py`
- Python 標準庫：`sqlite3`

執行：

```bash
python3 build_sqlite.py
```

產生檔案：

- `corpus.sqlite`

檢查資料庫：

```bash
sqlite3 corpus.sqlite ".tables"
sqlite3 corpus.sqlite "select count(*) from paragraph;"
sqlite3 corpus.sqlite "select canonical_name, count(*) from ner group by canonical_name order by count(*) desc limit 10;"
```

注意：`corpus.sqlite` 是可重建的大型產物，預設不建議提交 GitHub。

## Step 9: Build Website Data

目的：把 CSV/JSON 轉成前端可讀的資料格式。

操作指令範例：

```text
請依目前 CSV 與 JSON 產生 site/data/*.json，讓靜態網站可以讀取全文、查詢、統計、人物關係與共現資料。
```

使用工具：

- Python 腳本：`build_platform_site.py`
- 來源表：`chapter.csv`、`paragraph.csv`、`sentence.csv`、`ner.csv`、`motif*.csv`、`person_social_network.json`

執行：

```bash
python3 build_platform_site.py
```

產生檔案：

- `site/data/ebook.json`
- `site/data/search_index.json`
- `site/data/basic_entity_index.json`
- `site/data/entity_chapter_summary.json`
- `site/data/entity_paragraph_index.json`
- `site/data/statistics.json`
- `site/data/person_social_network.json`
- `site/data/articles.json`

同步 demo：

```bash
python3 build_demo_site.py
```

`build_demo_site.py` 會複製 `site/data/*.json` 到 `demo/data/*.json`，並產生對應的 `demo/data/*.json.js`：

```javascript
window.DEMO_JSON["data/ebook.json"] = {...};
```

注意：`build_platform_site.py` 目前的 `articles.json` 會重建為占位資料；若已手動編輯探索文章資料，執行後需要再確認。

## Source Text Format

目前 `build_tables.py` 預設讀取：

```text
red-chamber-dream.txt
```

章回標題需符合這種格式：

```text
第一回 甄士隱夢幻識通靈 賈雨村風塵懷閨秀
第二回 賈夫人仙逝揚州城 冷子興演說榮國府
```

每個非空白行會被視為一個段落。句子由 `。！？；：` 等標點切分。

## Reusing the Workflow with Another Text

例如要改處理《三國演義》：

1. 將文本放到專案根目錄，例如：

```text
三國演義.txt
```

2. 修改 `build_tables.py` 開頭常數：

```python
SOURCE = Path("三國演義.txt")
DOC_ID = "sanguoyanyi"
CHAPTER_RE = re.compile(r"^第([一二三四五六七八九十百〇零0-9]+)回\s*(.*)$")
```

3. 修改文件 metadata：

```python
"title": "三國演義",
"author": "羅貫中",
```

4. 修改章回數檢查。

目前紅樓夢寫死為 120 回：

```python
expected = list(range(1, 121))
```

如果是《三國演義》通行本 120 回，可以不改；如果是其他章回數，請改成對應數字，例如 100 回：

```python
expected = list(range(1, 101))
```

若暫時不想限制章回數，也可以改成只檢查是否有讀到章回。

5. 後續 `build_ner_tables.py` 也有：

```python
DOC_ID = "hongloumeng"
```

請改成同一個 document id，例如：

```python
DOC_ID = "sanguoyanyi"
```

處理其他文本時，以下資料一定要重新校對：

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`
- `motif_rule.csv`
- `build_person_relationships.py` 或 `person_relationship.csv`

## Rebuild Commands

完整重建時可直接執行：

```bash
python3 build_all.py
```

`build_all.py` 預設不執行 `build_ner_seed_tables.py`，避免覆蓋已人工校對的 `entity_authority.csv`、`entity_alias.csv`、`ner_rule.csv`。

若要連種子表也重建：

```bash
python3 build_all.py --with-seed
```

若只想重建 CSV/JSON/demo，不建立 SQLite：

```bash
python3 build_all.py --skip-sqlite
```

若只想重建 CSV/JSON/SQLite，不同步 demo：

```bash
python3 build_all.py --skip-demo
```

`build_all.py` 預設等同於依序執行：

```bash
python3 build_tables.py
python3 build_ner_tables.py
python3 build_motif_tables.py
python3 build_person_social_network.py
python3 build_platform_site.py
python3 build_person_relationships.py
python3 build_demo_site.py
python3 build_sqlite.py
```

若需要重建 NER seed tables，請先執行 `python3 build_ner_seed_tables.py`，人工校對 `entity_authority.csv`、`entity_alias.csv`、`ner_rule.csv` 後，再執行後續流程。

## Rerun Matrix

本專案目前不是即時資料庫網站。多數頁面讀取的是已產生的 CSV/JSON 檔，因此修改來源表後需要重新執行對應腳本，網站資料才會更新。

| 修改內容 | 常見修改檔案 | 需要重跑的腳本 |
| --- | --- | --- |
| 更換原始文本、章回規則、書名、作者、章回數 | `red-chamber-dream.txt`、`build_tables.py` | `python3 build_tables.py`，再依完整重建順序往下跑 |
| 修改權威表、別名表、NER 規則 | `entity_authority.csv`、`entity_alias.csv`、`ner_rule.csv` | `python3 build_ner_tables.py`、`python3 build_motif_tables.py`、`python3 build_person_social_network.py`、`python3 build_platform_site.py`、`python3 build_person_relationships.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改 NER 種子產生邏輯 | `build_ner_seed_tables.py` | `python3 build_ner_seed_tables.py`，人工校對後再跑 `python3 build_ner_tables.py` 與後續腳本 |
| 修改意象 / motif 規則 | `motif_rule.csv` | `python3 build_motif_tables.py`、`python3 build_platform_site.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改人物共現演算法 | `build_person_social_network.py` | `python3 build_person_social_network.py`、`python3 build_platform_site.py`、`python3 build_person_relationships.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改人物語義關係 | `build_person_relationships.py` 內的 `RELATIONS`，或後續改成 `person_relationship.csv` | `python3 build_person_relationships.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改網站資料產生邏輯 | `build_platform_site.py` | `python3 build_platform_site.py`，必要時再跑 `python3 build_person_relationships.py`，最後跑 `python3 build_demo_site.py` |
| 修改 SQLite 匯入表或索引 | `build_sqlite.py` | `python3 build_sqlite.py` |
| 只修改網站樣式 | `demo/assets/*.css`、`site/assets/*.css`、`templates/demo-site/assets/*.css` | 不需重跑資料腳本，重新整理瀏覽器即可 |
| 只修改 `site/` 或 `demo/` HTML/JS | `site/*.html`、`demo/*.html` | 不需重跑資料腳本，重新整理瀏覽器即可 |

如果只要把已產生的 `site/data/*.json` 同步到展示站，執行：

```bash
python3 build_demo_site.py
```

## Current Limitations

- 目前多數腳本仍以《紅樓夢》為預設，部分常數需要手動修改。
- `build_tables.py` 假設文本是章回小說，章回標題符合「第X回」格式。
- `build_ner_tables.py` 需要 CKIP NER。
- `build_person_relationships.py` 目前內建紅樓夢人物關係，不適合直接套用其他小說。
- `build_all.py` 預設不重建 NER seed tables，避免覆蓋人工校對資料。

## Future Work

- 將 `SOURCE`、`DOC_ID`、書名、作者、章回數改成 `config.json`。
- 將人物關係從 Python 常數改成可校對的 CSV。
- 為 SQLite 加上更完整的欄位型別、主鍵與外鍵。
- 建立正式公開文件，補充欄位說明、NER 校對指南與資料流程圖。
