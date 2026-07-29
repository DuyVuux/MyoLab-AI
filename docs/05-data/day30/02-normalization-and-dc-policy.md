# Chính sách DC và normalization

## Quyết định

- DC removal offline primary: trừ mean theo từng record và từng kênh.
- Không raw z-score per trial cho primary.
- Không dùng global full-dataset statistics.
- Feature scaler chỉ fit trong inner-train fold.
- `none` là comparator bắt buộc.
- z-score và robust scaler là optional arms.
- Day 30 không định nghĩa lại band-pass filter.

## Vì sao

Biên độ khác nhau giữa hai thiết bị là domain gap thật. Ép tất cả tín hiệu về unit variance trước split sẽ che gap và có thể gây leakage.

## Toán

\[
x'_c[n]=x_c[n]-rac{1}{N}\sum_{n=1}^{N}x_c[n]
\]

Feature z-score:

\[
z_j=rac{f_j-\mu_{j,	ext{inner-train}}}{\sigma_{j,	ext{inner-train}}}
\]
