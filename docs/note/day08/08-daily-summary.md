# Tổng kết Day 8

Day 8 đã triển khai thành công `features_semg_v0.1` tập trung trích xuất 2 đặc trưng miền thời gian là RMS và MAV.

- **Tests đã chạy:**
  - Analytical verification tests (RMS = A/sqrt(2) cho sine wave, unit check, `RMS >= MAV`).
  - Unit/Negative tests (Test invalid windows `not_computed`, Upstream block propagation, Config/Profile mismatches block, Không có raw samples).
  - Validation test của JSON Schemas (`feature-row`, `time-domain-feature-result`, `time-domain-feature-verification`).
- **Golden row counts:** 
  - `total_row_count`: 239
  - `computed_row_count`: 239
  - `not_computed_row_count`: 0
- **Result hash trên máy hiện tại:** `04145c778010bfe0946347ee56d083a84982f8e149aab0238474433345777546`
- **Limitations (Hạn chế):**
  - Chỉ tính được RMS/MAV theo từng time-domain window 500 ms.
  - Không có MVC hay baseline normalization.
  - Evidence hiện tại chỉ là synthetic/software verification, không phải clinical validation.
- **Blockers / Open questions:** 
  - Chưa có chuẩn xác nhận lâm sàng từ chuyên gia y tế cho việc sử dụng RMS/MAV trong chẩn đoán mỏi cơ.
- **External review required:** 
  - Cần review lâm sàng để đánh giá ý nghĩa các chỉ số này, cũng như wording để report cho KTV/bác sĩ. Cần quyết định về cross-session amplitude comparison cho các phiên bản tiếp theo.
- **Handoff Day 9:**
  - Day 9 sẽ kế thừa output của Day 8 và tập trung triển khai đặc trưng miền tần số (Frequency-domain features: PSD, MDF, MNF) mà Day 8 đã cố ý để lại.
