# Ghi chú triển khai Day 12 — Fatigue Evidence Engine v0.1

- Engine chỉ chuyển trend thành structured observations.
- Threshold hiện tại là engineering defaults chưa được xác nhận lâm sàng.
- Output pattern không phải fatigue diagnosis/classification.
- Không probability, không FRS, không khuyến nghị dừng/tăng tải.
- Upstream fail phải tạo `abstained`; human review guard luôn được giữ.
