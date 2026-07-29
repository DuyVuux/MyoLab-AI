# Day 31 risk register

| Risk | Control | Residual status |
|---|---|---|
| Sealed-test leakage | Exact partition allowlist and path-token guard before any batch I/O | Controlled and adversarially tested |
| Source substitution | Source path containment and SHA-256 verification | Controlled for canonical sources |
| Channel-map guessing | Explicit binary channel map; registered source-view policies | Controlled |
| Float overflow | Scale-safe math, no infinity output, QC reason codes | Controlled with missing affected values |
| Non-standard JSON NaN | Strict `allow_nan=false`, missing values serialized as `null` | Controlled |
| Feature redundancy | Train-only Pearson and Spearman reporting, no automatic drop | Analysis deferred to Day 32 inner training |
| Raw entropy cross-source comparability | Versioned raw bits; normalized entropy excluded from core 14 | Known limitation |
| Spectral instability at 200 ms | Registered 250/500 ms sensitivity lanes | To be quantified on real train data |
| Missing real Zone 2 root | Smoke-only gate; full gate remains unavailable | Open operational dependency |
| Clinical overclaim | No fatigue inference or clinical-use authorization | Controlled |
