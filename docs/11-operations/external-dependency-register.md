# External Dependency Register

Danh sách các phụ thuộc bên ngoài ảnh hưởng đến tiến độ dự án.
Một dependency có status `BLOCKED_EXTERNAL` **không có nghĩa dự án dừng**.

---

## EXT-NORAXON-001 — Motion Lab Actual Export

```yaml
dependency_id: EXT-NORAXON-001
title: Motion Lab actual export
owner_external: Motion Lab / Noraxon support
project_owner: Single Operator
status: BLOCKED_EXTERNAL
created: 2026-07-27
last_reviewed: 2026-07-27

blocks:
  - site_verified_adapter
  - site_channel_mapping
  - local_model_training
  - mfcv_activation
  - clinical_performance_claims
  - patient_facing_deployment

does_not_block:
  - public_data_pipeline
  - canonical_contract
  - baseline_training_on_public_data
  - DSP_QC_development
  - UI_API_development
  - experiment_design
  - report_generation

review_checkpoints:
  - Day30
  - Day36
  - before_local_adaptation

resolution_criteria:
  - Actual de-identified export received
  - inspect_unknown_export.py output generated
  - Field dictionary built
  - Mapping profile created and locked
  - Conformance tests passed
  - Adapter promoted to SITE_VERIFIED

escalation:
  if_not_resolved_by: Day36
  action: Re-evaluate site integration scope and timeline
```

---

## EXT-ETHICS-001 — Clinical Protocol Approval

```yaml
dependency_id: EXT-ETHICS-001
title: Ethics/IRB approval for clinical data collection
owner_external: Vinmec IRB / Ethics Committee
project_owner: Project Lead
status: NOT_STARTED
created: 2026-07-27

blocks:
  - clinical_model_training
  - patient_data_collection
  - clinical_validation
  - patient_facing_deployment

does_not_block:
  - all_engineering_activities
  - public_data_research
  - site_equipment_verification

review_checkpoints:
  - before_clinical_data_collection

resolution_criteria:
  - Approved clinical protocol document
  - IRB/Ethics committee approval letter
  - Data governance agreement signed
```
