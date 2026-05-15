# Data Architecture Overview

This document provides a high-level overview of the data architecture behind the Red Chamber Dream Knowledge Platform. It is intentionally conceptual. It does not disclose production table names, field definitions, SQL schema, indexes, JSON contracts, or implementation-level data structures.

## Overview

The project treats a classical Chinese novel as an annotation-oriented research corpus. The workflow begins with literary text and moves through several methodological stages:

```text
textual source
  -> corpus segmentation
  -> linguistic processing
  -> named entity annotation
  -> authority normalization
  -> motif and thematic annotation
  -> relationship and network modeling
  -> research aggregation
  -> static presentation layer
```

The architecture is designed for digital humanities research rather than production database exposure. Its goal is to preserve traceability between text, annotation, interpretation, and visualization.

## Conceptual Layers

### Corpus Layer

The corpus layer organizes the source text into stable reading and analysis units. These units support navigation, citation, textual comparison, annotation anchoring, and later aggregation.

### Annotation Layer

The annotation layer records interpretive and computational marks over the text. It combines automated NLP output, rule-based reinforcement, authority normalization, alias handling, and human review.

### Authority Layer

The authority layer separates textual mentions from normalized research identities. This makes it possible to connect variant names, forms of address, titles, and aliases to stable interpretive entities without treating every textual form as a separate object.

### Motif Layer

The motif layer supports thematic and literary interpretation. It allows recurring images, narrative markers, symbolic objects, emotions, or conceptual patterns to be studied across the text.

### Relationship Layer

The relationship layer distinguishes curated semantic relations from statistical proximity. It can support kinship, marriage, affiliation, service, conflict, emotional relation, or other project-defined interpretive categories.

### Network Layer

The network layer models co-occurrence and structural proximity. It is intended as an exploratory tool, not as a substitute for curated literary interpretation.

### Presentation Layer

The presentation layer converts selected research outputs into static website-ready materials for reading, search, visualization, and public demonstration.

## Methodological Principles

- The workflow is hybrid: computational extraction and human curation are both necessary.
- Textual occurrence and normalized identity should remain conceptually distinct.
- Statistical co-occurrence and semantic relationship should not be treated as the same kind of evidence.
- Annotation should remain traceable to textual context and research decisions.
- Public documentation should describe the method without exposing production schema or complete data contracts.

## Public Scope

This public repository does not include:

- production table definitions
- full field lists
- SQL schema
- database indexes
- generated JSON contracts
- complete rebuild scripts
- production data exports

The purpose of this file is to document the methodological architecture at a level suitable for public digital humanities citation and discussion.

## Final Note

This project is a demonstration platform for a digital humanities workflow and an annotation-oriented corpus architecture. Its public data architecture description is conceptual, methodology-oriented, and intentionally separate from production engineering documentation.
