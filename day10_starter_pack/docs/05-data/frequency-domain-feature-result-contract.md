# Hợp đồng dữ liệu kết quả MDF/MNF v0.1

Kết quả cấp session dùng schema `frequency-feature-extraction-result.v0.1`.

Các trường trọng yếu:

- `session_id`;
- `status` và `downstream_allowed`;
- `config.config_id`;
- `inherited_spectral.result_hash_sha256`;
- `analysis_band`;
- `summary`;
- `rows[]`;
- `result_hash_sha256`;
- `limitations`.

`not_computed` là trạng thái hợp lệ, không được thay bằng số 0 hoặc nội suy.
