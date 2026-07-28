# Day 27 — Decision Record

> Cập nhật: 2026-07-28

## D01: Dataset primary/fallback

| Field | Value |
|---|---|
| **Primary** | `MENDELEY_4CH_GESTURE` |
| **Fallback** | `GRABMYO_V1_1` |
| **Status** | `PRESELECTED_PENDING_CANONICAL_VERIFICATION` |

**Rationale:** Mendeley 4-channel phù hợp nhất với hướng sparse-channel (4–16 kênh) của MVP. Label vocabulary gần UC1 Gesture Recognition. Dataset nhỏ, thuận lợi cho việc khóa adapter, label mapper và canonical contract trước.

**Fallback triggers:** DOI/version không xác định, license không xác minh được, archive thiếu subject hierarchy, format không đọc được, hoặc label mapping cần suy diễn.

## D02: Scope chính — Task A Gesture Recognition

- Task A là scope chính của Day 27.
- Task B (Fatigue) và Task C (MFCV) **không** dùng dataset này làm corpus chính.
- MFCV **disabled** cho dataset này.
- Cross-session/cross-day chỉ được bật nếu metadata thật hỗ trợ.

## D03: Training vẫn bị khóa

```yaml
public_dataset_engineering_ready: pending  # chờ gate với data thật
public_baseline_training_eligible: pending
training_execution_allowed: false          # bất biến trong Day 27
motionlab_training_allowed: false
clinical_training_allowed: false
```

## D04: Phân biệt ba trạng thái

| Trạng thái | Ý nghĩa |
|---|---|
| `engineering-ready` | Dataset đã vượt Engineering Data Gate: nguồn gốc, license, hash, schema, label, split đều verified |
| `training-eligible` | Dataset đủ điều kiện kỹ thuật để dùng trong training pipeline |
| `training-authorized` | Environment lock, experiment manifest, test seal, leakage preflight và authorization record đều hoàn tất (Day 29+) |

## D05: Tooling validation — PASS

Day 27 tooling pipeline (artifact checker, 13 pytest, source template negative test, synthetic fixture verification) đã **PASS** trên synthetic data. Pipeline sẵn sàng nhận dataset thật.
