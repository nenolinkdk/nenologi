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
4. Expand deterministic semantic normalization and grammar coverage for selected committed gold cases. Flat object conjunction, positional entity/predicate correspondence, exact numeric thresholds, and one structured prefix-IF condition are now supported.
5. Add cautious plain-English rendering over structured expressions.
6. ~~Implement initial deterministic comparison rules.~~ Modality, quantifier, explicit negation, flat conjunction, positional entity/predicate change, and equivalence are implemented.

## Current Phase 1 status

The callable pipeline now covers 17 exact comparison/equivalence gold cases. Conditions reference normalized antecedent/consequent propositions, reuse numeric constraints, and compare add/remove or changed antecedents without duplicate omission/addition findings.

## Next implementation milestone

Implement Temporal Relations v0.1 as the next isolated deterministic extension. Keep general tense parsing, causal readings, condition chains, and broad scope resolution outside that milestone.

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
