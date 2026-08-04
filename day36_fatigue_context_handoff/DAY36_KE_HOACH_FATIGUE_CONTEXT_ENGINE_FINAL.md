# DAY 36 — FATIGUE-CONTEXT ARCHITECTURE

**Điều kiện vào ngày:** Day 35 confidence calibration và abstention đã hoàn tất.  
**Mục tiêu:** tạo context engine hỗ trợ diễn giải, supportability và confidence adjustment.  
**Cấm:** hard fatigue diagnosis, treatment recommendation, một-feature diagnosis.

## 1. Định vị

Day 36 không trả lời:

```text
Subject có mỏi cơ hay không?
```

Day 36 trả lời:

```text
Có bằng chứng bối cảnh nào có thể làm thay đổi độ tin cậy,
supportability hoặc cách diễn giải output Task A/Task C?
```

Architecture:

```text
rules-first
explainable
provenance-first
human review
abstention-aware
```

## 2. Inputs

### Signal evidence
- RMS/MAV trend;
- MDF/MNF trend;
- spectral entropy;
- repetition duration;
- disagreement/performance consistency;
- within-session drift.

### Protocol/context
- protocol ID/version;
- contraction type;
- active duration;
- target muscle;
- load/%MVC nếu có;
- repetition index;
- rest interval;
- session/day;
- electrode reapplication indicator.

### Safety/confidence
- Day 35 calibrated confidence;
- Day 35 abstention decision;
- quality gate status;
- unsupported gesture/protocol;
- missing metadata;
- MFCV eligibility;
- provenance hashes.

## 3. Output states

Không dùng `fatigued=true/false`.

```text
NO_CONTEXT_EVIDENCE
POSSIBLE_FATIGUE_CONTEXT
FATIGUE_CONTEXT_SUPPORTED
CONFLICTING_EVIDENCE
INSUFFICIENT_EVIDENCE
UNSUPPORTED_PROTOCOL
QUALITY_BLOCKED
```

`FATIGUE_CONTEXT_SUPPORTED` chỉ là multi-source context evidence, không phải diagnosis.

## 4. Evidence lanes

### E1 — Amplitude trend
RMS/MAV tăng hoặc đổi theo time-on-task. Không độc lập vì force/gain/placement ảnh hưởng.

### E2 — Spectral trend
MDF/MNF giảm có thể phù hợp fatigue context nhưng bị force, contraction mode, placement và artifact ảnh hưởng.

### E3 — Performance consistency
Calibrated confidence giảm, repetition disagreement tăng hoặc Task C performance giảm.

### E4 — Exposure/protocol
Duration, repetitions, rest interval, phase và load.

### E5 — Quality/supportability
QC fail block context interpretation. Missing load/protocol làm giảm supportability.

Mỗi lane xuất:

```text
status
direction
strength
evidence_count
reason_codes
provenance
```

## 5. Combination rules

| Spectral | Amplitude | Performance | Quality | State |
|---|---|---|---|---|
| supportive | supportive | supportive | pass | `FATIGUE_CONTEXT_SUPPORTED` |
| supportive | neutral | supportive | pass | `POSSIBLE_FATIGUE_CONTEXT` |
| supportive | contradictory | bất kỳ | pass | `CONFLICTING_EVIDENCE` |
| missing | missing | missing | pass | `INSUFFICIENT_EVIDENCE` |
| bất kỳ | bất kỳ | bất kỳ | fail | `QUALITY_BLOCKED` |

Không dùng một feature đơn lẻ để tạo `SUPPORTED`.

## 6. Confidence adjustment

```text
calibrated_confidence
→ context modifier
→ adjusted_support_confidence
```

Engineering defaults:

```yaml
quality_warning_penalty: 0.10
possible_context_penalty: 0.05
conflicting_evidence_penalty: 0.15
insufficient_metadata_penalty: 0.10
```

Phải lưu cả original và adjusted confidence.

Context engine chỉ giữ nguyên hoặc giảm confidence; không được tăng.

## 7. Abstention interaction

Thứ tự:

```text
Quality Gate
→ Day 35 confidence abstention
→ protocol supportability
→ context evidence
→ final routing
```

Routes:

```text
CONTINUE_WITH_CONTEXT
CONTINUE_WITH_WARNING
ABSTAIN_LOW_CONFIDENCE
ABSTAIN_QUALITY_FAIL
ABSTAIN_UNSUPPORTED_PROTOCOL
ABSTAIN_CONFLICTING_EVIDENCE
```

Mandatory wording:

> Quality fail không được biến thành “không phát hiện mỏi”.

## 8. Context contract

### Input event

```text
session_id
subject_id
protocol_id/version
repetition_id
time_index
quality_status
calibrated_confidence
abstention_decision
feature_trends
performance_trends
metadata_availability
mfcv_eligible
provenance hashes
```

### Output event

```text
context_state
supportability
evidence_lanes
original_confidence
adjusted_confidence
final_route
reason_codes
human_readable_summary
provenance
```

## 9. Các bước tuần tự

### Bước 0 — Day 35 handoff gate
**Stop:** calibrator/threshold fit trên validation, score contract fail hoặc policy chưa freeze.

### Bước 1 — Protocol support audit
Kiểm protocol ID/version, active phase, duration, force/load và target muscle.

### Bước 2 — Evidence contract
Không định nghĩa lại 14 features; chỉ dùng versioned outputs và trends.

### Bước 3 — Trend computation
Mỗi trend phải có:

```text
baseline segment
comparison segment
minimum repetitions
robust slope
coverage
reason codes
```

### Bước 4 — Lane evaluation
Mỗi lane tạo status, strength và provenance.

### Bước 5 — Deterministic combination
Dùng rule table đã version, không train hidden classifier.

### Bước 6 — Confidence adjustment
Chỉ giảm/giữ nguyên.

### Bước 7 — Final routing
Kết hợp QC, confidence abstention, protocol supportability và context.

### Bước 8 — Language guard
Chặn diagnosis/treatment language.

### Bước 9 — Scenario tests

```text
multi-lane supportive
single spectral lane
amplitude/spectral conflict
quality fail
low confidence
unsupported protocol
missing load metadata
MFCV ineligible nhưng basic sEMG hợp lệ
```

### Bước 10 — Day 37 handoff
Chỉ bắt đầu Task C khi Day 36 real handoff pass.

## 10. Outputs

```text
fatigue-context-policy.yaml
context-engine-contract.json
context-engine-scenarios.csv
context-engine-report.json
confidence-adjustment-policy.json
day37-handoff-gate.md
```

Không cần notebook. Implementation chính là package + tests.

## 11. Acceptance criteria

```text
[ ] Day35 handoff pass
[ ] không hard diagnosis
[ ] không treatment recommendation
[ ] multi-lane evidence
[ ] one-feature diagnosis bị cấm
[ ] quality fail block
[ ] lưu original/adjusted confidence
[ ] confidence không tăng
[ ] MFCV ineligible không block basic sEMG
[ ] provenance đầy đủ
[ ] deterministic rules
[ ] language guard pass
[ ] Day37 handoff contract tồn tại
```

## 12. Readiness

```text
GO_FOR_DAY37_TASK_C_QUANTITATIVE_CONTRACTS
GO_FOR_DAY37_WITH_CONTEXT_LIMITATIONS
BLOCKED_WITH_EVIDENCE
```
