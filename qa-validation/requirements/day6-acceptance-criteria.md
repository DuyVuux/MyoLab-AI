# Tiêu chí nghiệm thu Day 6

## AC-D6-01 — Kiểm thử hồi quy

Day 5 tests phải pass trước kiểm chứng phân tích.

## AC-D6-02 — Đáp ứng lý thuyết

Tất cả criterion trong `preprocess_verification_v0.1.yaml` pass.

## AC-D6-03 — Kiểm chứng thực nghiệm đa tần

Gain đo bằng sinusoidal projection nằm trong tolerance được version hóa.

## AC-D6-04 — Pha bằng không

Impulse peak offset bằng 0 và normalized symmetry error không vượt tolerance.

## AC-D6-05 — Hành vi tại biên

Interior RMSE nhỏ và edge/interior ratio vượt threshold; edge guard vẫn tồn tại.

## AC-D6-06 — Tính xác định

Ba run trong cùng environment cho output hash giống nhau.

## AC-D6-07 — Contract

Verification JSON hợp lệ theo schema.

## AC-D6-08 — Freeze governance

Registry chỉ ghi status pass khi overall verification pass, và phải giữ `clinical_validation_status: not_validated`.

## AC-D6-09 — Wording

Không có claim diagnosis, realtime clinical hoặc universal filter validity.

## AC-D6-10 — Bàn giao

Có quyết định rõ `READY/NOT READY` cho Day 7 windowing.
