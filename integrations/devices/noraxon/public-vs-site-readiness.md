# Noraxon Public Capability vs Site Readiness

## Quy tắc

```text
Vendor capability công khai
≠ capability đã được cài, licensed và cấu hình tại site.
```

## Kết luận Day 25

- Public documentation đủ để lập câu hỏi và adapter candidates.
- Chưa đủ để freeze field-level schema.
- CSV/C3D/MAT/native package chỉ được coi là candidate path cho tới khi có actual site artifact.
- JSON vẫn `NOT_VERIFIED`.
- Raw-per-channel site availability vẫn `NOT_VERIFIED`.
- MFCV vẫn `NOT_VERIFIED`.

## Gate chuyển sang site adapter implementation

```text
exact version
+ module/license
+ actual de-identified export
+ source hash
+ field dictionary
+ unit/time/channel mapping
+ privacy pass
```

## Adapter classification

| Class              | Verification                      | Status hiện tại       |
|--------------------|-----------------------------------|-----------------------|
| `generic`          | `PROJECT_VERIFIED`                | Sẵn sàng              |
| `vendor_candidate` | `OFFICIAL_PUBLIC_CAPABILITY_ONLY` | Có thể tạo provisional |
| `site_verified`    | `SITE_VERIFIED`                   | Chưa tồn tại          |

Chi tiết: `integrations/devices/noraxon/adapter-verification-policy.md`

## Scenario matrix

| Output nhận được           | Xử lý                                    |
|----------------------------|-------------------------------------------|
| CSV/ASCII raw              | Mapping profile + CSV adapter             |
| MATLAB `.mat`              | Inspect variables + MAT adapter           |
| C3D                        | C3D adapter + analog channels             |
| Native proprietary         | Re-export qua MR3                         |
| Processed report only      | ProcessedMetricsAdapter, no reprocessing   |
| PDF only                   | Archival only, không đủ cho training      |
| Không có usable export     | Site BLOCKED, public pipeline tiếp tục    |
| JSON do team tạo           | PROJECT_DERIVED, không gọi native Noraxon |

## Capability degradation

Khi thiếu field, pipeline giảm chức năng có kiểm soát thay vì crash:

| Capability             | Yêu cầu tối thiểu                                    |
|------------------------|-------------------------------------------------------|
| Raw signal analysis    | raw signal + sampling rate + unit                     |
| Gesture training       | raw signal + labels + channel mapping + trial structure |
| Longitudinal metrics   | compatible protocol + preprocessing + same subject    |
| MFCV                   | ordered geometry + IED + alignment + propagation      |

Chi tiết: `noraxon-output-uncertainty-resolution-addendum.md` §8

## Tham chiếu

- [Addendum](../day25-research/noraxon-output-uncertainty-resolution-addendum.md)
- [ADR-0009](../../03-architecture/adr/ADR-0009-isolate-unknown-vendor-output-behind-adapters.md)
- [Adapter Policy](./adapter-verification-policy.md)
- [Onboarding Runbook](./site-export-onboarding-runbook.md)
- [Mapping Profile Template](./mapping-profile.template.yaml)
- [External Dependencies](../../11-operations/external-dependency-register.md)
