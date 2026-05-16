# 紅樓夢知識平台

《紅樓夢知識平台》是一個以《紅樓夢》為範例的數位人文研究 workflow 說明專案。它不只是《紅樓夢》網站，而是一套可重用的 Digital Humanities 方法框架：從古典小說文本出發，透過 NLP、權威表、標註、知識圖譜與靜態展示資料，建立可查詢、可分析、可視覺化、可引用的研究平台。

本 repo 提供數位人文 workflow 的方法論概覽、資料架構說明、研究腳本、引用規範與授權資訊，適合作為古典小說語料處理、標註設計與知識圖譜建構的參考基礎。

## Project Overview

本專案展示一種 annotation-oriented corpus architecture。其核心不是單一資料庫或單一網站，而是將文學文本轉換為可檢查、可重建、可延伸的研究資料流程。

方法特色包括：

- Digital Humanities：以可引用、可重建的方式整理文學文本。
- NLP：使用斷詞、命名實體辨識與規則補強建立初步標註。
- Annotation：結合自動處理、權威表、別名表與人工校對。
- Knowledge Graph：整理人物、地點、建築、身份、意象與關係。
- Hybrid Workflow：保留演算法產物與人工研究判讀的共存空間。
- Static Publication：將研究資料轉為可部署的靜態展示資料。

## Research Goals

本專案希望回答：

- 古典小說如何從純文字轉換為結構化語料？
- 人物、地點、建築、身份與意象如何被標註與校對？
- 自動 NER、人工權威表與規則補強如何形成可解釋的 annotation pipeline？
- 人物共現網絡與人工整理的語義關係如何並存？
- 數位人文資料如何以可重建、可引用、可展示的方式保存？

## Repository Contents

本 repo 主要包含：

- 數位人文 workflow 說明
- annotation-oriented corpus architecture 概覽
- corpus construction、annotation、motif、network 與 relationship modeling 相關 scripts
- 學術引用與 Research Attribution 規範
- GPL-3.0-or-later 授權

研究者可依自身語料、標註規則與研究問題調整 scripts，建立適合不同古典小說或文學文本的 annotation workflow。

## Conceptual Workflow

```text
plain text
  -> corpus segmentation
  -> tokenization
  -> named entity recognition
  -> authority table normalization
  -> annotation review
  -> motif and thematic tagging
  -> social network / relationship modeling
  -> research database
  -> static digital humanities website
```

## Getting Started

使用本 repo 時，建議先釐清下列研究層次：

- corpus segmentation：文本層級與可引用的閱讀單位
- authority normalization：人物、別名與實體標準化方法
- annotation workflow：NER、motif 與人工校對流程
- relationship modeling：人物語義關係、親屬、婚姻、主僕或其他研究關係
- presentation outputs：查詢、統計、網絡與展示層所需的衍生資料

更多概念層資料架構說明請見 [DATA_SCHEMA.md](DATA_SCHEMA.md)。

## Run the Example Workflow

本 repo 內含一組 minimal example，可用來測試 workflow scripts：

```bash
python3 build_tables.py
python3 build_ner_seed_tables.py
python3 build_person_authority.py
python3 build_ner_tables.py
python3 build_motif_tables.py
python3 build_person_relationships.py
python3 build_person_occurrence_summary.py
python3 build_person_social_network.py
python3 build_annotated_texts.py
python3 build_basic_annotation_browser.py
```

輸出會產生於：

```text
public_output/
```

這組 example 展示從文本切分、實體標註、motif 標註、人物關係、共現網絡到簡易 HTML 檢視頁的基本流程。

## Citation

若您在論文、研究計畫、教學、網站、軟體、資料庫、數位人文平台或衍生系統中使用、引用、改作或參考本專案的方法論、資料流程、標註流程、knowledge graph 設計或展示架構，請註明來源。

建議引用格式：

```text
林春成. 紅樓夢知識平台：數位人文工作流與知識圖譜建構示範. GitHub repository, 2026.
https://github.com/cclintw/red-chamber-dream
```

完整引用格式與方法論引用規範請見 [CITATION.md](CITATION.md)。

## Research Attribution

本專案屬於數位人文研究 workflow 示範平台。若引用、改作或延伸以下內容，請保留方法論來源說明：

- 從文本到 corpus layer 的建構流程。
- 權威表、別名表與規則補強結合的 annotation workflow。
- 人物、地點、建築、身份與意象的標註方法。
- 人物譜、共現網絡與知識圖譜的概念設計。
- annotation-oriented corpus architecture。
- hybrid workflow 在古典小說研究中的應用。

## License

本專案授權資訊請以 repository 中的正式授權檔案或 citation metadata 為準；目前採用 GPL-3.0-or-later。

程式碼授權不代表放棄研究方法、文件架構、schema 設計、標註流程與 knowledge graph workflow 的學術署名需求。若引用、改作、移植或延伸本專案的研究流程與方法論，請保留適當學術引用與來源說明。

## Documentation

- [DATA_SCHEMA.md](DATA_SCHEMA.md)：公開版資料架構概覽。
- [CITATION.md](CITATION.md)：學術引用格式、Research Attribution 與方法論引用規範。
- [LICENSE](LICENSE)：授權條款。
