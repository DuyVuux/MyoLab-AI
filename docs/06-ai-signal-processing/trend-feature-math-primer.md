# Nền tảng toán học Trend Features — Day 11

## 1. Mô hình tuyến tính

\[
y_i = a + bt_i + \epsilon_i
\]

- `b`: slope theo đơn vị feature/giây;
- `a`: intercept;
- `t_i`: tâm cửa sổ theo giây, không phải window index.

\[
b = \frac{\sum (t_i-\bar t)(y_i-\bar y)}{\sum(t_i-\bar t)^2}
\]

## 2. R² và RMSE

\[
R^2=1-\frac{SSE}{SST}
\]

\[
RMSE=\sqrt{\frac{1}{N}\sum (y_i-\hat y_i)^2}
\]

R² cao chỉ cho biết đường thẳng mô tả chuỗi tốt hơn; không chứng minh cơ mỏi.

## 3. Early/late median

Day 11 lấy 20% số điểm đầu và 20% số điểm cuối, dùng median để giảm ảnh hưởng outlier.

\[
\Delta y = median(y_{late})-median(y_{early})
\]

\[
\Delta y_{\%}=100\frac{\Delta y}{|median(y_{early})|}
\]

## 4. Overlap và autocorrelation

Các window overlap dùng chung mẫu nên không độc lập. Vì vậy Day 11 không tạo p-value hoặc confidence interval. Split ML sau này phải theo subject/session trước windowing.
