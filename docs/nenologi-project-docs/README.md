# Nenologi

Nenologi is a reusable semantic and logical text-analysis engine.

It converts natural-language text into a structured representation of meaning and can compare two texts to identify semantic and logical differences that ordinary spelling, terminology, keyword or similarity analysis may not expose.

Examples include AND→OR, MUST→MAY, ALL→SOME, BEFORE→AFTER, >→>=, changed negation, conditions, scope, additions, omissions and contradictions.

The default result should be clear natural language. Formal notation is an optional advanced view.

## Product strategy

The first usable version should be a **small standalone Windows application**.

The Windows application is a test and demonstration client for the Nenologi engine. The engine must be separated from the UI from the beginning.

Later, the same engine will be integrated into **Trawedit** as a Semantic / Logic QA module.

```text
nenologi-core
    ├── nenologi-windows
    └── Trawedit integration
```

## Initial profiles

General text, Biography, Procedure / recipe, Technical instructions, Rules / legal, Argumentation, Historical / news, Literary / poetry, Specifications, Prompt, SEO / web.

## Modes

Single text, Source / translation comparison, Version comparison, Prompt / output comparison, SEO localization comparison.

See `docs/project/` and `docs/roadmap/`.
