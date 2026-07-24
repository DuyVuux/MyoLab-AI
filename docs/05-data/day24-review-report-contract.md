# Contract Review và Report Day 24

```text
analysis_result (immutable)
  1 ── 1 review_case
review_case
  1 ── N review_event
review_case approved
  1 ── N report_package (draft/final versions)
feedback_event
  0 ── N adjudication_event
```

Mọi object phải giữ source/result hash và version metadata. Raw signal không được nhúng vào review/report JSON.
