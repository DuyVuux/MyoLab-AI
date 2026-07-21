# Nhập môn toán cho Segmentation và Windowing sEMG

**Phiên bản:** Day 7 — MVP-0  
**Đối tượng:** Người mới học DSP/sEMG  
**Mục tiêu:** hiểu đủ toán để tự kiểm tra hình học cửa sổ trước khi trích RMS, MAV, PSD, MDF hoặc MNF.

> Tài liệu này giải thích kỹ thuật xử lý tín hiệu. Nó không đưa ra ngưỡng lâm sàng và không kết luận mỏi cơ.

## 1. Tại sao phải chia cửa sổ?

Một bản ghi co cơ 60 giây không phải lúc nào cũng có đặc tính thống kê bất biến trong toàn bộ 60 giây. Khi cơ thay đổi mức hoạt hóa hoặc xuất hiện xu hướng mỏi, biên độ và phổ có thể thay đổi theo thời gian. Vì vậy, ta chia pha phân tích thành các đoạn ngắn hơn để tính feature theo thời gian.

```text
active_contraction 60 s
        ↓
window 0,5 s cho RMS/MAV
window 1,0 s cho PSD/MDF/MNF
        ↓
chuỗi feature theo thời gian
        ↓
slope/evidence ở những ngày sau
```

Windowing không tạo ra thông tin mới. Nó chỉ quyết định mẫu nào được dùng chung trong một phép tính.

## 2. Các ký hiệu cần nhớ

| Ký hiệu | Ý nghĩa |
|---|---|
| `Fs` | Tần số lấy mẫu, đơn vị Hz |
| `T` | Độ dài phase, đơn vị giây |
| `N` | Số mẫu trong phase |
| `L` | Số mẫu trong một window |
| `O` | Tỷ lệ overlap |
| `H` | Hop size, số mẫu dịch giữa hai window liên tiếp |
| `K` | Số full-length windows |

Quan hệ cơ bản:

\[
N = F_s T
\]

\[
L = F_s T_w
\]

\[
H = L(1-O)
\]

Với chính sách không nhận partial final window:

\[
K = \left\lfloorrac{N-L}{H}ightfloor + 1
\]

nếu `N >= L`; ngược lại `K = 0`.

## 3. Hai profile của protocol v0.1

Protocol `quad-isometric-60s.v0.1` đã định nghĩa hai độ dài khác nhau:

| Profile | Mục đích | Độ dài | Overlap |
|---|---|---:|---:|
| `time_domain` | RMS, MAV | 500 ms | 50% |
| `frequency_domain` | PSD, MDF, MNF | 1000 ms | 50% |

Không nên ép hai nhóm feature dùng cùng một cửa sổ chỉ để code đơn giản hơn. Cửa sổ ngắn hơn cho cập nhật biên độ dày hơn; cửa sổ dài hơn cung cấp nhiều mẫu hơn cho ước lượng phổ.

## 4. Ví dụ tính tay tại Fs = 1000 Hz

### 4.1. Pha active 60 giây

\[
N = 1000 	imes 60 = 60000\;mẫu
\]

### 4.2. Profile miền thời gian

```text
T_w = 0,5 s
L = 0,5 × 1000 = 500 mẫu
O = 0,5
H = 500 × (1 - 0,5) = 250 mẫu
```

\[
K = \left\lfloorrac{60000-500}{250}ightfloor + 1
= 239
\]

### 4.3. Profile miền tần số

```text
T_w = 1,0 s
L = 1,0 × 1000 = 1000 mẫu
O = 0,5
H = 1000 × (1 - 0,5) = 500 mẫu
```

\[
K = \left\lfloorrac{60000-1000}{500}ightfloor + 1
= 119
\]

## 5. Half-open interval `[start, end)`

Dự án dùng khoảng nửa mở:

```text
[start_sample, end_sample_exclusive)
```

Window gồm `start_sample` nhưng không gồm `end_sample_exclusive`.

Ví dụ:

```text
W0000 = [5000, 5500)
```

chứa các index:

```text
5000, 5001, ..., 5499
```

và có đúng 500 mẫu.

Lợi ích:

- `sample_count = end - start`;
- không đếm lặp mẫu ở biên;
- khớp slicing của Python/NumPy;
- dễ kiểm tra window có vượt phase hay không.

## 6. Overlap không có nghĩa là có thêm dữ liệu độc lập

Với overlap 50%, hai window liên tiếp chia sẻ một nửa số mẫu. Do đó:

- feature sequence mượt hơn;
- thời điểm cập nhật dày hơn;
- nhưng các feature liên tiếp tương quan mạnh;
- số window không phải số quan sát độc lập.

Điều này đặc biệt quan trọng khi làm machine learning sau này: không được chia ngẫu nhiên window của cùng một session vào cả train và test, vì sẽ gây leakage.

## 7. Time resolution và frequency resolution

### 7.1. Độ phân giải thời gian

Hop quyết định tần suất tạo feature mới:

\[
\Delta t_{update} = H/F_s
\]

- Time-domain: `250/1000 = 0,25 s`.
- Frequency-domain: `500/1000 = 0,5 s`.

### 7.2. Độ phân giải tần số trực giác

Nếu dùng một FFT có `L` mẫu:

\[
\Delta f pprox F_s/L
\]

- 500 mẫu tại 1000 Hz: khoảng 2 Hz.
- 1000 mẫu tại 1000 Hz: khoảng 1 Hz.

Welch PSD còn có `nperseg`, window function và averaging riêng, nên con số trên chỉ là trực giác hình học, không phải toàn bộ đặc tả phổ.

## 8. Quasi-stationarity

Khi tính PSD/MDF/MNF trong một window, ta giả định tín hiệu đủ gần stationarity trong khoảng ngắn đó. Đây là giả định mô hình hóa, không phải điều đã được bảo đảm.

Cửa sổ quá dài:

- có thể trộn nhiều trạng thái;
- làm mờ thay đổi nhanh.

Cửa sổ quá ngắn:

- phổ có độ phân giải kém hơn;
- feature dao động mạnh hơn;
- có thể không đủ mẫu cho Welch ổn định.

Vì vậy 500 ms và 1000 ms hiện chỉ là mặc định kỹ thuật có version, cần đánh giá lại trên dữ liệu thật.

## 9. Invalid sample propagation

Nếu một sample bị mask invalid, mọi window chứa sample đó phải invalid khi policy yêu cầu 100% valid samples.

Ví dụ sample index `5750`:

### Profile 500 ms, hop 250

```text
W0001 = [5250, 5750)  → không chứa 5750
W0002 = [5500, 6000)  → chứa 5750
W0003 = [5750, 6250)  → chứa 5750
```

Invalid windows: `[2, 3]`.

### Profile 1000 ms, hop 500

```text
W0000 = [5000, 6000)  → chứa 5750
W0001 = [5500, 6500)  → chứa 5750
```

Invalid windows: `[0, 1]`.

Bài toán này kiểm tra đồng thời overlap và quy ước half-open.

## 10. Partial final window

MVP-0 không tạo window cuối ngắn hơn `L`.

Lý do:

- feature trên window ngắn có phân phối khác;
- PSD/MDF/MNF không còn cùng geometry;
- so sánh theo thời gian khó giải thích hơn;
- dễ tạo lỗi silent padding.

Nếu phase không chia hết theo hop, phần dư được ghi trong provenance nhưng không pad và không lặp mẫu.

## 11. Hann window được áp dụng ở đâu?

Day 7 chỉ tạo index plan. Không nhân Hann tại tầng này.

```text
Windowing
→ trả view untapered
→ RMS/MAV dùng trực tiếp
→ frequency feature stage mới áp dụng Hann/Welch
```

Nếu nhân Hann trước RMS/MAV, biên độ sẽ bị thay đổi bởi taper. Vì vậy, taper phải là quyết định của feature spectral branch, không phải của geometry chung.

## 12. Tự kiểm tra cuối bài

Bạn cần trả lời được:

1. Tại sao 60 giây với window 500 ms, overlap 50% tạo 239 window?
2. Tại sao window 1000 ms tạo 119 window?
3. `[5000, 5500)` chứa bao nhiêu mẫu?
4. Overlap có làm tăng số quan sát độc lập không?
5. Vì sao RMS/MAV và MDF/MNF có thể dùng geometry khác nhau?
6. Vì sao không pad partial window trong MVP-0?
7. Vì sao Hann chưa được áp dụng ở Day 7?
8. Vì sao invalid sample phải lan tới tất cả window giao với nó?
