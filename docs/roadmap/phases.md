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

The [Phase 2 Completion Audit](../architecture/phase-2-completion-audit.md) freezes the deterministic core under the contract in [Deterministic Core Contract](../architecture/deterministic-core-contract.md). Phase 3.0 policy architecture is specified separately; client work must preserve the frozen boundary.

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

## Phase 3.0 — Interpretation and policy architecture

The [Phase 3.0 architecture](../architecture/phase-3-interpretation-policy-architecture.md), [interpretation-status contract](../architecture/interpretation-status-contract.md), and [policy registry](../architecture/phase-3-policy-registry.md) define a parser-independent layer over `UNSUPPORTED / NOT_ESTABLISHED`. [Defeasible Recurrence Prediction Policy v0.1](../architecture/defeasible-recurrence-prediction-v0.1.md) is the first implementation and raises the separate full-pipeline metric to 40/42 without changing Phase 2. The next milestone is Phase 3.2 Alternative-reading Evaluation v0.1.

**Deliverable:** versioned policy/result contracts that preserve Phase 2 and work with AI disabled.

## Phase 3.1 — Specialized profiles
Add Biography, Procedure / recipe, Technical instructions, Prompt, Prompt / output, Specifications and SEO / web after the policy boundary is implemented and validated.

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
