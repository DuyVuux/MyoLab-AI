# DAY04 Acceptance Criteria

## Roadmap acceptance

- [x] `clinical/quality/qc-taxonomy.v0.1.yaml` exists and is machine-readable.
- [x] `clinical/quality/artifact-vs-physiology-guidance.v0.1.md` exists.
- [x] `packages/common-schemas/json/quality-reason-codes.schema.json` exists.
- [x] All unverified thresholds/references remain `TBD`, `NOT_VERIFIED`, `POLICY_DEPENDENT`, or equivalent explicit state.
- [x] `FR-030..040`, `NFR-009`, `PRD-JTBD-03` are traceable.
- [x] Typed happy path/boundary/failure tests pass on synthetic QA fixtures.
- [x] Contexts such as stroke, paresis/paralysis, muscle atrophy and body habitus are not QC-failure reason codes.
- [x] Ambiguous artifact-vs-physiology evidence routes to review rather than forced cleanup.
- [x] No numerical clinical/site QC threshold is frozen.
- [x] No patient raw data, training or model artifact is introduced by DAY04.

## Upstream gate

Roadmap DAY04 requires accepted DAY03 outputs. The packaged DAY03 validation report is `BLOCKED_WITH_EVIDENCE`, because no reviewed baseline-eligible site observation was supplied.

Therefore the truthful DAY04 closeout status is:

`BLOCKED_WITH_EVIDENCE_UPSTREAM_DAY03`

The taxonomy may be technically valid, but `GO_FOR_DAY_05` must not be claimed until DAY03 is accepted and the DAY04 review is rerun in that integrated state.
