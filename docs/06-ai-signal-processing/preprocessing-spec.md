# Đặc tả tiền xử lý sEMG v0.1

**Trạng thái:** Mặc định kỹ thuật tạm thời cho MVP-0, chưa clinical validated.  
**Đầu vào:** `NormalizedSignal` + `QCResult` có `analysis_allowed=true`.  
**Đầu ra:** `PreprocessedSignal` band-pass, provenance đầy đủ và JSON summary không chứa raw array.

## 1. Mục tiêu

Tiền xử lý làm giảm thành phần ngoài dải quan tâm và chuẩn hóa dữ liệu để windowing/feature extraction có đầu vào nhất quán. Tiền xử lý không được dùng để biến tín hiệu kém chất lượng thành tín hiệu “đạt chuẩn”, và không được xóa warning từ Quality Gate.

## 2. Pipeline v0.1

```text
NormalizedSignal
  -> kiểm tra QC cho phép phân tích
  -> kiểm tra toàn bộ mẫu hữu hạn
  -> trừ trung bình từng kênh trên toàn bản ghi
  -> Butterworth band-pass 20–400 Hz, order=4, SOS, sosfiltfilt
  -> notch 50 Hz, Q=30 chỉ khi QC có POWERLINE_NOISE_HIGH
  -> giữ nguyên Fs, time axis, sample count, channel identity, uV
  -> đánh dấu edge guard 0,25 s ở hai đầu bản ghi
  -> tạo hash đầu ra và provenance
```

## 3. Hai đường tín hiệu phải phân biệt

### 3.1. Đường phân tích phổ

Dùng tín hiệu đã band-pass nhưng **không rectify** để tính PSD, MDF và MNF. Rectification làm thay đổi phổ, tạo thành phần DC/tần số thấp và do đó không phù hợp làm đầu vào trực tiếp cho fatigue spectral features.

### 3.2. Đường hiển thị biên độ

Rectification/envelope có thể được tạo sau này cho visualization. RMS và MAV không cần lưu một bản rectified riêng vì công thức đã chứa bình phương hoặc trị tuyệt đối.

## 4. Lựa chọn filter

- Butterworth vì đáp ứng passband phẳng, dễ giải thích và là baseline phổ biến.
- SOS để tránh bất ổn số của dạng hệ số đa thức bậc cao.
- `sosfiltfilt` chạy tiến-lùi nên phase tổng bằng gần 0 trong offline analysis.
- Do chạy hai chiều, đây không phải causal filter và không dùng nguyên trạng cho near-real-time.

## 5. Điều kiện Nyquist

Với `Fs`, Nyquist là `Fs/2`. Cấu hình yêu cầu:

```text
0 < low_cut < high_cut < 0,90 × Nyquist
```

Ví dụ `Fs=1000 Hz`: Nyquist 500 Hz, mức tối đa theo margin là 450 Hz; high-cut 400 Hz hợp lệ.

## 6. Notch có điều kiện

Notch 50 Hz chỉ chạy khi QC phát hiện `POWERLINE_NOISE_HIGH`. Không notch mặc định vì:

- notch không cần thiết có thể làm biến dạng nội dung quanh 50 Hz;
- mức nhiễu phụ thuộc site, thiết bị và setup;
- quyết định phải được audit bằng reason code.

Với `Q=30`:

```text
bandwidth xấp xỉ f0 / Q = 50 / 30 ≈ 1,67 Hz
```

## 7. Hành vi lỗi

| Điều kiện | Hành vi |
|---|---|
| QC không cho phép | Block, không chạy filter |
| Có NaN/Inf | Block; không nội suy im lặng |
| Cutoff vi phạm Nyquist margin | Config/runtime error |
| Bản ghi quá ngắn cho filtfilt | Block với reason code kỹ thuật |
| Notch không được trigger | Step được ghi `skipped` |
| Warning QC khác | Tiếp tục và giữ reason code trong provenance |

## 8. Invariant

- Số mẫu không đổi.
- Timestamp không đổi.
- Sampling rate không đổi.
- Channel ID/muscle/side/role không đổi.
- Đơn vị vẫn là `uV`.
- Raw arrays không nằm trong JSON summary.
- Kết quả lặp lại cho cùng input/config phải có cùng hash trong cùng môi trường dependency đã khóa.

## 9. Các nội dung cần external review

- Filter range phù hợp với Noraxon export và hardware filter thực tế.
- Notch frequency/Q tại Motion Lab.
- Edge guard tối thiểu cho protocol thật.
- Có cần resample khi tích hợp nhiều thiết bị.
- Causal filter và latency nếu phát triển near-real-time.
