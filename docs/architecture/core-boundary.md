# Core boundary

## Rule

Nenologi Core is a reusable library with no dependency on PySide6, Windows UI APIs, Trawedit, export formats, licensing services, or a specific commercial AI provider.

```text
standalone Windows client --\
                            -> application adapter -> nenologi-core
future Trawedit integration-/
```

## Core responsibilities

- Validate analysis requests and language/profile/mode metadata.
- Run structural, semantic, normalization, comparison, and bounded-inference stages.
- Produce schema-versioned analyses, findings, and explanation data.
- Preserve provenance, uncertainty, alternative readings, and diagnostics.
- Apply provider-neutral interfaces where a future extraction component is replaceable.

## Client and adapter responsibilities

- Collect input and choose UI/source/target languages.
- Enforce edition features through a centralized policy service.
- Localize visible strings and render formulas.
- Handle files, clipboard, progress, cancellation, and presentation.
- Convert core data to future export formats.

The core accepts and returns serializable data rather than UI widgets. Dependency direction points inward: clients may import the core; the core never imports clients. Initial deterministic fixtures and rules must run offline. A future AI-assisted extractor must sit behind an interface and may not leak provider-specific response objects into the schema.

## Proposed Phase 1 package boundaries

```text
nenologi_core/
  models/          # schema-aligned domain objects
  structure/       # segmentation and structural relations
  semantics/       # entities, propositions, roles, operators
  logic/           # normalization and safe inference
  comparison/      # alignment and difference rules
  interpretation/  # provider-neutral explanation data
  profiles/        # profile configuration and hooks
  validation/      # request and output validation
```

The first implementation fixes Python 3.11 as the minimum and provides the typed/serialization layer described in [Python core domain layer](python-core.md). Parser dependencies and strategy remain unresolved.
