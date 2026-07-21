# Ghi chú Toán học Day 8

## Bài 1 — zero vector
```text
x = [0, 0, 0, 0]
RMS = 0
MAV = 0
```

## Bài 2 — symmetric vector
```text
x = [-3, -1, 1, 3]
RMS = sqrt(5) ≈ 2.2360679
MAV = 2
```

## Bài 3 — constant magnitude
```text
x = [-5, 5, -5, 5]
RMS = 5
MAV = 5
```

**Nhận xét:** 
Tính tay không dùng code giúp khẳng định `RMS >= MAV`. RMS nhạy với peak do có phép bình phương, trong khi MAV trung bình hoá trị tuyệt đối đồng đều hơn. Nếu nhân vector với hằng số `c`, RMS và MAV sẽ nhân với `|c|`. Đổi dấu vector không làm thay đổi giá trị.
