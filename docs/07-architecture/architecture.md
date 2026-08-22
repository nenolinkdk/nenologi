# Architecture

Nenologi should be implemented as a reusable engine rather than embedded directly in Trawedit.

Conceptual architecture:

```text
Input
  ↓
Pre-processing
  ↓
AI semantic extraction
  ↓
Structured semantic representation
  ↓
Deterministic comparison / rules
  ↓
Findings
  ↓
Natural-language explanation
  ↓
JSON / UI / PDF
```

Trawedit is one client of the engine.
