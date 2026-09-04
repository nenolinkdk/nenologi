# Nenologi – Looking Beneath the Words

## Structural, semantic and logical analysis of natural-language text

Nenologi is being designed for translators, linguists, authors, researchers, journalists, web-content creators, analysts, and curious users who need to inspect meaning more closely.

Conventional tools often ask:

> How similar are these texts?

or:

> What is this text about?

Nenologi asks a different question:

> What does the text assert, which relations and conditions does it establish, what follows from them, and is that still true in the other text?

It first examines sentence, clause, and discourse structure. It then represents entities, propositions, semantic roles, negation, quantities, modality, time, conditions, scope, and references. Where appropriate, it creates an explicit normalized logical representation for comparison or cautious inference.

```text
Natural language
  -> explicit structure and semantics
  -> normalized logical representation
  -> comparison / inference
```

For example, changing “All employees **must** register” to “All employees **may** register” preserves many words but weakens an obligation into permission or possibility. Changing “A **and** B” to “A **or** B” can similarly change a combined requirement into alternatives. Nenologi aims to make such changes visible and explain them in ordinary language.

Natural language is often genuinely ambiguous. Nenologi therefore does not promise one uniquely correct formalization. It can report alternate readings, uncertainty, unsupported conclusions, contradictions within the analysed material, or that a passage cannot be safely formalized. Confidence in the analysis is kept separate from the potential severity of a finding.

Nenologi does not claim access to hidden neural representations inside a language model. It creates its own explicit intermediate representation that people and tests can inspect. Future multi-source analysis may flag conflicting or unsupported claims within a supplied source set and suggest verification candidates; it will not declare that something is “fake” or that someone is lying.

The project is currently moving from specification to Nenologi Core v0.1: a reusable engine that will remain independent of its future Windows interface and later Trawedit integration.
