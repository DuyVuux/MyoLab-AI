# Weak-Supervision Aggregation Contract v0.1

## Purpose
DAY30 chuẩn hóa cách QC aggregation **tiêu thụ** weak-label candidates mà không biến chúng thành clinical truth.

## Three-layer isolation
1. **Raw detector evidence**: measurement/evidence fact. Không phải PASS/WARNING/FAIL policy.
2. **Provisional weak label**: `PASS_CANDIDATE`, `WARNING_CANDIDATE`, `FAIL_CANDIDATE`, `ABSTAIN`, `UNKNOWN`. `ground_truth_claim=false`, `expert_label_claim=false`.
3. **QC policy decision**: deterministic `PASS`, `WARNING`, `FAIL` hoặc `null` nếu chưa đủ evidence.

Không layer nào được silently overwrite layer trước. Output policy phải giữ `source_refs` để truy ngược evidence.

## Precedence
- DAY29 hard integrity blocking evidence thắng mọi weak-label vote và mọi ratio.
- Missing required LF hoặc required LF `ABSTAIN/UNKNOWN` → `INSUFFICIENT_EVIDENCE`, `signal_quality=null`.
- `MISSING_DROPOUT`/`FLATLINE_DETECTED` chỉ trở thành window FAIL theo **versioned policy**, không phải ground truth.
- Clipping/power-line/motion/poor-contact suspected mặc định là review evidence; không majority-vote thành FAIL.
- `PHYSIOLOGICAL_VARIATION_POSSIBLE` không làm tăng bad-window count.

## No label model
DAY30 không train label model, không fit weights, không tạo probability và không gọi weighted voting là clinical truth.

## Threshold maturity
`0.80` usable-window ratio và `max_bad_channels=1` chỉ tồn tại trong profile `synthetic-engineering-only` để test code path. Site profile giữ `NOT_VERIFIED/null` cho tới DAY35 evidence-gated threshold configuration.
