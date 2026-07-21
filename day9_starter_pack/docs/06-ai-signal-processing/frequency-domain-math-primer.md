# Nền tảng toán học miền tần số cho sEMG — Day 9

> Mục tiêu của tài liệu này là giúp người mới hiểu chính xác DFT, FFT, power spectrum, PSD, Hann và Welch trước khi viết MDF/MNF. Tài liệu không phải hướng dẫn chẩn đoán và không xác nhận lâm sàng bất kỳ chỉ số nào.

## 1. Vì sao cần miền tần số?

Tín hiệu sEMG trong miền thời gian cho biết điện áp thay đổi theo thời gian. Tuy nhiên, nhiều hiện tượng liên quan đến mỏi cơ được mô tả bằng sự phân bố công suất theo tần số. Trong các co cơ đẳng trường kéo dài, phổ sEMG thường có xu hướng dịch về tần số thấp hơn, nhưng xu hướng này còn phụ thuộc protocol, lực co, điện cực, nhiễu và phương pháp xử lý.

Day 9 chỉ xây dựng phép ước lượng PSD có thể tái lập. Chưa được phép suy luận:

```text
PSD thay đổi
→ bệnh nhân chắc chắn mỏi
```

## 2. Tín hiệu rời rạc và DFT

Với một cửa sổ gồm `N` mẫu:

\[
x[0], x[1], \ldots, x[N-1]
\]

Biến đổi Fourier rời rạc:

\[
X[k] = \sum_{n=0}^{N-1} x[n]e^{-j2\pi kn/N},
\quad k=0,1,\ldots,N-1
\]

`X[k]` là số phức. Nó chứa:

- biên độ của thành phần tần số;
- pha của thành phần tần số.

### Điều phải hiểu kỹ

- DFT là định nghĩa toán học.
- FFT là họ thuật toán tính DFT nhanh hơn.
- FFT không phải một phép biến đổi khác DFT.
- Kết quả FFT phải khớp DFT trực tiếp trong sai số số học.

Độ phức tạp trực tiếp của DFT xấp xỉ `O(N²)`, trong khi FFT thường xấp xỉ `O(N log N)`.

## 3. Trục tần số

Với tần số lấy mẫu `Fs` và `Nfft` điểm FFT:

\[
f[k] = k\frac{F_s}{N_{fft}}
\]

Khoảng cách giữa hai bin:

\[
\Delta f_{bin} = \frac{F_s}{N_{fft}}
\]

Với `Fs = 1000 Hz`, `Nfft = 1000`:

```text
Δf_bin = 1000 / 1000 = 1 Hz
```

Tín hiệu thực chỉ cần phổ một phía từ 0 đến Nyquist:

\[
f_{Nyquist} = \frac{F_s}{2}
\]

Với `Fs = 1000 Hz`:

```text
f_Nyquist = 500 Hz
số bin một phía = N/2 + 1 = 501
```

## 4. Khoảng cách bin khác độ phân giải thực

Độ phân giải Rayleigh gần đúng do độ dài segment quyết định:

\[
\Delta f_{Rayleigh} \approx \frac{F_s}{N_{segment}}
\]

Nếu tăng `Nfft` bằng zero-padding nhưng giữ nguyên `Nsegment`:

- khoảng cách bin nhỏ hơn;
- đường phổ nhìn mượt hơn;
- không tạo thêm thông tin vật lý;
- không thực sự tách được hai tần số gần nhau tốt hơn tương ứng.

Day 9 v0.1 khóa:

```text
Nsegment = outer window length
Nfft = Nsegment
zero padding = false
```

## 5. Amplitude spectrum, power spectrum và PSD

### 5.1. Amplitude spectrum

Một cách biểu diễn đơn giản:

\[
A[k] = |X[k]|
\]

Đơn vị phụ thuộc cách chuẩn hóa FFT. Không được dùng amplitude spectrum và PSD như hai khái niệm đồng nhất.

### 5.2. Power spectrum

Dạng cơ bản:

\[
P[k] \propto |X[k]|^2
\]

Với `scaling='spectrum'`, đơn vị thường tương ứng bình phương đơn vị tín hiệu, ví dụ `uV²`.

### 5.3. Power Spectral Density — PSD

PSD mô tả công suất trên mỗi đơn vị tần số. Với input `uV`:

```text
PSD unit = uV²/Hz
```

Tích phân PSD theo tần số có đơn vị:

```text
uV²/Hz × Hz = uV²
```

Đây là lý do Day 9 dùng `scaling='density'`.

## 6. Phổ một phía và hệ số nhân hai

Với tín hiệu thực, phổ hai phía có tính đối xứng liên hợp. Khi chỉ giữ nửa dương, các bin nội bộ thường được nhân hai để bảo toàn tổng công suất. Hai ngoại lệ:

- DC, `f = 0`;
- Nyquist khi `N` chẵn.

Không nên tự nhân hai thủ công nếu thư viện đã trả one-sided PSD đúng chuẩn.

## 7. Spectral leakage

Nếu tần số sine không rơi đúng vào bin FFT, năng lượng bị rò sang nhiều bin. Ví dụ:

```text
Fs = 1000 Hz
N = 1000
bin spacing = 1 Hz
sine = 80.5 Hz
```

`80.5 Hz` không nằm đúng một bin, nên rectangular window tạo sidelobe lớn.

Leakage không phải là nhiễu ngẫu nhiên. Nó là hệ quả của việc quan sát tín hiệu hữu hạn.

## 8. Hann taper

Hann window dạng trực giác:

\[
w[n] = 0.5 - 0.5\cos\left(\frac{2\pi n}{N}\right)
\]

Tùy convention thư viện, mẫu cuối có thể dùng `N` hoặc `N-1`. Day 9 dùng Hann theo convention DFT-even/periodic của SciPy.

Hann:

- giảm sidelobe xa peak;
- giảm leakage;
- làm main lobe rộng hơn;
- thay đổi công suất miền thời gian nên cần normalization theo năng lượng window.

### Quy tắc kiến trúc

```text
Windowing layer
→ chỉ cắt segment, chưa taper

Spectral layer
→ mới áp dụng Hann

RMS/MAV
→ không dùng Hann
```

## 9. Periodogram

Modified periodogram có dạng khái quát:

\[
\hat S_{xx}(f)
\propto
\frac{|FFT\{w[n]x[n]\}|^2}{F_s\sum_n w[n]^2}
\]

Ưu điểm:

- đơn giản;
- có độ phân giải theo chiều dài segment;
- dễ kiểm chứng bằng tín hiệu sine.

Nhược điểm:

- phương sai cao;
- nhạy với realization và cửa sổ hữu hạn.

## 10. Welch PSD

Welch thường thực hiện:

1. chia một đoạn dài thành nhiều segment;
2. cho các segment overlap;
3. áp dụng taper cho từng segment;
4. tính modified periodogram;
5. lấy trung bình.

Kết quả thường giảm phương sai nhưng giảm độ phân giải nếu segment ngắn hơn.

### Quyết định v0.1

Outer frequency window hiện chỉ dài 1000 ms. Day 9 dùng:

```text
nperseg = toàn outer window
noverlap = 0
nfft = outer window length
```

Khi đó Welch v0.1 tương đương một modified periodogram. Lý do vẫn dùng API Welch:

- contract downstream ổn định;
- có thể mở rộng sang nhiều segment ở version sau;
- tránh thay đổi API khi local validation yêu cầu tuning.

Không được diễn giải rằng v0.1 đã có lợi ích giảm phương sai của Welch nhiều segment.

## 11. Detrend constant

Trước PSD, Day 9 dùng:

```text
detrend = constant
```

Tức là trừ mean của mỗi outer frequency window trong estimator.

Lý do:

- giảm thành phần DC còn sót;
- tránh DC ảnh hưởng normalization;
- đây là một phần của spectral estimator và phải được version hóa.

Việc này không thay thế high-pass filtering đã có trong preprocessing.

## 12. Parseval và năng lượng Hann

Một nhầm lẫn phổ biến là so tích phân PSD Hann với variance không trọng số và đòi bằng nhau tuyệt đối. Với taper, tham chiếu đúng hơn là công suất đã được chuẩn hóa theo năng lượng taper:

\[
P_{weighted}
=
\frac{
\sum_n \left(w[n](x[n]-\bar{x})\right)^2
}{
\sum_n w[n]^2
}
\]

Với PSD density theo convention SciPy:

\[
\sum_k PSD[k]\Delta f
\approx P_{weighted}
\]

Day 9 lưu cả hai:

- `time_domain_variance_uV2`: variance không trọng số;
- `window_weighted_power_uV2`: công suất có Hann normalization;
- `parseval_ratio = integrated_psd / window_weighted_power`.

`parseval_ratio` là QA metric, không phải biomarker mỏi cơ.

## 13. Dải phân tích 20–400 Hz

Day 9 cắt PSD về:

```text
20 Hz <= f <= 400 Hz
```

Lý do kỹ thuật MVP-0:

- preprocessing v0.1 dùng band-pass 20–400 Hz;
- tài liệu nghiên cứu nền dùng dải tương tự;
- tránh DC/low-frequency artifact và vùng sát Nyquist.

Nhưng đây chưa phải cấu hình xác nhận cho mọi thiết bị/cơ/task. Sau Motion Lab audit cần kiểm tra:

- hardware filter của Noraxon;
- sampling rate;
- export đã processed hay raw;
- notch/band-pass đã được áp dụng trước đó;
- protocol và muscle target.

## 14. Tích phân PSD trên trục đều

Với trục đều:

\[
P \approx \sum_k PSD[k]\Delta f
\]

Trong code:

```python
power = float(np.sum(psd) * df)
```

Không được cộng PSD mà quên nhân `df`, vì PSD là mật độ theo Hz.

## 15. Peak frequency chỉ là QA

Day 9 lưu tần số có PSD lớn nhất để:

- kiểm tra sine synthetic;
- kiểm tra component trội trong fixture;
- phát hiện lỗi mapping trục.

Peak frequency không được dùng thay MDF/MNF và không được gọi là fatigue feature chính.

## 16. Chuẩn hóa tên MDF và MNF

Tài liệu có thể đảo tên trong tiêu đề hoặc công thức. Dự án khóa định nghĩa chuẩn:

### Mean Frequency — MNF

\[
MNF = \frac{\sum_k f_kP_k}{\sum_kP_k}
\]

### Median Frequency — MDF

MDF là tần số chia tổng công suất thành hai nửa:

\[
\sum_{f_k \le MDF}P_k
\ge
\frac{1}{2}\sum_kP_k
\]

Day 9 chưa triển khai hai công thức này. Day 10 phải viết test có nghiệm biết trước để tránh đảo nhãn.

## 17. Bài tập bắt buộc

### Bài 1

Với `Fs=2000 Hz`, `N=1000`:

```text
bin spacing = ?
Rayleigh resolution = ?
Nyquist = ?
```

Đáp án:

```text
2 Hz
2 Hz
1000 Hz
```

### Bài 2

Với sine biên độ đỉnh `A=10 uV`, mean bằng 0:

\[
P = \frac{A^2}{2}=50\;uV^2
\]

### Bài 3

PSD bằng `2 uV²/Hz` trên 10 Hz:

```text
power = 2 × 10 = 20 uV²
```

### Bài 4

Giải thích vì sao `Nfft=4096` với segment 1000 mẫu không tạo độ phân giải vật lý `Fs/4096` theo cùng nghĩa với segment 4096 mẫu.

## 18. Checklist tự đánh giá

Bạn chỉ nên sang Day 10 khi giải thích được:

- [ ] DFT khác FFT ở điểm nào.
- [ ] Bin spacing khác Rayleigh resolution thế nào.
- [ ] PSD có đơn vị gì.
- [ ] Vì sao tích phân PSD phải nhân `df`.
- [ ] Spectral leakage là gì.
- [ ] Hann đổi leakage và main lobe thế nào.
- [ ] Welch v0.1 hiện có bao nhiêu segment.
- [ ] Vì sao `parseval_ratio` dùng weighted power.
- [ ] Vì sao peak frequency không phải MDF.
- [ ] Công thức chuẩn của MDF và MNF khác nhau thế nào.
