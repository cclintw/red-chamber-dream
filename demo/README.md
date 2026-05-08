# 紅樓夢知識平台 Demo

這個目錄是一份可部署的純靜態網站版本，使用 HTML + JavaScript + JSON，不需要後端。

Demo 同時支援兩種打開方式：

- 直接打開 `index.html`
- 用本機或正式網站伺服器打開

## 入口

- `index.html`：平台首頁
- `person_social_graph.html`：人物社會網絡 / 人物關係圖

## 目錄

- `assets/`：展示站 CSS 樣式，包含主站、人物關係圖、共現圖
- `data/`：前端實際讀取的 JSON 資料
- `data/*.json.js`：給 `file://` 直接開啟時使用的資料包裝檔
- `vendor/`：第三方前端函式庫，目前只有本地版 D3
- `csv/`：來源與校對用 CSV 表，不直接被前端讀取

## 本機測試

### 只下載 demo 到本機展示

如果只想瀏覽展示版，不需要下載整個專案或重新建置資料。請保留並下載完整 `demo/` 資料夾，目錄結構至少要包含：

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

`demo/data/*.json.js` 是為了支援直接用 `file://` 開啟而產生的資料包裝檔，因此一般瀏覽功能、查詢、統計、人物關係圖與共現圖都可以在本機展示。

注意事項：

- 不要只複製單一 `index.html`，否則 CSS、JSON 與圖表函式庫會無法載入。
- `vendor/` 內含本地版 D3，人物關係圖與共現圖需要它。
- 若瀏覽器限制本機檔案讀取，請改用下方本機伺服器方式開啟。

在專案根目錄執行：

```bash
python3 -m http.server 8767 --directory demo
```

然後打開：

```text
http://127.0.0.1:8767/
```

## 部署

將整個 `demo/` 目錄部署到任何靜態網站主機即可。請保持 `data/`、`vendor/` 與 HTML 的相對路徑不變。
