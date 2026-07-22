# ADR-0017 — Analysis package ngoại tuyến, versioned và publish nguyên tử

## Quyết định

MVP-0 dùng file-based offline orchestration. Output được ghi vào temporary directory; chỉ khi toàn bộ stage hoàn thành mới thay thế final directory.

## Lý do

- tránh để lại package nửa chừng;
- dễ audit và replay;
- phù hợp team một người và dữ liệu file export;
- chưa phụ thuộc DB, queue hoặc streaming infrastructure.

## Hệ quả

- near-real-time vẫn chỉ là demo wording;
- thay đổi stage/config phải cập nhật manifest/fingerprint;
- output directory không rỗng bị từ chối trừ khi dùng `--overwrite` có chủ đích.
