# Ghi chú toán — Normalization

## Mean

\[
ar{x}=rac{1}{N}\sum_{n=1}^{N}x[n]
\]

## Variance

\[
s^2=rac{1}{N-1}\sum_{n=1}^{N}(x[n]-ar{x})^2
\]

## Z-score

\[
z[n]=rac{x[n]-\mu}{\sigma}
\]

Phải xác định rõ \(\mu,\sigma\) được fit từ đâu. Trong ML hợp lệ, chúng chỉ đến từ training fold.
