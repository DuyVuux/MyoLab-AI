# Nền tảng toán học MDF và MNF — Day 10

## 1. Mục tiêu học

Sau tài liệu này, bạn phải phân biệt được:

- PSD là mật độ công suất, không phải tần số đặc trưng;
- MNF là trọng tâm công suất;
- MDF là phân vị 50% của công suất;
- peak frequency, MNF và MDF là ba đại lượng khác nhau;
- MDF/MNF phụ thuộc estimator, dải tần và độ phân giải.

## 2. Mean Frequency — MNF

Với các bin tần số `f[k]` và PSD `P[k]` trên trục đều:

\[
MNF = \frac{\sum_k f[k]P[k]}{\sum_k P[k]}
\]

Nếu viết rõ công suất mỗi bin là `P[k]Δf`, thì `Δf` triệt tiêu khi trục đều.

### Ví dụ tính tay

| f (Hz) | Trọng số PSD |
|---:|---:|
| 50 | 1 |
| 100 | 2 |
| 150 | 1 |

\[
MNF = \frac{50\times1 + 100\times2 + 150\times1}{1+2+1}=100\;Hz
\]

## 3. Median Frequency — MDF

MDF là tần số mà công suất tích lũy đạt 50% tổng công suất:

\[
\int_{f_{low}}^{MDF} PSD(f)df
= \frac{1}{2}\int_{f_{low}}^{f_{high}} PSD(f)df
\]

Trong dữ liệu rời rạc, mỗi bin có khối lượng gần bằng:

\[
B_k = PSD[k]\Delta f
\]

Day 10 dùng CDF của `B_k`, tìm bin chứa 50% và nội suy tuyến tính trong bin.

## 4. Peak frequency khác MDF/MNF

- Peak frequency: bin có PSD lớn nhất.
- MNF: trung bình có trọng số của toàn bộ phổ.
- MDF: điểm chia đôi tổng công suất.

Một peak hẹp ở 80 Hz nhưng có đuôi dài phía cao tần có thể có MNF lớn hơn 80 Hz.

## 5. Bất biến scale

Nếu nhân toàn bộ PSD với hằng số dương `c`:

\[
MDF(cP)=MDF(P),\quad MNF(cP)=MNF(P)
\]

Nhưng tổng công suất tăng `c` lần. Đây là test phần mềm bắt buộc.

## 6. Các giới hạn phải nhớ

- MDF/MNF thay đổi khi đổi dải 20–400 Hz sang dải khác.
- Đổi window length, taper, Welch config hoặc sampling rate có thể thay đổi kết quả.
- Một cửa sổ MDF/MNF chưa đủ để kết luận mỏi cơ.
- Xu hướng theo thời gian và protocol mới tạo được bằng chứng có ý nghĩa hơn.
