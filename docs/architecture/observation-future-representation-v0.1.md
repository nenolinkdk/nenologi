# Controlled Observation and Future Representation v0.1

This representation-first milestone targets `entailment_003`:

```text
Source: The light flickered on each of the last five evenings.
Query:  The light will flicker this evening.
Gold:   PROBABLE
```

Both texts now parse into explicit normalized semantics. Prediction remains deliberately unimplemented, so deterministic inference returns `UNSUPPORTED` with `NOT_ESTABLISHED`; the audit retains `INFERENCE_NOT_IMPLEMENTED / DEFEASIBLE_PREDICTION` while marking parser and analysis readiness complete.

## Controlled grammar

Only these forms are added:

```text
The SUBJECT flickered on each of the last NUMBER evenings
The SUBJECT will flicker this evening
```

`NUMBER` is an integer or the existing number words zero through ten. The grammar does not generalize future tense, aspect, recurrence, or temporal noun phrases.

## Normalized semantics

Both forms assert the ordinary unary proposition `FLICKER(subject)`. “Observation” describes the evidential role of the source in the gold case; it is not part of the asserted content, so no special observation object or epistemic operator is introduced.

Each proposition is governed by the existing `TemporalRelation` with relation `ON`. The repeated source uses canonical reference `LAST_5_EVENINGS`; the future query uses `THIS_EVENING`. These are typed structural temporal values rather than resolved dates. They require no system clock or calendar arithmetic.

For this narrow form, `will` is a syntactic future marker realized through `THIS_EVENING`; it is not a Nenologi modality operator. This does not introduce a generic tense model or a new difference type. The existing semantic signature includes temporal relations, so the two claims are not exactly identical despite sharing predicate and entity.

## Conservative inference boundary

No prediction, persistence, recurrence, trend, or weather rule is added. Repeated past observations do not deterministically establish a future event, and the result is not a contradiction. Identical future propositions still match through `EXACT_EXPLICIT`.

The comparator is unchanged and reports the existing `TEMPORAL_CHANGE` between `ON LAST_5_EVENINGS` and `ON THIS_EVENING`. Inference code, schemas, entity taxonomy, and `DifferenceType` remain unchanged.

## Audit and limitations

The 42-case totals remain 30 exact, 0 analyzable-but-inexact, 7 parser-unsupported, 2 comparator-unsupported, and 3 inference-not-implemented. Internally, `entailment_003` changes from parser `UNSUPPORTED` / analysis `INCOMPLETE` to parser `SUPPORTED` / analysis `AVAILABLE`; only `DEFEASIBLE_PREDICTION` remains.

Unsupported forms include `tomorrow`, `later`, `next week`, progressive or modal futures, other recurrence phrases, other times of day, multi-event input, temporal arithmetic, probability language, and domain forecasting.

The next milestone for this case would be an explicit defeasible-prediction policy with calibrated evidence and confidence. Until that policy exists, the safer next deterministic representation milestone is controlled coreference alternatives for `entailment_006`, without selecting a referent.
