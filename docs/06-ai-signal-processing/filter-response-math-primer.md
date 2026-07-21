# Ghi chú toán nền tảng — Đáp ứng tần số và kiểm chứng bộ lọc sEMG

## 1. Hệ LTI và hàm truyền

Với hệ tuyến tính bất biến theo thời gian:

\[
y[n]=(h*x)[n]
\]

Trong miền tần số:

\[
Y(e^{j\omega})=H(e^{j\omega})X(e^{j\omega})
\]

`|H|` là tỷ lệ biên độ; góc của `H` là phase shift.

## 2. Decibel

Biên độ:

\[
G_{dB}=20\log_{10}(A_{out}/A_{in})
\]

Công suất:

\[
G_{dB}=10\log_{10}(P_{out}/P_{in})
\]

Vì công suất tỷ lệ bình phương biên độ nên hai công thức nhất quán.

## 3. Lọc tiến/lùi để đạt pha bằng không

Nếu one-pass response là `H`, forward/backward response là:

\[
H_{eff}=H\cdot H^*=|H|^2
\]

Do đó độ dốc attenuation tăng và cutoff one-pass -3 dB trở thành khoảng -6 dB về biên độ hiệu dụng.

## 4. Sinusoidal projection

Với tần số đã biết, chiếu lên sin/cos giúp đo amplitude mà không cần phụ thuộc vào việc chọn FFT peak:

\[
A_c=\frac{2}{N}\sum x[n]\cos(2\pi ft_n)
\]

\[
A_s=\frac{2}{N}\sum x[n]\sin(2\pi ft_n)
\]

\[
A=\sqrt{A_c^2+A_s^2}
\]

Phương pháp chính xác nhất khi cửa sổ chứa số chu kỳ nguyên và không có thành phần trùng tần số.

## 5. Impulse response symmetry

Zero-phase filter có impulse response đối xứng trong kiểm thử offline. Sai số đối xứng chuẩn hóa:

\[
E_{sym}=\frac{\max_k|h[n_0-k]-h[n_0+k]|}{\max_n|h[n]|}
\]

## 6. Quá độ tại biên

`filtfilt` cần padding/context. Đầu và cuối bản ghi có thể khác vùng nội bộ. Vì thế preprocessing không trim dữ liệu âm thầm mà cung cấp edge guard/valid mask cho windowing.

## 7. Khả năng tái lập

- Bitwise equality: mạnh nhất trong cùng Python/NumPy/SciPy/platform.
- Numerical equivalence: dùng tolerance khi môi trường khác.
- Config hash: chứng minh file config không đổi.
- Code hash: chứng minh implementation tham gia verification không đổi.

## 8. Kiểm chứng phân tích không phải xác nhận lâm sàng

Analytical verification trả lời: “Code có làm đúng điều được đặc tả trên fixture kiểm soát không?”  
Xác nhận lâm sàng trả lời: “Output có đáng tin và hữu ích trên population/use case lâm sàng cụ thể không?”
