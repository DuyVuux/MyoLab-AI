# Quyết định Ngày 4

| ID | Quyết định | Các giải pháp thay thế đã xem xét | Lý do | Bằng chứng | Trạng thái |
|---|---|---|---|---|---|
| D4-N01 | Dùng `Abstention` cho lỗi Flatline thay vì cố nội suy (interpolate). | Nội suy dữ liệu mất mát hoặc đệm số 0. | Nội suy trên sEMG dẫn đến sai số giả (artifacts) lớn ở các tần số cao. An toàn nhất là chặn (fail). | Khuyến nghị của chuẩn y tế. | PHÊ DUYỆT |
| D4-N02 | Chuyển cảnh báo 50Hz sang trạng thái `Warning` thay vì `Fail`. | Đánh dấu Fail tín hiệu. | Nhiễu 50Hz có thể lọc Notch ở bước tiền xử lý mà không làm hỏng hoàn toàn dải tần mỏi cơ. | Thử nghiệm trên Golden Data. | PHÊ DUYỆT |
