# Protocol Library — sEMG Fatigue Assessment

**Document ID:** `DOC-CLINICAL-PROTOCOL-LIBRARY`  
**Document version:** `0.1.0`  
**Repository path:** `docs/02-clinical/protocol-library.md`  
**Status:** Draft for technical development and external clinical review  
**Applies to:** MVP-0 offline technical feasibility  
**Protocol owner:** Project Owner / Biomedical Signal Processing Lead  
**Required external reviewers:** Clinical Lead, Motion Lab/KTV representative  

> **not approved for patient use**

---

## 1. Purpose

Tài liệu này định nghĩa thư viện protocol tối thiểu cho nền tảng phân tích mỏi cơ dựa trên sEMG. Mục tiêu là chuẩn hóa ngữ cảnh thu nhận và phân tích để mọi kết quả đều truy vết được về:

- protocol ID và version;
- cơ mục tiêu và bên cơ thể;
- loại co cơ và thời lượng active;
- yêu cầu dữ liệu đầu vào;
- feature được phép tính;
- điều kiện tương thích khi so sánh dọc;
- giới hạn của MFCV/CV;
- trạng thái review lâm sàng.

Tài liệu này **không phải** hướng dẫn điều trị, đơn tập, SOP thu dữ liệu lâm sàng đã được phê duyệt hoặc hướng dẫn sử dụng thiết bị cho người bệnh. Phần mềm không phát hành chỉ dẫn điều trị, tăng/giảm tải, dừng bài tập hoặc quyết định return-to-play.

---

## 2. Protocol registry

| Field | Value |
|---|---|
| Protocol ID | `quad-isometric-60s` |
| Protocol version | `0.1.0` |
| Display name | Quadriceps sustained isometric 60-second protocol |
| Status | `draft_technical_demo_only` |
| Target muscle | `vastus_lateralis` |
| Body side | Session parameter: `left`, `right`, hoặc convention đã định nghĩa |
| Contraction type | `isometric` |
| Active duration | `60 s` |
| Intended MVP use | Synthetic/offline pipeline development và verification |
| Clinical approval | Required; current status: `not_reviewed` |
| Basic sEMG channel requirement | Tối thiểu 1 kênh hợp lệ |
| Raw signal requirement | Có |
| Minimum sampling rate | `1000 Hz` |
| Preferred sampling rate | `2000 Hz` |
| MFCV required | Không |

Protocol machine-readable tương ứng:

```text
clinical/protocols/quad-isometric-60s.v0.1.yaml
```

Schema kiểm tra cấu trúc:

```text
clinical/protocols/protocol-schema.json
```

---

## 3. Protocol definition

### 3.1. Target muscle

Protocol v0.1 xác định cơ mục tiêu là:

```text
vastus_lateralis
```

Việc lựa chọn cơ này trong MVP-0 chỉ nhằm tạo một protocol chuẩn hóa cho phát triển kỹ thuật. Các nội dung sau chưa được coi là phê duyệt lâm sàng:

- chỉ định đối tượng;
- bên cần đo;
- mốc giải phẫu và vị trí điện cực;
- điều kiện da và chuẩn bị người tham gia;
- mức lực mục tiêu;
- tiêu chí loại trừ;
- tiêu chí kết thúc thu nhận.

Những nội dung trên phải được xác nhận bởi Clinical Lead và Motion Lab/KTV trước khi chuyển protocol sang trạng thái `draft_clinical_review` hoặc `approved`.

### 3.2. Contraction type

Loại co cơ:

```text
isometric
```

Trong protocol này, `isometric` mô tả task giữ co cơ trong một khoảng thời gian đã định nghĩa. Nó không tự động xác nhận rằng lực được giữ ổn định. Nếu có force signal đồng bộ, dữ liệu lực nên được lưu để kiểm tra protocol adherence; nếu không có, giới hạn này phải được ghi trong kết quả phân tích.

### 3.3. Protocol phases

| Phase | Duration | Required | Analysis use |
|---|---:|---:|---|
| `baseline_rest` | 5 s | Có | Ước lượng nền và kiểm tra chất lượng ban đầu |
| `active_contraction` | 60 s | Có | Pha chính để windowing và trích xuất feature |
| `recovery` | 5 s | Không | Chỉ lưu phục vụ review; chưa dùng cho fatigue score v0.1 |

`active_contraction` là phase duy nhất được dùng cho phân tích fatigue evidence trong MVP-0.

### 3.4. Effort metadata

Protocol yêu cầu session cung cấp:

```text
target_mvc_percent
```

Giá trị `30% MVC` trong fixture hoặc synthetic demo chỉ là mặc định kỹ thuật. Giá trị này chưa được phê duyệt cho thu dữ liệu người bệnh và không được trình bày như mức lực khuyến nghị.

---

## 4. Supported features

Nếu Signal Quality Gate trả `pass` hoặc mức `warning` được policy cho phép tiếp tục, protocol v0.1 hỗ trợ các feature sau:

| Feature | Domain | Unit/output | Role |
|---|---|---|---|
| RMS | Time domain | Theo đơn vị signal sau chuẩn hóa | Mô tả mức biên độ/hoạt hóa theo window |
| MAV | Time domain | Theo đơn vị signal sau chuẩn hóa | Mô tả biên độ tuyệt đối trung bình |
| MDF | Frequency domain | Hz | Tần số chia phổ công suất thành hai phần bằng nhau |
| MNF | Frequency domain | Hz | Trung bình có trọng số theo power spectrum |
| RMS slope | Trend | Feature unit/s hoặc normalized unit/s | Xu hướng biên độ theo thời gian |
| MDF slope | Trend | Hz/s | Xu hướng dịch phổ theo thời gian |
| MNF slope | Trend | Hz/s | Xu hướng dịch phổ theo thời gian |

Windowing mặc định:

```text
time-domain window:      500 ms
frequency-domain window: 1000 ms
overlap:                  50%
```

Các giá trị này là cấu hình MVP-0 để phát triển và verification. Mọi analysis run phải lưu:

- protocol version;
- preprocessing config version;
- feature extractor version;
- windowing parameters;
- signal unit;
- sampling rate;
- processing history.

Protocol này chưa phê duyệt threshold lâm sàng cho fatigue onset, fatigue severity hoặc Fatigue Resistance Score.

---

## 5. Signal and metadata requirements

### 5.1. Required session metadata

Một session phải có tối thiểu:

```text
session_id
data_source
sampling_rate_hz
protocol_id
protocol_version
target_muscle
side
target_mvc_percent
channel_map
signal_unit
phase_markers
processing_history
```

Thiếu metadata bắt buộc phải dẫn tới một trong hai kết quả:

- `blocked`: không thể xác định đúng protocol hoặc không thể phân tích an toàn;
- `warning`: dữ liệu có thể xử lý kỹ thuật nhưng giới hạn phải được ghi rõ.

### 5.2. Input boundary

Input ưu tiên cho MVP-0:

```text
Motion Lab / Noraxon export / Synthetic CSV
```

Synthetic CSV không được dùng làm bằng chứng hiệu năng lâm sàng và không được so sánh dọc với session người thật.

---

## 6. MFCV/CV boundary

### 6.1. Eligibility requirements

MFCV/CV chỉ được phép tính khi xác nhận đủ các điều kiện:

```text
linear electrode array
+ known inter-electrode distance
+ orientation along muscle fibres
+ at least 3 suitable adjacent channels
+ sampling rate >= 1000 Hz
+ adjacent-channel quality acceptable
```

Ngưỡng tương quan kênh lân cận `0.75` chỉ được lưu như **research reference** và chưa phải threshold đã được xác nhận cho vận hành lâm sàng.

### 6.2. Failure behavior

Nếu không đủ điều kiện MFCV/CV, hệ thống phải trả:

```json
{
  "mfcv": {
    "eligible": false,
    "status": "not_eligible",
    "reason_codes": [
      "MFCV_REQUIRED_ELECTRODE_GEOMETRY_NOT_CONFIRMED"
    ]
  }
}
```

**MFCV failure hoặc `not_eligible` không block basic sEMG analysis.**

Basic sEMG analysis vẫn được tiếp tục khi:

- Signal Quality Gate cho phép;
- active phase đủ dữ liệu;
- sampling rate phù hợp với feature cơ bản;
- metadata bắt buộc đầy đủ;
- RMS, MAV, MDF và MNF có thể được tính hợp lệ.

MFCV chỉ block khi một use case hoặc analysis profile được cấu hình rõ là `mfcv_required`. Protocol v0.1 không đặt yêu cầu đó.

---

## 7. Compatibility rules

### 7.1. Within-session compatibility

Các kênh trong cùng session chỉ được tổng hợp khi:

- cùng sampling timeline hoặc đã được đồng bộ hợp lệ;
- đơn vị đo đã được chuẩn hóa;
- channel map xác định được cơ và vị trí;
- cùng active phase;
- không thuộc nhóm bad channel đã bị loại;
- cùng preprocessing và feature configuration.

### 7.2. Longitudinal compatibility

Hai session chỉ được so sánh longitudinal khi thỏa **tất cả** điều kiện tối thiểu:

```text
same protocol family
same target muscle
same body-side convention
compatible device and signal units
same or explicitly compatible sampling configuration
same preprocessing version
same feature extractor version
compatible windowing configuration
comparable effort metadata
valid phase markers
```

Rule bắt buộc:

> Nếu một trong các điều kiện compatibility cốt lõi không đạt, hệ thống phải trả `not_comparable` và không tính phần trăm cải thiện, suy giảm hoặc trend lâm sàng.

Ví dụ output:

```json
{
  "longitudinal_comparison": {
    "status": "not_comparable",
    "reason_codes": [
      "PREPROCESSING_VERSION_MISMATCH",
      "EFFORT_METADATA_NOT_COMPARABLE"
    ]
  }
}
```

Các version khác nhau chỉ được coi là tương thích khi có compatibility matrix được review, test và version hóa. Không được tự suy luận rằng hai version là tương đương.

### 7.3. Prohibited comparisons

Không thực hiện longitudinal comparison giữa:

- synthetic session và patient/pilot session;
- hai cơ khác nhau;
- hai loại co cơ khác nhau;
- hai protocol không cùng family;
- session thiếu phase marker đáng tin cậy;
- session dùng feature definitions khác nhau mà chưa có compatibility evidence;
- session bị QC fail.

---

## 8. Quality gate and abstention

Protocol không thay thế `signal-validation-spec.md` hoặc cấu hình `qc_v0.1.yaml`. Nó chỉ định rằng QC phải chạy trước feature extraction.

Các trường hợp phải block analysis gồm tối thiểu:

- active duration không đủ;
- sampling rate dưới mức protocol cho phép;
- signal file hỏng hoặc không đọc được;
- active phase không xác định;
- dropout nghiêm trọng;
- clipping/saturation nghiêm trọng;
- metadata cốt lõi thiếu;
- usable window ratio dưới ngưỡng QC được version hóa.

Khi block, output phải là:

```text
abstained / data not eligible for analysis
```

Không được chuyển QC failure thành kết luận “không mỏi”.

---

## 9. Clinical review debt

Protocol v0.1 còn các khoản review debt sau trước khi có thể xem xét dùng trong pilot:

| Review debt | Required reviewer | Exit evidence |
|---|---|---|
| Xác nhận cơ mục tiêu và intended population | Clinical Lead | Biên bản review và protocol revision |
| Xác nhận electrode placement và channel mapping | Motion Lab/KTV + Signal Lead | Placement guide đã duyệt |
| Xác nhận mức effort/MVC và cách đo lực | Clinical Lead + Motion Lab | SOP hoặc protocol appendix |
| Xác nhận active duration và phase definitions | Clinical Lead | Approval record |
| Xác nhận minimum sampling rate theo thiết bị thật | Signal Lead + Motion Lab | Technical audit evidence |
| Xác nhận QC thresholds | Signal Lead + QA + Clinical reviewer | Golden tests và pilot evidence |
| Xác nhận MFCV eligibility trên cấu hình Noraxon | Motion Lab + Signal Lead | Hardware/electrode audit |
| Xác nhận report wording | Clinical Lead | Approved phrase library |
| Xác nhận stop criteria thuộc SOP bên ngoài | Clinical governance owner | External SOP reference |
| Xác nhận longitudinal compatibility tolerance | Signal Lead + Clinical Lead | Compatibility matrix |
| Xác nhận consent, privacy và data handling | Site governance/security | Approved data workflow |
| Xác nhận protocol repeatability | QA/Validation + Motion Lab | Repeatability report |

Protocol chỉ được đổi status khi có evidence:

```text
draft_technical_demo_only
    -> draft_clinical_review
    -> approved
```

Không được bỏ qua bước review bằng cách đổi trực tiếp file YAML.

---

## 10. Versioning and change control

Mọi thay đổi ảnh hưởng đến phép đo hoặc cách diễn giải phải tạo version mới, bao gồm:

- target muscle;
- contraction type;
- active duration;
- effort definition;
- acquisition requirement;
- phase definition;
- windowing;
- supported feature;
- MFCV eligibility;
- longitudinal compatibility rule;
- QC dependency;
- report wording boundary.

Quy ước:

```text
quad-isometric-60s.v0.1.yaml
quad-isometric-60s.v0.2.yaml
quad-isometric-60s.v1.0.yaml
```

- Patch/minor draft: thay đổi kỹ thuật chưa dùng lâm sàng.
- Major version: thay đổi làm mất compatibility hoặc protocol đã được phê duyệt chính thức.
- Mỗi analysis run phải giữ nguyên protocol version đã dùng, kể cả khi protocol mới được phát hành.

---

## 11. Acceptance criteria

Tài liệu này đạt yêu cầu khi:

- [x] Có protocol ID và semantic version.
- [x] Có target muscle.
- [x] Có contraction type.
- [x] Có active duration.
- [x] Có supported feature list.
- [x] Có MFCV eligibility boundary.
- [x] Có câu chính xác: **not approved for patient use**.
- [x] Có longitudinal compatibility rule và trạng thái `not_comparable`.
- [x] Nêu rõ MFCV failure không block basic sEMG.
- [x] Có clinical review debt và exit evidence.
- [x] Không chứa treatment instruction.
- [x] Không claim diagnosis hoặc autonomous clinical decision.
- [x] Có quality-gate-before-analysis và abstention behavior.
- [x] Có versioning/change-control rule.

---

## 12. Related artifacts

```text
clinical/protocols/quad-isometric-60s.v0.1.yaml
clinical/protocols/protocol-schema.json
docs/06-ai-signal-processing/signal-import-spec.md
docs/06-ai-signal-processing/signal-validation-spec.md
docs/06-ai-signal-processing/preprocessing-spec.md
docs/06-ai-signal-processing/feature-extraction-spec.md
docs/02-clinical/quality-escalation-policy.md
services/quality-gate-service/configs/qc_v0.1.yaml
packages/common-schemas/json/qc-result.schema.json
```

---

## 13. Source notes

Protocol v0.1 được xây dựng để phục vụ technical feasibility theo nguyên tắc:

- protocol và processing phải versioned;
- signal quality phải được kiểm tra trước analysis;
- MFCV/CV là optional capability;
- abstention là output hợp lệ;
- clinical report yêu cầu human review;
- synthetic data không đại diện cho hiệu năng lâm sàng.
