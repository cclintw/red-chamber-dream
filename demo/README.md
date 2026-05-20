# 紅樓夢知識圖譜展示版

這是一個可下載到本機使用的《紅樓夢》知識圖譜展示網站。網站使用純 HTML、CSS、JavaScript 與靜態 JSON，不需要安裝後端、不需要資料庫，也不需要重新建置資料。

展示版包含：

- 查詢：支援精確字串與實體擴展查詢。
- 瀏覽：閱讀原文、章節切換、文內標註、詞頻資訊與共現。
- 人物關係圖：人物共現與人物語義關係視覺化。
- 共現圖：人物、身份、建築、地點、花草等實體共現。
- 統計：人物、NER 類型、意象、章回字數與段落統計。

## 使用方式

1. 在 GitHub 頁面點選 `Code`。
2. 選擇 `Download ZIP`。
3. 將 ZIP 解壓縮。
4. 打開資料夾中的 `index.html`。

一般情況下，直接雙擊 `index.html` 即可使用。

## 目錄說明

```text
.
├── index.html
├── person_social_graph.html
├── cooccurrence_graph.html
├── assets/
├── data/
└── vendor/
```

- `index.html`：展示網站入口。
- `person_social_graph.html`：人物關係圖。
- `cooccurrence_graph.html`：實體共現圖。
- `assets/`：網站樣式。
- `data/`：展示資料，包含 JSON 與支援本機開啟的 `*.json.js`。
- `vendor/`：本地第三方函式庫，目前包含 D3。

## 注意事項

- 請保留完整資料夾結構，不要只複製單一 `index.html`。
- 請不要刪除 `assets/`、`data/`、`vendor/`，否則網站無法正常運作。
- 若瀏覽器限制本機檔案讀取，可用本機伺服器開啟。

## 本機伺服器方式

若直接打開 `index.html` 有問題，可在資料夾上一層執行：

```bash
python3 -m http.server 8767 --directory red-chamber-dream-demo
```

然後打開：

```text
http://127.0.0.1:8767/
```

## 資料來源與完整專案

完整建置流程、CSV、資料庫與產生腳本請見：

[https://github.com/cclintw/red-chamber-dream](https://github.com/cclintw/red-chamber-dream)

本展示版由完整專案中的 `demo/` 目錄整理而成。
