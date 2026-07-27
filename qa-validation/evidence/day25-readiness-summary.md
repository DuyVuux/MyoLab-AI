# Tóm tắt bằng chứng Day 25

## Gate

```text
status                = CONDITIONAL_READY
implementationAllowed = true
trainingAllowed       = false
siteStatus            = NOT_VERIFIED
nativeJsonVerified    = false
mfcvVerified          = false
```

## Blockers

- Chưa kiểm actual de-identified Motion Lab export.
- Chưa khóa field-level export schema tại site.
- Chưa có site export vượt privacy screening.
- Native JSON export chưa được xác minh; không được claim.
- MFCV eligibility chưa được xác minh; module phải disabled.
- Chưa có selected model-ready dataset manifest đã được legal/governance phê duyệt.

## Hành động được phép

- Dựng dataset registry và adapter scaffolding.
- Kiểm thử canonical contract và subject-safe split.
- Gửi site evidence request package.
- Chuẩn bị model research blueprint Day 26 với resultStatus=not_run.

## Hành động bị cấm

- Train hoặc tune model.
- Freeze exact Noraxon parser schema.
- Gọi JSON là native MR3 output.
- Bật MFCV khi chưa đủ eligibility evidence.
- Dùng restricted data ngoài DUA/IRB.
- Claim clinical performance từ public healthy datasets.
