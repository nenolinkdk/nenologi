# Language and internationalization

English is canonical for source code, identifiers, schemas, tests, developer documentation, and development discussions recorded in the repository.

Nenologi keeps three dimensions separate:

- **UI language** — labels, messages, and explanations shown by a client
- **Source text language** — the language of the first or only analysed text
- **Target text language** — the language of the second text in applicable comparisons

An English UI must be able to analyse French source text against Danish target text. Changing the UI language must not alter source/target language metadata or the analysis result.

Initial UI localization is planned for English (`en`), Danish (`da`), and French (`fr`). Visible UI strings belong in client localization resources, not core analysis rules. Machine identifiers, enum values, and JSON keys remain English and stable. Human-readable explanations carry a language tag and use a replaceable rendering/localization layer.

Language-specific tokenization, morphology, parsing, and lexical resources implement core-facing interfaces. Phase 1 begins with controlled English input, but the schema includes language metadata from the outset.
