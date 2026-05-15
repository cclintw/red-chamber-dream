# Red Chamber Dream Knowledge Platform

The demonstration site is maintained separately by the author. This public repository does not include generated site data.

The Red Chamber Dream Knowledge Platform is a digital humanities research platform for classical Chinese fiction, using *Dream of the Red Chamber* as its primary example. It is not only a website about *Dream of the Red Chamber*, but also a reusable Digital Humanities workflow: starting from plain text, it progressively builds chapters, paragraphs, sentences, tokens, named entities, motif annotations, character relationships, co-occurrence networks, a SQLite database, and a static website deployable to Firebase Hosting.

This project combines NLP, rule-based annotation, authority table curation, Knowledge Graph construction, and static website publishing to demonstrate how a chapter-based classical novel can be transformed into a searchable, analyzable, visualizable, and reproducible research dataset. It preserves both algorithmic outputs and space for human review, making it suitable as a teaching and research model for classical Chinese fiction, literary social networks, corpus annotation, knowledge graphs, and digital curation.

## Project Overview

The core purpose of this repo is to serve as an open research platform rather than a single finished website. It provides a hybrid workflow: first, Python scripts and NLP tools build the foundational corpus tables; then authority tables, alias tables, and rule tables refine named entities; finally CSV, SQLite, and JSON are converted into static data usable by the frontend.

The project focuses on:

- Digital Humanities: transforming literary texts into reproducible, citable, and inspectable research data.
- NLP: using CKIP, jieba, or regex to establish word segmentation, POS tagging, and NER foundations.
- Knowledge Graph: building data for characters, places, buildings, identities, motifs, and relationships.
- Annotation: preserving annotation sources, offsets, entity keys, canonical names, and rule priorities.
- Hybrid Workflow: combining model outputs, rule matching, and human curation rather than relying entirely on automation.
- Static site deployment: using Firebase Hosting to present full-text reading, search, statistics, and graph visualization.

## Live Demo

The demonstration site is maintained separately by the author. To avoid publishing production data and generated JSON, this public repository does not include `site/` or `demo/`.

After local builds, the project produces two website versions:

- `site/`: the production static website output. It loads `data/*.json` through `fetch()`. Formal local review and Firebase Hosting deployment should use this directory.
- `demo/`: a file-openable mirror. It additionally includes `data/*.json.js`, so `demo/index.html` can be opened directly by double-clicking.
- `templates/demo-site/`: reusable template specifications and CSS for the demo website.

The public GitHub repository should not include complete `site/`, `demo/`, production CSV tables, SQLite databases, or generated JSON. These files are local research and deployment outputs that can be rebuilt locally and deployed to the project owner's own website.

## Research Goals

The goal of this repo is not to turn *Dream of the Red Chamber* into a single closed database, but to demonstrate a portable Chinese text processing workflow. Users can replace `red-chamber-dream.txt` with another chapter-based novel, such as *Romance of the Three Kingdoms*, and rebuild corpus tables, annotation tables, character networks, SQLite, and the display website with the same workflow.

This project aims to address questions such as:

- How can classical fiction be transformed from plain text into a structured corpus?
- How can characters, places, buildings, identities, and motifs in literary texts be annotated and reviewed?
- How can automatic NER, human-curated authority tables, and rule-based reinforcement form an interpretable annotation pipeline?
- How can character co-occurrence networks and manually curated semantic relationships coexist in one knowledge graph?
- How can research data be published, rebuilt, and cited through CSV, SQLite, JSON, and static website output?

## Core Features

- Full-text reading: chapter list, paragraph numbers, inline annotations, and word frequency information.
- Search: supports exact string search and entity-expanded search.
- NER: uses CKIP, authority tables, alias tables, and rule tables to build basic entity annotations.
- Annotation pipeline: preserves char offsets, token alignment, source, priority, and confidence.
- Social network graph: integrates character co-occurrence, family nodes, and manually curated semantic relationships.
- Character genealogy view: presents family generations, marriage, spouse/concubine relations, collateral kin, and service relations as a tree-oriented view.
- Co-occurrence graph: builds paragraph-level co-occurrence among characters, buildings, places, identities, flowers, and plants.
- Motif analysis: uses motif rules to annotate research-oriented word groups such as flowers, fragrance, dreams, tears, and illness.
- Statistics: character counts, NER types, motifs, chapter word counts, and paragraph statistics.
- SQLite: imports major CSV tables into `corpus.sqlite` for querying, APIs, or later research.
- Static site deployment: the site can be deployed to Firebase Hosting without a backend service.

## Core Workflow

The core workflow of this project is:

```text
red-chamber-dream.txt
        |
        v
document / chapter / paragraph / sentence / token CSV
        |
        v
entity authority / alias / NER rules
        |
        v
NER candidates -> NER -> conflict and summary tables
        |
        v
motif annotations + person cooccurrence + semantic relationships
        |
        v
SQLite database + site/data JSON
        |
        v
site/ production static website + demo/ mirror
```

Simplified rebuild command:

```bash
python3 build_all.py
```

To regenerate the NER seed tables as well:

```bash
python3 build_all.py --with-seed
```

For the full pipeline, steps 0-9, rerun matrix, and limitations, see [WORKFLOW.md](WORKFLOW.md).

## Quick Start

Python 3.10 or later is recommended.

Install the basic packages:

```bash
python3 -m pip install ckip-transformers jieba
```

If you only want to build chapters, paragraphs, sentences, and tokens first, you can install:

```bash
python3 -m pip install jieba
```

Rebuild the main data:

```bash
python3 build_all.py
```

Rebuild only CSV, JSON, and static website output, without building SQLite:

```bash
python3 build_all.py --skip-sqlite
```

Build website data:

```bash
python3 build_platform_site.py
python3 build_demo_site.py
```

Preview the production `site/` output:

```bash
make preview
```

Open:

```text
http://127.0.0.1:8767/
```

Or without Makefile:

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory site
```

Deploy to Firebase Hosting:

```bash
firebase deploy
```

With an explicit Firebase project:

```bash
make deploy-firebase FIREBASE_PROJECT=your-project-id
```

Preview the `demo/` mirror:

```bash
make preview-demo
```

Or:

```bash
python3 -m http.server 8767 --bind 127.0.0.1 --directory demo
```

Open:

```text
http://127.0.0.1:8767/
```

Use `site/` as the final review target before production deployment. `demo/index.html` can still be opened directly in a browser because it includes `data/*.json.js` as `file://` preview support. For the full local preview and deployment workflow, see [DEPLOY.md](DEPLOY.md).

## Repository Structure

```text
.
├── red-chamber-dream.txt          # Source text
├── build_all.py                   # One-command rebuild for the main data pipeline
├── build_tables.py                # Builds document/chapter/paragraph/sentence/token
├── build_ner_seed_tables.py        # Builds authority, alias, and NER rule tables
├── build_person_authority.py        # Builds person authority tables and syncs NER aliases
├── build_ner_tables.py             # Builds NER candidates, results, conflicts, and summaries
├── build_person_occurrence_summary.py # Builds person occurrence summaries from NER
├── build_motif_tables.py           # Builds motif annotations and statistics
├── build_person_social_network.py  # Builds the character co-occurrence network
├── build_person_relationships.py   # Builds semantic character relationships
├── build_platform_site.py          # Builds site/data/*.json
├── build_demo_site.py              # Syncs site/assets and builds the demo mirror
├── firebase.json                   # Firebase Hosting config; public points to site/
├── Makefile                        # rebuild / preview / deploy command entrypoint
├── build_sqlite.py                 # Imports major CSV tables into corpus.sqlite
├── *.csv                           # Corpus, person authority, NER, motif, and character relationship tables
├── site/                           # Locally generated Firebase Hosting output; not recommended for public git
├── demo/                           # Locally generated file-openable mirror; not recommended for public git
├── templates/demo-site/            # Demo templates and CSS
├── WORKFLOW.md                     # Full pipeline and rebuild workflow
├── DATA_SCHEMA.md                  # CSV / SQLite / JSON structure documentation
├── DEPLOY.md                       # Local preview and Firebase Hosting deployment
└── CITATION.md                     # Academic citation and methodological attribution guidelines
```

For detailed CSV, SQLite, and JSON field documentation, see [DATA_SCHEMA.md](DATA_SCHEMA.md).

## Citation

If you use, cite, adapt, or refer to this project's methodology, data workflow, table design, annotation workflow, knowledge graph architecture, website presentation, or code in a paper, research project, teaching material, website, software, database, digital humanities platform, or derived system, please cite the source.

Recommended citation:

```text
Chun-Cheng Lin. Red Chamber Dream Knowledge Platform: A Digital Humanities Workflow and Knowledge Graph Construction Demonstration for Classical Chinese Fiction. GitHub repository, 2026.
https://github.com/cclintw/red-chamber-dream
```

BibTeX:

```bibtex
@misc{lin2026redchamberdream,
  author       = {Lin, Chance},
  title        = {紅樓夢知識平台：中文古典小說數位人文工作流與知識圖譜建構示範},
  year         = {2026},
  howpublished = {GitHub repository},
  url          = {https://github.com/cclintw/red-chamber-dream}
}
```

For full citation formats and methodological attribution guidelines, see [CITATION.md](CITATION.md).

## Research Attribution

This project is a demonstration platform for a digital humanities research workflow. If you cite, adapt, or extend any of the following, please retain methodological attribution:

- The corpus construction workflow from plain text to chapters, paragraphs, sentences, and tokens.
- The NER annotation workflow combining authority tables, alias tables, and rule tables.
- Analysis of characters, places, buildings, identities, motifs, and co-occurrence in literary texts.
- Methods for generating character genealogy views, co-occurrence networks, and statistical data.
- Conversion workflows among CSV, SQLite, JSON, and static websites.
- A digital humanities display website architecture deployable to Firebase Hosting.
- Annotation pipeline, schema design, knowledge graph design, and hybrid workflow.

If you adapt this project, it is recommended to include the following note in your README, paper footnote, website description, or project documentation:

> Part of this project's methodology, data workflow, or system design is based on Chance Lin's "Red Chamber Dream Knowledge Platform" project.

This project retains the right to original methodological and academic attribution. Code licensing does not waive the need for scholarly attribution of the research methodology, documentation architecture, schema design, annotation workflow, and knowledge graph workflow.

## License and Sources

Licensing information for this project should follow the repository's official license file or citation metadata; the project currently uses GPL-3.0-or-later.

When citing this project's methodology, documentation, data workflow, or architecture, please follow the "Citation" section in this document and [CITATION.md](CITATION.md).

Please verify the copyright and license status of the text source you use. If replacing the source with another text, make sure that text can be publicly used, modified, and redistributed.

## Documentation

- [WORKFLOW.md](WORKFLOW.md): full pipeline, steps 0-9, script purposes, full rebuild workflow, and rerun matrix.
- [DATA_SCHEMA.md](DATA_SCHEMA.md): CSV, SQLite, and JSON field and data structure documentation.
- [CITATION.md](CITATION.md): academic citation formats, Research Attribution, and methodological citation guidelines.
- [WEBPUBLISH.md](WEBPUBLISH.md): existing supplementary notes on website generation and publishing.
- [templates/demo-site/README.md](templates/demo-site/README.md): demo website template specification.
