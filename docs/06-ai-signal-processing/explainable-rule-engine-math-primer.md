# Nền tảng logic cho Explainable Rule Engine v0.1

## 1. Rule engine là gì?

Rule engine là tập các luật xác định trước để ánh xạ đầu vào có cấu trúc sang một kết luận kỹ thuật. Day 13 không huấn luyện mô hình và không ước lượng xác suất.

```text
FatigueEvidenceResult
→ pattern category
→ decision table
→ technical conclusion
```

## 2. Logic mệnh đề tối thiểu

Ký hiệu:

- `F`: miền tần số hỗ trợ;
- `A`: miền biên độ hỗ trợ;
- `C`: có bằng chứng mâu thuẫn;
- `I`: dữ liệu không đủ.

Ví dụ rule bảo thủ:

```text
F ∧ A ∧ ¬C ∧ ¬I → supported_pattern
F ∧ ¬A ∧ ¬C ∧ ¬I → supported_pattern mức vừa
A ∧ ¬F             → inconclusive
C ∨ I               → inconclusive
¬F ∧ ¬A ∧ ¬C ∧ ¬I → no_supported_pattern
```

`no_supported_pattern` không có nghĩa là `no_fatigue`. Nó chỉ có nghĩa dữ liệu đủ điều kiện nhưng chưa đáp ứng rule v0.1.

## 3. Decision table

| Pattern Day 12 | Kết luận Day 13 | Lý do |
|---|---|---|
| `multi_domain_change_pattern_observed` | `supported_pattern` | Hai domain đồng thuận |
| `frequency_decline_pattern_observed` | `supported_pattern` | Miền tần số hỗ trợ, amplitude không bắt buộc |
| `amplitude_increase_pattern_observed` | `inconclusive` | Amplitude không đặc hiệu |
| `partial_change_pattern_observed` | `inconclusive` | Chưa đủ feature đồng thuận |
| `evidence_mixed_or_opposite` | `inconclusive` | Có mâu thuẫn |
| `insufficient_evidence` | `inconclusive` | Chất lượng/độ dài trend chưa đủ |
| `no_predefined_change_pattern_observed` | `no_supported_pattern` | Không đạt magnitude kỹ thuật tạm thời |

## 4. Thứ tự ưu tiên an toàn

```text
1. Upstream abstained?
   Có → abstained

2. Contract/version mismatch?
   Có → abstained

3. Có ít nhất một channel evaluated?
   Không → abstained

4. Ánh xạ từng channel

5. Tổng hợp đa channel
   Không đồng thuận → inconclusive
```

## 5. Vì sao không dùng xác suất?

Một rule deterministic không tự sinh ra xác suất. Con số `0.8` chỉ trở thành xác suất khi có định nghĩa thống kê, dữ liệu hiệu chỉnh và đánh giá calibration phù hợp. Day 13 không có các điều kiện đó.

## 6. Bài tập tự làm

1. Lập truth table cho `F`, `A`, `C`, `I`.
2. Giải thích vì sao `A=true`, `F=false` không nên thành `supported_pattern` mạnh.
3. Giải thích khác biệt giữa `no_supported_pattern` và `abstained`.
4. Thiết kế một ví dụ hai channel không đồng thuận và giải thích vì sao tổng hợp thành `inconclusive`.
