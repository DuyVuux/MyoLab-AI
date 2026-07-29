# Signal-quality audit

Day 29 chỉ tạo **descriptive/engineering flags**. Không kết luận lâm sàng.

| Reason code | Ý nghĩa |
|---|---|
| `NONFINITE_PRESENT` | Có NaN/Inf |
| `FLATLINE_CANDIDATE` | Nhiều sample liên tiếp không đổi |
| `CONSTANT_CHANNEL` | Channel gần như hằng |
| `CLIPPING_CANDIDATE` | Nhiều giá trị chạm min/max observed |
| `SHORT_RECORD` | Record quá ngắn cho analysis đã định |
| `SAMPLING_RATE_CONFLICT` | Rate không nhất quán |
| `UNIT_CONFLICT` | Unit không nhất quán |
| `CHANNEL_COUNT_CONFLICT` | Số kênh mismatch |

Absolute amplitude threshold bị tắt vì unit, gain, protocol và electrode setup cần được chứng minh trước.
