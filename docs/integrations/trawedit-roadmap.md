# Trawedit integration roadmap

Nenologi should not initially be developed inside the Trawedit codebase.

When the core data model is stable, Trawedit should call Nenologi for:
- selected source-target segments
- multiple aligned segments
- document sections
- full documents within limits

Default output should stay concise:

```text
Meaning:        Possible change
Modality:       MUST → MAY
Conjunction:    Same
Negation:       Same
Time:           Same
Confidence:     High
```

Advanced users may expand structured representation, formal notation, evidence and debug data.

Document-level analysis may later generate a Nenologi QA PDF directly from Trawedit.
