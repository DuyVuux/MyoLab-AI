# Báo cáo kiểm chứng phân tích — `preprocess_v0.1`

## 1. Phạm vi

- MVP-0 ngoại tuyến.
- Fixture synthetic có tính xác định.
- Sampling rate: 1000.0 Hz.
- Band-pass/conditional notch theo config `preprocess_v0.1`.

## 2. Khả năng truy xuất

- Config path: `services/preprocessing-service/configs/preprocess_v0.1.yaml`
- Config SHA-256: `844e19bb7da7161deadd51c3aeece0ddebf314e0c57b112f96bbf269454e56fa`
- Verification profile: `preprocess_verification_v0.1`
- Verification report schema: `preprocessing-verification-report.v0.1`

## 3. Kết quả

| Hạng mục | Kết quả |
|---|---|
| Đáp ứng lý thuyết | PASS |
| Thực nghiệm đa tần | PASS |
| Pha bằng không | PASS |
| Hành vi tại biên | PASS |
| Tính xác định trong cùng môi trường | PASS |
| Overall analytical verification | **PASSED** |

## 4. Quyết định

- Trạng thái kiểm chứng phân tích preprocessing: **PASSED**.
- Trạng thái xác nhận lâm sàng: **CHƯA XÁC NHẬN**.
- Khả năng tương thích thời gian thực: **KHÔNG**.
- Mức sẵn sàng cho windowing Day 7: **SẴN SÀNG**.

## 5. Giới hạn

- Profile này chỉ là engineering acceptance cho MVP-0 offline.
- Chưa xác nhận trên Noraxon export thật hoặc dữ liệu lâm sàng.
- Chỉ kiểm chứng Fs=1000 Hz trong Day 6.
- Exact output hash được yêu cầu trong cùng environment; qua environment khác cần numerical tolerance.
- Không kiểm chứng electrode placement, crosstalk, protocol adherence hoặc clinical interpretation.
- Không kiểm chứng MFCV/CV preprocessing.

## 6. Tuyên bố an toàn

Báo cáo này chỉ xác nhận implementation phù hợp specification trên fixture kiểm soát. Nó không xác nhận giá trị lâm sàng, không xác nhận electrode placement, không xác nhận dữ liệu Noraxon thật và không tạo kết luận về mỏi cơ.
