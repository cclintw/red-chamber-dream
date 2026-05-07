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
