# Segmentation and Windowing Specification v0.1

## 1. Input Context
**Input là gì?**
- Dữ liệu sEMG đã được tiền xử lý (preprocessed signal), có trạng thái hợp lệ (`require_preprocessing_downstream_allowed: true`).
- Bắt buộc phải khớp với `preprocess_v0.1` (`required_preprocess_config_id: preprocess_v0.1`).
- Đầu vào phải bao gồm đối tượng protocol tham chiếu đúng phiên bản (`require_protocol_object: true`, `require_protocol_ref_match: true`).
- Trục thời gian đồng nhất (uniform time axis).
- Đơn vị chuẩn: `uV`.
- **Lưu ý:** Không truyền mảng raw samples trực tiếp trong chuỗi JSON (`raw_arrays_in_json: false`).

## 2. Phase Boundary
**Phase được lấy từ đâu?**
- Phân đoạn (Segmentation) sẽ lấy tham chiếu từ `protocol.analysis.active_phase_id`.
- ID pha kỳ vọng trong phiên bản này: `active_contraction`.
- **Quy ước biên (Boundary Convention):** Nửa mở `[start, end)` (`half_open`).
- **Thuật toán ánh xạ:** Sử dụng `numpy.searchsorted(side='left')` để cắt mảng mẫu theo timestamp của protocol.

## 3. Profiles
**Hai profile là gì?**
Cấu trúc Windowing sẽ tạo ra 2 plan song song (Profiles):
1. **Time Domain (Miền Thời Gian):**
   - **Mục đích:** Tính toán các đặc trưng biên độ như RMS, MAV.
   - **Độ dài (Duration):** `500 ms` (tham chiếu từ `protocol.time_domain_window_ms`).
   - **Độ chồng chéo (Overlap):** `50%` (0.50).
2. **Frequency Domain (Miền Tần Số):**
   - **Mục đích:** Tính toán các đặc trưng phổ như PSD, MDF, MNF.
   - **Độ dài (Duration):** `1000 ms` (tham chiếu từ `protocol.frequency_domain_window_ms`).
   - **Độ chồng chéo (Overlap):** `50%` (0.50).

*Quy tắc:* Khung thời gian này được quy định bởi Technical Default MVP-0, không được dùng để thay thế chẩn đoán y tế. Bắt buộc validate alignment giữa Config và Protocol.

## 4. Công thức tính L, H, K
**L/H/K tính thế nào?**
Do `sample_rounding_policy: exact_integer_required` và `allow_partial_final_window: false`, quá trình tính toán trên mảng (array) với tần số lấy mẫu $F_s$ (Hz) sẽ tuân theo:
- **L (Window Length - số mẫu mỗi cửa sổ):** 
  $L = \text{duration\_ms} \times \frac{F_s}{1000}$
- **H (Hop Length - bước nhảy):** 
  $H = L \times (1 - \text{overlap\_fraction})$
- **K (Số lượng cửa sổ - Number of Windows):**
  Tổng số mẫu trong pha là $N$.
  $K = \lfloor \frac{N - L}{H} \rfloor + 1$ (Nếu $N < L$, $K = 0$).

## 5. Xử lý Invalid Window
**Invalid window được xử lý thế nào?**
- Đánh giá trên từng channel riêng biệt (`evaluate_per_channel: true`).
- Bất kỳ cửa sổ nào dính mẫu `nonfinite` (NaN, Inf) hoặc nằm trong khoảng bị đánh dấu là lỗi từ bước trước (`invalid_mask`) sẽ bị loại bỏ nguyên cửa sổ (`invalidate_window`).
- Mức độ chịu lỗi: `minimum_valid_sample_ratio: 1.0` (Không chấp nhận cửa sổ chứa bất kỳ lỗi nào, phải sạch 100%).
- **TUYỆT ĐỐI KHÔNG:** Nội suy hoặc điền 0 một cách im lặng. Dữ liệu lỗi thì cửa sổ đó bị loại.

## 6. Blocking Rule
**Khi nào block?**
- Nếu kiểm tra Protocol Alignment phát hiện sai lệch thông số giữa Protocol và Config $\rightarrow$ **Block** ngay với mã `WINDOWING_PROTOCOL_CONFIG_MISMATCH`.
- Nếu sau khi lọc Invalid Window, một trong các Profile (Time hoặc Frequency) **không còn bất kỳ cửa sổ nào hợp lệ** $\rightarrow$ **Block** (`block_if_no_valid_windows_in_profile: true`). (Vì hệ thống `require_all_profiles_for_downstream: true`).

## 7. Taper (Window Function)
**Taper ở đâu?**
- Ở giai đoạn Windowing: **KHÔNG ÁP DỤNG TAPER** (`apply_taper_during_windowing: false`).
- Dữ liệu trả về cho Time Domain là tín hiệu bandpassed thuần (untapered).
- Taper (Cửa sổ Hann - `hann`) chỉ được áp dụng độc lập ở giai đoạn trích xuất đặc trưng phổ (`spectral_taper_application_stage: frequency_feature_extraction`).

## 8. Provenance
**Version/provenance nào phải lưu?**
Cần lưu vết chéo để đảm bảo tính toàn vẹn (longitudinal validity):
- Protocol version (`protocol.version`).
- Preprocessing version.
- Windowing config (`windowing_v0.1`).
- Feature version (kế thừa chuẩn bị).
- Hash của Output Plan (`sha256_canonical_json`).
