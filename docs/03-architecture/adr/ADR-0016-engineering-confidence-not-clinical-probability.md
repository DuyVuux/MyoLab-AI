# ADR-0016 — Engineering confidence không phải clinical probability

## Quyết định

Dùng weighted engineering confidence có component breakdown và prefix `engineering_`. Không gọi score là probability, sensitivity, certainty lâm sàng hoặc model confidence.

## Lý do

Chưa có local labels, calibration cohort hoặc clinical validation. Một weighted heuristic không có diễn giải xác suất hợp lệ.

## Hệ quả

Mọi UI/report phải hiển thị component breakdown, `not_calibrated` và human-review requirement.
