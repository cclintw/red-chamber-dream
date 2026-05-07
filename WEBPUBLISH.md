# 網站生成與發布說明

目前展示網站：[https://cclintw.github.io/red-chamber-dream/](https://cclintw.github.io/red-chamber-dream/)

本文件說明如何把已處理好的 CSV、JSON 或 SQLite 資料轉成靜態展示網站，並部署到 GitHub Pages。

## 網站定位

目前專案有兩個網站目錄：

- `site/`：一般靜態網站 prototype，使用 `fetch("data/*.json")` 載入資料。
- `demo/`：GitHub Pages 展示站，額外用 `data/*.json.js` 支援直接打開 `index.html`。

目前建議：

- GitHub repo 保留完整專案。
- GitHub Pages 指向 `/demo`。
- `demo/` 只展示，不接 AI API，不做後台維護。
- 正式網站、AI API、資料維護後台，未來另開 app 或 repo。

## 目前 demo 網站頁面

`demo/` 包含：

- `index.html`：主入口，包含閱讀、查詢、統計，以及 iframe 載入圖表頁。
- `person_social_graph.html`：人物關係圖。
- `cooccurrence_graph.html`：共現圖。
- `vendor/d3.v7.min.js`：圖表使用的 D3。
- `data/*.json`：server 或 GitHub Pages 使用。
- `data/*.json.js`：`file://` 直接開啟時使用。
- `csv/`：可選下載資料，不直接被前端讀取。

## 頁面與資料依賴

### 閱讀頁

功能：

- 章節清單
- 原文閱讀
- 文內實體標註
- 右側詞頻資訊
- 段落與共現資訊

主要資料：

- `data/ebook.json`
- `data/basic_entity_index.json`

### 查詢頁

功能：

- 精確字串查詢
- 實體擴展查詢
- 分頁
- 展開 / 收合結果
- 顯示共現

主要資料：

- `data/search_index.json`
- `data/basic_entity_index.json`
- `data/ebook.json`

### 人物關係圖

功能：

- 人物共現
- 家族 / 陣營
- 語義關係：親屬、婚姻、主僕、情感、衝突等
- D3 force graph

主要資料：

- `data/person_social_network.json`
- `data/person_relationships.json`

### 共現圖

功能：

- 以段落為單位建立實體共現
- 支援人物、建築、地點、身份、花草
- 可查詢節點
- 可調整 force 物理參數

主要資料：

- `data/ebook.json`

### 統計頁

功能：

- summary cards
- 人物出現次數
- NER 類型占比
- NER 來源分布
- 意象類型占比
- 章回字數 / 段落趨勢

主要資料：

- `data/statistics.json`

## 版型範本

本專案的 demo 版型已將 CSS 從 HTML 抽出，方便後續新文本重用與修改。範本規格見：

```text
templates/demo-site/README.md
templates/demo-site/site.config.json
templates/demo-site/assets/
```

未來新文本網站應盡量只改：

- 站名
- data 檔
- 標註類型
- 顏色表
- 頁面開關

不應重新手改整份 CSS/HTML。

目前可重用的 CSS 檔：

- `assets/index.css`：主站、閱讀頁、查詢頁、統計頁、header、footer、RWD。
- `assets/person-social-graph.css`：人物關係圖。
- `assets/cooccurrence-graph.css`：共現圖。

## 建議的網站生成流程

建立 `site/data/*.json`：

```bash
python3 build_platform_site.py
```

產生 `site/data/*.json`。

接著同步到 `demo/data/`，並產生 `.json.js`：

```bash
python3 build_demo_site.py
```

目前自動完成：

1. 讀取 `site/data/*.json`
2. 複製到 `demo/data/*.json`
3. 產生 `demo/data/*.json.js`
4. 從 `templates/demo-site/assets/` 同步 CSS 到 `demo/assets/`

HTML template 產生、graph html 更新與依 `templates/demo-site/site.config.json` 套用站名/顏色仍是後續工作。

## GitHub Pages 發布

建議先使用同一個 repo：

```text
red-chamber-dream/
├── README.md
├── build_*.py
├── *.csv
├── site/
└── demo/
```

本專案已提供 GitHub Actions workflow：

```text
.github/workflows/pages.yml
```

它會在 push 到 `main` 時，把 `demo/` 目錄發布到 GitHub Pages。

GitHub Pages 設定：

1. 到 GitHub repo。
2. `Settings` -> `Pages`。
3. Source 選 `GitHub Actions`。
4. 儲存。
5. push 到 `main` 後，到 `Actions` 查看 `Deploy demo to GitHub Pages` 是否成功。

注意：若使用 GitHub Pages 的 `Deploy from a branch` 模式，GitHub 只能選 root `/` 或 `/docs` 作為發布資料夾；本專案要發布 `demo/`，所以使用 GitHub Actions。

## 正式網站與 demo 的差異

`demo/` 是靜態展示站，不建議加入：

- AI API
- 登入
- 後台維護
- 資料庫寫入
- 使用者校對流程

正式網站應另做，例如：

```text
red-chamber-dream-app/
```

正式網站可讀：

- `corpus.sqlite`
- JSON API
- PostgreSQL
- 後台校對資料表
