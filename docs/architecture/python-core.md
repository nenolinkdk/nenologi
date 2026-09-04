# Python core domain layer

Nenologi Core v0.1 requires Python 3.11 or later and currently has no runtime dependencies outside the standard library. Python 3.11 provides `StrEnum`, modern typing, and broad active support without forcing a newer interpreter than the project presently needs.

## Package layout

```text
src/nenologi/
  models/          # values and structural, semantic, logical, analysis, comparison models
  serialization/   # explicit JSON conversion and deterministic validation
```

The package has no GUI, AI-provider, web-framework, database, or persistence dependency. The first parser-neutral interface and deliberately narrow implementation are documented in [Controlled English Analyzer v0.1](controlled-english-analyzer.md).

## Public API

Common construction requires only imports from `nenologi`. The public surface includes `Analyzer`, `ControlledEnglishAnalyzer`, `UnsupportedConstructionError`, `Analysis`, `Comparison`, `Difference`, `Confidence`, stable enums, component dataclasses, JSON conversion functions, and `validate_analysis` / `validate_comparison`. Internal token and grammar helpers are not public API.

```python
from nenologi import (
    Analysis, Confidence, Document, LocalizedText,
    analysis_to_json, validate_analysis,
)

analysis = Analysis(
    document=Document("doc_001", "en", "The valve is open."),
    profile="general",
    confidence=Confidence(1.0, "Controlled explicit wording"),
    plain_language_interpretation=LocalizedText("en", "The valve is open."),
)
validate_analysis(analysis)
payload = analysis_to_json(analysis)
```

The complete employees/MUST example and a manually constructed MUST→MAY comparison are in [`examples/core_v01.py`](../../examples/core_v01.py).

The controlled analyzer can be invoked directly:

```python
from nenologi import ControlledEnglishAnalyzer

analysis = ControlledEnglishAnalyzer().analyze("All employees must register.")
```

## Model and schema relationship

The dataclasses correspond to `analysis-v0.1.schema.json` and `comparison-v0.1.schema.json`. Tuples provide stable collection ordering in memory. Enums are defined once in `models/common.py` and serialize to the schema's uppercase identifiers. Conversion is explicit and uses UTF-8-friendly JSON (`ensure_ascii=False`), so display formulas retain Unicode.

Structured logical `expression` data is authoritative. The optional `display` formula is derived. v0.1 requires only an expression `operator` and JSON-compatible content; it intentionally does not freeze a complete logical AST.

## Validation levels

1. `DomainValidationError` — a directly constructed Python value violates an invariant, such as confidence outside `0.0–1.0`.
2. `SchemaValidationError` — input JSON/dictionaries have missing or unknown fields, wrong container shapes, invalid enums, or domain-invalid values.
3. `ReferenceValidationError` — typed data contains duplicate or unresolved IDs.

No level silently repairs data. `validate_analysis` and `validate_comparison` accept either typed models or mappings and return the validated typed model.

## v0.1 cross-reference rules

- Identified analysis objects must have globally unique IDs within one analysis.
- Structural parents and discourse endpoints resolve to structural nodes.
- Proposition arguments resolve to entities.
- Semantic arguments, operator scopes, `derived_from`, inference sources, and ambiguity readings resolve within the same analysis.
- Comparison finding references are explicitly qualified as `source.<id>` or `target.<id>` and must resolve in the corresponding analysis.
- Difference IDs must be unique within a comparison.

The document ID is metadata and is not part of the semantic reference namespace. v0.1 does not validate references nested inside the deliberately open logical-expression object; formal AST reference rules remain deferred.

## Development commands

From the repository root:

```text
python -m unittest discover -s tests -p "test_*.py"
python tests/validation/validate_gold_standard.py
python examples/core_v01.py
```

When running directly from a checkout without installation, add `src` to `PYTHONPATH`. An editable install also works with standard Python packaging tools.
