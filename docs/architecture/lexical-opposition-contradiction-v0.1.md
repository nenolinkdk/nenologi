# Lexical Opposition Contradiction v0.1

This Phase 2 milestone extends the existing parser-independent inference engine with one closed lexical rule. It makes `entailment_005` exact without adding a general antonym system.

## Gold requirement

`entailment_005` contains source `The switch is off.` and query `The switch is on.`. They normalize respectively to `OFF(switch)` and `ON(switch)`, each with one `ENTITY_CLASS` entity and no quantifier, modality, negation, condition, scope wrapper, numeric constraint, temporal relation, or additional semantic relation. Gold expects the existing `CONTRADICTED` interpretation status.

Exact Explicit Inference v0.1 correctly returned `UNSUPPORTED`/`NOT_ESTABLISHED`: the graphs were not identical, and it had no declared knowledge that these two controlled state predicates are incompatible.

## Closed registry

`LEXICAL_OPPOSITION_PAIRS` is immutable, public, and currently contains exactly:

```text
OFF <-> ON
```

`are_lexical_opposites` provides symmetric lookup over normalized predicate identifiers. The registry is source-controlled and manually auditable. No reverse entries are generated into hidden state, and no dictionary, WordNet, embedding, fuzzy match, morphology, external service, or LLM participates.

Pairs such as `OPEN/CLOSED`, `HOT/COLD`, `BIG/SMALL`, `GOOD/BAD`, and `POSSIBLE/IMPOSSIBLE` are intentionally absent. A future addition requires an explicit controlled-domain review.

## Matching and safeguards

The `LEXICAL_OPPOSITION` rule applies only when each analysis contains exactly one proposition, its predicates form a registered pair, and the complete normalized semantic signature is otherwise identical. This preserves:

- entity type and normalized label;
- arity and ordered arguments;
- relations and sets;
- quantifier, modality, and negation operators;
- numeric values, operators, units, and scopes;
- temporal relation, reference, and governed proposition;
- condition topology;
- explicit scope topology and interpretation statuses.

Different entities, argument order, arity, modality, quantification, conditions, scope, numeric thresholds, temporal structure, or spatial predicates therefore yield `UNSUPPORTED` with `NOT_ESTABLISHED`. Conditional lexical contradiction and modal reasoning are not attempted. Positive-versus-explicit-negation contradiction remains a separate, unimplemented inference route.

## Results, evidence, and precedence

The engine applies rules in this fixed order:

1. `EXACT_EXPLICIT` -> `EXPLICIT`
2. `LEXICAL_OPPOSITION` -> `CONTRADICTED`
3. `NOT_ESTABLISHED` -> `UNSUPPORTED`

Lexical-opposition evidence is the premise entity ID or IDs followed by its proposition ID. The query proposition belongs to a separate `Analysis` ID namespace and therefore cannot be placed in `Inference.derived_from`, whose schema requires references to resolve inside the analysis that stores the inference. The public rule identifier and closed registry together identify the opposition pair without weakening reference validation.

The explanation states only that the conclusion conflicts with an explicitly represented predicate under the controlled lexical rule set. It makes no real-world truth claim.

If a premise explicitly contains both `OFF(switch)` and `ON(switch)`, a query for an explicitly present bare proposition is still classified `EXPLICIT`. Exact support has priority. v0.1 does not perform knowledge-base consistency analysis or return combined support/conflict evidence.

## Architectural boundary and non-goals

The rule remains inside `DeterministicInferenceEngine`, consumes normalized `Analysis`, and does not alter the parser, comparator, aligner, `DifferenceType`, logical-relation taxonomy, domain model, or JSON Schema. Lexical contradiction is an inference result, not a comparison finding.

No synonymy, general antonymy, lexical similarity, prefix-derived polarity, scalar reasoning, ontology, hypernymy, negation inference, modal logic, conditional reasoning, numeric/temporal/spatial inference, coreference, commonsense, metaphor interpretation, or probabilistic reasoning is implemented.

## Gold impact and roadmap

The 42-case audit moves from 27 to **28 `END_TO_END_EXACT`** and from 6 to **5 `INFERENCE_NOT_IMPLEMENTED`**. All other totals remain unchanged.

| Case | Parser | Representation | Current inference status | Missing capability | Recommended milestone |
| --- | --- | --- | --- | --- | --- |
| `entailment_002` | Supported | Rule and membership available | Not implemented | Universal instantiation | Universal Instantiation v0.1 |
| `entailment_003` | Unsupported | Incomplete | Not implemented | Defeasible prediction | Observation and Prediction Semantics |
| `entailment_004` | Unsupported | Incomplete | Not implemented | Open-world unsupported judgment | Controlled Residence/Fluency Parsing and Non-entailment Policy |
| `entailment_006` | Unsupported | Incomplete | Not implemented | Embedded propositions and coreference ambiguity | Controlled Coreference Readings |
| `entailment_007` | Unsupported | Incomplete | Not implemented | Non-literal safety classification | Metaphor/Formalization Safety Boundary |

Controlled Rule and Membership Representation v0.1 subsequently establishes the parser and representation prerequisites for `entailment_002`. The next milestone is Universal Instantiation v0.1 over normalized structures.
