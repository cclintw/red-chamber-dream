# Red Chamber Dream Knowledge Platform

The Red Chamber Dream Knowledge Platform is a digital humanities research workflow project using *Dream of the Red Chamber* as its primary example. It is not only a website about the novel, but also a reusable Digital Humanities framework for transforming literary texts into searchable, analyzable, visualizable, and citable research data.

This repository provides a methodological overview, conceptual data architecture, research scripts, citation guidelines, and license information for digital humanities work on classical Chinese fiction.

Demo:

[https://textoria.cclin.cc/red-chamber-dream](https://textoria.cclin.cc/red-chamber-dream/ )

## Project Overview

This project demonstrates an annotation-oriented corpus architecture for converting literary texts into inspectable, reproducible, and extensible research data.

The project emphasizes:

- Digital Humanities: preserving literary texts as citable and reproducible research data.
- NLP: using segmentation, named entity recognition, and rule-based reinforcement.
- Annotation: combining automatic processing, authority tables, aliases, and human review.
- Knowledge Graph: modeling characters, places, buildings, identities, motifs, and relationships.
- Hybrid Workflow: allowing computational output and scholarly interpretation to coexist.
- Static Publication: converting research data into static website-ready outputs.

## Research Goals

This project addresses questions such as:

- How can classical fiction be transformed from plain text into a structured corpus?
- How can characters, places, buildings, identities, and motifs be annotated and reviewed?
- How can automatic NER, authority tables, and rule-based reinforcement form an interpretable annotation pipeline?
- How can character co-occurrence networks and curated semantic relationships coexist?
- How can digital humanities data be rebuilt, cited, preserved, and presented?

## Repository Contents

This repository includes:

- a digital humanities workflow overview
- an overview of annotation-oriented corpus architecture
- scripts related to corpus construction, annotation, motif analysis, network modeling, and relationship modeling
- academic citation and Research Attribution guidelines
- GPL-3.0-or-later licensing

Researchers may adapt the scripts according to their own corpus, annotation rules, and research questions.

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

When adapting this workflow, first clarify the following research layers:

- corpus segmentation: textual hierarchy and citable reading units
- authority normalization: methods for resolving persons, aliases, and normalized entities
- annotation workflow: NER, motifs, and human review
- relationship modeling: semantic character relations, kinship, marriage, service relations, or other research-defined relations
- presentation outputs: derived materials for search, statistics, network views, and display layers

For a public data architecture overview, see [DATA_SCHEMA.md](DATA_SCHEMA.md).

## Run the Example Workflow

This repository includes a minimal example for testing the workflow scripts:

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

Outputs are written to:

```text
public_output/
```

The example demonstrates a basic path from text segmentation, entity annotation, motif annotation, person relationships, co-occurrence networks, and simple HTML review pages.

## Citation

If you use, cite, adapt, or refer to this project's methodology, data workflow, annotation workflow, knowledge graph design, or display architecture in a paper, research project, teaching material, website, software, database, digital humanities platform, or derived system, please cite the source.

Recommended citation:

```text
Chun-Cheng Lin. Red Chamber Dream Knowledge Platform: A Digital Humanities Workflow and Knowledge Graph Construction Demonstration for Classical Chinese Fiction. GitHub repository, 2026.
https://github.com/cclintw/red-chamber-dream
```

For full citation formats and methodological attribution guidelines, see [CITATION.md](CITATION.md).

## Research Attribution

This project is a demonstration platform for a digital humanities research workflow. If you cite, adapt, or extend any of the following, please retain methodological attribution:

- corpus construction from text to structured corpus layers
- annotation workflows combining authority tables, aliases, and rule-based reinforcement
- annotation methods for characters, places, buildings, identities, and motifs
- conceptual design of genealogy views, co-occurrence networks, and knowledge graphs
- annotation-oriented corpus architecture
- hybrid workflow for classical fiction research

## License

This project uses layered licensing to distinguish code, documentation, and research data:

- Code: GPL-3.0-or-later.
- Documentation: CC BY 4.0.
- Data: CC BY-NC 4.0, unless a specific data file or source states otherwise.

Code licensing does not waive the need for scholarly attribution of the research methodology, documentation architecture, schema design, annotation workflow, and knowledge graph workflow. If you cite, adapt, migrate, or extend this project's research workflow and methodology, please retain appropriate attribution.

## Documentation

- [DATA_SCHEMA.md](DATA_SCHEMA.md): public data architecture overview.
- [CITATION.md](CITATION.md): academic citation formats, Research Attribution, and methodological citation guidelines.
- [LICENSE](LICENSE): license terms.
