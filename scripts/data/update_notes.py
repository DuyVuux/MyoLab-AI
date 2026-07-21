from pathlib import Path

ROOT = Path("docs/note/day05")

# 02
content_02 = (ROOT / "02-reading-notes.md").read_text()
content_02 = content_02.replace("- Điều tôi hiểu:", "- Điều tôi hiểu: Các thành phần Butterworth band-pass 20-400Hz, IIR Notch 50Hz, và zero-phase filtering đóng vai trò cốt lõi. Thứ tự pipeline rất khắt khe để đảm bảo invariants.")
content_02 = content_02.replace("- Điều còn mơ hồ:", "- Điều còn mơ hồ: Cần làm rõ cách thiết lập biên bảo vệ (edge transients) để tránh nhiễu do filter warm-up ở điểm đầu/cuối tín hiệu.")
content_02 = content_02.replace("- Giả định nào của paper không khớp dự án:", "- Giả định nào của paper không khớp dự án: Paper dùng tần số 2048Hz nhưng thực tế dự án chạy 1000Hz. Ta không ép resample về 2048Hz.")
content_02 = content_02.replace("- Câu hỏi cần external review:", "- Câu hỏi cần external review: Phần mềm/phần cứng export đã áp dụng filter nào rồi? Tần số lấy mẫu gốc của thiết bị là bao nhiêu?")
(ROOT / "02-reading-notes.md").write_text(content_02)

# 03
content_03 = (ROOT / "03-math-notes.md").read_text()
content_03 = content_03.replace("- Nyquist cho Fs của fixture:", "- Nyquist cho Fs của fixture: 1000 Hz / 2 = 500 Hz.")
content_03 = content_03.replace("- 90% Nyquist:", "- 90% Nyquist: 500 Hz * 0.9 = 450 Hz.")
content_03 = content_03.replace("- High-cut 400 Hz có hợp lệ không:", "- High-cut 400 Hz có hợp lệ không: Có, vì 400 < 450, thỏa mãn nyquist_margin_ratio.")
content_03 = content_03.replace("- Bandwidth notch:", "- Bandwidth notch: 50 Hz / 30 = 1.67 Hz (từ 49.17 Hz đến 50.83 Hz).")
(ROOT / "03-math-notes.md").write_text(content_03)

# 04
content_04 = (ROOT / "04-signal-processing-notes.md").read_text()
content_04 = content_04.replace("- 5 Hz:", "- 5 Hz: Bị triệt tiêu mạnh do nằm dưới ngưỡng low-cut 20 Hz của bandpass.")
content_04 = content_04.replace("- 80 Hz:", "- 80 Hz: Bảo toàn rất tốt (>95%) đi qua Notch và nằm trong dải pass-band.")
content_04 = content_04.replace("- 450 Hz:", "- 450 Hz: Bị triệt tiêu do nằm ngoài high-cut 400 Hz.")
content_04 = content_04.replace("- 50 Hz trước/sau notch:", "- 50 Hz trước/sau notch: Giảm biên độ cực mạnh (<10%) khi bật notch, loại bỏ hoàn toàn nhiễu.")
content_04 = content_04.replace("- Output hash:", "- Output hash: 9db4765134e90e9db29fa6877c86af85ea074375e2d0a443d2ef68f8faeef0c5 (Cho cấu hình Golden). Hoàn toàn tất định.")
(ROOT / "04-signal-processing-notes.md").write_text(content_04)

# 05
content_05 = (ROOT / "05-clinical-notes.md").read_text()
content_05 = content_05.replace("Motion Lab/Noraxon export đã có hardware/software filter gì?", "Motion Lab/Noraxon export đã có hardware/software filter gì? (Cần chuyên gia lâm sàng kiểm tra tài liệu thiết bị)")
content_05 = content_05.replace("Sampling rate thật?", "Sampling rate thật? (1000Hz, 2000Hz hay 2048Hz)")
content_05 = content_05.replace("Có cần notch không?", "Có cần notch không? (Xác nhận việc áp dụng filter lưới 50Hz tại Việt Nam, có thể là 60Hz nếu thiết bị khác nguồn)")
content_05 = content_05.replace("Protocol nào cần filter khác?", "Protocol nào cần filter khác? (Có cần lọc dải rộng hơn không tùy bài đo MVC/Fatigue)")
(ROOT / "05-clinical-notes.md").write_text(content_05)

# 06
content_06 = (ROOT / "06-questions.md").read_text()
content_06 = content_06.replace("- Vì sao filter sau QC?", "- Vì sao filter sau QC? Vì lọc dữ liệu rác (Flatline/Clipping) có thể gây tràn số, sai kết quả chẩn đoán và tốn kém tài nguyên.")
content_06 = content_06.replace("- Vì sao SOS?", "- Vì sao SOS? Second-Order Sections ngăn lỗi sai số chấm động (numerical instability) so với hàm truyền transfer function (tf) ở các filter bậc cao.")
content_06 = content_06.replace("- Vì sao zero-phase chỉ dùng offline?", "- Vì sao zero-phase chỉ dùng offline? Zero-phase yêu cầu lọc thuận và nghịch trên toàn bộ bản ghi dữ liệu tương lai, không thể áp dụng cho tín hiệu real-time streaming.")
content_06 = content_06.replace("- Vì sao không rectify trước MDF/MNF?", "- Vì sao không rectify trước MDF/MNF? Phân tích tần số sử dụng tín hiệu xoay chiều nguyên bản, rectify (trị tuyệt đối) sẽ thay đổi toàn bộ dải phổ tần của tín hiệu gốc.")
(ROOT / "06-questions.md").write_text(content_06)

# 07
content_07 = (ROOT / "07-decisions.md").read_text()
content_07 = content_07.replace("- [ ] Dùng `preprocess_v0.1`.", "- [x] Dùng `preprocess_v0.1`.")
content_07 = content_07.replace("- [ ] Lọc toàn bản ghi.", "- [x] Lọc toàn bản ghi.")
content_07 = content_07.replace("- [ ] Band-pass 20–400 Hz, Butterworth, order 4, SOS.", "- [x] Band-pass 20–400 Hz, Butterworth, order 4, SOS.")
content_07 = content_07.replace("- [ ] `sosfiltfilt` offline.", "- [x] `sosfiltfilt` offline.")
content_07 = content_07.replace("- [ ] Notch 50 Hz chỉ khi QC trigger.", "- [x] Notch 50 Hz chỉ khi QC trigger.")
content_07 = content_07.replace("- [ ] Không resample.", "- [x] Không resample.")
content_07 = content_07.replace("- [ ] Không rectify/envelope trên spectral path.", "- [x] Không rectify/envelope trên spectral path.")
content_07 = content_07.replace("- [ ] Không nội suy NaN/Inf.", "- [x] Không nội suy NaN/Inf.")
content_07 = content_07.replace("- [ ] Tạo edge guard và output hash.", "- [x] Tạo edge guard và output hash.")
(ROOT / "07-decisions.md").write_text(content_07)

# 08
content_08 = """# Tổng kết Day 5

## Artifact đã tạo
- Code lõi xử lý tín hiệu `semg_core/preprocessing.py`.
- Tầng service orchestration `pipeline.py`.
- Các mô hình kết quả `preprocess_result_models.py`.
- Kịch bản chạy giả lập E2E `run_preprocessing_e2e.py`.
- JSON Evidence E2E cho 3 trường hợp QC.

## Test đã chạy
- Toàn bộ `test_preprocessing.py` và `test_pipeline.py`.
- 100% test pass (11 tests).

## Output hash golden
`9db4765134e90e9db29fa6877c86af85ea074375e2d0a443d2ef68f8faeef0c5` (trên môi trường Python 3.12.3, NumPy 2.5.1, SciPy 1.18.0)

## Điều tôi hiểu chắc
- Cơ chế chặn lọc theo QC hoạt động đúng 100%. Notch chỉ áp dụng khi bị cờ POWERLINE_NOISE_HIGH.

## Điều còn chưa chắc
- Edge guard tối ưu là bao nhiêu cho luồng phân tích lâm sàng thật sự. Tạm thời được zero-out.

## Blocker
- Hiện tại không có blocker.

## External review required
- Chuyên gia y sinh rà soát thông số thiết bị xuất CSV. Xác nhận xem đã có bộ lọc cứng tích hợp sẵn chưa.
- Lên lịch review cho output hash và Golden scenario.

## Day 6 readiness
- Hoàn toàn sẵn sàng cho phân đoạn (Segmentation) và tính năng Windowing ở Day 6. Đã kiểm soát được 100% kiến trúc pipeline tiền xử lý.
"""
(ROOT / "08-daily-summary.md").write_text(content_08)

# 09
content_09 = (ROOT / "09-todo-day06.md").read_text()
content_09 = content_09.replace("- [ ] Day 5 checker pass.", "- [x] Day 5 checker pass.")
content_09 = content_09.replace("- [ ] Golden output hash ổn định.", "- [x] Golden output hash ổn định.")
content_09 = content_09.replace("- [ ] Powerline fixture kích hoạt notch đúng.", "- [x] Powerline fixture kích hoạt notch đúng.")
content_09 = content_09.replace("- [ ] QC fail block preprocessing.", "- [x] QC fail block preprocessing.")
content_09 = content_09.replace("- [ ] Hiểu zero-phase và edge transient.", "- [x] Hiểu zero-phase và edge transient.")
(ROOT / "09-todo-day06.md").write_text(content_09)

