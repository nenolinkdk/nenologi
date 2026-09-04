# Nenologi Analysis Schema v0.1

This document defines the conceptual JSON shape for Phase 1. It is deliberately small: field meaning and stable identifiers matter more than predicting every future use.

## Single analysis

```json
{
  "schema_version": "0.1",
  "document": {"id": "doc_1", "language": "en", "text": "All employees must register."},
  "profile": "general",
  "structure": {"sentences": [], "clauses": [], "discourse_relations": []},
  "entities": [],
  "propositions": [],
  "relations": [],
  "quantifiers": [],
  "modality": [],
  "negation": [],
  "conditions": [],
  "temporal_relations": [],
  "sets": [],
  "logical_representation": [],
  "inferences": [],
  "ambiguities": [],
  "confidence": {"value": 0.0, "rationale": ""},
  "plain_language_interpretation": {"language": "en", "text": ""}
}
```

Lists contain objects with stable local `id` values and references to related IDs. Derived items should include `derived_from` identifiers or a rule identifier. Source-grounded items should use character spans or equivalent provenance. Confidence values use a documented scale; missing confidence is not treated as zero.

Propositions may carry `interpretation_state`: `explicit`, `entailed`, `probable`, `ambiguous`, `unsupported`, `contradicted`, or `cannot_be_safely_formalized`. Ambiguity objects link competing readings rather than forcing one reading into the main result.

`logical_representation` stores structured expressions plus an optional human-readable rendering. Rendered formula text is never the only machine-readable form.

## Comparison

```json
{
  "schema_version": "0.1",
  "mode": "source_translation",
  "source_analysis": {},
  "target_analysis": {},
  "differences": [
    {
      "id": "diff_1",
      "difference_type": "MODALITY_CHANGE",
      "source_value": "MUST",
      "target_value": "MAY",
      "severity": "HIGH",
      "confidence": {"value": 0.98, "rationale": "Explicit modal verbs"},
      "interpretation": "The requirement becomes permission or possibility.",
      "evidence": []
    }
  ]
}
```

`source_analysis` and `target_analysis` are complete single analyses. Difference types are defined in the [MVP specification](../project/mvp-specification.md). Severity and confidence are separate required concepts.

## Future provenance extension

Claim/source analysis may add `sources` and `claims` using concepts such as source, author/publisher, date, claim, support, contradiction, `derived_from`, and confidence. This extension must describe consistency only within the analysed source set and avoid unsupported truth or deception labels.

## Deferred decisions

The formal JSON Schema file, identifier format, exact confidence scale, span convention, nullability rules, and expression AST are Phase 1 design tasks. Once chosen, examples become validation fixtures and schema changes follow explicit versioning.
