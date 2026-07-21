# Hợp đồng Dữ liệu: Kết quả Trích xuất Đặc trưng Miền thời gian (Time-Domain Feature Result)

**Artifact:** `docs/05-data/time-domain-feature-result-contract.md`
**Phiên bản:** v0.1 (Day 8)

Tài liệu này định nghĩa cấu trúc, trạng thái và các ràng buộc dữ liệu cho kết quả của bước trích xuất đặc trưng miền thời gian (RMS/MAV). Hợp đồng này đảm bảo tính nhất quán, bảo mật và khả năng truy xuất nguồn gốc của dữ liệu trước khi chuyển sang các bước phân tích, tổng hợp tiếp theo.

## 1. Mô hình trạng thái (Status Model)

### 1.1. Trạng thái kết quả toàn cục (Result Status)

| Trạng thái | Ý nghĩa | Xử lý downstream |
|---|---|---|
| `completed` | Tất cả các cửa sổ hợp lệ đều được tính toán thành công. | Được phép xử lý tiếp |
| `completed_with_exclusions` | Có một số cửa sổ hợp lệ không thể tính toán hoặc bị loại trừ. | Được phép xử lý tiếp (có kèm cảnh báo) |
| `blocked` | Quá trình trích xuất bị chặn (ví dụ: lỗi phiên bản, không có dữ liệu đầu vào). | **Chặn** xử lý tiếp |

### 1.2. Trạng thái từng dòng (Row Status)

| Trạng thái | Ý nghĩa | Dữ liệu đặc trưng |
|---|---|---|
| `computed` | Tính toán thành công trên cửa sổ hợp lệ. | Có giá trị số thực cho RMS và MAV. |
| `not_computed` | Dòng không thể tính toán (cửa sổ gốc invalid hoặc lỗi toán học). | Các giá trị `rms` và `mav` là `null`. |

---

## 2. Ví dụ JSON

### 2.1. Dòng tính toán thành công (`computed` row JSON example)

```json
{
  "row_id": "feat_tim_SYNTH_D3_GOLDEN_001_VL_R_01_w000",
  "window_id": "win_SYNTH_D3_GOLDEN_001_VL_R_01_w000",
  "session_id": "SYNTH_D3_GOLDEN_001",
  "channel_id": "VL_R_01",
  "profile_id": "time_domain",
  "purpose": "rms_mav",
  "geometry": {
    "start_sample": 0,
    "end_sample": 500,
    "length_samples": 500
  },
  "status": "computed",
  "features": {
    "rms": 34.502,
    "mav": 28.215
  },
  "reason_codes": [],
  "provenance": {
    "feature_config_id": "features_semg_v0.1",
    "window_config_id": "windowing_v0.1",
    "preprocess_config_id": "preprocess_v0.1",
    "window_plan_hash": "e586acf98af66da40605b062a21fa42397bdb3d46c91f4426286362ca22cb8b5"
  }
}
```

### 2.2. Dòng không thể tính toán (`not_computed` row JSON example)

```json
{
  "row_id": "feat_tim_SYNTH_D3_GOLDEN_001_VL_R_01_w005",
  "window_id": "win_SYNTH_D3_GOLDEN_001_VL_R_01_w005",
  "session_id": "SYNTH_D3_GOLDEN_001",
  "channel_id": "VL_R_01",
  "profile_id": "time_domain",
  "purpose": "rms_mav",
  "geometry": {
    "start_sample": 1250,
    "end_sample": 1750,
    "length_samples": 500
  },
  "status": "not_computed",
  "features": {
    "rms": null,
    "mav": null
  },
  "reason_codes": [
    "FEATURE_COMPUTATION_FAILED",
    "UPSTREAM_WINDOW_MASKED"
  ],
  "provenance": {
    "feature_config_id": "features_semg_v0.1",
    "window_config_id": "windowing_v0.1",
    "preprocess_config_id": "preprocess_v0.1",
    "window_plan_hash": "e586acf98af66da40605b062a21fa42397bdb3d46c91f4426286362ca22cb8b5"
  }
}
```

---

## 3. Đơn vị (Units)

- **Đơn vị chuẩn (Canonical Unit):** `uV` (Microvolt).
- **Tính bảo toàn:** Feature extractor không thực hiện bất kỳ việc chuẩn hóa biên độ nào (không MVC, không baseline). Giá trị của RMS và MAV tính toán được trực tiếp phản ánh đơn vị `uV` gốc của tín hiệu, đồng thời tuân thủ các quy tắc không tự ý thay đổi scale (không rectifying, không tapering thêm).

---

## 4. Truy xuất nguồn gốc (Provenance)

Mọi đối tượng kết quả phải chứa dấu vết lịch sử xử lý một cách rõ ràng (Traceability):
- `feature_config_id`: Định danh cấu hình logic trích xuất đặc trưng hiện hành.
- `window_config_id`: Cấu hình cắt cửa sổ đã được sử dụng trước đó.
- `preprocess_config_id`: Cấu hình thuật toán tiền xử lý đã áp dụng lên dòng tín hiệu thô.
- `window_plan_hash`: Mã băm SHA-256 từ pipeline windowing để liên kết ngược một cách an toàn, chống giả mạo.

---

## 5. Mã định danh và mã băm xác định (Deterministic ID / Hash)

- **Deterministic Row ID:** Dựa vào thông tin phiên (session), kênh (channel), profile, mục đích, và chỉ số thứ tự cửa sổ. **Không dùng UUID ngẫu nhiên** ở mức dòng nhằm cho phép rerun test sinh ra ID giống hệt nhau.
- **Deterministic Result Hash:** Metadata toàn cục (của đối tượng file JSON) và toàn bộ các đối tượng mảng tính toán bên trong sẽ được mã hóa về định dạng JSON chuẩn (Canonical JSON) rồi băm bằng thuật toán SHA-256 để ghi nhận mã kiểm tra tính toàn vẹn (tương tự `plan_hash_sha256` của windowing).

---

## 6. Bảo vệ quyền riêng tư & Tối thiểu hóa dữ liệu (Privacy / Data Minimization)

- Dữ liệu thô (raw signal samples) hoàn toàn bị lược bỏ. Đầu ra này chỉ chứa các con số mang tính đặc trưng tổng hợp trên không gian mẫu của mỗi cửa sổ.
- Cấm lưu trữ các thông tin liên quan tới bệnh nhân thật (PHI), mã số y tế (MRN), hay tên người dùng.
- Định danh cho file (ID) và dòng (row ID) không mang ý nghĩa cá nhân hoá, mà dùng metadata kỹ thuật.

---

## 7. Khả năng tương thích phiên bản (Version Compatibility)

Extractor sẽ kiểm tra cứng ranh giới phiên bản và tiến hành **Block (Tạo reason code `FEATURE_PREPROCESS_CONFIG_MISMATCH` hoặc `FEATURE_WINDOWING_CONFIG_MISMATCH`)** nếu kết quả windowing đưa vào không khớp:
- Phiên bản trích xuất đặc trưng: yêu cầu là `features_semg_v0.1`.
- Cấu hình cửa sổ phải là `windowing_v0.1`.
- Cấu hình tiền xử lý phải là `preprocess_v0.1`.
Bất kỳ sự thiếu đồng bộ nào sẽ khiến Status Model lập tức chuyển qua `blocked`.

---

## 8. Các trường bị cấm (Forbidden Fields)

Theo quy định khóa phạm vi phát triển hiện tại, hệ thống không cho phép các trường thông tin sau tồn tại trong kết quả của module này:
1. `fatigue_status` hoặc `is_fatigued`.
2. `frs` (Fatigue Risk Score).
3. `ml_confidence`, `predictions`, hay các class học máy.
4. `spectral_features` (PSD, MDF, MNF – những yếu tố này thuộc về module khác).
5. Các chẩn đoán lâm sàng hay khuyến nghị y khoa.

Tất cả các con số hiện có mang giá trị purely technical data. Trạng thái chứng nhận lâm sàng của dữ liệu này là `not_validated`.
