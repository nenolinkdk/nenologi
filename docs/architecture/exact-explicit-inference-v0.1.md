# Exact Explicit Inference v0.1

This Phase 2 milestone adds a parser-independent inference layer and makes `entailment_001` exact. It recognizes only a candidate whose complete normalized semantic graph is already present as the premise graph. It does not add implication, prediction, world knowledge, lexical opposition, or ambiguity resolution.

## Public contract

`InferenceEngine.infer(premise, conclusion)` consumes two `Analysis` values and returns the existing serializable `Inference` model. `DeterministicInferenceEngine` never inspects premise text to decide a result; raw text is retained only as the human-readable candidate `claim`.

An exact match returns:

- `interpretation_status = EXPLICIT`
- `rule = EXACT_EXPLICIT`
- confidence `1.0`
- ordered `derived_from` IDs for every premise semantic object used as evidence

A non-match returns `UNSUPPORTED` with rule `NOT_ESTABLISHED`, confidence `1.0`, and no evidence IDs. `NOT_ESTABLISHED` is a rule outcome, not a new interpretation status: it says that this deliberately narrow engine proved nothing. It does not assert falsity or contradiction.

## Exact semantic identity

Identity includes the full normalized semantic graph:

- predicate and ordered entity arguments, including normalized entity type and label;
- semantic relations and sets;
- quantifier, modality, and negation operators with their exact scopes;
- numeric operator, exact decimal value, unit, and scope;
- temporal relation, normalized reference, and governed proposition;
- condition antecedent and consequent references;
- interpretation status on each semantic object.

Analysis-local IDs are replaced by stable typed references before comparison. Source spans, structure nodes, confidence rationale, display formulas, document IDs, source spelling/casing/spacing, logical display objects, existing inferences, ambiguities, and plain-language rendering are not semantic match authority.

The original v0.1 rule compares complete graphs. Lexical Opposition Contradiction v0.1 subsequently adds one conservative selection case for rule precedence: an unwrapped bare proposition may be found explicitly inside a larger premise, while any relation, operator, condition, constraint, temporal relation, set, or scope wrapper blocks extraction. This supports deterministic handling of simultaneously present opposing bare states without introducing general subgraph inference.

## Conservative boundary

A conditional proposition never establishes its unconditional consequent. Even when an antecedent and consequent can both be represented, v0.1 performs no modus ponens. Differences in scope, modality, quantification, negation, numeric thresholds, temporal relations, spatial predicates, entity order, or condition wrappers therefore produce `NOT_ESTABLISHED`.

No parser, comparator, aligner, schema, or gold expectation changed in this milestone.

## Remaining inference cases

| Case | Parser | Semantic representation | Required inference capability | v0.1 applies? | Next missing capability |
| --- | --- | --- | --- | --- | --- |
| `entailment_002` | Unsupported | Incomplete | Universal instantiation and membership | No | Multi-sentence parsing, membership representation, and a sound rule contract |
| `entailment_003` | Unsupported | Incomplete | Defeasible prediction | No | Observation/future representation and calibrated non-deductive reasoning |
| `entailment_004` | Unsupported | Incomplete | Open-world non-entailment | No | Residence/fluency parsing and an explicit unsupported policy |
| `entailment_005` | Supported | Available: `OFF(switch)` / `ON(switch)` | Lexical opposition contradiction | No | Auditable `ON`/`OFF` opposition data and a contradiction rule |
| `entailment_006` | Unsupported | Incomplete | Coreference ambiguity | No | Embedded propositions and competing pronoun readings |
| `entailment_007` | Unsupported | Incomplete | Non-literal safety classification | No | Metaphor detection and a safe formalization boundary |

Lexical Opposition Contradiction v0.1 subsequently implements `entailment_005` with the single closed pair `OFF/ON`. The next recommended milestone is Controlled Rule and Membership Representation v0.1 for `entailment_002`.

## Verification

Unit tests cover exact identity, non-authoritative raw text, ordered entities and predicates, every supported operator/constraint family, spatial predicates, condition wrappers, absence of modus ponens, scope topology, structured evidence, stable explanations, serialization, and comparator regression. The 42-case audit moves from 26 to **27 `END_TO_END_EXACT`** and from 7 to **6 `INFERENCE_NOT_IMPLEMENTED`**; other totals are unchanged.
