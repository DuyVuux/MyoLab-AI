# Kế hoạch kiểm thử Day 8 — Trích xuất RMS/MAV v0.1

**Phạm vi:** kiểm chứng phân tích phần mềm/DSP trên dữ liệu synthetic và các vector kiểm soát  
**Không thuộc phạm vi:** xác nhận lâm sàng, xác nhận mô hình hoặc kiểm thử khả dụng

## 1. Mục tiêu

Xác nhận rằng implementation:

- tính đúng RMS/MAV theo công thức đã đặc tả;
- bảo toàn unit;
- chỉ tính trên valid time-domain windows;
- giữ traceability cho invalid windows;
- deterministic;
- không làm rò raw samples;
- không sinh fatigue/clinical output;
- chặn khi upstream không hợp lệ.

---

## 2. Test levels

| Level | Scope | Files |
|---|---|---|
| Pure unit | công thức RMS/MAV | `packages/semg-core/tests/test_features.py` |
| Config guardrail | input/output/safety contract | `test_feature_config.py` |
| Service unit | wrapper `uV` | `test_time_domain_features.py` |
| Integration | WindowingResult → feature rows | `test_feature_extractor.py` |
| Analytical | sine/scale/unit properties | `qa-validation/automated-tests/test_time_domain_feature_analytical.py` |
| E2E | CSV → QC → preprocess → window → features | `run_time_domain_features.py` |
| Contract | JSON Schema | common schemas |
| Governance | registry/artifact/safety | `check_day8_artifacts.py` |

---

## 3. Mathematical test matrix

| ID | Input | Expected | Tolerance |
|---|---|---|---:|
| TD-MATH-001 | `[-3,-1,1,3]` | RMS=`sqrt(5)`, MAV=`2` | `1e-12` |
| TD-MATH-002 | `[-5,5,-5,5]` | RMS=MAV=`5` | `1e-12` |
| TD-MATH-003 | zero vector | RMS=MAV=`0` | exact |
| TD-MATH-004 | sine, known amplitude | RMS=`A/sqrt(2)` | stated tolerance |
| TD-MATH-005 | sign inversion | unchanged | `1e-12` |
| TD-MATH-006 | scale `c` | multiply by `|c|` | `1e-12` |
| TD-MATH-007 | random finite vectors | RMS≥MAV | tolerance |
| TD-MATH-008 | very large finite values | finite output | boolean |

### Invalid input tests

| ID | Input | Expected |
|---|---|---|
| TD-ERR-001 | empty array | `FeatureExtractionError` |
| TD-ERR-002 | 2-D array | error |
| TD-ERR-003 | contains NaN | error |
| TD-ERR-004 | contains Inf | error |

---

## 4. Config guardrail tests

| ID | Mutation | Expected |
|---|---|---|
| CFG-001 | enable rectification before RMS | reject |
| CFG-002 | enable MVC normalization | reject |
| CFG-003 | add MDF in Day 8 feature list | reject |
| CFG-004 | allow cross-session comparison | reject |
| CFG-005 | enable aggregation/trend | reject |
| CFG-006 | enable ML/FRS interpretation | reject |

---

## 5. Window integration tests

### Golden

Input:

```text
active phase = 60 s
Fs = 1000 Hz
time-domain window = 500 ms
overlap = 50%
window count = 239
all windows valid
```

Expected:

```text
status = completed
downstream_allowed = true
total rows = 239
computed rows = 239
not-computed rows = 0
usable ratio = 1.0
```

### Invalid mask propagation

Inject one invalid sample that intersects two overlapping 500 ms windows.

Expected:

```text
status = completed_with_exclusions
computed = 237
not_computed = 2
not_computed window indices = [2,3]
features = null on excluded rows
reason codes preserved
```

### Upstream block

Expected:

```text
status = blocked
rows = []
result_hash = null
reason = FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING
```

### Version mismatch

- wrong preprocess ID → blocked;
- wrong windowing ID → blocked;
- wrong profile purpose → blocked.

---

## 6. Determinism tests

Chạy cùng input/config hai lần trong cùng environment:

```text
result_hash_run_1 == result_hash_run_2
feature_row_ids_run_1 == feature_row_ids_run_2
row ordering identical
```

Exact hash giữa môi trường khác có thể bị ảnh hưởng bởi numerical stack; environment/version phải được giữ trong validation evidence hoặc release manifest khi cần.

---

## 7. Schema tests

Validate:

- `feature-row.schema.json`;
- `time-domain-feature-result.schema.json`;
- `time-domain-feature-verification.schema.json`.

Invariants:

```text
computed → features object and empty reasons
not_computed → features null and non-empty reasons
blocked → no rows and null result hash
completed → at least one row and non-null result hash
```

---

## 8. Data minimization tests

Serialized JSON không được chứa token:

```text
samples_uV
raw_samples
patient_name
medical_record_number
```

CSV chỉ chứa feature/metadata/provenance cần thiết.

---

## 9. Safety tests

- Extractor không import `sklearn`, TensorFlow hoặc PyTorch.
- Không có FRS.
- Không có fatigue status.
- Không có diagnosis/recommendation.
- `clinical_validation_status` vẫn `not_validated`.
- Registry cấm cross-session comparison.

---

## 10. Synthetic sanity trend

Golden synthetic generator được thiết kế có amplitude envelope tăng nhẹ. Test xác nhận mean RMS/MAV của 20 window cuối lớn hơn 20 window đầu.

Kết luận được phép:

> Generator và feature extractor nối với nhau đúng theo synthetic design.

Kết luận không được phép:

> RMS/MAV tăng chứng minh fatigue detection đúng.

---

## 11. Pass criteria

- 100% required tests pass.
- Không có xfail cho safety-critical behavior.
- Golden 239 rows đúng.
- Deterministic hash đúng.
- Schemas pass.
- Registry pass.
- Artifact checker pass.
- No raw samples.
- No clinical overclaim.

## 12. Failure handling

Nếu mathematical test fail:

```text
STOP
→ không sửa expected value để làm test pass
→ kiểm tra công thức, sampling assumption, tolerance
```

Nếu E2E fail nhưng pure math pass:

```text
kiểm tra unit, window geometry, profile selection, version mapping
```

Nếu deterministic hash fail:

```text
kiểm tra ordering, non-deterministic metadata, float serialization, environment
```

Nếu schema fail:

```text
contract hoặc serializer drift; không được bỏ validation
```
