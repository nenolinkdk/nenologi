# Schemas

Nenologi v0.1 uses JSON Schema draft 2020-12:

- `analysis-v0.1.schema.json` — a single-text structural, semantic, and logical analysis
- `comparison-v0.1.schema.json` — two complete analyses plus semantic/logical findings
- `test-case-v0.1.schema.json` — controlled change, equivalence, and inference fixtures

Schema files use semantic artifact versions independent of the application version. Compatible clarifications retain `0.1`; incompatible changes require a new schema filename/version and an explicit migration decision. Relative `$id` values make local cross-schema references portable.

Before the v0.1 release, one taxonomy correction removed `CONTRADICTION` from `DifferenceType` and added optional comparison-level `logical_relation`. This distinguishes what changed from the logical relation between propositions; the rationale is documented in [deterministic comparison](../docs/architecture/deterministic-comparison.md).

The structured expression object is authoritative. Any `display` formula is derived for humans and must not be parsed as the canonical meaning.

Analysis v0.1 includes normalized `numeric_constraints`. Their exact decimal values are serialized as strings; optional units are preserved but never converted. See [controlled analysis](../docs/architecture/controlled-english-analyzer.md) and [deterministic comparison](../docs/architecture/deterministic-comparison.md).

Run the repository validator as described in [the gold-standard guide](../tests/gold_standard/README.md).
