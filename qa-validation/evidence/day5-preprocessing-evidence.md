# Evidence Day 5 — Preprocessing v0.1

## Môi trường

- Python: 3.12.3
- NumPy: 2.5.1
- SciPy: 1.18.0
- Commit: 647e7d8c7b5a16d3d8ce4fd64923326800d5b5f9

## Kết quả

- Unit tests: 11/11 tests (10 core, 1 orchestration) PASS (100% coverage).
- Integration tests: 3/3 E2E Scenarios (Golden, Powerline, Flatline) PASS.
- Frequency response verification: Notch filter bảo toàn tín hiệu 80Hz (>95%) và triệt tiêu triệt để nhiễu 50Hz (<10% amplitude). Butterworth chặn tốt các tần số ngoài 20-400Hz.
- Golden result hash: 9db4765134e90e9db29fa6877c86af85ea074375e2d0a443d2ef68f8faeef0c5 (Hoàn toàn tất định, chạy 2 lần ra cùng 1 hash).
- Powerline fixture notch status: Kích hoạt đúng trạng thái `applied` khi `inherited_qc` chứa `POWERLINE_NOISE_HIGH`.
- QC-fail fixture block status: Preprocessing trả về `blocked`, không chạy bộ lọc, `signal` bằng `null`, ghi nhận `PREPROCESSING_BLOCKED_BY_QC`.
- JSON schema validation: 3/3 tệp output hoàn toàn khớp chuẩn `preprocessing-result.schema.json`.

## Giới hạn

- Synthetic-only.
- Chưa kiểm tra Noraxon export thật.
- Chưa clinical validation.
- Chưa causal/near-real-time.
