# Bổ sung nhật ký quyết định — Day 6

## Quyết định D6-01 — Kiểm chứng trước windowing

`preprocess_v0.1` phải vượt qua đáp ứng lý thuyết, empirical multi-tone, zero-phase, edge-effect và determinism checks trước khi được dùng làm input chuẩn cho windowing.

## Quyết định D6-02 — Freeze không đồng nghĩa xác nhận lâm sàng

Sau khi pass, config được ghi `analytically_verified_for_mvp0` trong registry. Trạng thái lâm sàng vẫn là `not_validated`.

## Quyết định D6-03 — Vùng bảo vệ biên là hợp đồng cho các bước sau

Windowing phải loại hoặc đánh dấu invalid mọi cửa sổ chạm vùng edge guard do preprocessing cung cấp.

## Quyết định D6-04 — Khả năng tái lập hai tầng

- Cùng environment: exact output hash.
- Khác environment: numerical tolerance + environment record; không giả định bitwise identity.

## External review required

- Xác nhận filter/config trên sample export thật từ Noraxon/Motion Lab.
- Xác nhận dải lọc phù hợp từng protocol/device tại pilot.
