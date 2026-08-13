# Public Benchmark Evidence Index — GATE E-R Attempt

| Evidence | Status | Role |
|---|---|---|
| `public-benchmark-selection-v1.0.yaml` | FROZEN INPUT | DAY64 governance |
| `public-benchmark-protocol.v1.0.yaml` | FROZEN INPUT | DAY66 anti-leakage protocol |
| `public-benchmark-splits-v1.0.csv` | FROZEN INPUT | subject-wise public split plan |
| DAY67 completion summary | SITE TECHNICAL EVIDENCE | 187 CSV, 183 parseable, 4 PHI-aware exclusions |
| `public-feature-summary-v1.1.parquet` | SITE TECHNICAL FEATURE EVIDENCE | 12/12 available features, exact SHA recorded |
| `cross-dataset-domain-shift-v1.0.csv` | RESEARCH EVIDENCE | public comparisons explicitly `INCOMPARABLE/UNKNOWN` |
| `cross-dataset-generalization-v1.0.md` | RESEARCH EVIDENCE | denominator-linked generalization limits |
| `ml-feasibility-v0.1.md` | RESEARCH DECISION | `ML_NO_GO` |
| `gate-e-r-evaluation.json` | GATE EVIDENCE | `BLOCKED_WITH_EVIDENCE` |

## Evidence-tier warning

The word `public` in an artifact filename/version is not evidence origin. The
current DAY68 rows are site-derived technical evidence. Public datasets remain
catalogued/frozen inputs but not evaluated feature domains in the supplied
DAY68 table.
