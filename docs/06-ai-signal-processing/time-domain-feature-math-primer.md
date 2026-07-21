# Nền tảng toán học Day 8 — RMS và MAV của tín hiệu sEMG

**Trạng thái:** tài liệu học và kiểm chứng phần mềm MVP-0  
**Phạm vi:** đặc trưng miền thời gian trên từng cửa sổ hợp lệ  
**Không thuộc phạm vi:** MDF, MNF, PSD, slope, FRS, phân loại ML và diễn giải lâm sàng

## 1. Mục tiêu học tập

Sau khi đọc tài liệu này, người thực hiện phải giải thích được:

1. RMS và MAV đo đại lượng gì trong một cửa sổ sEMG.
2. Vì sao cả hai dùng mẫu số `N`, không dùng `N - 1`.
3. Vì sao đầu vào `uV` tạo đầu ra `uV`.
4. Vì sao RMS luôn lớn hơn hoặc bằng MAV đối với cùng một vector hữu hạn.
5. Vì sao RMS nhạy với đỉnh lớn hơn MAV.
6. Vì sao đổi dấu tín hiệu không thay đổi RMS/MAV.
7. Vì sao nhân tín hiệu với hệ số `c` làm RMS/MAV nhân với `|c|`.
8. Vì sao không cần rectify tín hiệu trước khi tính RMS/MAV.
9. Vì sao RMS/MAV không tự động đồng nghĩa với mỏi cơ.
10. Vì sao các cửa sổ overlap không phải các quan sát độc lập cho ML.

---

## 2. Ký hiệu

Cho một cửa sổ tín hiệu rời rạc:

\[
x[0], x[1], \ldots, x[N-1]
\]

Trong đó:

- `x[n]`: biên độ mẫu thứ `n`;
- `N`: số mẫu trong cửa sổ;
- đơn vị canonical của pipeline là microvolt (`uV`);
- Day 8 dùng cửa sổ `time_domain` dài 500 ms;
- với `Fs = 1000 Hz`, mỗi cửa sổ có `N = 500` mẫu.

Input Day 8 phải là:

```text
band-passed
+ unrectified
+ untapered
+ finite
+ window status = valid
```

---

## 3. Root Mean Square — RMS

### 3.1. Công thức rời rạc

\[
\operatorname{RMS}(x)
=
\sqrt{\frac{1}{N}\sum_{n=0}^{N-1}x[n]^2}
\]

RMS thực hiện ba bước:

1. bình phương từng mẫu;
2. lấy trung bình;
3. lấy căn bậc hai.

RMS có cùng đơn vị với tín hiệu đầu vào. Nếu `x[n]` có đơn vị `uV`, thì:

```text
x[n]^2      → uV²
mean(x²)    → uV²
sqrt(mean)  → uV
```

### 3.2. Ví dụ tính tay

Với:

```text
x = [-3, -1, 1, 3] uV
```

Ta có:

\[
\operatorname{RMS}
=
\sqrt{\frac{9+1+1+9}{4}}
=
\sqrt{5}
\approx 2.2361\;uV
\]

### 3.3. Quan hệ giữa RMS, mean và variance

Với population variance:

\[
\operatorname{Var}(x)
=
\frac{1}{N}\sum_{n=0}^{N-1}(x[n]-\bar{x})^2
\]

ta có:

\[
\operatorname{RMS}(x)^2
=
\operatorname{Var}(x)+\bar{x}^2
\]

Hệ quả:

- nếu mean gần 0, RMS gần population standard deviation;
- nếu còn DC offset, RMS tăng do thành phần `mean²`;
- đây là một lý do pipeline phải mean-center/band-pass trước feature extraction;
- Day 8 không tự ý trừ mean lại trên từng window vì thay đổi đó phải thuộc preprocessing contract và version riêng.

---

## 4. Mean Absolute Value — MAV

### 4.1. Công thức rời rạc

\[
\operatorname{MAV}(x)
=
\frac{1}{N}\sum_{n=0}^{N-1}|x[n]|
\]

MAV lấy trung bình trị tuyệt đối của các mẫu. Nó cũng giữ nguyên đơn vị đầu vào.

### 4.2. Ví dụ tính tay

Với cùng vector:

```text
x = [-3, -1, 1, 3] uV
```

\[
\operatorname{MAV}
=
\frac{3+1+1+3}{4}
=2\;uV
\]

---

## 5. Vì sao mẫu số là N, không phải N - 1?

RMS và MAV trong feature extraction mô tả **toàn bộ các mẫu trong cửa sổ đang xét**. Ta không dùng chúng để ước lượng phương sai dân số từ một mẫu thống kê theo nghĩa classical inference.

Do đó:

```text
RMS: chia N
MAV: chia N
```

`N - 1` thường xuất hiện trong sample variance để hiệu chỉnh bias của ước lượng variance. Nó không phải định nghĩa chuẩn của RMS/MAV sEMG theo cửa sổ.

---

## 6. Bất đẳng thức RMS ≥ MAV

Đối với vector hữu hạn, áp dụng bất đẳng thức Cauchy–Schwarz:

\[
\left(\sum_{n=0}^{N-1}|x[n]|\right)^2
\le
N\sum_{n=0}^{N-1}x[n]^2
\]

Chia hai vế cho `N²`:

\[
\left(\frac{1}{N}\sum |x[n]|\right)^2
\le
\frac{1}{N}\sum x[n]^2
\]

Lấy căn hai vế:

\[
\operatorname{MAV}(x)
\le
\operatorname{RMS}(x)
\]

Đây là một **software invariant** rất hữu ích. Nếu cùng một row có `MAV > RMS` vượt tolerance số học, implementation hoặc data mapping có vấn đề.

Trường hợp bằng nhau xảy ra khi mọi `|x[n]|` bằng nhau, ví dụ:

```text
[-5, 5, -5, 5]
RMS = 5
MAV = 5
```

---

## 7. Tính bất biến theo dấu và tính đồng nhất theo scale

### 7.1. Đổi dấu

\[
\operatorname{RMS}(-x)=\operatorname{RMS}(x)
\]

\[
\operatorname{MAV}(-x)=\operatorname{MAV}(x)
\]

Điều này phù hợp vì RMS/MAV đo độ lớn, không đo polarity.

### 7.2. Nhân scale

Với hằng số `c`:

\[
\operatorname{RMS}(cx)=|c|\operatorname{RMS}(x)
\]

\[
\operatorname{MAV}(cx)=|c|\operatorname{MAV}(x)
\]

Đây là lý do unit normalization phải hoàn thành trước feature extraction. Nếu cùng signal được biểu diễn bằng `mV` thay vì `uV`, giá trị số sẽ khác 1000 lần dù hiện tượng vật lý giống nhau.

---

## 8. RMS nhạy với đỉnh lớn hơn MAV

Xét hai vector:

```text
A = [1, 1, 1, 1]
B = [1, 1, 1, 10]
```

Với A:

```text
RMS = 1
MAV = 1
```

Với B:

\[
RMS_B=\sqrt{\frac{1+1+1+100}{4}}\approx 5.074
\]

\[
MAV_B=\frac{1+1+1+10}{4}=3.25
\]

Bình phương làm RMS tăng mạnh hơn khi có peak lớn. Vì vậy:

- RMS có thể nhạy hơn với bursts thật;
- RMS cũng có thể nhạy hơn với artifact hoặc clipping;
- không được bỏ qua QC chỉ vì đã có RMS;
- so sánh RMS cần context về force/task/electrode setup.

---

## 9. Tín hiệu sin: nghiệm tham chiếu

Với tín hiệu liên tục lý tưởng:

\[
x(t)=A\sin(2\pi ft)
\]

trên số chu kỳ nguyên:

\[
RMS=\frac{A}{\sqrt{2}}
\]

và trong miền liên tục:

\[
MAV=\frac{2A}{\pi}
\]

Ví dụ `A = 100 uV`:

```text
RMS ≈ 70.7107 uV
MAV ≈ 63.6620 uV
```

### Cảnh báo về lấy mẫu rời rạc

MAV rời rạc của một sine phụ thuộc lưới mẫu. Nếu mỗi chu kỳ chỉ có ít mẫu, trung bình `|sin|` rời rạc có thể khác `2/π`. Vì vậy test phải:

- dùng sampling đủ dày;
- dùng tolerance rõ ràng;
- phân biệt nghiệm liên tục với tổng hữu hạn rời rạc.

Đây không phải lỗi của MAV; đây là hệ quả của sampling.

---

## 10. Có cần rectify trước RMS/MAV không?

Không cần.

RMS đã có bình phương:

\[
(-x)^2=x^2
\]

MAV đã có trị tuyệt đối:

\[
|-x|=|x|
\]

Do đó:

```text
RMS(x) = RMS(abs(x))
MAV(x) = MAV(abs(x))
```

Nhưng Day 8 vẫn dùng **band-passed unrectified signal** để giữ một signal path nhất quán và tránh hiểu nhầm rằng rectification là denoising.

Rectification/envelope có thể được dùng cho visualization hoặc activation envelope, nhưng phải là một transform có version riêng, không làm ngầm trong feature extractor.

---

## 11. Có cần Hann taper trước RMS/MAV không?

Không.

Hann taper nhân mỗi mẫu với trọng số khác nhau. Điều này thay đổi biên độ và vì thế thay đổi RMS/MAV.

```text
Time-domain RMS/MAV:
→ dùng untapered window

PSD/MDF/MNF sau này:
→ có thể dùng Hann trong spectral estimator
```

Day 7 chỉ tạo geometry; Day 8 lấy đúng read-only untapered view.

---

## 12. Overlap và tính không độc lập

Window 500 ms, overlap 50% tại `Fs = 1000 Hz`:

```text
window length = 500 samples
hop = 250 samples
```

Hai window kế tiếp chia sẻ 250 mẫu. Vì vậy:

- feature curve có update dày hơn;
- các row liền nhau tương quan;
- 239 row không đồng nghĩa 239 đối tượng độc lập;
- khi ML, phải split theo subject/session trước windowing;
- không được random-split các window từ cùng session vào train và test.

---

## 13. RMS/MAV có nói được “mỏi cơ” không?

Không, nếu đứng riêng.

RMS/MAV chịu ảnh hưởng bởi:

- mức lực và %MVC;
- recruitment và firing pattern;
- vị trí/hướng điện cực;
- impedance da;
- gain và unit thiết bị;
- crosstalk;
- movement artifact;
- normalization;
- protocol và kiểu co cơ.

Trong một số protocol mỏi, biên độ có thể tăng; trong một số tình huống khác, biên độ có thể giảm khi force output suy giảm. Vì vậy Day 8 chỉ được phát biểu:

> “Đây là các quan sát biên độ theo cửa sổ trong protocol hiện tại.”

Không được phát biểu:

> “RMS tăng nên bệnh nhân bị mỏi.”

Fatigue evidence phải kết hợp spectral trend, protocol context, QC, local validation và human review.

---

## 14. Bài tập bắt buộc

### Bài 1

Tính RMS và MAV của:

```text
x = [-2, 0, 2, 0]
```

### Bài 2

Nếu tín hiệu `uV` được nhân 1000 do nhầm coi `mV` là `uV`, RMS/MAV thay đổi thế nào?

### Bài 3

Chứng minh ngắn gọn RMS không đổi khi đảo dấu tín hiệu.

### Bài 4

Giải thích vì sao `[0, 0, 0, 20]` có RMS tăng mạnh hơn MAV so với `[0, 0, 0, 4]`.

### Bài 5

Tại sao 239 overlapping windows không thể được coi như 239 người bệnh độc lập?

---

## 15. Đáp án kiểm tra nhanh

### Bài 1

\[
RMS=\sqrt{\frac{4+0+4+0}{4}}=\sqrt{2}\approx1.4142
\]

\[
MAV=\frac{2+0+2+0}{4}=1
\]

### Bài 2

Cả RMS và MAV tăng 1000 lần. Đó là lỗi unit, không phải thay đổi sinh lý.

### Bài 3

Vì `(-x[n])² = x[n]²`, nên tổng bình phương và RMS không đổi.

### Bài 4

RMS bình phương peak nên peak 20 đóng góp 400, còn MAV chỉ dùng trị tuyệt đối 20.

### Bài 5

Vì các window dùng chung mẫu và cùng thuộc một session/subject; chúng tương quan và gây leakage nếu split sai.

---

## 16. Checklist tự đánh giá

- [ ] Tôi tính được RMS/MAV bằng tay cho vector ngắn.
- [ ] Tôi giải thích được `RMS ≥ MAV`.
- [ ] Tôi hiểu unit được giữ nguyên.
- [ ] Tôi hiểu vì sao không dùng `N - 1`.
- [ ] Tôi hiểu vì sao không rectify/taper ở Day 8.
- [ ] Tôi hiểu residual mean có thể làm RMS tăng.
- [ ] Tôi hiểu overlap gây tương quan.
- [ ] Tôi không diễn giải RMS/MAV đơn lẻ thành fatigue status.
