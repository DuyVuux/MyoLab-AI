# Day 02 — Daily Summary

## Đã hoàn thành
- Xác định protocol v0.1 và protocol schema.
- Chốt Generic CSV + JSON sidecar manifest.
- Viết signal import và signal validation contract.
- Chốt QC status, reason code và abstention behavior.
- Tách MFCV eligibility khỏi basic sEMG validity.
- Tạo validator cho protocol và signal file.
- Tạo expected-negative test cho duration không đủ.

## Kết quả kỹ thuật

```text
Readable file
≠ Valid signal
≠ Eligible analysis
≠ Eligible MFCV
```

## Chưa xác nhận
- Format export Noraxon thực tế.
- Sampling rate/site configuration.
- Electrode geometry cho MFCV.
- Protocol được bác sĩ/KTV chấp thuận.
- QC thresholds trên dữ liệu thật.

## Trạng thái
- Engineering foundation: ready for Day 3.
- Clinical approval: pending external review.