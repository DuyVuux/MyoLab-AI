# BÁO CÁO KIỂM TOÁN KHẢ NĂNG TRUY CẬP (ACCESSIBILITY - WCAG 2.2 AA)

---

## 1. TỔNG QUAN ĐÁNH GIÁ KHẢ NĂNG TRUY CẬP

Hệ thống UI MyoLab-AI được xây dựng với định hướng đạt tiêu chuẩn **WCAG 2.2 AA**, **IEC 62366-1** và **FDA Human Factors Guidance**.

---

## 2. KẾT QUẢ KIỂM TOÁN CHI TIẾT THEO TIÊU CHÍ WCAG 2.2 AA

| Tiêu chí WCAG 2.2 AA | Trạng thái | Minh chứng & Đánh giá trong Codebase | Lỗi / Cần cải thiện |
|---|---|---|---|
| **1.3.1 Info and Relationships** | **PASS** | Sử dụng đúng thẻ semantic HTML5 (`<header>`, `<main>`, `<nav>`, `<section>`, `<h1>`-`<h3>`, `<label>`). | Không |
| **1.4.3 Contrast (Minimum)** | **PASS** | Bảng màu định nghĩa trong `src/styles/tokens.css` với tỷ lệ tương phản văn bản > 4.5:1 (Background #0f172a / Card #1e293b / Text #f8fafc). | Không |
| **1.4.11 Non-text Contrast** | **PASS** | Đạt tỷ lệ tương phản 3:1 cho các viền UI control, icon trạng thái và focus ring (`var(--color-primary)` cyan/teal). | Không |
| **2.1.1 Keyboard** | **PASS** | Tất cả các form control, button, tab và dropdown đều có thể tương tác đầy đủ bằng phím Tab / Shift+Tab / Enter / Space. | Không |
| **2.4.3 Focus Order** | **PASS** | Thứ tự focus tuân thủ luồng đọc tự nhiên từ trên xuống dưới, từ trái sang phải. | Không |
| **2.4.7 Focus Visible** | **PASS** | Định nghĩa outline focus chuẩn trong `src/styles/global.css`: `*:focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px; }`. | Không |
| **3.2.2 On Input** | **PASS** | Thay đổi lựa chọn radio/select không tự động chuyển trang bất ngờ (không gây unexpected context change). | Non-issue |
| **3.3.1 Error Identification** | **PASS** | Thông báo lỗi form và validation summary hiển thị văn bản mô tả rõ ràng kèm icon minh họa. | Không |
| **4.1.2 Name, Role, Value** | **PASS** | Component `Button`, `Input`, `Alert`, `Badge` truyền aria-label và aria-describedby chính xác. | Thêm `aria-live="polite"` cho kết quả stream |

---

## 3. KHẢ NĂNG TƯƠNG TÁC BẰNG BÀN PHÍM VÀ BẢNG DỮ LIỆU THAY THẾ (TEXT ALTERNATIVES)

- **Biểu đồ sóng & Tiến trình (Charts & Visualizations):**
  - Component `SignalPreviewChart.tsx`, `FeatureTrendChart.tsx`, `LongitudinalTrendChart.tsx` render qua thẻ SVG có nhãn `aria-label` và cấu trúc điểm vector rõ ràng.
  - Cần bổ sung bảng số liệu dạng HTML Table ẩn/hiện làm giải pháp thay thế (Text Alternative) cho người dùng sử dụng trình đọc màn hình (Screen Reader) khi xem xu hướng longitudinal phức tạp.
