---
document_id: DAY25-NORAXON-OUTPUT-ADDENDUM
version: 1.0.0
status: approved_engineering_policy
scope: pre_site_verification
date: 2026-07-27
---

# Noraxon Output Uncertainty Resolution Addendum

> Day 25 không thể xác minh thay Motion Lab rằng file thực tế có cấu trúc gì.
> Nhưng Day 25 có thể giải quyết hoàn toàn rủi ro kỹ thuật do sự chưa biết đó
> bằng cách cô lập phần không chắc chắn trong lớp adapter, định nghĩa quy trình
> xác minh sau này và không để nó chặn public-data engineering.

## 1. Quyết định vận hành

Việc chưa có actual export từ Motion Lab **không chặn**:

- Public dataset ingestion
- Canonical data engineering
- DSP/QC development
- Baseline model research
- Experiment design
- UI/API/report development

Việc chưa có actual export **chỉ chặn**:

- Noraxon Motion Lab production adapter
- Site-specific channel mapping
- Local model adaptation
- MFCV activation tại site
- Clinical performance claims
- Patient-facing deployment

## 2. Trạng thái dự án

```yaml
project_status: CONTINUE_WITH_CONSTRAINTS

public_data_engineering: GO
canonical_pipeline: GO
public_baseline_training: CONDITIONAL_GO
noraxon_candidate_adapter: GO_PROVISIONAL
noraxon_site_verified_adapter: BLOCKED_EXTERNAL
motionlab_local_training: BLOCKED_EXTERNAL
mfcv_site_activation: BLOCKED_EXTERNAL
clinical_claims: NOT_ALLOWED
```

## 3. Training permissions (thay thế cờ đơn `trainingAllowed`)

```yaml
training_permissions:
  public_engineering_baseline:
    allowed: true
    conditions:
      - dataset_source_verified
      - license_verified
      - immutable_hash_available
      - subject_session_structure_available
      - label_mapping_frozen
      - leakage_safe_split_passed

  motionlab_local_model:
    allowed: false
    blocked_by:
      - no_actual_site_export
      - no_site_data_contract
      - no_site_channel_mapping
      - no_local_validation_data

  clinical_model:
    allowed: false
    blocked_by:
      - no_approved_clinical_protocol
      - no_ethics_governance_approval
      - no_patient_dataset
      - no_clinical_validation
```

## 4. Evidence status taxonomy

Mọi claim Noraxon phải được gán một trong các trạng thái:

| Trạng thái                  | Định nghĩa                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `OFFICIAL_PUBLIC_VERIFIED`  | Được xác nhận bởi tài liệu chính thức công khai của Noraxon                |
| `SITE_VERIFIED`             | Đã xác minh trực tiếp tại site với artifact thực tế                        |
| `INFERRED`                  | Suy diễn từ thông tin gián tiếp, chưa kiểm chứng                           |
| `NOT_VERIFIED`              | Chưa có bằng chứng                                                         |
| `CONFLICTING`               | Có thông tin mâu thuẫn giữa các nguồn                                      |

**Quy tắc:** `OFFICIAL_PUBLIC_VERIFIED ≠ SITE_VERIFIED`

## 5. Data-layer separation

| Layer | Tên                          | Quy tắc                                                       |
|-------|-------------------------------|----------------------------------------------------------------|
| L1    | Native acquisition record     | Không được gọi là CSV nếu chưa xác minh                       |
| L2    | Vendor export artifact        | Không được coi là raw nếu chưa xác minh export stage           |
| L3    | Project-normalized signal     | Phải ghi adapter và conversion provenance                      |
| L4    | Feature/metric store          | Phải ghi preprocessing/feature version                         |
| L5    | Model-ready dataset           | Chỉ được tạo sau data/license/split gate                      |

Ví dụ manifest layer tag:

```json
{
  "dataLayer": "L3_PROJECT_NORMALIZED",
  "sourceLayer": "L2_VENDOR_EXPORT",
  "nativeVendorFormatVerified": false,
  "sourceHashSha256": "sha256:...",
  "adapterId": "generic-csv",
  "adapterVersion": "0.2.0",
  "conversionPerformedByProject": true
}
```

## 6. Adapter classification

```yaml
adapter_classes:
  generic:
    verification: PROJECT_VERIFIED
    examples:
      - generic_csv
      - generic_mat
      - generic_c3d

  vendor_candidate:
    verification: OFFICIAL_PUBLIC_CAPABILITY_ONLY
    examples:
      - noraxon_ascii_candidate
      - noraxon_mat_candidate
      - noraxon_c3d_candidate

  site_verified:
    verification: SITE_VERIFIED
    examples:
      - noraxon_motionlab_v1
```

Mỗi candidate adapter phải chứa:

```yaml
site_verified: false
clinical_use_allowed: false
derived_from_real_motionlab_export: false
production_support_claimed: false
```

## 7. No invented site schema

Không được hard-code hoặc công bố các tên cột như `Time`, `Sensor 1.EMG`, `Event`, `Frame`, `Ultium Channel 01` như thể đó là schema thật của Motion Lab khi chưa có sample export.

Các tên trên chỉ được sử dụng trong test fixture nếu:

- Có namespace `candidate`
- Có manifest `synthetic`
- Có disclaimer
- Không được dùng cho claim tương thích site

## 8. Capability degradation policy

```yaml
capabilities:
  raw_signal_analysis:
    requires:
      - raw_or_near_raw_signal
      - sampling_rate
      - unit

  gesture_training:
    requires:
      - raw_signal
      - labels_or_markers
      - channel_mapping
      - repetition_or_trial_structure

  longitudinal_metrics:
    requires:
      - compatible_protocol
      - compatible_channel_map
      - compatible_preprocessing
      - same_subject_reference

  mfcv:
    requires:
      - ordered_electrode_geometry
      - known_ied
      - fibre_alignment
      - adequate_sampling
      - propagation_evidence
```

Nếu chỉ có processed RMS/MDF → chỉ report/longitudinal processed metrics. Không raw reprocessing, gesture model training, MFCV.

## 9. Scenario matrix

| Scenario                   | Xử lý                                                    |
|----------------------------|-----------------------------------------------------------|
| CSV/ASCII raw              | Mapping profile + CSV adapter                             |
| MATLAB `.mat`              | Inspect variables + MAT adapter                           |
| C3D                        | C3D adapter + analog channels/events                      |
| Native proprietary bundle  | Re-export qua MR3 sang format hỗ trợ                     |
| Processed report only      | ProcessedMetricsAdapter, không raw reprocessing            |
| PDF only                   | Chỉ archival/reference, không đủ cho training             |
| Không có usable export     | Site BLOCKED, public pipeline vẫn tiếp tục                |
| JSON do team tạo           | Đánh dấu `PROJECT_DERIVED`, không gọi native Noraxon      |

## 10. Definition of Done

Day 25 chỉ được coi là "giải quyết hoàn toàn về mặt engineering" khi:

- [x] Public capability và site capability đã tách
- [x] Native JSON vẫn NOT_VERIFIED
- [x] MFCV site vẫn NOT_VERIFIED
- [x] Canonical contract đã khóa
- [x] Adapter interface đã khóa
- [x] Vendor-candidate và site-verified adapter đã tách
- [x] Không có hard-coded site field names
- [x] Unknown-export inspector đã có
- [x] Mapping-profile schema đã có
- [x] Site onboarding runbook đã có
- [x] Capability degradation policy đã có
- [x] External blocker không chặn public engineering
- [x] Public/local/clinical training permissions đã tách
- [x] Conformance test contract đã có
- [x] Site adapter promotion gate đã có
