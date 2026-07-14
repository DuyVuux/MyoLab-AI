# Signal Import Specification — Generic CSV v0.1

**Status:** DRAFT  
**MVP phase:** MVP-0  
**Adapter:** `generic_csv_v0.1`  
**Repository path:** `docs/06-ai-signal-processing/signal-import-spec.md`

> **not approved for patient use**

---

## 1. Purpose

Tài liệu này định nghĩa contract cho việc import tín hiệu sEMG từ file CSV generic vào hệ thống phân tích. Nó quy định:

- format đầu vào (CSV + manifest JSON);
- quy tắc parsing và validation;
- unit normalization;
- cấu trúc normalized object sau import;
- hash semantics để đảm bảo traceability;
- các trường hợp import failure và hành vi tương ứng;
- scope v0.1 và những gì chưa hỗ trợ.

**Đối tượng implement:** developer viết adapter `generic_csv_v0.1`.

**Phạm vi MVP-0:** chỉ hỗ trợ Generic CSV export (comma-delimited, single sampling clock). Đây là bước đầu tiên để hỗ trợ Noraxon CSV export trong tương lai; Noraxon export file CSV mà adapter này có thể đọc nếu file tuân thủ contract bên dưới.

**Liên hệ với pipeline:** import là bước đầu tiên trong pipeline:

```text
Signal import → Signal validation → Preprocessing → Segmentation → Feature extraction → ...
```

Xem thêm: `docs/06-ai-signal-processing/signal-validation-spec.md` (downstream).

---

## 2. Input package

Một import package gồm **hai file** đặt cùng thư mục:

```text
<name>.csv                    # signal data
<name>.manifest.json          # metadata mô tả CSV
```

Quy tắc liên kết:

- Manifest phải chứa trường `signal_file` trỏ đến tên CSV tương ứng.
- CSV không có manifest → `IMPORT_REJECTED`.
- Manifest trỏ đến CSV không tồn tại → `IMPORT_REJECTED`.
- Manifest và CSV phải nằm trong cùng thư mục.

---

## 3. CSV contract

### 3.1. Encoding và format

| Property | Requirement |
|---|---|
| Encoding | UTF-8 |
| Delimiter | Comma (`,`) |
| Decimal separator | Period (`.`) |
| Header rows | Đúng 1 header row |
| Data rows | Một row trên mỗi sampling instant |
| Line ending | `\n` hoặc `\r\n` |

### 3.2. Time column

- Tên cột thời gian được khai báo trong manifest trường `time_column`.
- Nếu manifest không có `time_column`, adapter dùng `default_column` từ adapter config (mặc định: `time_s`).
- Nếu cả hai không có → `IMPORT_REJECTED`.
- Đơn vị: giây (s).
- Giá trị: numeric (float64).
- Timestamp phải tăng nghiêm ngặt (strictly increasing); adapter reject nếu vi phạm.

**Quy tắc precedence:**

```text
manifest.time_column → adapter-config.time.default_column → IMPORT_REJECTED
```

### 3.3. Signal columns

- Tên các cột signal được khai báo trong manifest trường `channels[].column`.
- Mỗi channel trong manifest phải có cột tương ứng trong CSV header; nếu thiếu → `IMPORT_REJECTED`.
- Mọi channel dùng chung sampling clock (shared sampling clock); adapter không hỗ trợ channel với sampling rate khác nhau trong v0.1.
- Giá trị signal: numeric (float64).

### 3.4. Xử lý giá trị đặc biệt

| Giá trị | Hành vi |
|---|---|
| Empty cell | Ghi nhận là `NaN`; đánh dấu cho QC |
| `NaN` | Giữ nguyên; đánh dấu cho QC |
| `Inf` / `-Inf` | Giữ nguyên; đánh dấu cho QC |
| Non-numeric trong cột signal | `IMPORT_REJECTED` |
| Non-numeric trong cột time | `IMPORT_REJECTED` |

Giá trị `NaN`/`Inf` không gây reject import nhưng phải được chuyển cho signal validation/QC downstream. Adapter config `allow_nonfinite_values_for_qc: true` kiểm soát hành vi này.

### 3.5. Privacy

CSV không được chứa trực tiếp thông tin nhận dạng cá nhân (PHI/PII). Adapter không tự phát hiện PHI trong CSV body, nhưng manifest phải không chứa các trường bị cấm (xem phần 4.5).

---

## 4. Manifest contract

### 4.1. Required fields

| Field | Type | Mô tả |
|---|---|---|
| `schema_version` | string | Version của manifest schema, ví dụ `"semg-session-manifest.v0.1"` |
| `session_id` | string | Unique identifier cho recording session |
| `data_source` | string enum | Nguồn dữ liệu |
| `signal_file` | string | Tên file CSV tương ứng |
| `sampling_rate_hz` | number > 0 | Sampling rate danh định (Hz) |
| `time_column` | string | Tên cột thời gian trong CSV |
| `protocol` | object | Protocol reference (xem 4.2) |
| `channels` | array (non-empty) | Channel mapping (xem 4.3) |
| `phase_markers` | array | Phase markers cho segmentation (xem 4.4) |
| `processing_history` | object | Lịch sử xử lý trước import (xem 4.6) |

### 4.2. Protocol reference

```json
{
  "id": "quad-isometric-60s",
  "version": "0.1.0"
}
```

- `id`: protocol ID từ protocol library (`docs/02-clinical/protocol-library.md`).
- `version`: semantic version của protocol.

Lưu ý: tên file protocol dùng shorthand (`quad-isometric-60s.v0.1.yaml`), nội dung protocol dùng semantic version (`0.1.0`). Validator phải kiểm tra cả hai cùng trỏ đến một protocol definition.

### 4.3. Channel mapping

Mỗi phần tử trong `channels`:

| Field | Type | Mô tả |
|---|---|---|
| `column` | string | Tên cột trong CSV header |
| `channel_id` | string | Unique channel identifier |
| `muscle` | string | Tên cơ mục tiêu (ví dụ `vastus_lateralis`) |
| `side` | string enum | `left` hoặc `right` |
| `unit` | string enum | Đơn vị signal: `uV`, `mV`, hoặc `V` |
| `role` | string enum | Vai trò kênh: `bipolar_semg` |

Ràng buộc:

- `channels` không được rỗng.
- `column` và `channel_id` không được trùng nhau giữa các channel.
- Muscle và side mapping đến từ manifest, không được suy đoán từ tên cột CSV (`infer_muscle_or_side_from_column_name: false`).

### 4.4. Phase markers

Mỗi phần tử trong `phase_markers`:

| Field | Type | Ràng buộc |
|---|---|---|
| `phase_id` | string | Tên phase (ví dụ `active_contraction`) |
| `start_s` | number | Thời điểm bắt đầu (giây) |
| `end_s` | number | Thời điểm kết thúc (giây); `end_s > start_s` |

Phase markers xác định các đoạn thời gian cho segmentation downstream. Phase `active_contraction` là phase dùng cho phân tích fatigue trong protocol `quad-isometric-60s` (xem `docs/02-clinical/protocol-library.md` section 3.3).

### 4.5. Privacy — forbidden manifest keys

Manifest không được chứa các trường sau (direct identifiers):

```text
patient_name, full_name, mrn, medical_record_number,
date_of_birth, dob, phone, email
```

Nếu phát hiện bất kỳ trường nào trong danh sách → `IMPORT_REJECTED`.

### 4.6. Processing history

```json
{
  "raw_export": true,
  "hardware_filter_known": false,
  "software_filter_applied": false
}
```

Trường `processing_history` là bắt buộc (adapter config: `require_processing_history: true`). Nó giúp preprocessing downstream biết tín hiệu đã qua bước xử lý nào trước khi import.

### 4.7. Optional fields

| Field | Type | Mô tả |
|---|---|---|
| `fixture_type` | string | `"format_only"` cho test fixture |
| `analysis_ready` | boolean | `false` nếu chưa đủ điều kiện phân tích |
| `notes` | string | Ghi chú tự do cho fixture/session |

---

## 5. Unit normalization

Adapter chuẩn hóa mọi signal về đơn vị canonical `uV` (microvolt) trước khi đưa vào normalized object.

| Source unit | Conversion | Formula |
|---|---|---|
| `uV` | Identity | `x_uV = x` |
| `mV` | Millivolt → Microvolt | `x_uV = x × 1,000` |
| `V` | Volt → Microvolt | `x_uV = x × 1,000,000` |

Quy tắc:

- Đơn vị nguồn phải được khai báo trong manifest (`channels[].unit`).
- Đơn vị phải nằm trong danh sách `supported_units` của adapter config.
- Unit không được suy đoán từ biên độ signal.
- Unit không hỗ trợ → `IMPORT_REJECTED`.
- Sau normalization, `source_unit` gốc phải được giữ lại trong normalized object để truy vết.

---

## 6. Canonical normalized object

Sau khi import thành công, adapter tạo một normalized object với cấu trúc sau:

```json
{
  "schema_version": "normalized-signal.v0.1",
  "session_id": "SYNTH_D2_FORMAT_001",
  "sampling_rate_hz": 1000.0,
  "time_s": "array<float64>",
  "channels": {
    "VL_R_01": {
      "samples_uV": "array<float64>",
      "muscle": "vastus_lateralis",
      "side": "right",
      "source_unit": "uV"
    }
  },
  "protocol_ref": {
    "id": "quad-isometric-60s",
    "version": "0.1.0"
  },
  "phase_markers": [
    {
      "phase_id": "active_contraction",
      "start_s": 0.0,
      "end_s": 1.0
    }
  ],
  "processing_history": {
    "raw_export": true,
    "hardware_filter_known": false,
    "software_filter_applied": false
  },
  "adapter_ref": {
    "id": "generic_csv_v0.1"
  },
  "source_file": "sample_file.csv",
  "source_hash_sha256": "<hex string>"
}
```

**Các trường bắt buộc trong normalized object:**

| Field | Nguồn |
|---|---|
| `schema_version` | Hardcoded `"normalized-signal.v0.1"` |
| `session_id` | Từ manifest |
| `sampling_rate_hz` | Từ manifest, đã validate |
| `time_s` | Parsed từ CSV |
| `channels` | Parsed từ CSV + mapping từ manifest |
| `channels[].samples_uV` | Signal đã normalize về uV |
| `channels[].source_unit` | Unit gốc từ manifest |
| `protocol_ref` | Từ manifest `protocol` |
| `phase_markers` | Từ manifest `phase_markers` |
| `processing_history` | Từ manifest `processing_history` |
| `adapter_ref.id` | Từ adapter config `adapter_id` |
| `source_file` | Tên file CSV nguồn |
| `source_hash_sha256` | SHA-256 của CSV (xem section 7) |

---

## 7. Hash semantics

```text
source_hash_sha256 = SHA-256 trên raw bytes của file CSV trước mọi normalization
```

Quy tắc:

- Hash được tính trên toàn bộ nội dung file CSV nguyên gốc (raw bytes), bao gồm header, BOM nếu có, và line endings.
- Hash được tính **trước** khi adapter parse hoặc normalize bất kỳ giá trị nào.
- Hash cho phép xác minh rằng file CSV không bị thay đổi sau import.
- Nếu cần hash cho toàn bộ bundle (CSV + manifest), sử dụng trường riêng biệt `import_bundle_hash_sha256` (chưa yêu cầu trong v0.1).

---

## 8. Import failure behavior

### 8.1. Outcome categories

| Outcome | Mô tả | Ví dụ |
|---|---|---|
| `IMPORT_REJECTED` | Không thể đọc hoặc parse; import dừng ngay | JSON lỗi, CSV thiếu, time không numeric |
| `FORMAT_VALID_BUT_PROTOCOL_INCOMPATIBLE` | Đọc được, metadata đúng format, nhưng không thỏa protocol | Active phase chỉ có 1 giây (fixture `SYNTH_D2_FORMAT_001`) |
| `IMPORTED_PENDING_QC` | Import thành công, chờ signal validation/QC | File đọc được và metadata đầy đủ |
| `QC_FAIL` | Signal validation phát hiện vấn đề chất lượng | Clipping, nhiễu, dropout nghiêm trọng |
| `QC_PASS` | Signal đạt chất lượng, được phép đi tiếp | Tất cả signal quality checks pass |

Lưu ý: `QC_FAIL` và `QC_PASS` thuộc phạm vi `signal-validation-spec.md`, không phải import adapter. Import adapter chỉ chịu trách nhiệm đến `IMPORTED_PENDING_QC` hoặc reject trước đó.

### 8.2. Import rejection rules

Adapter phải reject import (`IMPORT_REJECTED`) khi:

| Điều kiện | Lý do |
|---|---|
| Manifest không tồn tại hoặc không đi kèm CSV | Thiếu metadata |
| Manifest JSON không hợp lệ (parse error) | Không đọc được metadata |
| CSV không tồn tại (manifest trỏ sai `signal_file`) | Thiếu signal data |
| CSV header trùng tên cột | Ambiguous column mapping |
| CSV header thiếu cột mà manifest channel tham chiếu | Channel không có signal |
| Timestamp không phải numeric | Không xác định được thời gian |
| Timestamp không tăng nghiêm ngặt | Vi phạm shared sampling clock |
| Signal column chứa giá trị non-numeric | Data corruption |
| Unit trong manifest không thuộc `supported_units` | Không normalize được |
| Manifest chứa forbidden key (PHI/PII) | Vi phạm privacy |
| Manifest thiếu required field | Metadata không đủ |
| `channels` rỗng | Không có signal nào |
| `sampling_rate_hz` ≤ 0 | Sampling rate không hợp lệ |

### 8.3. Protocol incompatibility (non-blocking import)

Sau import thành công, protocol validation kiểm tra:

- Active duration so với protocol requirement (`active_contraction` = 60 s cho `quad-isometric-60s`).
- Nếu không đạt → `FORMAT_VALID_BUT_PROTOCOL_INCOMPATIBLE` với reason code phù hợp.

Ví dụ với fixture `SYNTH_D2_FORMAT_001`:

```json
{
  "format_validation": "pass",
  "protocol_validation": "fail",
  "expected_reason_code": "ACTIVE_DURATION_TOO_SHORT"
}
```

Fixture này có `analysis_ready: false` nên hệ thống không được chạy preprocessing, feature extraction, hoặc inference trên nó.

### 8.4. Sampling rate validation

Adapter kiểm tra sampling rate ước lượng từ CSV (dựa trên khoảng cách timestamp thực tế) so với `sampling_rate_hz` trong manifest:

```text
|Fs_estimated - Fs_declared| / Fs_declared ≤ tolerance
```

Tolerance: `0.01` (1%), từ adapter config `sampling_rate_relative_tolerance`.

Nếu vượt tolerance → `IMPORT_REJECTED`.

---

## 9. Scope exclusions — v0.1 chưa hỗ trợ

Các khả năng sau **nằm ngoài phạm vi** v0.1 và không được implement trong adapter `generic_csv_v0.1`:

| Exclusion | Lý do |
|---|---|
| Proprietary Noraxon binary format | Chỉ hỗ trợ CSV export |
| Channel với sampling rate khác nhau | `shared_sampling_clock_required: true` |
| Irregular sampling (non-uniform dt) | Yêu cầu `strict_monotonic` và uniform |
| Các format khác: C3D, MAT, EDF, BDF | Ngoài scope adapter CSV |
| Real-time streaming | MVP-0 chỉ hỗ trợ offline file import |
| Tự suy đoán muscle/side từ tên cột CSV | `infer_muscle_or_side_from_column_name: false` |
| MFCV từ single bipolar channel | MFCV yêu cầu linear electrode array ≥ 3 kênh (xem `docs/02-clinical/protocol-library.md` section 6) |
| Multi-file session (nhiều CSV cho một session) | Một manifest → một CSV |
| Automatic PHI detection trong CSV body | Chỉ kiểm tra manifest keys |

---

## 10. Related artifacts

```text
integrations/devices/generic-csv/adapter-config.yaml
integrations/devices/generic-csv/sample_file.manifest.json
integrations/devices/generic-csv/sample_file.csv
docs/02-clinical/protocol-library.md
docs/06-ai-signal-processing/signal-validation-spec.md
docs/06-ai-signal-processing/preprocessing-spec.md
docs/06-ai-signal-processing/feature-extraction-spec.md
```
