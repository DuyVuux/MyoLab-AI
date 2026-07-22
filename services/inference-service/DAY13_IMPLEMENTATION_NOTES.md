# Ghi chú triển khai Day 13

- Rule engine đọc structured evidence, không đọc raw signal.
- Không hard-code rule trong UI.
- Không sửa config v0.1 sau khi đã register; thay đổi logic phải tạo version mới.
- `supported_pattern` là thuật ngữ kỹ thuật, không phải chẩn đoán.
