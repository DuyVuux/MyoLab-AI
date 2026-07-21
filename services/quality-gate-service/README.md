# Dịch vụ tiền xử lý sEMG — MVP-0

Dịch vụ này nhận `NormalizedSignal` đã qua Signal Quality Gate và tạo tín hiệu band-pass dạng `float64` theo cấu hình `preprocess_v0.1`.

## Guardrail

- Chỉ chạy khi `qc_result.analysis_allowed = true`.
- Không nội suy NaN/Inf.
- Không thay đổi timestamp, số mẫu, channel ID hoặc đơn vị `uV`.
- Dùng Butterworth 20–400 Hz dạng SOS và `sosfiltfilt` cho offline MVP.
- Notch 50 Hz chỉ chạy khi QC có `POWERLINE_NOISE_HIGH`.
- Không rectify hoặc tạo envelope trên đường tín hiệu dùng cho MDF/MNF.
- Không claim tương thích streaming hoặc clinical validation.

## Chạy thử

```bash
python -m pip install numpy scipy pyyaml jsonschema pytest
bash scripts/dev/run_day5_checks.sh
```