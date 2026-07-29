# Ghi chú toán Day 29

## Median

Giá trị nằm giữa sau khi sắp xếp; bền vững trước outlier hơn mean.

## MAD

```text
MAD = median(|x - median(x)|)
```

## Robust shift

```text
(median_B - median_A) / (1.4826 * pooled_MAD + epsilon)
```

Không phải p-value và không cho biết nguyên nhân.

## Ratio

```text
median_B / (median_A + epsilon)
```

Cần cảnh giác khi mẫu số gần 0 hoặc hai ngày khác unit/gain.
