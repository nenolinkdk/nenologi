# Nenologi Core v0.1 MVP specification

## Purpose

Phase 1 proves that short English texts can be converted into understandable, testable representations and that two such representations can be compared. The core must preserve uncertainty instead of forcing every input into one formal reading.

## Required pipeline

1. Accept text, language metadata, an analysis profile, and a comparison mode.
2. Identify document, sentence, clause, coordination, subordination, sequence, and discourse structure.
3. Extract semantic objects and operators.
4. Normalize supported content without discarding alternate interpretations.
5. Produce structured JSON, a plain-English interpretation, and a logical representation.
6. In comparison mode, align relevant propositions and report material differences.

The analytical layers are defined in [Multilayer analysis](multilayer-analysis.md), and the interchange model in [Analysis Schema v0.1](../architecture/semantic-json-schema.md).

## Profiles

Priority profiles are General text, Translation comparison, Biography, Procedure / recipe, Technical instructions, Prompt, Prompt → Output, Specifications, and SEO / web content. Implementation begins with General text and Translation comparison.

Later or experimental profiles are Rules / legal, Argumentation, Historical / news, Literary / poetry, Professional profile / application analysis, and Claim & source consistency analysis. Profiles tune extraction and presentation; they do not create separate engines.

## Comparison modes

- Single text
- Source ↔ translation
- Version A ↔ Version B
- Prompt ↔ AI output
- SEO source ↔ localized page

Analysis profile and comparison mode are independent dimensions. A future professional-profile workflow may compare a job advertisement, LinkedIn PDF, CV, and application to relate requirements, claims, and evidence—not to decide whether a person should be hired.

## Difference taxonomy

- `NEGATION_CHANGE`
- `CONJUNCTION_CHANGE`
- `QUANTIFIER_CHANGE`
- `MODALITY_CHANGE`
- `CONDITION_CHANGE`
- `TEMPORAL_CHANGE`
- `SCOPE_CHANGE`
- `ENTITY_RELATION_CHANGE`
- `ADDITION`
- `OMISSION`
- `CONTRADICTION`
- `NUMERIC_THRESHOLD_CHANGE`

Critical minimal pairs include MUST/MAY, AND/OR, ALL/SOME, BEFORE/AFTER, `>`/`>=`, added or removed negation, and added or removed conditions.

```text
Source: All patients must receive treatment A and treatment B.
Target: All patients may receive treatment A or treatment B.
```

The result must report both `MODALITY_CHANGE` (obligation becomes permission or possibility) and `CONJUNCTION_CHANGE` (both treatments become alternatives).

## Interpretation and findings

Allowed interpretation states are `EXPLICIT`, `ENTAILED`, `PROBABLE`, `AMBIGUOUS`, `UNSUPPORTED`, `CONTRADICTED`, and `CANNOT_BE_SAFELY_FORMALIZED`. Ambiguous inputs may carry multiple candidate readings. `PROBABLE` is not entailment. Severity expresses potential impact; confidence expresses support for an analysis. Neither determines the other. The exact v0.1 representations are documented in [Analysis Schema v0.1](../architecture/semantic-json-schema.md).

## Out of scope for Phase 1

- GUI implementation or a full text editor
- External AI APIs or selection of a commercial LLM provider
- PDF export, licensing enforcement, and Trawedit integration
- Automated hiring decisions
- Truth, deception, or “fake news” classification
- Complete formalization of unrestricted natural language

Future claim/source analysis may report conflicting claims, temporal inconsistencies, unsupported claims within the supplied source set, changing claims over time, possible common-source dependencies, and verification candidates. It must not label a claim “fake” or a person a liar.

## Acceptance criteria

1. A controlled English sentence produces schema-valid JSON, a plain-English interpretation, and a logical representation.
2. A controlled source/target pair produces two independent analyses and correctly classified differences.
3. Automated tests cover critical minimal pairs and uncertainty states.
4. Core tests run without PySide6 or any GUI package.
5. Outputs are deterministic where rules are deterministic and record uncertainty where interpretation is not unique.
