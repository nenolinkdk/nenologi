# Edition and feature model

Nenologi uses one codebase and a centralized, declarative feature policy. Clients ask the policy whether a capability is enabled and which limit applies; screens and analysis modules must not scatter edition-name checks.

Planned editions are `DEMO`, `CONFERENCE`, `PROFESSIONAL`, and `DEVELOPMENT`. They are planning concepts, not a licensing implementation.

```yaml
edition: DEMO
max_words_single: 250
max_words_comparison: 150
enabled_profiles:
  - general
  - translation
  - prompt_output
features:
  pdf_export: false
  json_export: false
  batch_analysis: false
  advanced_logic: limited
```

`PROFESSIONAL` may later allow higher limits, all production-ready profiles, exports, and batch analysis. `CONFERENCE` may expose a stable curated demonstration set. `DEVELOPMENT` may enable diagnostics and experimental profiles.

The policy returns structured capability decisions that clients can explain. Licensing, payment, activation, cryptographic enforcement, and final commercial limits are unresolved and outside Phase 1.
