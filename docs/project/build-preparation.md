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

1. ~~Choose Python/package tooling and record the decision.~~ Python 3.11+, `src` layout, and standard-library runtime selected.
2. ~~Add typed domain models corresponding to the committed v0.1 JSON Schemas.~~ Implemented with explicit serialization and validation.
3. ~~Add controlled-English structural segmentation behind a parser-neutral interface.~~ Initial narrow analyzer implemented.
4. Expand deterministic semantic normalization and grammar coverage for selected committed gold cases. Flat object conjunction, positional entity/predicate correspondence, exact numeric thresholds, structured prefix-IF, and proposition-scoped temporal relations are now supported.
5. Add cautious plain-English rendering over structured expressions.
6. ~~Implement deterministic comparison rules.~~ The complete controlled Phase 1 taxonomy, alignment, and safe addition/omission are implemented.

## Current Phase 1 status

Phase 1 is complete. The reproducible exit decision, 42-case pipeline matrix, quality baseline, and single recommended Phase 2 milestone are maintained in the [Phase 1 completion audit](../architecture/phase-1-completion-audit.md).

After the third Phase 2 parser milestone, the callable pipeline covers 23 exact end-to-end gold cases out of 42. The reproducible audit classifies the remainder as 10 parser-unsupported, 2 comparator-unsupported, and 7 inference-not-implemented, with no analyzable-but-inexact cases. See [Contraction Normalization v0.3](../architecture/contraction-normalization-v0.3.md).

## Next implementation milestone

The next recommended Phase 2 milestone is **Controlled Spatial Copular Relations v0.1**, narrowly targeting `entity_relation_003` without general prepositional-phrase parsing.

## Definition of ready

Phase 0 is ready when scope, layers, boundaries, schema direction, language policy, comparison taxonomy, testing policy, and deferred decisions are explicit. Phase 1 is complete only when both success criteria run in automated tests without GUI or provider dependencies.

## Reproducibility and conference readiness

Development should preserve minimal pairs, reference analyses, intermediate representations, architecture diagrams, reproducible tests, benchmark examples, and later screenshots. These assets may support a conference presentation, poster, paper, handout, or product demonstration, but demonstration needs must not bypass test or provenance standards.

## Decisions still to make

- Structural parser strategy and whether initial parsing is rule-based or library-assisted
- Exact expression AST beyond the deliberately open v0.1 operator object
- Confidence calibration method beyond the v0.1 numeric representation
- Exact Phase 1 subset of priority profiles beyond General and Translation comparison
- Final edition limits, licensing, and distribution approach (post-Phase 1)
- Provider strategy for later AI-assisted extraction; no provider is selected now
