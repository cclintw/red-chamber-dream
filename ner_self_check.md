# NER Self Check

本次先略過人工校對，保留現有 `ner.csv` 結果。

## Current Tables

- `ner_candidate.csv`: 72426 candidates
- `ner.csv`: 48815 merged entities
- `ner_conflict.csv`: 17419 conflicts
- `ner_summary.csv`: 100 summary rows
- `entity_occurrence_summary.csv`: 77 keyed entities

## Observations

1. 人物類整體可用。
   - 高頻人物如賈寶玉、賈母、王熙鳳、林黛玉、襲人、薛寶釵、王夫人都有大量命中。
   - 多數 `alias|ckip-albert-tiny` 衝突只是 CKIP 與別名表同時命中，解析結果通常正確。

2. 高歧義單字規則造成大量衝突。
   - `玉`: 常與賈寶玉、通靈寶玉、一般玉器混淆。
   - `紅`、`白`、`青`、`綠`、`紫`: 顏色單字可能出現在人名、院名、普通形容詞中。
   - `香`: 可能是氣味、物件、名字的一部分。
   - `夢`、`病`、`淚`: 更適合後續 `motif.csv`，不一定適合作為 NER 強規則。
   - `蓮`、`柳`、`竹`: 單字植物規則可能誤抓人物名或普通詞。

3. 建築與空間規則有價值。
   - `榮國府`、`寧國府`、`大觀園`、`怡紅院`、`瀟湘館` 等規則能修正 CKIP 將建築判成 PERSON/ORG/FAC 的情況。

4. `TITLE_ROLE` 類型可用但需要後續語境判斷。
   - `姑娘`、`太太`、`老爺`、`老太太` 等稱謂可做社會關係分析，但不應直接等同特定人物。

## Recommended Next Run

下一版若要提高精度，建議：

1. 將高歧義單字規則從 `ner_rule.csv` 移出，改放後續 `motif_rule.csv`。
2. 保留多字詞規則，例如 `通靈寶玉`、`大觀園`、`怡紅院`、`海棠`、`菊花`。
3. 新增中文校對表，欄位與值都以中文為主，key 只作輔助欄。

## Future Review Table Format

建議之後另產生 `ner_conflict_review_zh.csv`：

```text
衝突編號,句子編號,原句,命中文字,起始字元,結束字元,候選中文名稱,候選類型中文,目前建議中文,目前建議key,處理建議,人工決定,備註
```

中文類型建議：

```text
PERSON=人物
BUILDING=建築
PLACE=地點
ROOM_SPACE=空間
OBJECT=物件
FLOWER=花
PLANT=植物
COLOR=顏色
TITLE_ROLE=身份稱謂
MOTIF=意象
TIME=時間
FOOD=飲食
CLOTHING=服飾
MEDICINE=藥物
RELIGION_MYTH=神佛仙道
```
