# Nền tảng toán cho Engineering Confidence v0.1

## 1. Mục tiêu

Engineering confidence đo mức đầy đủ và nhất quán **nội bộ** của pipeline. Nó không phải xác suất mỏi và chưa được clinical calibration.

## 2. Tổng trọng số

\[
C_{raw}=w_qC_q+w_uC_u+w_tC_t+w_eC_e
\]

Trong v0.1:

```text
wq = 0,35  — QC quality
wu = 0,25  — usable-window ratio
wt = 0,20  — trend quality
we = 0,20  — evidence consistency
```

Tổng trọng số phải bằng 1.

Ví dụ:

```text
Cq = 1,0
Cu = 0,8
Ct = 0,5
Ce = 1,0
```

\[
C_{raw}=0.35+0.20+0.10+0.20=0.85
\]

## 3. Chuẩn hóa về [0,1]

Mỗi thành phần phải có nghĩa rõ ràng và được clamp về `[0,1]`. Clamp không được dùng để che dữ liệu sai; non-finite input phải bị reject.

## 4. Confidence cap

Nếu rule là `inconclusive`, score cuối bị giới hạn tối đa 0,59:

\[
C_{final}=\min(C_{raw},0.59)
\]

Cap ngăn output vừa nói “không kết luận được” vừa hiển thị confidence rất cao.

## 5. Category

```text
>= 0,80 → engineering_high
>= 0,60 → engineering_moderate
>= 0,40 → engineering_low
<  0,40 → engineering_very_low
```

Tên category luôn có tiền tố `engineering_` để tránh bị hiểu là clinical confidence.

## 6. Tại sao đây không phải probability?

Probability cần một biến cố xác định, dữ liệu ground truth, mô hình thống kê và calibration. Weighted score từ các heuristic component không tự trở thành xác suất.

## 7. Bài tập

1. Tính score khi QC=`warning` (0,75), usable=0,9, trend=0,6, consistency=0,8.
2. Áp dụng cap nếu conclusion là `inconclusive`.
3. Giải thích vì sao confidence cao không sửa được electrode placement sai.
