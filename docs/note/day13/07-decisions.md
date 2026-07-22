# Nhật ký các quyết định

- **Quyết định 1:** Tách biệt hoàn toàn Rule Engine khỏi Evidence Engine (Day 12).
- **Quyết định 2:** Sử dụng Rule-based (Deterministic) thay vì Machine Learning cho MVP-0 để đảm bảo khả năng giải thích (Explainable).
- **Quyết định 3:** Enum trạng thái kết quả đầu ra bị giới hạn cứng ở 4 giá trị (`supported_pattern`, `no_supported_pattern`, `inconclusive`, `abstained`). Tuyệt đối không xuất ra tỷ lệ phần trăm mỏi cơ (`probability`).
- **Quyết định 4:** Cấu trúc Pipeline phải kiểm tra cờ `abstention` và hợp lệ của Version/Schema từ Day 12 trước khi thực thi Rule Mapping.
