# Ghi chú đọc hiểu JSON Day 12

1. `pattern_category` nằm ở đâu?
- Nằm trong kết quả của mỗi kênh cụ thể (`channels` -> `pattern_category`), ví dụ: `multi_domain_change_pattern_observed`.

2. `feature_assessments` ghi gì?
- Ghi lại đánh giá (supporting, contradicting, insufficient) của từng feature (như mdf, mnf, rms) đóng góp vào kết luận của kênh đó.

3. `frequency_domain_status` và `amplitude_domain_status` khác nhau thế nào?
- Thể hiện trạng thái đồng thuận của từng miền riêng biệt. Frequency là miền tần số (mnf, mdf), Amplitude là miền biên độ (rms, mav). Mỗi miền có thể có trạng thái đánh giá riêng.

4. `downstream_allowed` khác `abstention` thế nào?
- `abstention` mang ý nghĩa hệ thống chủ động từ chối xử lý (do lỗi hoặc dữ liệu hỏng), còn `downstream_allowed` là cờ báo hiệu cho các module phía sau (như Rule Engine) biết có được phép sử dụng kết quả này tiếp tục tính toán hay không.

5. Tại sao Day 12 chưa được gọi là inference?
- Day 12 chỉ mới tổng hợp bằng chứng (evidence) và nhận diện pattern, nó chưa ra quyết định (decision) hay kết luận cuối cùng dựa trên các rule. Day 13 mới làm nhiệm vụ inference (đưa ra suy luận kết luận).
