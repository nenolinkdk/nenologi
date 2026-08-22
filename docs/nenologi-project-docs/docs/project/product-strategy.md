# Product strategy

## Decision

The first Nenologi user interface should be a **standalone Windows application**. Trawedit integration should come later.

## Why standalone first?

It provides a controlled environment for:
- testing the semantic model
- testing prompts and structured output
- refining word limits
- comparing model outputs
- developing PDF reports
- building reproducible test cases
- demonstrating Nenologi independently of translation editing

This avoids coupling the semantic model too early to Trawedit-specific code.

## Architectural rule

The Windows application must not contain its own separate analysis engine.

```text
Windows UI
  ↓
Nenologi application layer
  ↓
Nenologi core
  ↓
AI provider + deterministic comparison
```

Later:

```text
Trawedit
  ↓
Nenologi integration layer
  ↓
Nenologi core
```

## Role of Trawedit

Trawedit becomes the first major production integration, especially for:
- source-target Semantic QA
- selected segment analysis
- document-level logical differences
- explanations of findings
- optional formal representation
