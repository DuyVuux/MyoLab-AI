# Canonical Research Dataset Contract v0.2

## Mục tiêu

Tạo một contract trung gian độc lập vendor để các adapter public dataset và adapter Noraxon có thể ánh xạ vào cùng một cấu trúc mà không làm mất provenance.

## 1. Identity và provenance

```text
dataset_id
canonical_name
version
record_id
source_url_or_doi
source_hash_sha256
retrieval_date
native_or_converted
adapter_id/version
```

## 2. Legal và governance

```text
access_class
license_class
license_text
commercial_use_allowed
redistribution_allowed
dua_required
ethics_or_irb_required
allowed_purposes
```

## 3. Hierarchy

```text
subject_id
session_id
day_id
trial_id
repetition_id
window_id
```

`subject_id` và `session_id` phải là pseudonymous/non-PHI.

## 4. Signal metadata

```text
sampling_rate_hz
unit
channel_count
sample_count
time_axis_type
raw_or_processed
preprocessing_already_applied
missing_value_representation
```

Không đoán unit từ amplitude.

## 5. Electrode/channel metadata

```text
channel_index
source_channel_name
canonical_channel_id
sensor_id
muscle
body_side
electrode_type
electrode_geometry
inter_electrode_distance_mm
orientation
layout_version
```

## 6. Task và labels

```text
task_type
label_taxonomy_version
label
label_source
label_timestamp_or_segment
cue_source
reviewer/adjudication status
```

## 7. Fatigue/context metadata

```text
MVC
force
RPE
elapsed_time
fatigue_label_level
before/during/after context
```

## 8. Synchronization

```text
event_markers
sync_method
sync_offset
modalities
VICON/force/pressure/video/IMU references
```

## 9. Privacy

```text
contains_direct_identifiers = false
phi_screening = pass
raw_samples_embedded_in_manifest = false
```

## 10. Split contract

```text
group_unit = subject | session
random_window_split = false
split_seed
split_hash
```

## 11. Readiness

```text
status = go | conditional_go | no_go
blocking_items
```

## 12. Training permissions (thay thế `training_allowed` đơn)

```yaml
training_permissions:
  public_engineering_baseline:
    allowed: true | false
    conditions: [...]
  motionlab_local_model:
    allowed: true | false
    blocked_by: [...]
  clinical_model:
    allowed: true | false
    blocked_by: [...]
```

## 13. Data layer tag

```text
data_layer = L1_NATIVE | L2_VENDOR_EXPORT | L3_PROJECT_NORMALIZED | L4_FEATURE_STORE | L5_MODEL_READY
source_layer
native_vendor_format_verified = true | false
conversion_performed_by_project = true | false
```

## 14. Adapter provenance

```text
adapter_id
adapter_version
adapter_class = generic | vendor_candidate | site_verified
site_verified = true | false
clinical_use_allowed = true | false
derived_from_real_site_export = true | false
mapping_profile_id
mapping_profile_hash
```

## 15. Capability-gated fields

```text
electrode_order
inter_electrode_distance_mm
fibre_orientation
propagation_evidence
mfcv_eligibility
```

Nếu thiếu trường required → `import_rejected` hoặc `mapping_required`.
Nếu thiếu trường MFCV → `mfcv.eligible = false`, basic sEMG pipeline vẫn chạy.
MFCV là optional capability, không block toàn bộ phân tích sEMG.

Contract này không chứng minh dữ liệu phù hợp lâm sàng; nó chỉ giúp dữ liệu được truy vết, kiểm tra và chia tập đúng.
