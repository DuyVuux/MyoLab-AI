---
trigger: manual
description: Tự động sử dụng prr-kit để check và review code sau mỗi lần thay đổi
---

# PRR-CODE-REVIEW.MD - Automatic Quality & Security Review

> **Mục tiêu**: Đảm bảo tất cả các thay đổi về mã nguồn (tạo mới, chỉnh sửa, refactor) do AI (IDE) thực hiện đều phải được quét và review tự động bởi `prr-kit` trước khi coi như hoàn thành, nhằm ngăn chặn nợ kỹ thuật và lỗ hổng bảo mật.

---

## 🚀 1. QUY TẮC KÍCH HOẠT (TRIGGER)

Quy tắc này PHẢI được kích hoạt **BẮT BUỘC** trong các tình huống sau:
- Ngay sau khi Agent hoàn thành một khối lượng thay đổi code đáng kể (viết mới function, sửa logic, refactor).
- Trước khi thực hiện `git commit` hoặc chuẩn bị tạo Pull Request/Merge Request.
- Khi người dùng yêu cầu kiểm tra lại chất lượng code.

---

## 🔄 2. QUY TRÌNH REVIEW BẮT BUỘC

Sau khi Agent thay đổi code, Agent **PHẢI THỰC HIỆN** các bước sau:

### Bước 1: Khởi chạy PR Review
Sử dụng công cụ `prr-kit` (đã được cài đặt qua `npx prr-kit install`) bằng cách gọi lệnh tắt của IDE định nghĩa.
- Chạy lệnh: `/prr-quick` (cho 1 lần quét toàn diện: chọn PR -> lấy context -> chạy 5 reviewer -> xuất report).
- Hoặc mở menu tổng để tuỳ chọn: `/prr-master`.
*(Nếu AI chạy lệnh bị giới hạn, hãy thông báo để người dùng chủ động gõ `/prr-quick` trên khung chat của IDE).*

### Bước 2: Đọc báo cáo kết quả
Mặc định báo cáo phân tích sâu sẽ được `prr-kit` trích xuất ra folder cấu hình. 
- Agent PHẢI tìm và đọc file báo cáo review tại thư mục: `_prr-output/reviews/`.

### Bước 3: Đánh giá và Khắc phục (Auto-Fixing)
Dựa theo phân cấp lỗi (Severity Levels) chuẩn của `prr-kit`, Agent PHẢI hành động tương ứng đối với code vừa viết:
- 🔴 **[BLOCKER]**: Lỗi nghiêm trọng (VD: Lỗ hổng bảo mật, lỗi logic sai nghiệp vụ). **Bắt buộc** Agent phải tự tạo Plan và fix lại code ngay lập tức. Cấm commit/merge.
- 🟡 **[WARNING]**: Lỗi tiềm ẩn (VD: Cấu trúc chưa tối ưu, tốn memory). Cố gắng fix nếu trong phạm vi an toàn, hoặc báo cho người dùng biết.
- 🟢 **[SUGGESTION]**: Đề xuất cải thiện (nice-to-have). Có thể hỏi ý kiến người dùng xem có muốn áp dụng không.
- ❓ **[QUESTION]**: Nếu công cụ hỏi thêm về business logic, Agent phải hỏi lại người dùng để làm rõ.

---

## 👓 3. 5 BỘ LỌC CHẤT LƯỢNG (Lưu ý cho Agent)

Khi tạo code, Agent hãy lập trình theo tiêu chuẩn cao nhất để vượt qua 5 chuyên gia đánh giá của `prr-kit`:
1. **👁️ General Review**: Logic chính xác? Đặt tên theo chuẩn? Có vi phạm nguyên tắc DRY? Có thiếu Unit test?
2. **🔒 Security Review**: Có lỗi Injection, XSS? Có hardcode secret key? Phân quyền (Auth) đã đúng chuẩn OWASP chưa?
3. **⚡ Performance Review**: Có tối ưu vòng lặp, N+1 query database không? Có dọn dẹp bộ nhớ (memory leak) không?
4. **🏗️ Architecture Review**: Có vi phạm SOLID, phá vỡ cấu trúc layer/pattern của cả project không?
5. **💼 Business Review**: Chức năng có đạt đủ yêu cầu thực tế, an toàn dữ liệu và GDPR không?

---

> ⚠️ **Hành vi sai trái cần tránh**: Agent tuyệt đối KHÔNG ĐƯỢC báo cáo "Đã hoàn thành công việc" nếu chưa chạy `/prr-quick` và chưa giải quyết dứt điểm các lỗi 🔴 **[BLOCKER]**.