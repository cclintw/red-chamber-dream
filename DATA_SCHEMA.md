# Data Schema

This document provides a public overview of the corpus and annotation architecture used in the Red Chamber Dream Knowledge Platform project. It is intended as a methodological guide for digital humanities readers, not as production database documentation.

## Overview

This project transforms a plain-text classical Chinese novel into a structured, annotation-oriented research corpus. The workflow begins with raw text and proceeds through segmentation, sentence splitting, tokenization, named entity recognition, rule-based annotation, motif tagging, social graph construction, SQLite aggregation, and static site generation.

At a conceptual level, the data flow is:

```text
plain text
  -> chapters / paragraphs / sentences
  -> tokens
  -> person authority and aliases
  -> named entities and annotations
  -> motifs and thematic markers
  -> person relationships and social graph
  -> SQLite research database
  -> static website data
```

The design emphasizes traceable transformation rather than opaque automation. Each layer preserves enough structure to support review, correction, aggregation, visualization, and scholarly reuse.

## Core Tables

### `document.csv`

Stores basic metadata for the source text, including the document identifier, title, author, source file, language, and corpus-level counts.

### `chapter.csv`

Represents the chapter structure of the novel. It provides the primary literary division used for reading, navigation, chapter-level statistics, and longitudinal analysis.

### `paragraph.csv`

Stores paragraph-level text units. Paragraphs are the main contextual unit for reading, annotation display, and many co-occurrence calculations.

### `sentence.csv`

Stores sentence-level text units derived from each paragraph. Sentences provide a more precise unit for tokenization, named entity recognition, and annotation alignment.

### `token.csv`

Stores tokenized text and basic linguistic segmentation results. This table supports downstream NLP, entity alignment, frequency analysis, and annotation anchoring.

### `ner.csv`

Stores named entity annotations, including entities such as people, places, buildings, identities, and other domain-relevant categories. It is the central annotation table for linking textual occurrences to normalized entities.

### `person_authority.csv`

Stores curated person identities independently from textual occurrence records. It defines who a person is, while `ner.csv` records where that person appears in the text.

The person authority layer separates broad household affiliation from spatial residence. `household` records府第 / 家宅層級 such as 榮國府 or 寧國府, while `residence` and `residence_detail` are reserved for spaces such as 大觀園, 怡紅院, 瀟湘館, or other nested literary locations.

### `person_alias.csv`

Stores names, aliases, variant names, and forms of address used to connect textual mentions to person authority records.

### `motif.csv`

Stores motif and thematic annotations, such as flowers, dreams, illness, tears, fragrance, and other recurring literary markers. This layer supports interpretive and thematic analysis beyond named entities.

### `person_relationship.csv`

Stores curated semantic relationships among characters, such as kinship, marriage, master-servant relations, emotional relations, and conflict. This table complements statistical co-occurrence with human-readable relationship interpretation.

### `person_occurrence_summary.csv`

Stores derived occurrence summaries for people, including first and last chapter appearances computed from the current NER result. These values are treated as textual evidence, not as fixed authority metadata.

## Architecture Layers

### Corpus Layer

The corpus layer converts the source text into structured units: document, chapter, paragraph, sentence, and token. This layer establishes stable textual references for reading, search, annotation, and later analysis.

### Annotation Layer

The annotation layer records named entities, normalized entity references, person authority records, aliases, rule-based annotations, and motif markers. It is designed for a hybrid workflow in which NLP output, authority tables, aliases, rules, and human review can coexist.

### Graph Layer

The graph layer represents relationships and co-occurrence patterns. It includes curated character relationships, kinship-oriented data, marriage relations, service relations, and network-oriented data derived from textual proximity. This distinction keeps interpretive relationships separate from statistical co-occurrence.

### Website Layer

The website layer converts research data into static JSON files for reading, search, statistics, and visualization. This allows the project to be published as a static digital humanities website through Firebase Hosting without requiring a backend service.

## SQLite

`corpus.sqlite` is a rebuildable research database generated from the project CSV files. It is intended for local querying, aggregation, exploratory analysis, and possible downstream API development.

The SQLite database is not presented here as a production database design. SQL schema details, indexes, optimization decisions, cache strategy, and deployment-specific database concerns are outside the scope of this public overview.

## Final Note

This project is a demonstration platform for a digital humanities workflow and an annotation-oriented corpus architecture. Its data structure is designed to make literary text computationally inspectable while preserving methodological traceability, scholarly attribution, and room for human interpretation.
