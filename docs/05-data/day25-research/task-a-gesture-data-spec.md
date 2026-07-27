# Task A — Data Specification cho UC1 Gesture Recognition

## Intended engineering task

Phân loại một cửa sổ sEMG đa kênh thành một trong năm trạng thái kỹ thuật:

```text
rest
hand_open
hand_close
wrist_flexion
wrist_extension
```

## Input contract

- samples không nằm trong manifest;
- `subject_id`, `session_id`, `trial_id`, `repetition_id`;
- exact window segment reference;
- channel order và electrode layout version;
- sampling rate và unit;
- calibration context;
- target cue và label provenance;
- activity-gate status;
- QC result.

## Label states bổ sung

```text
unknown
ambiguous
artifact
not_attempted
```

Không map `unknown` hoặc `artifact` thành `rest`.

## Public-data role

- Mendeley 4-channel: sparse adapter và label mapper.
- GRABMyo: cross-day robustness.
- Hyser: HD/spatial research.

## Grouping/split

Primary group:

```text
subject
```

Cross-session experiment:

```text
session/day held out inside or across subject according to declared protocol
```

Không random split windows.

## Prohibited claims

- Không claim hiệu năng stroke từ healthy datasets.
- Không claim personalized performance nếu không có calibration data.
- Không gọi classifier score là clinical probability.
