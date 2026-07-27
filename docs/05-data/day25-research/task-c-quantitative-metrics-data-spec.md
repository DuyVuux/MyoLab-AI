# Task C — Data Specification cho UC2 Quantitative Assessment

## Framing

Task C là metric pipeline có provenance, chưa phải một classifier tổng hợp.

## Metric families

```text
gesture repertoire
repeatability
symmetry
co-contraction
reference similarity
fatigue/endurance
```

## Status bắt buộc cho từng metric

```text
computed
experimental
not_available
blocked
```

Không dùng `0` thay cho dữ liệu thiếu.

## Required metadata

- subject/session IDs;
- affected/reference side;
- target muscle/channel map;
- protocol ID/version;
- gesture vocabulary;
- unit/sampling rate;
- preprocessing/feature version;
- QC status;
- reference session/source;
- formula version.

## Public-data role

- Lucchetti/Mendeley post-stroke: clinical metric provenance.
- Hyser: force/MVC/spatial support.
- GRABMyo: repeatability across days.
- PhysioMio: restricted longitudinal clinical reference.

## Longitudinal compatibility

Metric trend chỉ được tính khi các session tương thích về:

```text
subject
side
muscles
protocol
gesture vocabulary
unit
channel map
preprocessing/feature version
QC
```

Nếu không:

```text
status = blocked
reason = longitudinal_incompatible
```
