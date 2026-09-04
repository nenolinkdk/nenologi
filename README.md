# Nenologi

Nenologi is a reusable structural, semantic, and logical analysis engine for natural-language text. It builds an explicit, inspectable intermediate representation so that a text can be interpreted, compared with another text, and—where justified—used for limited inference.

```text
TEXT
  -> structural analysis
  -> semantic analysis
  -> logical representation
  -> inference / comparison
  -> plain-language interpretation
```

Conventional tools often ask how similar two texts are or what a text is about. Nenologi asks what the text asserts, which relations and conditions it establishes, what follows from them, and whether those properties remain true in another text.

Nenologi does not assume that natural language has one uniquely correct formalization. Analyses can be explicit, entailed, probable, ambiguous, unsupported, contradicted, or unable to be safely formalized. Confidence in an analysis and severity of a finding are separate values.

## Project status

Phase 0 and **Phase 1: Nenologi Core v0.1** are complete. The canonical evidence and Phase 2 recommendation are recorded in the [Phase 1 completion audit](docs/architecture/phase-1-completion-audit.md). No GUI, external AI provider, PDF export, licensing system, or Trawedit integration was part of Phase 1.

The first success criterion is:

```text
English sentence -> Nenologi Core -> structured JSON
                 -> plain-English interpretation
                 -> logical representation
```

The second is a source/target comparison in which both texts are independently represented and semantic or logical differences are reported.

## Architecture direction

`nenologi-core` is a UI-independent library. A small standalone Windows client is planned as its first client; Trawedit integration comes later. Analysis profiles and comparison modes are independent dimensions. English is the canonical language for code, schemas, tests, and technical documentation.

## Start reading

1. [MVP specification](docs/project/mvp-specification.md)
2. [Multilayer analysis model](docs/project/multilayer-analysis.md)
3. [Core boundary](docs/architecture/core-boundary.md)
4. [Analysis schema v0.1](docs/architecture/semantic-json-schema.md)
5. [Python core domain layer](docs/architecture/python-core.md)
6. [Controlled English Analyzer v0.1](docs/architecture/controlled-english-analyzer.md)
7. [Deterministic semantic comparison v0.1](docs/architecture/deterministic-comparison.md)
8. [Phase 1 semantic core consolidation](docs/architecture/semantic-core-consolidation.md)
9. [Scope v0.1](docs/architecture/scope-v0.1.md)
10. [Proposition Alignment v0.1](docs/architecture/proposition-alignment-v0.1.md)
11. [Addition/Omission v0.1](docs/architecture/addition-omission-v0.1.md)
12. [Phase 1 completion audit](docs/architecture/phase-1-completion-audit.md)
13. [Simple Past Transitive Clauses v0.1](docs/architecture/simple-past-transitive-v0.1.md)
14. [Test corpus strategy](docs/testing/test-corpus-strategy.md)
15. [Build preparation](docs/project/build-preparation.md)

For a non-technical introduction, see [Nenologi – Looking Beneath the Words](docs/public/what-is-nenologi.md). The older topic-oriented documents under `docs/01-concept` through `docs/08-integrations` remain useful background; the files linked above are the canonical Phase 0 specification.

## Repository map

- `docs/project/` — product scope, language policy, editions, and milestones
- `docs/architecture/` — canonical core boundary, schema, and client contracts
- `docs/testing/` — corpus, gold-standard, and redistribution policy
- `docs/public/` — public-facing explanations
- `docs/references/` — future academic and technical bibliography
- `docs/01-concept` … `docs/08-integrations` — supporting topic notes
- `schemas/`, `src/`, `tests/`, `prompts/` — placeholders for Phase 1 implementation assets
