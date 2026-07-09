Dưới đây là file Skill được thiết kế theo đúng format chuẩn quốc tế mà bạn yêu cầu, áp dụng tư duy của "Token Budget Advisor" vào việc quản lý độ sâu khi phân tích mã nguồn với **Understand-Anything**.

Tôi đặt tên skill này là `codebase-depth-selector` để giúp AI của bạn không bao giờ "nói quá nhiều" hoặc "nói quá nông" khi bạn đang cần tập trung vào vibe coding.

```markdown
---
name: codebase-depth-selector
description: >-
  Cung cấp cho người dùng lựa chọn về độ sâu của phân tích mã nguồn trước khi thực hiện. 
  Sử dụng skill này khi người dùng muốn kiểm soát mức độ chi tiết của giải thích kiến trúc hoặc luồng logic.
  TRIGGER khi: "phân tích sâu", "tóm tắt thôi", "chi tiết kiến trúc", "cấu trúc tổng quát", 
  "deep dive", "high-level summary", "drill down", "low-level details", "explain briefly", 
  "full architectural breakdown", "soi kỹ cho tôi", "nói ngắn gọn", hoặc các biến thể yêu cầu kiểm soát độ chi tiết.
  DO NOT TRIGGER khi: người dùng đã chọn một mức độ trước đó trong phiên làm việc, 
  câu hỏi chỉ mang tính tra cứu từ khóa đơn giản, hoặc chỉ yêu cầu đọc một file đơn lẻ.
origin: community-expert-curated
---

# Codebase Depth Selector (CDS)

Chặn luồng phản hồi để đưa ra lựa chọn về độ sâu phân tích codebase **trước khi** AI đưa ra câu trả lời cuối cùng.

## Khi nào cần sử dụng

- Khi người dùng cần cân bằng giữa tốc độ phản hồi và độ chi tiết của kiến trúc.
- Khi người dùng đề cập đến các từ khóa về độ sâu (deep, brief, summary, exhaustive).
- Khi phân tích một module lớn có hàng chục dependency phức tạp.

**Không kích hoạt** khi: câu trả lời mang tính hiển nhiên hoặc người dùng đã thiết lập mức độ ưu tiên từ trước.

## Cách thức hoạt động

### Bước 1 — Ước lượng quy mô ảnh hưởng (Scope Estimation)

Dựa trên Knowledge Graph (`knowledge-graph.json`), ước lượng số lượng node (file/class/function) liên quan đến câu hỏi.

Hệ số ước lượng:
- **Files liên quan trực tiếp**: `N`
- **Dependencies (hàng xóm)**: `N × 2.5`
- **Total Context Units**: `(Files + Dependencies) × 1.2`

### Bước 2 — Phân loại độ phức tạp của truy vấn

| Độ phức tạp | Phạm vi Graph | Ví dụ câu hỏi |
|-------------|---------------|---------------|
| Thấp (Low)  | 1-3 files     | "Hàm X nằm ở đâu?", "File này làm gì?" |
| Trung bình  | 4-10 files    | "Luồng Login hoạt động như thế nào?" |
| Cao (High)  | 11-30 files   | "Ảnh hưởng của việc thay đổi Database Schema?" |
| Hệ thống    | >30 files     | "Tóm tắt toàn bộ kiến trúc dự án." |

### Bước 3 — Hiển thị các tùy chọn độ sâu

Hiển thị khối này **trước khi** thực hiện phân tích chi tiết:

```text
Đang phân tích phạm vi câu hỏi...

Scope: ~[N] files liên quan | Module: [Name] | Complexity: [Level] | Tool: Understand-Anything

Chọn mức độ sâu bạn muốn:

[1] Tổng quan (25%)   -> Chỉ nêu mục đích chính và entry point.
[2] Cấu trúc (50%)    -> Tóm tắt logic + danh sách các file/class phụ thuộc chính.
[3] Chi tiết (75%)    -> Giải thích luồng dữ liệu + phân tích tác động (impact).
[4] Toàn diện (100%)  -> Deep dive mọi ngóc ngách, code snippets, và sơ đồ tuần tự.

Bạn chọn mức nào? (1-4 hoặc gõ "tóm tắt", "chi tiết", "full")

Độ chính xác dựa trên Knowledge Graph hiện tại: ~95%.
```

### Bước 4 — Phản hồi theo mức độ đã chọn

| Mức độ           | Nội dung bao gồm                                     | Nội dung loại bỏ                                  |
|------------------|-----------------------------------------------------|---------------------------------------------------|
| 25% Tổng quan    | Mục đích, vị trí file chính, kết luận nhanh.        | Logic chi tiết, dependency con, code snippets.    |
| 50% Cấu trúc     | Giải thích luồng chính + 3 dependency quan trọng nhất. | Các trường hợp biên (edge cases), hướng dẫn refactor. |
| 75% Chi tiết     | Luồng dữ liệu, phân tích tác động, ví dụ cụ thể.    | Toàn bộ mã nguồn của các module không liên quan.  |
| 100% Toàn diện   | Phân tích kiến trúc, rủi ro, tối ưu hóa, sơ đồ luồng. | Không loại bỏ gì.                                 |

## Phím tắt (Shortcuts) — Bỏ qua bước hỏi

Nếu người dùng đã ra lệnh rõ ràng, hãy thực hiện ngay lập tức:

| Câu lệnh của người dùng                             | Mức độ |
|----------------------------------------------------|-------|
| "nói sơ qua", "tóm tắt", "brief", "TLDR"           | 25%   |
| "vừa đủ", "cấu trúc chính", "moderate"             | 50%   |
| "chi tiết", "soi kỹ", "detailed"                   | 75%   |
| "deep dive", "exhaustive", "phân tích toàn bộ"     | 100%  |

## Lưu ý về độ chính xác

Skill này dựa trên cấu trúc tĩnh của `Understand-Anything`. Nếu codebase vừa có thay đổi lớn mà chưa chạy `/understand`, kết quả ước lượng có thể sai lệch khoảng 10%.

## Ví dụ

### Kích hoạt (Triggers)
- "Soi kỹ cái module thanh toán này cho tôi."
- "Giải thích ngắn gọn cách hoạt động của middleware."
- "Cho tôi cái nhìn tổng quan (high-level) về repo này."

### Không kích hoạt (Does Not Trigger)
- "File main.py nằm ở đâu?"
- "Sửa lỗi typo trong file này."
- Các câu hỏi tiếp nối sau khi đã chọn độ sâu 75% ở lượt chat trước.

## Nguồn tham khảo
Dựa trên kiến trúc **Context-Aware Agentic Workflow** cho IDE Antigravity.
```