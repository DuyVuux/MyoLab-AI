# Label và Hierarchy Audit

## Three-layer label contract

```text
source_label
canonical_label
analysis_eligibility
```

## Core view

| Source | Canonical | Eligibility |
|---|---|---|
| Rest | rest | CORE_TASK_A |
| Grip | hand_close | CORE_TASK_A |
| Flexion | wrist_flexion | CORE_TASK_A |
| Extension | wrist_extension | CORE_TASK_A |
| Six remaining gestures | unknown | UNKNOWN_GESTURE_AUDIT |

`hand_open` = `UNSUPPORTED_BY_THIS_DATASET`.

## Hierarchy contract

```text
subject → session/day if observed → repetition → source file → samples
```

Windowing is not part of Day 28 structural EDA and must occur after split.
