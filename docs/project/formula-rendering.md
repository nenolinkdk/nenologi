# Formula rendering requirements

Future clients should display Unicode logical and mathematical notation clearly:

```text
∀x (P(x) → Q(x))
A ⊆ B     A ∩ B     x ∈ A
P ∧ Q     P ∨ Q     ¬P
P → Q     P ↔ Q     ⊨     ⊢
≤     ≥     ≠
```

The primary UI font and mathematical fallback font are separate configuration concerns. The fallback must cover the required glyphs and align acceptably with surrounding text.

No LaTeX editor is required. Possible later actions are Copy formula, Copy as plain text, and Copy as LaTeX. The core exposes structured expressions; the client controls display and copying.
