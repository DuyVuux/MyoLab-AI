# Environment notes

Không tạo dependency lock giả trong Day 30. Trước model fitting Day 31 phải sinh lock thật từ resolver của môi trường dự án.

`pyarrow` là optional. Nếu không có, dùng CSV fallback và ghi rõ format trong manifest.
