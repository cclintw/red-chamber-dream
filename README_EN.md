# Red Chamber Dream Knowledge Platform

The Red Chamber Dream Knowledge Platform is a digital humanities research workflow project using *Dream of the Red Chamber* as its primary example. It is not only a website about the novel, but also a reusable Digital Humanities framework for transforming literary texts into searchable, analyzable, visualizable, and citable research data.

This public repository preserves only the methodological overview, conceptual data architecture, citation guidelines, and license information. It does not include production data, complete tables, SQLite databases, generated JSON, website output, deployment settings, or full rebuild scripts.

## Project Overview

This project demonstrates an annotation-oriented corpus architecture. Its purpose is not to publish a complete production database, but to describe a research workflow for converting literary texts into inspectable, reproducible, and extensible research data.

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

## Public Repository Scope

This public repository does not publish the full production implementation. It excludes:

- source text
- complete CSV tables
- complete field schema
- SQLite databases
- generated JSON
- generated website output
- deployment settings
- production rebuild scripts

The full research data, generated website output, and deployment workflow are maintained by the author in a private repository and local environment.

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

## Minimal Data Requirements

A compatible system requires, at a conceptual level:

- corpus tables: text, chapters, paragraphs, sentences, and tokens
- authority tables: persons, aliases, and normalized entity names
- annotation tables: NER, motifs, and reviewed annotations
- relationship tables: semantic person relationships, kinship, marriage, service relations, or other research-defined relations
- derived outputs: search indexes, statistics, network data, and website-ready JSON

This repository does not list production field-level details. The public version only provides a methodological and architectural overview.

For a public data architecture overview, see [DATA_SCHEMA.md](DATA_SCHEMA.md).

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

Licensing information follows the repository's official license file and citation metadata. The project currently uses GPL-3.0-or-later.

Code licensing does not waive the need for scholarly attribution of the research methodology, documentation architecture, schema design, annotation workflow, and knowledge graph workflow. If you cite, adapt, migrate, or extend this project's research workflow and methodology, please retain appropriate attribution.

## Documentation

- [DATA_SCHEMA.md](DATA_SCHEMA.md): public data architecture overview.
- [CITATION.md](CITATION.md): academic citation formats, Research Attribution, and methodological citation guidelines.
- [LICENSE](LICENSE): license terms.
