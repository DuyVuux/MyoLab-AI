# Định nghĩa metric UC2 v0.1

- Percent change: `100·(current-baseline)/|baseline|`; không tính khi baseline gần 0.
- Symmetry ratio: `100·affected/reference`; chỉ dùng khi hai bên cùng protocol và normalization.
- Repeatability CoV: `100·population_std/|mean|`; thấp hơn thường ổn định hơn, không phải clinical score.
- CCI candidate: `200·min(A,B)/(A+B)`; có nhiều định nghĩa nên bắt buộc lưu formula version.
- Cosine similarity: đo hướng của vector đặc trưng, không chứng minh agreement hoặc clinical recovery.

Mọi metric Day 23 có `not_validated`.
