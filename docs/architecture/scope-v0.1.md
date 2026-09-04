# Scope v0.1

Scope states which normalized semantic component an operator governs. The structured `Operator.scope` references are authoritative; formulas and explanations are derived displays.

| Status | Capability |
| --- | --- |
| **SUPPORTED** | Acyclic, single-target scope chains involving one quantifier, one modality, explicit `NOT`, and one aligned proposition; deterministic `SCOPE_CHANGE`; JSON round-trip and reference validation. |
| **LIMITED** | The parser recognizes the dedicated `Not all SUBJECT [MODAL] PREDICATE` form and ordinary modal-internal `not`. The comparator also accepts manually constructed normalized analyses, independently of the parser. |
| **UNSUPPORTED** | General scope resolution, arbitrary nesting, quantifier raising, free word order, embedded-clause scope, distributivity, de re/de dicto readings, and broad ambiguity handling. |

For the controlled pair `Not all employees must register.` and `All employees must not register.`, normalization records respectively `NOT > ALL > MUST > proposition` and `ALL > MUST > NOT > proposition`. These yield one `SCOPE_CHANGE`, not duplicate `NEGATION_CHANGE` or `QUANTIFIER_CHANGE` findings. A real operator identity change, such as `ALL` to `SOME`, remains a separate finding and can coexist with `SCOPE_CHANGE`.

`Employees may not register.` retains the existing fixed controlled reading `MAY > NOT > proposition`. Nenologi does not claim that this resolves the natural-language **MAY NOT** ambiguity; other readings must be represented explicitly at domain level or rejected by the controlled parser.

A scope difference has comparison-level logical relation `UNDETERMINED`. Scope v0.1 adds no quantifier logic, modal logic, contradiction rule, entailment, or NLI.

The two existing scope gold cases use embedded verbs (`promise to leave` and `require ... to leave`) outside the controlled grammar. They therefore remain parser-unsupported: exact scope coverage stays 0 of 2, while domain-level and the dedicated controlled construction are covered by unit tests.
