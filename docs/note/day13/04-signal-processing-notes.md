# Ghi chú Xử lý Tín hiệu

- Trong Day 13, chúng ta không trực tiếp xử lý tín hiệu gốc (raw signal) mà làm việc hoàn toàn trên các metadata và bằng chứng kỹ thuật (evidence) đã được rút trích từ Day 12.
- Việc tách biệt thành 2 engine (Evidence Engine - Day 12 và Rule Engine - Day 13) giúp hệ thống tuân thủ tính mở (open-world).
- Sự mâu thuẫn tín hiệu giữa các kênh (multi-channel conflict) không được tự ý giải quyết bằng phương pháp vote (majority) mà bắt buộc phải trả về `inconclusive` để đảm bảo an toàn.
