# Windowing Result Contract v0.1

## 1. Mục đích
Tài liệu này định nghĩa cấu trúc Hợp đồng Dữ liệu (Data Contract) cho kết quả của quá trình Windowing, đảm bảo tạo ra một protocol-aligned window plan chính xác và mọi invalid window excluded khỏi dữ liệu tính toán. 

## 2. Output Data Structure
**Output có raw samples không?**
- **KHÔNG.** Output **không** chứa mảng raw samples.
- Hệ thống chỉ lưu **Index Plan** (`create_index_plan_only: true`). Nghĩa là chỉ trả về tọa độ `[start_index, end_index]` của các cửa sổ trên trục mảng dữ liệu đã nạp trong RAM. Không sao chép các mảng có overlap (`materialize_overlapping_windows: false`) để tránh nổ RAM.
- JSON Output chứa hình học cửa sổ (`include_geometry_in_json: true`), với window geometry verified on synthetic fixture, và trạng thái hợp lệ của cửa sổ đó (`include_validity_in_json: true`).
- Tính vẹn toàn của kết quả được bảo vệ bởi mã băm `sha256_canonical_json`.

## 3. Ý nghĩa của trạng thái "Completed"
**Completed có nghĩa gì?**
- **Completed** có nghĩa là bộ phân tích đã tìm thấy Phase thành công, đã thiết lập xong cấu trúc Index (tọa độ mảng) tạo thành protocol-aligned window plan cho cả hai Profile (Time Domain và Frequency Domain) tuân thủ đúng độ dài (L) và bước nhảy (H).
- Đồng thời đã đánh giá xong tính hợp lệ (`validity mask`) cho các cửa sổ đó và không bị vi phạm Rule chặn (Ví dụ: ít nhất vẫn còn 1 window hợp lệ trong mỗi profile), và mọi invalid window excluded hoàn toàn.
- Protocol Alignment Match đã thành công.

**Completed KHÔNG có nghĩa gì?**
- Không có nghĩa là 100% cửa sổ đều sạch (sẽ có cửa sổ bị đánh dấu invalid).
- Không có nghĩa là hệ thống đã sinh ra (materialized) các mảng 2D/3D (Tensors) vào bộ nhớ chứa tín hiệu. Khâu lấy (fetch) mảng vật lý sẽ do Feature Extraction Service tự đảm nhiệm từ Index Plan.
- Không có nghĩa là tín hiệu là hoàn hảo y tế, nó chỉ có nghĩa là pipeline lập trình chạy xong logic toán học.

## 4. Khế ước Hợp Lệ (Validity & Rejections)
- `WINDOWING_PROTOCOL_CONFIG_MISMATCH`: Chặn và huỷ bỏ (Plan=null) nếu Config `.yaml` không khớp với Protocol đang dùng, không được dùng config đè giao thức y tế ngầm.
- `NO_VALID_WINDOWS_REMAINING`: Chặn nếu sau khi loại bỏ lỗi, không còn window nào trên channel đó sống sót.
- `PHASE_NOT_FOUND`: Chặn nếu `active_contraction` phase không tồn tại.

## 5. Metadata bắt buộc đi kèm
Kết quả Windowing trả về ở JSON phải chứa cụm provenance sau để đảm bảo longitudinal comparision:
- `protocol_version`
- `preprocessing_config_id`
- `windowing_config_id`
- `windowing_plan_hash` (dùng SHA-256 canonical).
