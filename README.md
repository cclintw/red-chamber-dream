# 紅樓夢知識圖譜

展示網站：[https://cclintw.github.io/red-chamber-dream/](https://cclintw.github.io/red-chamber-dream/)

本專案是一個以《紅樓夢》為範例的中文古典小說數位人文工作流。它從純文字文本開始，逐步建立章節、段落、句子、token、NER、意象、人物關係、共現統計、SQLite 資料庫，以及可部署到 GitHub Pages 的靜態展示網站。

目前專案包含兩個網站版本：

- `site/`：一般靜態網站版本，透過 `fetch()` 讀取 `data/*.json`，建議用本機 server 或正式網站伺服器開啟。
- `demo/`：展示版網站，額外包含 `data/*.json.js`，可直接雙擊 `demo/index.html`，也可部署到 GitHub Pages。
- `templates/demo-site/`：展示網站版型規格與可重用 CSS。

## 專案目標

這個 repo 不只是一個《紅樓夢》網站，也是一套可重複使用的文本處理範本。使用者可以把 `red-chamber-dream.txt` 換成其他章回小說，例如 `三國演義.txt`，再依照流程重建：

- `document.csv`
- `chapter.csv`
- `paragraph.csv`
- `sentence.csv`
- `token.csv`
- `ner.csv`
- `motif.csv`
- 人物關係與共現表
- `corpus.sqlite`
- `site/data/*.json`
- `demo/data/*.json` 與 `demo/data/*.json.js`

## 目前功能

- 全文閱讀：章節清單、段落編號、文內標註、詞頻資訊。
- 查詢：支援精確字串與實體擴展查詢。
- NER：以 CKIP、權威表、別名表、規則表建立基本實體標註。
- 人物關係圖：整合人物共現與人工整理的親屬、婚姻、主僕、情感等關係。
- 共現圖：依段落建立人物、建築、地點、身份、花草等實體共現。
- 統計：人物、NER 類型、意象、章回字數與段落統計。
- SQLite：可將主要 CSV 表匯入 `corpus.sqlite`。

## 目錄說明

```text
.
├── red-chamber-dream.txt          # 原始文本
├── build_tables.py                # 建立 document/chapter/paragraph/sentence/token
├── build_ner_seed_tables.py        # 建立第一版權威表、別名表、NER 規則表
├── build_ner_tables.py             # 建立 NER 候選、NER 結果、衝突與摘要
├── build_motif_tables.py           # 建立意象/花草等 motif 表
├── build_person_social_network.py  # 建立人物共現網絡
├── build_person_relationships.py   # 建立人物語義關係
├── build_platform_site.py          # 建立 site/data/*.json
├── build_demo_site.py              # 同步 demo/data 並產生 demo/data/*.json.js
├── build_all.py                    # 一鍵重建主要資料流程
├── build_sqlite.py                 # 將主要 CSV 匯入 corpus.sqlite
├── *.csv                           # 語料表、NER 表、意象表、人物關係表
├── site/                           # 一般靜態網站
└── demo/                           # GitHub Pages 展示網站
```

## 環境需求

建議使用 Python 3.10 以上。

本專案可使用 CKIP 斷詞與 NER。若未安裝 CKIP，`build_tables.py` 會退回 `jieba` 或簡單 regex 斷詞，但 `build_ner_tables.py` 目前需要 `ckip-transformers`。

建議安裝：

```bash
python3 -m pip install ckip-transformers jieba
```

如果只想先建立章節、段落、句子、token，可先執行：

```bash
python3 -m pip install jieba
```

## 建置流程

以下流程說明如何從原始文本開始，逐步建立章節、段落、分句、token、NER、意象、人物關係、SQLite 資料庫與網站資料。每一步列出操作目標、建議指令、使用工具、輸出檔案與常見問題。

### 步驟 0：準備專案與文本

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

### 步驟 1：建立文獻表、章節表、段落表、分句表、token 表

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

可能安裝的套件：

```bash
python3 -m pip install ckip-transformers jieba
```

執行：

```bash
python3 build_tables.py
```

產生檔案：

- `document.csv`：文獻表
- `chapter.csv`：章節表
- `paragraph.csv`：段落表
- `sentence.csv`：分句表
- `token.csv`：斷詞與詞性表

常見問題：

- `Expected chapters 1-120` 錯誤：章回數與腳本預期不符，請修改 `expected = list(range(...))`。
- CKIP 下載模型失敗：先確認網路，或改用 jieba 建立初版 token。
- token 位置錯誤：通常是斷詞結果與原文 offset 對不齊，需要檢查標點或空白正規化。

### 步驟 2：建立 NER 權威表、別名表、規則表

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

### 步驟 3：建立 NER 候選、正式 NER 與衝突表

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

### 步驟 4：建立 HTML/XML 標註輸出

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

### 步驟 5：建立意象 / motif 表

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

### 步驟 6：建立人物共現網絡

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

### 步驟 7：建立人物語義關係

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

### 步驟 8：建立 SQLite 資料庫

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

注意：`corpus.sqlite` 是可重建的大型產物，預設不提交 GitHub。

### 步驟 9：產生網站資料

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

網站發布與版型模板請看：

- [WEBPUBLISH.md](WEBPUBLISH.md)
- [templates/demo-site/README.md](templates/demo-site/README.md)

## 原始文本格式

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

## 換成其他文本

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

## 建立基礎語料表

執行：

```bash
python3 build_tables.py
```

會輸出：

- `document.csv`
- `chapter.csv`
- `paragraph.csv`
- `sentence.csv`
- `token.csv`

其中：

- `document.csv`：文獻表
- `chapter.csv`：章節表
- `paragraph.csv`：段落表
- `sentence.csv`：分句表
- `token.csv`：斷詞與詞性表

## 建立 NER 權威表、別名表與規則表

第一次處理新文本時，先建立或重建種子表：

```bash
python3 build_ner_seed_tables.py
```

會產生或更新：

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`

這三個表是 NER 品質的核心：

- `entity_authority.csv`：權威表，定義標準實體。
- `entity_alias.csv`：別名表，例如同一人物的不同稱呼。
- `ner_rule.csv`：規則表，用於補強模型容易錯判的建築、地點、身份、花草等。

處理其他文本時，這三個表一定要人工校對。以《三國演義》為例，人物、地名、官職、陣營、戰役都應重新整理。

## 建立 NER 表

執行：

```bash
python3 build_ner_tables.py
```

會輸出：

- `ner_candidate.csv`
- `ner.csv`
- `ner_conflict.csv`
- `ner_summary.csv`
- `entity_occurrence_summary.csv`

建議先檢查：

- `ner_conflict.csv`：重疊候選與類型衝突。
- `ner_summary.csv`：各類型統計。
- `entity_occurrence_summary.csv`：實體出現次數。

## 建立意象 / motif 表

執行：

```bash
python3 build_motif_tables.py
```

會輸出：

- `motif.csv`
- `motif_summary.csv`
- `motif_chapter_summary.csv`
- `person_motif_cooccurrence.csv`

`motif_rule.csv` 是規則來源。若更換文本，請依文本特性重建規則。例如《紅樓夢》重視花、香、夢、病、淚；《三國演義》可能更重視戰爭、兵器、官職、地名、陣營、計策。

## 建立人物社會網絡

人物共現網絡：

```bash
python3 build_person_social_network.py
```

會輸出：

- `person_social_nodes.csv`
- `person_social_edges.csv`
- `person_social_network.json`

人物語義關係：

```bash
python3 build_person_relationships.py
```

會輸出：

- `person_relationship.csv`
- `site/data/person_relationships.json`

注意：`build_person_relationships.py` 目前內建的是《紅樓夢》人物關係。若更換文本，必須修改此腳本中的 `RELATIONS`，或改成讀取新的關係 CSV。

## 建立 SQLite 資料庫

執行：

```bash
python3 build_sqlite.py
```

會建立：

```text
corpus.sqlite
```

`corpus.sqlite` 是產生物，檔案可能很大，預設不建議提交到 GitHub。使用者下載專案後可自行執行 `python3 build_sqlite.py` 重建。

目前會匯入以下主要 CSV：

- `document`
- `chapter`
- `paragraph`
- `sentence`
- `token`
- `entity_authority`
- `entity_alias`
- `ner_rule`
- `ner_candidate`
- `ner`
- `ner_conflict`
- `ner_summary`
- `entity_occurrence_summary`
- `motif_rule`
- `motif`
- `motif_summary`
- `motif_chapter_summary`
- `person_motif_cooccurrence`
- `person_social_nodes`
- `person_social_edges`
- `person_relationship`

檢查資料庫：

```bash
sqlite3 corpus.sqlite ".tables"
sqlite3 corpus.sqlite "select count(*) from paragraph;"
sqlite3 corpus.sqlite "select canonical_name, count(*) from ner group by canonical_name order by count(*) desc limit 10;"
```

## 建立網站資料

產生 `site/data/*.json`：

```bash
python3 build_platform_site.py
```

目前會產生或更新：

- `site/data/ebook.json`
- `site/data/search_index.json`
- `site/data/basic_entity_index.json`
- `site/data/entity_chapter_summary.json`
- `site/data/entity_paragraph_index.json`
- `site/data/statistics.json`
- `site/data/person_social_network.json`
- `site/data/articles.json`

注意：`build_platform_site.py` 目前的 `articles.json` 會重建為占位資料；若你已手動編輯探索文章資料，執行後需要再確認。

## 建立 demo 資料

`demo/` 是展示站，需要同時有 `.json` 與 `.json.js`。

目前專案中已包含 demo 資料。如果重新產生 `site/data/*.json`，需要再同步到 `demo/data/`，並把 JSON 包成 JS：

```bash
python3 build_demo_site.py
```

`build_demo_site.py` 會複製 `site/data/*.json` 到 `demo/data/*.json`，並產生對應的 `demo/data/*.json.js`：

```javascript
window.DEMO_JSON["data/ebook.json"] = {...};
```

## 本機預覽

### 只下載 demo 到本機展示

如果只想試用展示網站，不需要下載整個專案、安裝 Python 套件或重新建立 CSV/JSON。請下載並保留完整 `demo/` 資料夾：

```text
demo/
├── index.html
├── person_social_graph.html
├── cooccurrence_graph.html
├── assets/
├── data/
└── vendor/
```

下載後可直接用瀏覽器打開：

```text
demo/index.html
```

`demo/` 已包含靜態 HTML、CSS、JavaScript、JSON、`data/*.json.js` 與圖表所需的本地函式庫。`data/*.json.js` 用於支援直接以 `file://` 開啟，因此不一定需要啟動本機伺服器。

注意事項：

- 必須保留整個 `demo/` 資料夾結構，不能只複製 `index.html`。
- `data/` 是網站資料，`assets/` 是樣式，`vendor/` 是圖表函式庫。
- 若瀏覽器或作業系統限制本機檔案讀取，請改用下方 `python3 -m http.server` 的方式預覽。

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

`demo/index.html` 也可以直接用瀏覽器打開，因為它有 `data/*.json.js`。

## 部署 demo 到 GitHub Pages

建議把 `demo/` 作為展示網站部署。

做法之一：

1. 建立 GitHub repo。
2. 將整個專案 push 到 GitHub。
3. 到 GitHub repo 的 `Settings` -> `Pages`。
4. Source 選擇 `GitHub Actions`。
5. 儲存後等待 `.github/workflows/pages.yml` 部署。

GitHub Pages 會以 `demo/index.html` 作為展示入口。

## 修改資料後要重跑哪些腳本

本專案目前不是即時資料庫網站。多數頁面讀取的是已產生的 CSV/JSON 檔，因此修改來源表後需要重新執行對應腳本，網站資料才會更新。

| 修改內容 | 常見修改檔案 | 需要重跑的腳本 |
| --- | --- | --- |
| 更換原始文本、章回規則、書名、作者、章回數 | `red-chamber-dream.txt`、`build_tables.py` | `python3 build_tables.py`，再依完整重建順序往下跑 |
| 修改權威表、別名表、NER 規則 | `entity_authority.csv`、`entity_alias.csv`、`ner_rule.csv` | `python3 build_ner_tables.py`、`python3 build_motif_tables.py`、`python3 build_person_social_network.py`、`python3 build_platform_site.py`、`python3 build_person_relationships.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改 NER 種子產生邏輯 | `build_ner_seed_tables.py` | `python3 build_ner_seed_tables.py`，人工校對後再跑 `python3 build_ner_tables.py` 與後續腳本 |
| 修改意象 / motif 規則 | `motif_rule.csv` | `python3 build_motif_tables.py`、`python3 build_platform_site.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改人物共現演算法 | `build_person_social_network.py` | `python3 build_person_social_network.py`、`python3 build_platform_site.py`、`python3 build_person_relationships.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改人物語義關係 | 目前主要是 `build_person_relationships.py` 內的 `RELATIONS`，或後續改成 `person_relationship.csv` | `python3 build_person_relationships.py`、`python3 build_demo_site.py`、`python3 build_sqlite.py` |
| 修改網站資料產生邏輯 | `build_platform_site.py` | `python3 build_platform_site.py`，必要時再跑 `python3 build_person_relationships.py`，最後跑 `python3 build_demo_site.py` |
| 修改 SQLite 匯入表或索引 | `build_sqlite.py` | `python3 build_sqlite.py` |
| 只修改網站樣式 | `demo/assets/*.css`、`site/assets/*.css`、`templates/demo-site/assets/*.css` | 不需重跑資料腳本，重新整理瀏覽器即可 |
| 只修改 `site/` 或 `demo/` HTML/JS | `site/*.html`、`demo/*.html` | 不需重跑資料腳本，重新整理瀏覽器即可 |

如果只要把已產生的 `site/data/*.json` 同步到展示站，執行：

```bash
python3 build_demo_site.py
```

這會複製 `site/data/*.json` 到 `demo/data/*.json`，並自動產生 `demo/data/*.json.js`，讓 `demo/index.html` 可以直接用 `file://` 開啟。

## 建議的重建順序

完整重建時可直接執行：

```bash
python3 build_all.py
```

`build_all.py` 預設不執行 `build_ner_seed_tables.py`，避免覆蓋已人工校對的 `entity_authority.csv`、`entity_alias.csv`、`ner_rule.csv`。若要連種子表也重建，使用：

```bash
python3 build_all.py --with-seed
```

若只想重建 CSV/JSON/demo，不建立 SQLite：

```bash
python3 build_all.py --skip-sqlite
```

等同於依序執行：

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

如果更換文本，最重要的是重新整理：

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`
- `motif_rule.csv`
- `build_person_relationships.py` 或 `person_relationship.csv`

## 目前限制

- 目前多數腳本仍以《紅樓夢》為預設，部分常數需要手動修改。
- `build_tables.py` 假設文本是章回小說，章回標題符合「第X回」格式。
- `build_ner_tables.py` 需要 CKIP NER。
- `build_person_relationships.py` 目前內建紅樓夢人物關係，不適合直接套用其他小說。
- `build_all.py` 預設不重建 NER seed tables，避免覆蓋人工校對資料。

## 後續建議

- 將 `SOURCE`、`DOC_ID`、書名、作者、章回數改成 `config.json`。
- 將人物關係從 Python 常數改成可校對的 CSV。
- 為 SQLite 加上更完整的欄位型別、主鍵與外鍵。
- 建立正式公開文件，補充欄位說明、NER 校對指南與資料流程圖。

## 授權與來源

請依你使用的文本來源確認版權與授權狀態。若更換為其他文本，請確認該文本可公開使用、修改與散布。
