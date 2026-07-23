# BÁO CÁO HIỆU NĂNG VÀ ĐỘ TIN CẬY HỆ THỐNG (PERFORMANCE & RELIABILITY)

---

## 1. KẾT QUẢ BUILD PRODUCTION VÀ DUNG LƯỢNG BẢN BẢN GÓI (CHUNK SIZES)

Build Production bằng `npx next build` tạo ra tổng cộng **22 trang tĩnh và động** với thông số bundle JS như sau:

- **First Load JS Shared by All Routes:** `87.5 kB`
  - `chunks/2749-*.js`: `31.7 kB`
  - `chunks/5b8f0dd8-*.js`: `53.7 kB`
  - Shared chunks khác: `2.13 kB`
- **Kích thước các Route chính (Page Size / First Load JS):**
  - `/dashboard`: `5.81 kB` / `102 kB`
  - `/sessions`: `4.26 kB` / `101 kB`
  - `/sessions/[sessionId]/context`: `8.68 kB` / `100 kB`
  - `/sessions/[sessionId]/calibration`: `7.2 kB` / `98.7 kB`
  - `/sessions/[sessionId]/quality`: `5.17 kB` / `101 kB`
  - `/sessions/[sessionId]/analysis`: `5.32 kB` / `96.8 kB`
  - `/sessions/[sessionId]/review`: `4.13 kB` / `95.6 kB`
  - `/sessions/[sessionId]/report`: `3.62 kB` / `95.1 kB`
  - `/uc1/intro`: `6.2 kB` / `103 kB`
  - `/uc2/intro`: `6.17 kB` / `103 kB`

---

## 2. ĐÁNH GIÁ RELIABILITY & MEMORY MANAGEMENT

- **Tải chậm trang (Lazy Loading):** Next.js App Router tự động phân đoạn code theo route (Code splitting), giúp tải nhanh dưới 100ms trên mạng local/broadband.
- **Xử lý chuỗi dữ liệu lớn (Signal Waveforms):** Các biểu đồ sóng dùng mẫu thu gọn (downsampling visualization) trong SVG để tránh đơ/giật giao diện khi xem các phiên đo dài.
- **Rò rỉ bộ nhớ (Memory Leak Prevention):** Dữ liệu mẫu tín hiệu thô được giải phóng khỏi bộ nhớ RAM của trình duyệt ngay sau khi hiển thị preview; không lưu bản tin thô vào `sessionStorage` hay `localStorage`.
