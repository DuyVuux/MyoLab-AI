# Free-First Research Stack cho Day 25

## Nguyên tắc

Một dataset không cần bao phủ đủ cả ba task. Stack được thiết kế theo vai trò.

## Stack tối thiểu

| Workstream | Dataset | Vai trò | Giới hạn |
|---|---|---|---|
| Task A | Mendeley 4-channel | Sparse forearm adapter và label mapping gần UC1 | Không có cross-day được xác minh |
| Task A | GRABMyo | Multi-day robustness và subject/session hierarchy | Healthy-only; label count còn conflict 16/17 |
| Task A/C | Hyser PR | HD-sEMG, WFDB, spatial/force ecosystem | Rất khác Ultium sparse setup |
| Task B | Cerqueira fatigue | Fatigue-context corpus chính free/open | Self-perceived labels, healthy-only |
| Task C | Lucchetti clinical | Post-stroke metric provenance, kinematics, bilateral context | Cohort nhỏ; không phải gesture classifier corpus |
| Task C | Mendeley post-stroke reaching | Rehab/reference metrics | Canonical record cần khóa trước reuse |

## Stack mở rộng có điều kiện

- GRABMyoFlow: dynamic transitions, sau khi xác minh license/version.
- putEMG: research-only vì CC BY-NC.
- Reach&Grasp: mẫu data-contract/sidecar, không mặc định là training corpus.

## Dataset không được đưa vào core stack ngay

- PhysioMio và restricted PhysioNet: cần DUA/IRB.
- Ninapro/GREAT/CapgMyo/CSL/mmGest/UCD-MyoVerse: legal hoặc access còn hở.
- Lower-limb walking: lệch scope upper-limb UC1/UC2.

## Attribution và immutable manifest

Trước khi tải bất kỳ dataset nào ở Day 27:

```text
canonical URL/DOI
+ version
+ license file/hash
+ retrieval date
+ archive hash
+ file inventory
+ subject/session fields
+ label dictionary
+ permitted use
```

phải được ghi vào immutable manifest.
