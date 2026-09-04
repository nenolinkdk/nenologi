# Development phases

## Phase 0 — Specification and reference cases
Define the semantic model, analysis profiles, comparison modes, difference taxonomy, confidence/ambiguity model, word limits and reference examples.

Create minimal pairs:
- AND / OR
- MUST / MAY
- ALL / SOME
- BEFORE / AFTER
- > / >=
- negation present / absent
- condition present / absent

**Deliverable:** stable specification and test corpus.

## Phase 1 — Nenologi Core v0.1
Implement a UI-independent core with input validation, segmentation, semantic extraction, normalized representation, entities/relations, logical operators, quantification, modality, time, conditions, comparison rules, confidence and plain-language explanations. Begin with controlled English and the General text and Translation comparison profiles. See the [canonical MVP specification](../project/mvp-specification.md) and [build preparation](../project/build-preparation.md).

Start with General text and Translation comparison.

**Deliverable:** callable core engine with structured JSON, plain-English interpretation, logical representation, source/target comparison, and tests. No GUI or external AI provider is part of this milestone.

## Phase 2 — Standalone Windows prototype
Build a small Windows client around the engine.

Functions:
- select analysis profile
- select Single or Compare
- paste/load text
- word counter
- enforce word limit
- run analysis
- show interpretation
- show findings
- expand formal representation
- export PDF

**Deliverable:** usable proof of concept.

## Phase 3 — Specialized profiles
Add Biography, Procedure / recipe, Technical instructions, Prompt, Prompt / output, Specifications and SEO / web.

Later/experimental: Rules/legal, Argumentation, Historical/news, Literary/poetry.

**Deliverable:** reusable profile framework.

## Phase 4 — Reporting and quality
Add PDF, JSON export, severity, confidence, ambiguity reporting, regression tests, configurable limits and chunking strategy.

**Deliverable:** stable reporting and QA framework.

## Phase 5 — Trawedit integration
Integrate Nenologi as Semantic / Logic QA for selected segments, aligned source-target pairs and document-level analysis.

**Deliverable:** Trawedit Semantic / Logic QA module.

## Phase 6 — Extended uses
Evaluate standalone distribution, batch processing, additional languages, SEO/localization workflows, API/local service and other Nenolink integrations.
