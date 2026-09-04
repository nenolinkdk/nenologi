# Phase 1 build preparation

## Milestone

**Phase 1 – Nenologi Core v0.1** delivers a callable, UI-independent core with structured output and automated tests.

First success criterion:

```text
English sentence -> Nenologi Core -> structured JSON
                 -> plain-English interpretation
                 -> logical representation
```

Second success criterion:

```text
source sentence -> representation A
target sentence -> representation B
A <-> B         -> semantic/logical findings
```

## Recommended implementation order

1. Choose Python/package tooling and record the decision.
2. Turn the conceptual v0.1 model into a JSON Schema and typed domain models.
3. Add request validation and controlled-English structural segmentation.
4. Implement enough semantic normalization for the first gold cases.
5. Add logical expression objects and cautious plain-English rendering.
6. Implement deterministic comparison rules for critical minimal pairs.
7. Expand the gold corpus toward 30 reviewed cases.

## Definition of ready

Phase 0 is ready when scope, layers, boundaries, schema direction, language policy, comparison taxonomy, testing policy, and deferred decisions are explicit. Phase 1 is complete only when both success criteria run in automated tests without GUI or provider dependencies.

## Reproducibility and conference readiness

Development should preserve minimal pairs, reference analyses, intermediate representations, architecture diagrams, reproducible tests, benchmark examples, and later screenshots. These assets may support a conference presentation, poster, paper, handout, or product demonstration, but demonstration needs must not bypass test or provenance standards.

## Decisions still to make

- Supported Python version, package layout, and dependency management
- Structural parser strategy and whether initial parsing is rule-based or library-assisted
- Formal JSON Schema details, identifier/span conventions, and expression AST
- Confidence scale and calibration method
- Exact Phase 1 subset of priority profiles beyond General and Translation comparison
- Final edition limits, licensing, and distribution approach (post-Phase 1)
- Provider strategy for later AI-assisted extraction; no provider is selected now
