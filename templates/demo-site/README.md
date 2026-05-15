# Static Site Template

此資料夾記錄《紅樓夢知識平台》靜態展示站的固定版型規格。正式預覽與 Firebase Hosting 以 `site/` 為準；`demo/` 是 file-openable / GitHub Pages 相容 mirror。未來要為其他文本產生展示站時，應依此模板產生，而不是重新手刻 CSS/HTML。

## 模板目標

固定以下項目：

- header RWD 行為
- 閱讀頁左右側欄
- 文內 tag 標註樣式
- 查詢頁版型
- 社會網絡圖版型
- 人物譜版型
- 共現圖版型
- 統計圖表版型
- footer
- 色系、字體、字級、間距

可變項目：

- 站名
- 專案 GitHub URL
- 文本名稱
- 作者
- 標註類型
- tag 顏色
- 是否啟用探索頁
- 是否啟用 csv 下載

## 目前固定頁面

### 主頁 `index.html`

包含以下 view：

- `reader`：閱讀
- `search`：查詢
- `network`：社會網絡圖 iframe
- `coGraph`：共現圖 iframe
- `stats`：統計

目前「探索」選單已關閉，但資料與函式仍可保留。

### 社會網絡圖

檔案：

```text
person_social_graph.html
```

資料：

```text
data/person_social_network.json
data/person_relationships.json
```

主要設計：

- 深色背景
- 左側控制欄
- D3 force graph
- 人物節點與家族節點分形狀
- 共現線與語義關係線分線型

### 人物譜

檔案：

```text
person_relationship_graph.html
```

資料：

```text
data/person_relationship_graph.json
data/person_family_tree.json
```

主要設計：

- 以家族為區塊
- 呈現世代、配偶、妻妾、旁系、姻親與僕役
- 用於人物關係閱讀，不作為共現網絡解讀

### 共現圖

檔案：

```text
cooccurrence_graph.html
```

資料：

```text
data/ebook.json
```

主要設計：

- 深色背景
- 左側控制欄
- 節點類型圖例
- 物理參數拉桿
- 查詢 / 聚焦 / 清除

## Style Tokens

目前展示站的實際 CSS 已抽出到：

```text
templates/demo-site/assets/index.css
templates/demo-site/assets/person-social-graph.css
templates/demo-site/assets/cooccurrence-graph.css
```

對應到 `demo/` mirror：

```text
demo/assets/index.css
demo/assets/person-social-graph.css
demo/assets/cooccurrence-graph.css
```

對應到正式靜態站：

```text
site/assets/index.css
site/assets/person-social-graph.css
site/assets/cooccurrence-graph.css
```

HTML 只保留 stylesheet link：

```html
<link rel="stylesheet" href="assets/index.css">
```

圖表頁：

```html
<link rel="stylesheet" href="assets/person-social-graph.css">
<link rel="stylesheet" href="assets/cooccurrence-graph.css">
```

目前展示站核心風格參數：

```text
font.sans: -apple-system, BlinkMacSystemFont, "Noto Sans TC", "PingFang TC", sans-serif
font.serif: "Noto Serif TC", "Songti TC", "PingFang TC", "Microsoft JhengHei", serif
page.bg: #fff
panel.bg: #fff
border: #d9dee7
ink: #182230
muted: #5f6b7a
accent: #b42318
reader.maxWidth: 960px
mobile.breakpoint: 1024px
```

文內標註色：

```text
person: #fff3bf
building: #dbeafe
place: #ede9fe
role: #dcfce7
flower: #fce7f3
```

閱讀正文：

```text
font-family: serif
font-size: 16px
line-height: 1.95
font-weight: 400
letter-spacing: 0
paragraph-indent: 2em
paragraph-margin-bottom: 1em
```

## RWD Header

桌機：

```text
[左側欄 icon] [站名] [選單] [tag chips] [右側欄 icon]
```

`max-width: 1024px` 以下：

```text
[左側欄 icon] [站名] [menu icon] [右側欄 icon]
[tag chips only in reader view]
```

行動版規則：

- 主選單收進 menu icon。
- tag chips 只在閱讀頁顯示。
- tag chips 橫向 scroll。
- 左右側欄浮動覆蓋，不推正文。
- 點選章節後左側欄自動收合。
- 點選正文實體後右側欄自動展開。

## Data Contract

未來模板生成器至少要輸入：

```text
data/ebook.json
data/search_index.json
data/basic_entity_index.json
data/statistics.json
data/person_social_network.json
data/person_relationships.json
```

`demo/` 若要支援 `file://`，還需：

```text
data/*.json.js
```

格式：

```javascript
window.DEMO_JSON = window.DEMO_JSON || {};
window.DEMO_JSON["data/ebook.json"] = {...};
```

## 下一步模板化工作

目前已完成第一階段：將 HTML 內的 `<style>` 區塊抽出為 `assets/*.css`。後續若要進一步模板化，建議把目前 `site/index.html` / `demo/index.html` 拆成：

```text
templates/demo-site/
├── index.template.html
├── person_social_graph.template.html
├── cooccurrence_graph.template.html
├── assets/
│   ├── index.css
│   ├── person-social-graph.css
│   └── cooccurrence-graph.css
├── reader.js
├── search.js
├── stats.js
├── config.js
└── site.config.json
```

然後新增：

```text
build_demo_site.py
```

由 `site.config.json` 與 `site/data/*.json` 自動產生正式 `site/`，再同步出 `demo/` mirror。

## 套用到新專案

新文本專案若要套用目前版型，可先複製：

```text
templates/demo-site/assets/
```

到新專案的：

```text
demo/assets/
site/assets/
```

然後在 HTML head 中引用對應 CSS。

主入口：

```html
<link rel="stylesheet" href="assets/index.css">
```

社會網絡圖：

```html
<link rel="stylesheet" href="assets/person-social-graph.css">
```

共現圖：

```html
<link rel="stylesheet" href="assets/cooccurrence-graph.css">
```

通常新專案只需要改：

- `:root` 色票
- `.entity-*` 與 `.tag-*` 標註色
- `#readerContent` 字體、行高、寬度
- graph 背景與線條顏色
- header 選單文字

若新文本的標註類型不同，例如戰役、官職、兵器、陣營，應新增對應的 tag class，並同步修改前端的 entity type mapping。
