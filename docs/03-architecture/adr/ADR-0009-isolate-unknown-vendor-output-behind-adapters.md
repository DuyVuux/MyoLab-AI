# ADR-0009: Isolate Unknown Vendor Output Behind Adapters

- **Status:** Accepted
- **Date:** 2026-07-27
- **Deciders:** Project Lead
- **Context:** Day 25 Data Readiness — Noraxon Output Uncertainty

## Context

Noraxon Motion Lab tại site chưa cung cấp actual export. Public documentation
xác nhận vendor có khả năng export CSV/ASCII/MATLAB/C3D, nhưng không chứng minh
exact field-level schema, installed modules, hay native JSON availability tại site.

Các báo cáo deep research (Day 25) xác nhận:

- `nativeJsonExportVerified = false`
- `mfcvEligibilityVerified = false`
- Exact column names, units, sampling rate tại site chưa verified

## Decision

1. Tất cả source-specific uncertainty được **cô lập trong adapter và mapping profile**.

2. Downstream QC, preprocessing, features, inference và report **chỉ phụ thuộc
   canonical contract** — không phụ thuộc trực tiếp file format của bất kỳ vendor nào.

3. **Không xây production integration** dựa trên schema Noraxon suy đoán.

4. Khi actual site export xuất hiện, bổ sung `SiteVerifiedAdapter` thay vì
   sửa toàn pipeline.

5. Pipeline flow:

   ```text
   Source file → Adapter → NormalizedSignal → QC → Preprocessing → Features → Model
   ```

## Consequences

### Positive

- Public dataset engineering, DSP development, baseline model research tiếp tục
  không bị chặn bởi external dependency
- Khi file thật đến, chỉ cần implement adapter mới — không rewrite pipeline
- Vendor lock-in được giảm thiểu — canonical contract là abstraction layer
- Capability degradation có kiểm soát: thiếu field → tắt capability, không crash

### Negative

- Cần maintain adapter registry và mapping profiles
- Initial integration khi file thật đến cần effort (Runbook 8 bước)
- Candidate adapters có thể accumulate nếu không prune

### Neutral

- Training permission tách thành 3 cấp (public / local / clinical) thay vì 1 cờ
- MFCV luôn optional capability, không block sEMG core

## References

- `docs/05-data/day25-research/noraxon-output-uncertainty-resolution-addendum.md`
- `integrations/devices/noraxon/adapter-verification-policy.md`
- `integrations/devices/noraxon/site-export-onboarding-runbook.md`
- `docs/05-data/day25-research/canonical-research-dataset-contract.md`
