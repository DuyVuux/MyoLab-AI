# Day 13 — learning objectives

## Ghi chép
- Xây dựng một Explainable Rule Engine v0.1 tiêu thụ kết quả từ Fatigue Evidence Engine của Day 12.
- Triển khai logic rule deterministic để đưa ra kết luận kỹ thuật có giải thích (basis/counterevidence) và hỗ trợ abstention.
- Không sử dụng Machine Learning, không đưa ra chẩn đoán lâm sàng.

## Điều tôi tự giải thích được
- Rule engine cung cấp sự minh bạch, kiểm soát hoàn toàn bằng luật logic định sẵn so với một "hộp đen" ML.
- Abstention (từ chối đưa ra kết luận) là cần thiết khi đầu vào từ Day 12 gặp lỗi (ví dụ: QC fail).

## Điều còn chưa chắc
- Cách thức hệ thống kết hợp kết quả Rule Engine này với dữ liệu lâm sàng thực tế để chẩn đoán y khoa.
