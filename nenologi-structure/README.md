# Nenologi

Nenologi is a semantic and logical analysis engine for text, translation, prompts and structured content.

The engine is intended to be reusable. Trawedit can use Nenologi as a Semantic/Logic QA module, while the same engine can later support standalone analysis, SEO analysis, prompt/output comparison and other clients.

## Core model

Nenologi focuses on what a text states, which entities and relations it establishes, which constraints apply, and what can reasonably be inferred.

Two independent dimensions are used:

- **Analysis profile** — e.g. biography, procedure, prompt or SEO.
- **Mode** — single-text analysis or comparison.

See `docs/` for the project specification.
