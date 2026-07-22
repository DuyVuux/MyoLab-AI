# Ghi chú logic mệnh đề

Bảng Logic (Decision Table):

| F | A | C | I | Output |
|---|---|---|---|---|
| 1 | 1 | 0 | 0 | supported_pattern |
| 1 | 0 | 0 | 0 | supported_pattern |
| 0 | 1 | 0 | 0 | inconclusive |
| * | * | 1 | * | inconclusive |
| * | * | * | 1 | inconclusive |
| 0 | 0 | 0 | 0 | no_supported_pattern |

**Giải thích vì sao amplitude-only (A=1, F=0) không đủ mạnh để đưa ra supported_pattern:**
- Biên độ (amplitude) phụ thuộc vào nhiều yếu tố nhiễu bên ngoài như lực co cơ, mức độ huy động đơn vị vận động (recruitment), hoặc thay đổi vị trí điện cực. Do đó, nếu chỉ có miền biên độ ủng hộ mà không có miền tần số, hệ thống sẽ đánh giá là `inconclusive` (chưa đủ bằng chứng đặc hiệu để kết luận).
