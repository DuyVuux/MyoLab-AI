# QC Adjudication Policy v0.2 — Research Continuation

## Purpose

Policy này định nghĩa điều kiện tối thiểu để một set annotation có thể được gọi `ADJUDICATED_REFERENCE`. DAY32 không tạo adjudicated reference; nó chỉ đóng contract để tương lai không gắn nhãn sai evidence tier.

## Rules

1. `EXPERT_ANNOTATION` là một qualified human opinion, không phải gold standard.
2. `ADJUDICATED_REFERENCE` cần ít nhất **hai independent expert annotation refs** và một explicit adjudication action.
3. Reviewer/adjudicator phải thuộc `CLINICAL_EXPERT` hoặc `BIOMEDICAL_SIGNAL_EXPERT` theo governance của research project. `NON_CLINICAL_REVIEWER` không được tạo expert tier.
4. Machine weak labels không được tính như một reviewer để đạt số lượng hai.
5. Disagreement không được giải quyết bằng majority vote mặc định. Adjudicator phải lưu rationale.
6. Nếu evidence vẫn ambiguous, final adjudication có thể là `UNRESOLVED`/`INSUFFICIENT_EVIDENCE`; không ép consensus.
7. `reference_scope=RESEARCH_ONLY` là default. `CLINICAL_GOVERNED` chỉ được dùng nếu một governance process độc lập, ngoài DAY32, thực sự tồn tại.
8. Một single expert + machine label **không phải** multi-expert adjudication.
9. Synthetic known truth không thay thế human adjudication và human adjudication không thay đổi truth-by-construction của synthetic fixture.

## Evidence preservation

Adjudication record phải giữ refs đến tất cả expert annotations, WindowIdentity, source evidence, rubric/config version và timestamp/event provenance. Không overwrite original expert annotation.

## Current project state

- expert annotations available: NOT_VERIFIED / not required for DAY32;
- clinician validation: NOT_PERFORMED;
- adjudicated reference set: NOT_AVAILABLE;
- policy status: ENGINEERING_READY.
