# DAY04_CLINICAL_DATA_QUALITY_TAXONOMY_HANDOFF

DAY04 implementation handoff for **Clinical Data-Quality Taxonomy: Artifact vs Physiological Variation**.

## Mandatory roadmap outputs

- `clinical/quality/qc-taxonomy.v0.1.yaml`
- `clinical/quality/artifact-vs-physiology-guidance.v0.1.md`
- `packages/common-schemas/json/quality-reason-codes.schema.json`

## Safety position

- pathology/context is not noise by default;
- physiological variation is not artifact by default;
- ambiguous evidence routes to review/abstention;
- no numerical clinical/site QC threshold is frozen;
- no training and no patient raw data are required by this pack.

## Upstream status

The packaged DAY03 validation status is `BLOCKED_WITH_EVIDENCE`. Therefore this DAY04 pack is technically complete but cannot truthfully claim `GO_FOR_DAY_05` until DAY03 is accepted and DAY04 is rerun/reviewed in that integrated state.

## Run

```bash
bash scripts/dev/run_day04_checks.sh
```
