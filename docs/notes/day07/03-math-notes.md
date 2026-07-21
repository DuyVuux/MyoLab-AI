# Day 7: Math Notes

## 1. 3 điểm đã hiểu
- **Chiều dài cửa sổ (L - Length):** Được tính chính xác bằng công thức $L = (\text{duration\_ms} \times F_s) / 1000$. Ví dụ $500 \times 1000 / 1000 = 500$ mẫu.
- **Bước nhảy (H - Hop Length):** Xác định khoảng cách tịnh tiến của mỗi cửa sổ: $H = L \times (1 - \text{overlap\_fraction})$.
- **Tổng số cửa sổ (K):** Số cửa sổ tối đa nằm gọn trong một phase (độ dài N) là $K = \lfloor(N - L)/H\rfloor + 1$.

## 2. 1 điểm chưa chắc
- Với cấu hình `sample_rounding_policy: exact_integer_required`, nếu một thiết bị có $F_s$ lẻ (ví dụ 1024 Hz), phép nhân có thể ra phần thập phân dẫn đến lỗi chặn (block) toàn bộ phân tích nếu không có hàm làm tròn phù hợp ở preprocessing.

## 3. Giới hạn / Assumption
- **Giới hạn:** Do `allow_partial_final_window: false`, đoạn dữ liệu lẻ cuối cùng của pha (nhỏ hơn L) sẽ bị vứt bỏ, làm mất lượng nhỏ dữ liệu gốc tại biên cuối của đồ thị.

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Tham vấn kỹ sư toán / DSP về chiến lược nội suy hoặc padding hợp lý hơn cho các pha mỏi cơ khi cửa sổ bị lẻ số lượng phân tách.
