# Dream of the Red Chamber Knowledge Graph

Demo website: [https://cclintw.github.io/red-chamber-dream/](https://cclintw.github.io/red-chamber-dream/)

This project is a digital humanities workflow for Chinese classical novels, using *Dream of the Red Chamber* as an example. Starting from a plain-text corpus, it gradually builds chapters, paragraphs, sentences, tokens, NER, motifs, character relationships, co-occurrence statistics, an SQLite database, and a static showcase website that can be deployed to GitHub Pages.

The project currently includes two website versions:

- `site/`: A standard static website version that uses `fetch()` to read `data/*.json`. It is recommended to open it through a local server or a production web server.
- `demo/`: A demo website version that additionally includes `data/*.json.js`. It can be opened directly by double-clicking `demo/index.html`, and it can also be deployed to GitHub Pages.
- `templates/demo-site/`: Demo website layout specifications and reusable CSS.

## Project Goals

This repository is not only a *Dream of the Red Chamber* website, but also a reusable text-processing template. Users can replace `red-chamber-dream.txt` with another chapter-based novel, such as `三國演義.txt`, and then rebuild the following according to the workflow:

- `document.csv`
- `chapter.csv`
- `paragraph.csv`
- `sentence.csv`
- `token.csv`
- `ner.csv`
- `motif.csv`
- Character relationship and co-occurrence tables
- `corpus.sqlite`
- `site/data/*.json`
- `demo/data/*.json` and `demo/data/*.json.js`

## Current Features

- Full-text reading: chapter list, paragraph numbering, inline annotations, and word frequency information.
- Search: supports exact string search and entity-expanded search.
- NER: builds basic entity annotations using CKIP, authority tables, alias tables, and rule tables.
- Character relationship graph: integrates character co-occurrence with manually curated relationships such as kinship, marriage, servant-master relationships, and emotional relationships.
- Co-occurrence graph: builds co-occurrence data by paragraph for entities such as characters, buildings, places, identities, and flowers/plants.
- Statistics: statistics for characters, NER types, motifs, chapter word counts, and paragraph counts.
- SQLite: imports the major CSV tables into `corpus.sqlite`.

## Directory Description

```text
.
├── red-chamber-dream.txt          # Original text
├── build_tables.py                # Build document/chapter/paragraph/sentence/token
├── build_ner_seed_tables.py        # Build the first version of authority tables, alias tables, and NER rule tables
├── build_ner_tables.py             # Build NER candidates, NER results, conflicts, and summaries
├── build_motif_tables.py           # Build motif tables such as imagery/flowers/plants
├── build_person_social_network.py  # Build the character co-occurrence network
├── build_person_relationships.py   # Build semantic character relationships
├── build_platform_site.py          # Build site/data/*.json
├── build_demo_site.py              # Sync demo/data and generate demo/data/*.json.js
├── build_all.py                    # One-click rebuild of the main data workflow
├── build_sqlite.py                 # Import major CSV files into corpus.sqlite
├── *.csv                           # Corpus tables, NER tables, motif tables, character relationship tables
├── site/                           # Standard static website
└── demo/                           # GitHub Pages demo website
```

## Environment Requirements

Python 3.10 or above is recommended.

This project can use CKIP for word segmentation and NER. If CKIP is not installed, `build_tables.py` will fall back to `jieba` or simple regex-based tokenization, but `build_ner_tables.py` currently requires `ckip-transformers`.

Recommended installation:

```bash
python3 -m pip install ckip-transformers jieba
```

If you only want to first build chapters, paragraphs, sentences, and tokens, you may run:

```bash
python3 -m pip install jieba
```

## Build Workflow

The following workflow explains how to start from the original text and gradually build chapters, paragraphs, sentence segmentation, tokens, NER, motifs, character relationships, the SQLite database, and website data. Each step lists the operational goal, suggested prompt/command, tools used, output files, and common issues.

### Step 0: Prepare the Project and Text

Goal: Create the project folder, place the original text inside it, and confirm that the text is UTF-8.

Example prompt:

```text
Please inspect the project folder, read the txt file inside it, determine whether it is a chapter-based novel, and tell me the chapter title format.
```

Tools used:

- shell: `ls`, `rg --files`, `sed`, `head`
- Python: read text files and check encoding and line count when necessary

Input file:

- `red-chamber-dream.txt`

Notes:

- The current scripts assume the default filename is `red-chamber-dream.txt`.
- Chapter titles are expected to match `第X回 標題`.
- Each non-empty line is treated as one paragraph.

Common issues:

- If chapter titles are not in the form `第X回`, modify `CHAPTER_RE` in `build_tables.py`.
- If the text is in simplified Chinese or contains special punctuation, normalization may be required first.

### Step 1: Build the Document, Chapter, Paragraph, Sentence, and Token Tables

Goal: Convert the plain-text corpus into basic corpus-layer data tables.

Example prompt:

```text
Please read red-chamber-dream.txt, automatically identify chapters, and build document.csv, chapter.csv, paragraph.csv, sentence.csv, and token.csv.
```

Tools used:

- Python script: `build_tables.py`
- CKIP: if `ckip-transformers` is installed, use CKIP WS/POS
- jieba: if CKIP is unavailable, fall back to jieba
- regex: if jieba is also unavailable, fall back to simple regex tokenization

Packages that may be installed:

```bash
python3 -m pip install ckip-transformers jieba
```

Run:

```bash
python3 build_tables.py
```

Generated files:

- `document.csv`: document table
- `chapter.csv`: chapter table
- `paragraph.csv`: paragraph table
- `sentence.csv`: sentence table
- `token.csv`: word segmentation and POS table

Common issues:

- `Expected chapters 1-120` error: the chapter count does not match the script expectation. Modify `expected = list(range(...))`.
- CKIP model download failure: first check network access, or use jieba to build the initial token version.
- Incorrect token positions: this is usually caused by tokenization results not aligning with original text offsets. Check punctuation or whitespace normalization.

### Step 2: Build NER Authority Tables, Alias Tables, and Rule Tables

Goal: First build a reviewable semantic foundation instead of directly trusting model output.

Example prompt:

```text
Please first build NER authority tables, alias tables, and rule tables for Dream of the Red Chamber, so that I can manually review them before rebuilding NER with these tables.
```

Tools used:

- Python script: `build_ner_seed_tables.py`
- Manually curated rules: characters, buildings, places, identities, flowers/plants, etc.

Run:

```bash
python3 build_ner_seed_tables.py
```

Generated files:

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`

Recommended review focus:

- `entity_authority.csv`: whether the canonical names, types, and `entity_key` values are correct.
- `entity_alias.csv`: whether aliases are over-expanded; for example, `怡紅` should not be directly equated with `怡紅公子` or `怡紅院`.
- `ner_rule.csv`: whether buildings, places, identities, flowers/plants, etc. require rule-based reinforcement.

Common issues:

- Chinese labels mixed with keys can be difficult to review: a separate Chinese review CSV can be generated.
- The same string may be ambiguous: for example, `寶玉` may refer to a person or an object, so rules or manual judgment are needed.

### Step 3: Build NER Candidates, Official NER, and Conflict Tables

Goal: Integrate CKIP NER, alias tables, and rule tables to produce analyzable named entity tables.

Example prompt:

```text
Please use CKIP, entity_authority.csv, entity_alias.csv, and ner_rule.csv to rebuild ner.csv, and output ner_candidate.csv, ner_conflict.csv, and ner_summary.csv.
```

Tools used:

- Python script: `build_ner_tables.py`
- CKIP NER: `CkipNerChunker`
- Rule matching: exact match
- Candidate merging: handle overlaps according to priority, length, and source score

Run:

```bash
python3 build_ner_tables.py
```

Generated files:

- `ner_candidate.csv`
- `ner.csv`
- `ner_conflict.csv`
- `ner_summary.csv`
- `entity_occurrence_summary.csv`

Common issues:

- CKIP identifies buildings as ORG/FAC: correct them using `ner_rule.csv`.
- Person names are identified as places: raise the priority of aliases/rules.
- Many entries in `ner_conflict.csv`: first handle high-frequency characters and core places; it is not necessary to finish all review at once.

### Step 4: Build HTML/XML Annotation Output

Goal: Return annotations to the original text for inspection and display.

Example prompt:

```text
Please generate HTML and XML annotated texts according to ner.csv. The annotations should preserve entity_key, type, start, end, and source.
```

Tools used:

- Python script: `build_annotated_texts.py`
- Source tables: `chapter.csv`, `paragraph.csv`, `sentence.csv`, `ner.csv`

Run:

```bash
python3 build_annotated_texts.py
```

Generated files:

- `annotated_paragraphs.html`
- `annotated_text.xml`
- `annotated_paragraphs.json`

Note: These are large generated outputs and are currently not committed by default in `.gitignore`. If you want to publish annotated texts, create a separate release or data download package.

### Step 5: Build Imagery / Motif Tables

Goal: Annotate meaningful word groups for research, such as flowers, fragrance, dreams, tears, and illness.

Example prompt:

```text
Please build motif.csv, motif_summary.csv, and motif_chapter_summary.csv according to motif_rule.csv, and calculate co-occurrence between characters and motifs.
```

Tools used:

- Python script: `build_motif_tables.py`
- Rule table: `motif_rule.csv`
- Source tables: `sentence.csv`, `token.csv`, `ner.csv`

Run:

```bash
python3 build_motif_tables.py
```

Generated files:

- `motif.csv`
- `motif_summary.csv`
- `motif_chapter_summary.csv`
- `person_motif_cooccurrence.csv`

Common issues:

- Motifs may be too broad: for example, `夢` may be an ordinary word or a narrative-level dream.
- For a new text, `motif_rule.csv` must be rewritten; the rules for *Dream of the Red Chamber* cannot be directly reused.

### Step 6: Build the Character Co-occurrence Network

Goal: Build character nodes and character co-occurrence edges from NER results.

Example prompt:

```text
Please build a character social network according to ner.csv, and output person_social_nodes.csv, person_social_edges.csv, and person_social_network.json.
```

Tools used:

- Python script: `build_person_social_network.py`
- Source tables: `ner.csv`, `entity_authority.csv`
- Algorithm: use paragraphs as the co-occurrence unit and count how often characters appear in the same paragraph

Run:

```bash
python3 build_person_social_network.py
```

Generated files:

- `person_social_nodes.csv`
- `person_social_edges.csv`
- `person_social_network.json`

Common issues:

- Co-occurrence is not a semantic relationship: appearing in the same paragraph does not mean kinship or emotional relationship.
- Too many nodes: the frontend can set node limits and weight thresholds.

### Step 7: Build Semantic Character Relationships

Goal: Add manually curated semantic relationships such as kinship, marriage, servant-master, emotional relationships, and conflict.

Example prompt:

```text
Please use the character authority table and character network to build the first version of person_relationship.csv. Relationship types should include kinship, marriage, servant-master, emotional relationship, and conflict, and please generate JSON for the website.
```

Tools used:

- Python script: `build_person_relationships.py`
- Source data: `site/data/person_social_network.json`
- Manually curated `RELATIONS`

Run:

```bash
python3 build_person_relationships.py
```

Generated files:

- `person_relationship.csv`
- `site/data/person_relationships.json`

Common issues:

- This script is currently specific to *Dream of the Red Chamber*.
- If replacing the text, `RELATIONS` should be changed into an external CSV to avoid modifying Python every time.

### Step 8: Build the SQLite Database

Goal: Import the major CSV files into SQLite for later queries, APIs, or use in a formal website.

Example prompt:

```text
Please import all current major CSV files into SQLite, create corpus.sqlite, and create commonly used query indexes.
```

Tools used:

- Python script: `build_sqlite.py`
- Python standard library: `sqlite3`

Run:

```bash
python3 build_sqlite.py
```

Generated file:

- `corpus.sqlite`

Note: `corpus.sqlite` is a large reproducible output and is not committed to GitHub by default.

### Step 9: Generate Website Data

Goal: Convert CSV/JSON into data formats readable by the frontend.

Example prompt:

```text
Please generate site/data/*.json according to the current CSV and JSON files, so that the static website can read the full text, search data, statistics, character relationships, and co-occurrence data.
```

Tools used:

- Python script: `build_platform_site.py`
- Source tables: `chapter.csv`, `paragraph.csv`, `sentence.csv`, `ner.csv`, `motif*.csv`, `person_social_network.json`

Run:

```bash
python3 build_platform_site.py
```

Generated files:

- `site/data/ebook.json`
- `site/data/search_index.json`
- `site/data/basic_entity_index.json`
- `site/data/entity_chapter_summary.json`
- `site/data/entity_paragraph_index.json`
- `site/data/statistics.json`
- `site/data/person_social_network.json`

For website publishing and layout templates, see:

- [WEBPUBLISH.md](WEBPUBLISH.md)
- [templates/demo-site/README.md](templates/demo-site/README.md)

## Original Text Format

Currently, `build_tables.py` reads the following file by default:

```text
red-chamber-dream.txt
```

Chapter titles must follow this format:

```text
第一回 甄士隱夢幻識通靈 賈雨村風塵懷閨秀
第二回 賈夫人仙逝揚州城 冷子興演說榮國府
```

Each non-empty line is treated as one paragraph. Sentences are split by punctuation such as `。！？；：`.

## Replacing the Text with Another Corpus

For example, to process *Romance of the Three Kingdoms*:

1. Place the text in the project root directory, for example:

```text
三國演義.txt
```

2. Modify the constants at the beginning of `build_tables.py`:

```python
SOURCE = Path("三國演義.txt")
DOC_ID = "sanguoyanyi"
CHAPTER_RE = re.compile(r"^第([一二三四五六七八九十百〇零0-9]+)回\s*(.*)$")
```

3. Modify the document metadata:

```python
"title": "三國演義",
"author": "羅貫中",
```

4. Modify the chapter count check.

Currently, *Dream of the Red Chamber* is hard-coded as 120 chapters:

```python
expected = list(range(1, 121))
```

If using the common 120-chapter edition of *Romance of the Three Kingdoms*, no change is needed. If using another chapter count, change it to the corresponding number; for example, 100 chapters:

```python
expected = list(range(1, 101))
```

If you do not want to limit the chapter count for the time being, you can also change it to only check whether chapters were read.

5. `build_ner_tables.py` also contains:

```python
DOC_ID = "hongloumeng"
```

Change it to the same document ID, for example:

```python
DOC_ID = "sanguoyanyi"
```

## Build Basic Corpus Tables

Run:

```bash
python3 build_tables.py
```

This will output:

- `document.csv`
- `chapter.csv`
- `paragraph.csv`
- `sentence.csv`
- `token.csv`

Where:

- `document.csv`: document table
- `chapter.csv`: chapter table
- `paragraph.csv`: paragraph table
- `sentence.csv`: sentence table
- `token.csv`: word segmentation and POS table

## Build NER Authority Tables, Alias Tables, and Rule Tables

When processing a new text for the first time, first build or rebuild the seed tables:

```bash
python3 build_ner_seed_tables.py
```

This will generate or update:

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`

These three tables are the core of NER quality:

- `entity_authority.csv`: authority table, defining canonical entities.
- `entity_alias.csv`: alias table, such as different names for the same character.
- `ner_rule.csv`: rule table, used to reinforce buildings, places, identities, flowers/plants, and other categories that the model tends to misidentify.

When processing another text, these three tables must be manually reviewed. Taking *Romance of the Three Kingdoms* as an example, characters, places, official titles, factions, and battles should all be reorganized.

## Build NER Tables

Run:

```bash
python3 build_ner_tables.py
```

This will output:

- `ner_candidate.csv`
- `ner.csv`
- `ner_conflict.csv`
- `ner_summary.csv`
- `entity_occurrence_summary.csv`

It is recommended to first inspect:

- `ner_conflict.csv`: overlapping candidates and type conflicts.
- `ner_summary.csv`: statistics by type.
- `entity_occurrence_summary.csv`: entity occurrence counts.

## Build Imagery / Motif Tables

Run:

```bash
python3 build_motif_tables.py
```

This will output:

- `motif.csv`
- `motif_summary.csv`
- `motif_chapter_summary.csv`
- `person_motif_cooccurrence.csv`

`motif_rule.csv` is the rule source. If replacing the text, rebuild the rules according to the text's characteristics. For example, *Dream of the Red Chamber* emphasizes flowers, fragrance, dreams, illness, and tears; *Romance of the Three Kingdoms* may place greater emphasis on warfare, weapons, official titles, place names, factions, and strategies.

## Build the Character Social Network

Character co-occurrence network:

```bash
python3 build_person_social_network.py
```

This will output:

- `person_social_nodes.csv`
- `person_social_edges.csv`
- `person_social_network.json`

Semantic character relationships:

```bash
python3 build_person_relationships.py
```

This will output:

- `person_relationship.csv`
- `site/data/person_relationships.json`

Note: `build_person_relationships.py` currently contains character relationships for *Dream of the Red Chamber*. If replacing the text, you must modify `RELATIONS` in this script, or change it to read from a new relationship CSV.

## Build the SQLite Database

Run:

```bash
python3 build_sqlite.py
```

This will create:

```text
corpus.sqlite
```

`corpus.sqlite` is a generated artifact and may be large, so it is not recommended to commit it to GitHub by default. After downloading the project, users can rebuild it by running `python3 build_sqlite.py`.

The following major CSV files are currently imported:

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

Check the database:

```bash
sqlite3 corpus.sqlite ".tables"
sqlite3 corpus.sqlite "select count(*) from paragraph;"
sqlite3 corpus.sqlite "select canonical_name, count(*) from ner group by canonical_name order by count(*) desc limit 10;"
```

## Build Website Data

Generate `site/data/*.json`:

```bash
python3 build_platform_site.py
```

This currently generates or updates:

- `site/data/ebook.json`
- `site/data/search_index.json`
- `site/data/basic_entity_index.json`
- `site/data/entity_chapter_summary.json`
- `site/data/entity_paragraph_index.json`
- `site/data/statistics.json`
- `site/data/person_social_network.json`
- `site/data/articles.json`

Note: The `articles.json` generated by `build_platform_site.py` is currently rebuilt as placeholder data. If you have manually edited exploratory article data, you should check it again after running the script.

## Build Demo Data

`demo/` is the showcase site and needs both `.json` and `.json.js`.

The project currently already includes demo data. If you regenerate `site/data/*.json`, you need to sync it to `demo/data/` and wrap JSON as JS:

```bash
python3 build_demo_site.py
```

`build_demo_site.py` copies `site/data/*.json` to `demo/data/*.json` and generates the corresponding `demo/data/*.json.js`:

```javascript
window.DEMO_JSON["data/ebook.json"] = {...};
```

## Local Preview

### Download Only the Demo for Local Display

If you only want to try the demo website, you do not need to download the entire project, install Python packages, or rebuild CSV/JSON. Download and keep the complete `demo/` folder:

```text
demo/
├── index.html
├── person_social_graph.html
├── cooccurrence_graph.html
├── assets/
├── data/
└── vendor/
```

After downloading, you can open it directly in the browser:

```text
demo/index.html
```

`demo/` already includes static HTML, CSS, JavaScript, JSON, `data/*.json.js`, and local libraries needed for charts. `data/*.json.js` is used to support opening directly via `file://`, so starting a local server is not always required.

Notes:

- You must preserve the entire `demo/` folder structure; do not copy only `index.html`.
- `data/` contains website data, `assets/` contains styles, and `vendor/` contains chart libraries.
- If your browser or operating system restricts local file reading, use the `python3 -m http.server` preview method below.

Preview `site/`:

```bash
python3 -m http.server 8766 --directory site
```

Open:

```text
http://127.0.0.1:8766/
```

Preview `demo/`:

```bash
python3 -m http.server 8767 --directory demo
```

Open:

```text
http://127.0.0.1:8767/
```

`demo/index.html` can also be opened directly in a browser because it has `data/*.json.js`.

## Deploy the Demo to GitHub Pages

It is recommended to deploy `demo/` as the showcase website.

One possible method:

1. Create a GitHub repository.
2. Push the entire project to GitHub.
3. Go to `Settings` -> `Pages` in the GitHub repository.
4. Set Source to `GitHub Actions`.
5. Save and wait for `.github/workflows/pages.yml` to deploy.

GitHub Pages will use `demo/index.html` as the showcase entry point.

## Which Scripts to Rerun After Modifying Data

This project is currently not a real-time database website. Most pages read generated CSV/JSON files, so after modifying source tables, you need to rerun the corresponding scripts before website data will be updated.

| Modified content | Common files modified | Scripts to rerun |
| --- | --- | --- |
| Replace the original text, chapter rules, book title, author, or chapter count | `red-chamber-dream.txt`, `build_tables.py` | `python3 build_tables.py`, then continue downward according to the full rebuild sequence |
| Modify authority tables, alias tables, or NER rules | `entity_authority.csv`, `entity_alias.csv`, `ner_rule.csv` | `python3 build_ner_tables.py`, `python3 build_motif_tables.py`, `python3 build_person_social_network.py`, `python3 build_platform_site.py`, `python3 build_person_relationships.py`, `python3 build_demo_site.py`, `python3 build_sqlite.py` |
| Modify NER seed generation logic | `build_ner_seed_tables.py` | `python3 build_ner_seed_tables.py`, manually review, then run `python3 build_ner_tables.py` and subsequent scripts |
| Modify imagery / motif rules | `motif_rule.csv` | `python3 build_motif_tables.py`, `python3 build_platform_site.py`, `python3 build_demo_site.py`, `python3 build_sqlite.py` |
| Modify the character co-occurrence algorithm | `build_person_social_network.py` | `python3 build_person_social_network.py`, `python3 build_platform_site.py`, `python3 build_person_relationships.py`, `python3 build_demo_site.py`, `python3 build_sqlite.py` |
| Modify semantic character relationships | Currently mainly `RELATIONS` inside `build_person_relationships.py`, or later changed to `person_relationship.csv` | `python3 build_person_relationships.py`, `python3 build_demo_site.py`, `python3 build_sqlite.py` |
| Modify website data generation logic | `build_platform_site.py` | `python3 build_platform_site.py`, rerun `python3 build_person_relationships.py` if necessary, and finally run `python3 build_demo_site.py` |
| Modify SQLite imported tables or indexes | `build_sqlite.py` | `python3 build_sqlite.py` |
| Modify only website styles | `demo/assets/*.css`, `site/assets/*.css`, `templates/demo-site/assets/*.css` | No data scripts need to be rerun; simply refresh the browser |
| Modify only `site/` or `demo/` HTML/JS | `site/*.html`, `demo/*.html` | No data scripts need to be rerun; simply refresh the browser |

If you only need to sync the generated `site/data/*.json` to the showcase site, run:

```bash
python3 build_demo_site.py
```

This copies `site/data/*.json` to `demo/data/*.json` and automatically generates `demo/data/*.json.js`, allowing `demo/index.html` to be opened directly via `file://`.

## Recommended Rebuild Order

For a complete rebuild, you can directly run:

```bash
python3 build_all.py
```

By default, `build_all.py` does not run `build_ner_seed_tables.py`, in order to avoid overwriting manually reviewed `entity_authority.csv`, `entity_alias.csv`, and `ner_rule.csv`. If you also want to rebuild the seed tables, use:

```bash
python3 build_all.py --with-seed
```

If you only want to rebuild CSV/JSON/demo data and not build SQLite:

```bash
python3 build_all.py --skip-sqlite
```

This is equivalent to running the following in order:

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

If you need to rebuild NER seed tables, first run `python3 build_ner_seed_tables.py`, manually review `entity_authority.csv`, `entity_alias.csv`, and `ner_rule.csv`, and then run the subsequent workflow.

If replacing the text, the most important items to reorganize are:

- `entity_authority.csv`
- `entity_alias.csv`
- `ner_rule.csv`
- `motif_rule.csv`
- `build_person_relationships.py` or `person_relationship.csv`

## Current Limitations

- Most scripts currently still use *Dream of the Red Chamber* as the default, and some constants need to be manually modified.
- `build_tables.py` assumes the text is a chapter-based novel and that chapter titles follow the `第X回` format.
- `build_ner_tables.py` requires CKIP NER.
- `build_person_relationships.py` currently contains built-in *Dream of the Red Chamber* character relationships and is not suitable for direct reuse with other novels.
- `build_all.py` does not rebuild NER seed tables by default, in order to avoid overwriting manually reviewed data.

## Future Recommendations

- Move `SOURCE`, `DOC_ID`, book title, author, and chapter count into `config.json`.
- Move character relationships from Python constants into a reviewable CSV.
- Add more complete column types, primary keys, and foreign keys to SQLite.
- Create formal public documentation with field descriptions, NER review guidelines, and data workflow diagrams.

## License and Sources

Please confirm the copyright and licensing status of the text source you use. If replacing it with another text, make sure that the text can be publicly used, modified, and distributed.
