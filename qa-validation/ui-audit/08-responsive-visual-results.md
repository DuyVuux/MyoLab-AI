# BÁO CÁO GIÁM SÁT GIAO DIỆN VÀ TƯƠNG THÍCH MÀN HÌNH (RESPONSIVE & VISUAL SYSTEM)

---

## 1. KẾT QUẢ KIỂM TOÁN THEO VIEWPORT

| Khung hình (Viewport) | Mức độ phù hợp | Đánh giá bố cục | Vấn đề ghi nhận |
|---|---|---|---|
| **360 × 800 (Mobile Portrait)** | **PASS** | AppShell tự động chuyển sidebar thành Mobile Drawer. Các nút bấm sticky vừa vặn, không bị tràn màn hình. | Bảng dữ liệu Channel Mapper chuyển sang chế độ cuộn ngang (horizontal scroll) mượt mà. |
| **768 × 1024 (Tablet Portrait)** | **PASS** | Bố cục dạng 2 cột co giãn linh hoạt. Các thẻ thông số (Metric Cards) tự động xếp hàng 2x2. | Không |
| **1024 × 768 (Tablet Landscape)** | **PASS** | Bố cục hoàn chỉnh với Sidebar cố định bên trái, khu vực nội dung chính chiếm không gian còn lại. | Không |
| **1366 × 768 (Laptop Standard)** | **PASS** | Hiển thị tối ưu cho quy trình làm việc lâm sàng chuyên nghiệp. | Không |
| **1440 × 900 (Desktop Large)** | **PASS** | Căn giữa khung nhìn tối đa 1400px, giữ khoảng đệm lề rộng rãi. | Không |

---

## 2. HỆ THỐNG THIẾT KẾ TRỰC QUAN (VISUAL SYSTEM & DESIGN TOKENS)

- **Hệ thống màu sắc (Color Tokens):**
  - Màu chủ đạo: Dark Mode Slate (`#0f172a`, `#1e293b`), Cyan/Teal accent (`#06b6d4`, `#0d9488`).
  - Màu ngữ nghĩa y tế (Semantic Colors): Green (Pass/Normal), Amber/Yellow (Warning), Red/Coral (Fail/Danger), Blue/Indigo (Info).
  - Không sử dụng màu đơn lẻ để thể hiện trạng thái (luôn kết hợp giữa Màu sắc + Icon Lucide + Văn bản tiếng Việt).
- **Phông chữ & Spacing Rhythm:**
  - Font gia đình: System Sans-Serif (`Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`).
  - Spacing: Quy chuẩn theo bội số 8px (`8px`, `16px`, `24px`, `32px`).
- **Icons & Visual Language:**
  - Sử dụng thống nhất bộ icon `lucide-react`. Không sử dụng emoji rải rác ngoài ý đồ thiết kế hệ thống.
