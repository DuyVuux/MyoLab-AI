# Ghi chú Xử lý tín hiệu Day 8

- **Không tự động chuẩn hóa:** Các đặc trưng được tính với đơn vị nguyên bản của dữ liệu (uV) không trải qua bước chuẩn hóa biên độ như MVC (Maximum Voluntary Contraction) hay theo đường nền (baseline normalization) để đảm bảo bảo toàn giá trị đo.
- **Không apply cửa sổ làm mượt (untapered):** Không sử dụng các taper như Hann Window trước khi tính toán RMS/MAV vì nó làm giảm amplitude ở rìa cửa sổ, ảnh hưởng trực tiếp đến kết quả RMS/MAV.
- **Tính toán trên tín hiệu chưa chỉnh lưu (unrectified):** RMS và MAV đã loại bỏ dấu âm thông qua bình phương và lấy trị tuyệt đối, do đó không cần rectify (chỉnh lưu) tín hiệu một lần nữa trước khi tính toán.
- **Trùng lặp cửa sổ (Overlap):** Việc dùng 500ms cửa sổ với 50% overlap sẽ khiến các cửa sổ không độc lập thống kê với nhau.
