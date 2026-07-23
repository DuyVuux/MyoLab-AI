# Contract Session Intake v0.1

## Resource

```text
SessionRecord
SignalImportRecord
ChannelMappingSet
PreflightSummary
CalibrationRecord
DetailedQualityResult
AnalysisHandoff
```

## Privacy boundary

Payload chỉ dùng `subject_ref` ẩn danh và hash/provenance. Không chứa tên, MRN, email, điện thoại hoặc raw sample array.

## State semantics

- `qc_ready` chỉ nghĩa intake đã đủ để chạy Quality Gate.
- `quality.pass` mới cho phép analysis trực tiếp.
- `quality.warning` cần acknowledgement theo role.
- `quality.fail` tạo `AnalysisHandoff.status=abstained`.
