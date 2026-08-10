# DAY15 Acceptance Criteria

## AC-D15-01 — Mandatory roadmap factory

`qa-validation/test-data/synthetic/generators/noraxon_corruption_factory.py` exists, is deterministic and never mutates its source seed.

## AC-D15-02 — Required corruption dimensions

Fixed/generative coverage includes malformed header, count mismatch, duplicate/out-of-order timestamp, missing row, unknown unit and malformed `signal_2d` shape.

## AC-D15-03 — Legal-edge protection

`MIXED_FS` and `UTF8_BOM` are accepted. Missing raw values are preserved. Unknown vendor fields are preserved/surfaced.

## AC-D15-04 — Four critical safety invariants

Machine-readable contract contains:

- `RAW_IMMUTABLE`
- `UNKNOWN_UNIT_NEVER_INFERRED`
- `NO_SILENT_CRASH`
- `FAIL_CLOSED`

## AC-D15-05 — Property-based verification

Generated constrained cases exercise the invariant harness; deliberate unsafe adapters are detected.

## AC-D15-06 — Typed failure

Every invalid fixed fixture has a stable reason code and cannot create final-looking output.

## AC-D15-07 — Determinism

Same seed/factory version/input seed produces deterministic fixture/property-case truth and repeated probes return the same outcome.

## AC-D15-08 — Evidence limits

All checked-in fixtures are synthetic, `clinical_evidence=false`, `site_verified=false`; production parser binding remains false.

## AC-D15-09 — Upstream regression

DAY09–DAY14 tests present in the integrated monorepo remain green.

## AC-D15-10 — Safety scope

No production MR4 parser, OOD model, SSL training, DSP preprocessing, clinical threshold fitting, raw patient data or model artifact is introduced.

## Gate

`GO_FOR_DAY_16` only after DAY15 tests + live upstream regression + human semantic review pass. Otherwise use `READY_WITH_LIMITATIONS` or `BLOCKED_WITH_EVIDENCE` according to impact.
