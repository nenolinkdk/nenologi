# Schemas

Nenologi v0.1 uses JSON Schema draft 2020-12:

- `analysis-v0.1.schema.json` — a single-text structural, semantic, and logical analysis
- `comparison-v0.1.schema.json` — two complete analyses plus semantic/logical findings
- `test-case-v0.1.schema.json` — controlled change, equivalence, and inference fixtures

Schema files use semantic artifact versions independent of the application version. Compatible clarifications retain `0.1`; incompatible changes require a new schema filename/version and an explicit migration decision. Relative `$id` values make local cross-schema references portable.

The structured expression object is authoritative. Any `display` formula is derived for humans and must not be parsed as the canonical meaning.

Run the repository validator as described in [the gold-standard guide](../tests/gold_standard/README.md).
