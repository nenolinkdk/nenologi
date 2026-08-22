# Logical-semantic analysis compared with other analysis

## Core difference

Many text-analysis methods primarily examine form, terminology, statistical similarity or general topic. Nenologi focuses on propositions, relations, constraints and consequences.

Example:

Source:
> All patients must receive treatment A and treatment B.

Target:
> All patients may receive treatment A or treatment B.

A conventional similarity measure may report high similarity because most content words are preserved. A logical-semantic analysis identifies at least two major changes:

- `MUST → MAY`: obligation becomes possibility/permission.
- `AND → OR`: both treatments become an alternative.

## Comparison

| Analysis | Strong at | Can miss |
|---|---|---|
| Spelling/grammar | Formal language errors | Whether the intended meaning is preserved |
| Terminology QA | Term consistency | Relations between the terms |
| Text similarity | Degree of textual resemblance | Small but critical logical changes |
| Embeddings | Broad semantic proximity | Precise negation, scope and quantification |
| General LLM judgement | Nuance and overall interpretation | Stable, inspectable reasoning structure |
| Keyword SEO | Terms and frequency | What relations the page actually establishes |
| Logical-semantic analysis | Assertions, relations, conditions, scope and consequences | Pragmatics, irony and cultural implication can require uncertain interpretation |

Nenologi is intended as an additional QA layer, not a replacement for the other methods.
