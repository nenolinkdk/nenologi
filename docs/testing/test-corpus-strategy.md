# Test corpus strategy

The future corpus is organized by purpose:

```text
test_corpus/
  synthetic/
  biography/
  news/
  procedure/
  technical/
  translation/
  prompt-output/
  seo/
  literary/
  ambiguous/
```

It contains three complementary categories:

1. Controlled minimal examples that isolate one operator or relation.
2. Real texts that exercise normal variation and interacting phenomena.
3. Source/target pairs with deliberately inserted semantic differences.

Each committed case records an ID, category, input language, profile, mode, expected structures or findings, provenance/license metadata, and reviewer notes. Tests should distinguish exact stable expectations from acceptable alternatives for ambiguous text.

The initial gold standard contains approximately 30 controlled change cases. Priority coverage includes negation, conjunction, quantification, modality, conditions, temporal order, scope, entity relations, addition/omission, contradiction relations, and numeric thresholds. See [Gold standard](gold-standard.md).

Reference analyses and intermediate representations should remain versioned. Changes require review because they support regression tests, architecture demonstrations, future benchmarks, and conference material.

Numeric Thresholds v0.1 executes all four committed numeric change cases and the controlled numeric equivalence case. General ranges, conversion, approximation, and entailment remain future corpus targets rather than current parser promises.

Conditions v0.1 executes the prefix-IF removal case. Suffix conditions and `UNLESS` remain future controlled-grammar decisions rather than being accepted merely for corpus coverage.

Temporal Relations v0.1 executes the weekday-based `BEFORE → ON` case. Event-clause anchors and nested temporal relations remain future grammar decisions.
