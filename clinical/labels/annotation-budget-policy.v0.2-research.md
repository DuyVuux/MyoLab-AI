# Annotation Budget Policy v0.2 — Time-Based Research Planning

## 1. Principle

Không hard-code “100”, “150” hoặc “300” windows trước khi biết tốc độ review thật. Budget được tính từ **available review time** và một pilot calibration ngắn.

## 2. Pilot

Nếu có reviewer trong tương lai, bắt đầu với 10–15 items đa dạng để đo:

- median seconds/item;
- p75 seconds/item;
- discussion overhead;
- unresolved fraction;
- fatigue/error signals.

Con số 10–15 là pilot planning range, **không phải clinical sample-size claim**.

## 3. Capacity formula

```text
raw_capacity = floor(available_minutes * 60 / median_seconds_per_item)
usable_capacity = floor(raw_capacity * effective_review_fraction)
final_target = min(usable_capacity, eligible_pool_size)
```

`effective_review_fraction` phải được ghi rõ cho từng workshop/session và bao gồm nghỉ, thảo luận, tool overhead; DAY32 không freeze một default site value.

## 4. Allocation

Sau khi có capacity, acquisition policy mới phân phối item giữa representative-random, disagreement, novelty, high-risk false-allow, high-workflow-impact và artifact-vs-physiology ambiguity. Không dùng diagnosis quota nếu pool không có verified diagnosis metadata.

## 5. If no reviewer exists

DAY32 vẫn PASS. Budget state = `NOT_APPLICABLE_FOR_CURRENT_ENGINEERING_DAY`. Dry-run có thể dùng scripted non-clinical reviewer để test tool ergonomics nhưng output = `NON_CLINICAL_REVIEW`, không `EXPERT_ANNOTATION`.

## 6. Stop conditions

- Reviewer fatigue/rapid inconsistency → stop batch.
- Median time thay đổi lớn → recalculate capacity.
- Pool lacks required evidence → mark stratum coverage gap; do not fabricate samples.
