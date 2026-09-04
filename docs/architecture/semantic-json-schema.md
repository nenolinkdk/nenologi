# Nenologi Analysis Schema v0.1

The machine-readable JSON Schema draft 2020-12 files are in [`schemas/`](../../schemas/README.md). Version `0.1` is deliberately small: field meaning and stable identifiers matter more than predicting every future use.

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
    "numeric_constraints": [],
  "conditions": [],
  "temporal_relations": [],
  "sets": [],
  "logical_representation": [],
  "inferences": [],
  "ambiguities": [],
  "confidence": {"value": 0.95, "rationale": "Explicit wording"},
  "plain_language_interpretation": {"language": "en", "text": ""}
}
```

Lists contain objects with stable local `id` values and references to related IDs. Derived items should include `derived_from` identifiers or a rule identifier. Source-grounded items use zero-based, end-exclusive character spans.

Confidence v0.1 is a number from `0.0` (no confidence) through `1.0` (maximum confidence), with an optional rationale. It describes confidence in the specific analysis—not truth probability—and is replaceable in a later schema version. Missing confidence is not treated as zero.

Propositions use stable uppercase statuses: `EXPLICIT`, `ENTAILED`, `PROBABLE`, `AMBIGUOUS`, `UNSUPPORTED`, `CONTRADICTED`, or `CANNOT_BE_SAFELY_FORMALIZED`. `PROBABLE` is defeasible support and is never a synonym for `ENTAILED`. Ambiguity objects link competing readings rather than forcing one reading into the main result.

`logical_representation` stores a structured expression object plus an optional human-readable `display`. The structured object is authoritative. A formula such as `∀x (Employee(x) → Must(Register(x)))` is derived for display and must never override or substitute for the structured semantics. v0.1 requires an expression operator but intentionally leaves its deeper AST extensible while Core work establishes the smallest useful vocabulary.

`numeric_constraints` contains authoritative normalized thresholds with `operator`, canonical string `value`, optional `unit`, and semantic `scope`. Operators are `GREATER_THAN`, `GREATER_THAN_OR_EQUAL`, `LESS_THAN`, `LESS_THAN_OR_EQUAL`, and `EQUAL`. Values are strings to preserve exact decimal meaning across JSON implementations; display symbols are derived.

`conditions` contains structured `Condition` objects with stable identity and non-empty `antecedent` and `consequent` proposition-reference arrays, plus status, confidence, and optional span. The referenced propositions and their existing operators/constraints remain authoritative; conditions do not duplicate their semantic content as text. A logical `P → Q` string is derived only for display.

## Comparison

```json
{
  "schema_version": "0.1",
  "mode": "source_translation",
  "logical_relation": "UNDETERMINED",
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
      "explanation": "The requirement becomes permission or possibility.",
      "references": []
    }
  ]
}
```

`source_analysis` and `target_analysis` are complete single analyses. Difference types are defined in the [MVP specification](../project/mvp-specification.md). Severity and confidence are separate required concepts.

`differences` describe what changed. The optional comparison-level `logical_relation` independently records `EQUIVALENT`, `CONTRADICTORY`, or `UNDETERMINED`. Pure polarity reversal is therefore a `NEGATION_CHANGE` with a `CONTRADICTORY` relation, not two difference findings. `CONTRADICTION` was removed from `DifferenceType` as a v0.1 taxonomy correction before release.

Severity v0.1 is `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. It estimates the impact of a comparison finding in context; it does not express confidence. Equivalence is represented by an empty `differences` list, not a synthetic `NONE` severity.

Document language uses a compact BCP-47-compatible language tag pattern. UI language does not belong in analysis or comparison data. A comparison carries source and target languages inside its two document objects.

## Versioning

Each artifact contains `schema_version: "0.1"`; filenames also carry the version. Compatible editorial clarification may retain `0.1`. An incompatible shape or semantic change requires a new schema version and an explicit migration decision. Test cases separately use the versioned [test-case schema](../../schemas/test-case-v0.1.schema.json).

## Future provenance extension

Claim/source analysis may add `sources` and `claims` using concepts such as source, author/publisher, date, claim, support, contradiction, `derived_from`, and confidence. This extension must describe consistency only within the analysed source set and avoid unsupported truth or deception labels.

## Deferred decisions

The complete logical-expression AST, reference-integrity rules, confidence calibration, and profile-specific extensions remain Phase 1 design tasks. The v0.1 schema fixes enough structure and enums to support fixtures and typed domain models without claiming a complete natural-language logic.
