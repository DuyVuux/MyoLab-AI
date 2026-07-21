# Day 7: Learning Objectives

## 1. 3 điểm đã hiểu
- **Mục tiêu phân mảnh (Windowing):** Mục tiêu cốt lõi của Windowing trong xử lý tín hiệu sEMG là biến một chuỗi dữ liệu liên tục dài (ví dụ 60s) thành các khối tín hiệu tĩnh cục bộ (quasi-stationary) để tính toán đặc trưng biên độ và phổ.
- **Tính Deterministic của Geometry:** Cấu trúc hình học của cửa sổ (Window geometry verified on synthetic fixture) được đảm bảo tính tất định qua công thức toán học L, H, K mà không phụ thuộc vào giá trị của tín hiệu.
- **Tách biệt Profile:** Sự cần thiết phải phân ly Time Domain (500ms) và Frequency Domain (1000ms), vì mỗi miền yêu cầu độ phân giải thời gian và tần số khác nhau.

## 2. 1 điểm chưa chắc
- Việc cố định trước hai kích thước cửa sổ này (500ms và 1000ms) cho mọi cơ (muscle) và protocol có thể làm mất đi độ nhạy cảm đối với các sự kiện cục bộ nhỏ (micro-events) trong một bài kiểm tra mỏi cơ cường độ cao.

## 3. Giới hạn / Assumption
- **Giới hạn:** Giai đoạn MVP-0 hiện chỉ hỗ trợ cắt cửa sổ trên một pha duy nhất là `active_contraction`. Không hỗ trợ phân mảnh trên giai đoạn nghỉ (baseline/recovery).

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Cần ý kiến từ kiến trúc sư hệ thống về việc MVP-1 có nên mở rộng Windowing cho nhiều pha (multi-phase windowing) hay không.
