# Contract dữ liệu Spectral Estimation Result v0.1

## 1. Mục đích

Contract này mô tả artifact trung gian giữa `Windowing v0.1` và MDF/MNF. Artifact chỉ chứa PSD/metadata/provenance, không chứa raw signal và không chứa kết luận lâm sàng.

## 2. Cấu trúc cấp result

```json
{
  "schema_version": "spectral-estimation-result.v0.1",
  "session_id": "SYNTH_D3_GOLDEN_001",
  "status": "completed",
  "downstream_allowed": true,
  "config": {
    "config_id": "spectral_estimation_v0.1",
    "profile_id": "frequency_domain",
    "canonical_amplitude_unit": "uV",
    "psd_unit": "uV^2/Hz",
    "mdf_mnf_computed": false
  },
  "frequency_axis": {},
  "estimator": {},
  "summary": {},
  "rows": [],
  "limitations": []
}
```

## 3. Status

| Status | Ý nghĩa |
|---|---|
| `completed` | Tất cả spectral windows hợp lệ đã được tính |
| `completed_with_exclusions` | Có ít nhất một window `not_computed` |
| `blocked` | Upstream không cho phép hoặc không có row nào tính được |

`blocked` luôn có:

```text
downstream_allowed = false
rows = []
frequency_axis = null
result_hash_sha256 = null
```

## 4. Shared frequency axis

Frequency axis được lưu một lần:

```json
{
  "values": [20.0, 21.0, 22.0],
  "unit": "Hz",
  "bin_count": 381,
  "lower_hz": 20.0,
  "upper_hz": 400.0,
  "bin_spacing_hz": 1.0,
  "rayleigh_resolution_hz": 1.0
}
```

Mọi computed row phải có PSD array cùng độ dài với `bin_count`.

## 5. Spectral row

```json
{
  "schema_version": "spectral-window-row.v0.1",
  "spectral_row_id": "SR-...",
  "session_id": "...",
  "channel": {
    "channel_id": "VL_R_01",
    "muscle": "vastus_lateralis",
    "side": "right",
    "role": "bipolar_semg"
  },
  "phase_id": "active_contraction",
  "profile_id": "frequency_domain",
  "window": {
    "window_id": "...",
    "window_index": 0,
    "start_sample": 5000,
    "end_sample_exclusive": 6000,
    "start_time_s": 5.0,
    "end_time_exclusive_s": 6.0,
    "center_time_s": 5.5,
    "sample_count": 1000
  },
  "status": "computed",
  "spectral": {},
  "reason_codes": [],
  "provenance": {}
}
```

## 6. Spectral payload

```json
{
  "psd": {
    "values": [],
    "unit": "uV^2/Hz"
  },
  "band_power": {
    "value": 1000.0,
    "unit": "uV^2"
  },
  "full_power": {
    "value": 1010.0,
    "unit": "uV^2"
  },
  "time_domain_variance": {
    "value": 1005.0,
    "unit": "uV^2"
  },
  "window_weighted_power": {
    "value": 1010.0,
    "unit": "uV^2"
  },
  "parseval_ratio": 1.0,
  "qa_flags": [],
  "peak_frequency": {
    "value": 80.0,
    "unit": "Hz",
    "purpose": "qa_only_not_fatigue_feature"
  }
}
```

## 7. `not_computed` row

```text
status = not_computed
spectral = null
reason_codes có ít nhất một phần tử
```

Các reason code chính:

- `WINDOW_CONTAINS_INVALID_SAMPLE` hoặc reason upstream;
- `SPECTRAL_POWER_TOO_LOW`;
- `SPECTRAL_COMPUTATION_FAILED`;
- `SPECTRAL_FREQUENCY_AXIS_MISMATCH`.

## 8. Provenance

Bắt buộc:

- `spectral_estimator_id`;
- `windowing_config_id`;
- `preprocess_config_id`;
- `source_signal_hash_sha256`;
- `window_plan_hash_sha256`.

## 9. Privacy

Không được có:

- raw signal samples;
- tên bệnh nhân;
- MRN;
- email/số điện thoại;
- fatigue diagnosis;
- treatment recommendation.

## 10. Lưu trữ MVP-0 và tương lai

MVP-0 lưu PSD array trong JSON để dễ kiểm chứng. Khi dữ liệu tăng, có thể chuyển PSD arrays sang Parquet/NPZ/object storage và chỉ giữ reference/hash trong result. Thay đổi này phải tạo schema/version mới.
