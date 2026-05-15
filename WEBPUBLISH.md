# 網站生成與發布說明

展示網站由作者另行部署維護；public repository 不包含 generated site data。

本文件說明如何把已處理好的 CSV、JSON 或 SQLite 資料轉成靜態展示網站，並部署到 Firebase Hosting。

## 網站定位

目前專案有兩個網站目錄：

- `site/`：本機正式靜態網站輸出目錄，使用 `fetch("data/*.json")` 載入資料。Firebase Hosting 與正式 review 以此目錄為準。
- `demo/`：本機 file-openable mirror，額外用 `data/*.json.js` 支援直接打開 `index.html`。

目前建議：

- GitHub repo 保留程式、模板、方法論文件、citation 與授權。
- Firebase Hosting 指向 `/site`。
- `site/`、`demo/`、完整 CSV、SQLite 與 generated JSON 不建議進 public git。
- `site/` 與 `demo/` 都只展示，不接 AI API，不做後台維護。
- AI API、資料維護後台，未來另開 app 或 repo。

## 目前靜態網站頁面

`site/` 與 `demo/` 包含：

- `index.html`：主入口，包含閱讀、查詢、統計，以及 iframe 載入圖表頁。
- `person_social_graph.html`：社會網絡圖。
- `person_relationship_graph.html`：人物譜。
- `cooccurrence_graph.html`：共現圖。
- `vendor/d3.v7.min.js`：圖表使用的 D3。
- `data/*.json`：`site/` 與一般靜態主機使用。
- `data/*.json.js`：`demo/` 在 `file://` 直接開啟時使用。
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

### 社會網絡圖

功能：

- 人物共現
- 家族節點
- 語義關係：親屬、婚姻、主僕、情感、衝突等
- D3 force graph

主要資料：

- `data/person_social_network.json`
- `data/person_relationships.json`

### 人物譜

功能：

- 以家族為主要區塊呈現人物樹狀關係
- 區分血親、姻親、配偶、妻妾、僕役與旁系人物
- 用於閱讀人物世代、婚姻與家族位置，不等同於共現網絡

主要資料：

- `data/person_relationship_graph.json`
- `data/person_family_tree.json`

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
- `assets/person-social-graph.css`：社會網絡圖與人物譜共用的深色圖表頁樣式。
- `assets/cooccurrence-graph.css`：共現圖。

## 建議的網站生成流程

建立 `site/data/*.json`：

```bash
python3 build_platform_site.py
```

產生 `site/data/*.json`。

接著同步網站 assets，並建立 `demo/` mirror：

```bash
python3 build_demo_site.py
```

目前自動完成：

1. 讀取 `site/data/*.json`
2. 複製到 `demo/data/*.json`
3. 產生 `demo/data/*.json.js`
4. 從 `templates/demo-site/assets/` 同步 CSS 到 `site/assets/` 與 `demo/assets/`

HTML template 產生、graph html 更新與依 `templates/demo-site/site.config.json` 套用站名/顏色仍是後續工作。

## Firebase Hosting 發布

正式發布建議使用 `site/`：

```text
red-chamber-dream/
├── firebase.json
├── site/
└── demo/
```

`firebase.json` 已設定：

```json
{
  "hosting": {
    "public": "site"
  }
}
```

正式預覽：

```bash
make preview
```

部署：

```bash
firebase deploy
```

若需指定 project：

```bash
make deploy-firebase FIREBASE_PROJECT=your-project-id
```

## GitHub repository 發布

公開 GitHub repository 建議只保留：

```text
red-chamber-dream/
├── README.md
├── build_*.py
├── templates/
├── DATA_SCHEMA.md
├── WORKFLOW.md
├── CITATION.md
└── LICENSE
```

若不希望公開資料架構與 generated data，不建議把 `site/` 或 `demo/` 發布到 GitHub Pages。展示網站應由本機 `site/` deploy 到 Firebase Hosting 或其他自有靜態主機。

## site 與 demo 的差異

`site/` 是 Firebase Hosting 的正式輸出；`demo/` 是 file-openable mirror。兩者都是本機 generated output，不建議加入 public git，也不建議加入：

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
