# Ghi chú đọc Ngày 4

## Các nguồn đã đọc

- [x] `docs/02-clinical/quality-escalation-policy.md`
- [x] `docs/06-ai-signal-processing/signal-validation-spec.md`
- [x] `docs/03-architecture/high-level-architecture.md`
- [x] `After-Fatigue_Condition_A_Novel_Analysis_Based_on_.pdf`

## Giải thích của tôi về kết quả QC

### Pass (Đạt)

Tín hiệu đủ chất lượng, cho phép tiếp tục luồng phân tích (`analysis_allowed = true`).

### Warning (Cảnh báo)

Tín hiệu có vấn đề nhẹ, vẫn cho phép tiếp tục phân tích nhưng ghi nhận cảnh báo vào kết quả và yêu cầu chuyên gia xem xét lại (review).

### Fail (Thất bại)

Tín hiệu kém chất lượng, chặn luồng phân tích, trả về trạng thái Abstention và kèm theo hướng dẫn khắc phục.

### Abstention (Từ chối đánh giá)

Hệ thống từ chối đưa ra kết luận về tình trạng mệt mỏi do tín hiệu bị Fail (không đủ điều kiện phân tích) hoặc do bằng chứng mâu thuẫn/yếu.

## Năm bài học chính

1. Việc kiểm soát chất lượng tín hiệu (QC) đóng vai trò quyết định; tín hiệu lỗi (Fail) sẽ chặn toàn bộ luồng phân tích.
2. Trạng thái Abstention là cơ chế an toàn để hệ thống không đưa ra dự đoán sai lệch khi thiếu dữ liệu chất lượng hoặc bằng chứng yếu.
3. Trạng thái Warning cho phép hệ thống linh hoạt xử lý tín hiệu có lỗi nhỏ, kết hợp với quy trình đánh giá lại của chuyên gia (Human-in-the-loop).
4. Các quy tắc escalation quy định rõ hành vi của hệ thống, giúp người vận hành (operator) biết cách khắc phục khi bị từ chối import hoặc fail QC.
5. Kiến trúc hệ thống phân tách rõ ràng giữa thu nhận dữ liệu (Ingestion), cổng chất lượng (Quality Gate) và phân tích mệt mỏi (Fatigue Evidence).
