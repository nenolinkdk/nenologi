# Standalone Windows client

The first client is planned as a small standalone Windows application, probably Python with PySide6. It is a test and demonstration shell around Nenologi Core, not a full text editor.

## Intended functions

- Select an analysis profile and an independent comparison mode.
- Select UI, source-text, and target-text languages.
- Paste or load one or two short texts and show word limits.
- Run analysis with progress and cancellation.
- Show plain-language interpretation and findings first.
- Offer expandable structure, JSON/debug, and logical views.

Formula rendering follows [Formula rendering requirements](../project/formula-rendering.md). Feature availability follows the [central edition model](../project/edition-feature-model.md).

## Boundaries

The client may depend on `nenologi-core`; the reverse dependency is forbidden. UI strings live in localization resources. Analysis must not depend on widget state or event-loop behavior. The client translates user actions into serializable requests and renders serializable results.

GUI implementation, PDF export, production packaging, installers, auto-update, and Trawedit integration are outside Phase 1.
