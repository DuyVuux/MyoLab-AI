# Day 02 — Signal Processing Notes

## Input contract
MVP-0 ưu tiên:
- CSV chứa `timestamp` và các channel sEMG.
- JSON sidecar chứa metadata.
- Unit phải khai báo rõ: `uV`, `mV` hoặc `V`.
- Không suy đoán muscle/side/channel từ tên file.

## Thứ tự xử lý

```text
Import
→ Metadata validation
→ Structural validation
→ Signal Quality Gate
→ Preprocessing
→ Windowing
→ Feature extraction
```

## Kiểm tra trước preprocessing
- File parse được.
- Timestamp tăng đơn điệu.
- Không có duplicate timestamp nghiêm trọng.
- Sampling rate khai báo khớp sampling rate ước lượng.
- Đủ duration theo protocol.
- Channel bắt buộc tồn tại.
- Missing/dropout trong giới hạn.

## QC status
- pass: được phép phân tích.
- warning: được phép tiếp tục nhưng phải gắn cờ.
- fail: block feature extraction và inference.

## MFCV eligibility
Chỉ eligible khi có:

- nhiều channel dọc theo sợi cơ;
- khoảng cách điện cực biết trước;
- channel order rõ;
- sampling rate phù hợp;
- chất lượng channel lân cận đạt yêu cầu
