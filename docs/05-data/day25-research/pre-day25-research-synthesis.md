# Tổng hợp bằng chứng tiền Day 25

## 1. Kết luận điều hành

Bốn báo cáo deep research cho phép đưa ra kết luận vận hành sau:

```text
Dataset/repository landscape đủ để bắt đầu evidence-backed engineering.
Site interface chưa đủ để khóa parser hoặc model-ready dataset.
Training chưa được phép.
```

### Trạng thái đề xuất

| Trục | Trạng thái |
|---|---|
| Landscape dataset công khai | Đủ để dựng catalog, adapter và baseline research |
| Priority free stack | Có shortlist khả dụng, nhưng từng dataset vẫn cần versioned manifest |
| Restricted clinical datasets | Đã nhận diện; chưa được phép dùng nếu chưa DUA/IRB |
| Noraxon public capability | Có bằng chứng vendor-level cho một số capability |
| Installed site hardware/software | Chưa xác minh đầy đủ |
| Actual de-identified site export | Chưa được kiểm |
| Exact export schema | Chưa xác minh |
| Native JSON export | `NOT_VERIFIED` |
| MFCV eligibility | `NOT_VERIFIED` |
| Model training | Không được phép |

## 2. Dataset strategy theo Task

### Task A — Gesture Recognition

Tổ hợp tối thiểu được đề xuất:

```text
Mendeley 4-channel
→ label set gần UC1 và sparse adapter

GRABMyo
→ multi-day/cross-session robustness

Hyser PR
→ HD-sEMG, spatial data contract và force/MVC ecosystem
```

Không dataset nào được coi là clinical deployment truth.

### Task B — Fatigue Context

```text
Cerqueira fatigue
→ raw upper-body sEMG + time-stamped self-perceived fatigue

Hyser MVC/force subsets
→ force/MVC/HD-sEMG contract support
```

Task B phải là context/confidence/abstention layer trước khi được xem như classifier.

### Task C — Quantitative Assessment

```text
Lucchetti clinical / Mendeley post-stroke records
→ clinical metric provenance

Hyser
→ MVC/force/spatial support

GRABMyo
→ repeatability across days
```

Task C bắt đầu bằng metric set, không phải một classifier tổng hợp.

## 3. Phân loại dataset vận hành

### PRIORITY_FREE_CORE

- GRABMyo.
- Hyser.
- Cerqueira fatigue.
- Mendeley 4-channel gesture.
- Lucchetti post-stroke kinematic+EMG.
- Mendeley post-stroke reaching, sau khi khóa canonical DOI/record.

### PRIORITY_FREE_CONDITIONAL

- GRABMyoFlow: giữ điều kiện xác minh license/version trước khi reuse.

### USEFUL_RESEARCH_ONLY

- putEMG: data `CC BY-NC 4.0`, không được đưa vào commercial reuse path.

### RESTRICTED_REFERENCE

- PhysioMio.
- PhysioNet hand-kinematics-sEMG.

### TO_VERIFY

- Ninapro family.
- CapgMyo.
- GREAT.
- CSL-HDEMG.
- mmGest.
- UCD-MyoVerse-Hand-1.
- Malešević 65 gestures.
- Rojas-Martínez elbow HD-sEMG.
- Zenodo fatigue records chưa phân biệt rõ.
- EMAHA-DB1.

## 4. Sự thật Noraxon được phép nói

Có thể nói ở mức public/vendor documentation:

- Ultium receiver hỗ trợ tối đa 16 wireless sensors trong tài liệu được trích dẫn bởi các báo cáo.
- Brochure công khai có sample-rate capability 2,000/4,000 Hz.
- MR có local storage và workflow export/import hoặc external location.
- Một deep audit báo cáo raw export qua Excel/MATLAB/ASCII CSV/C3D/native structure.
- Có public evidence về TTL synchronization, Vicon plugin và third-party/HTTP streaming ở một số version/workflow.

Không được suy ra rằng site hiện tại đã có hoặc đã bật đầy đủ các capability đó.

## 5. Sự thật chưa được phép nói

```text
“MR3 xuất JSON native.”
“Mọi 16-sensor setup đều tính được MFCV.”
“Raw per-channel export đã sẵn sàng tại Motion Lab.”
“Field schema của site đã biết.”
“Plugin/Vicon/module hiện đã cài và licensed.”
“Public-data accuracy dự báo hiệu năng stroke.”
```

## 6. Bằng chứng site cần lấy

1. Exact receiver/sensor model và revision.
2. Firmware.
3. Exact MR3/myoRESEARCH version.
4. Licensed modules.
5. Acquisition settings.
6. Rest export đã khử định danh.
7. Five-gesture export đã khử định danh.
8. Processed metrics/report export.
9. Synchronized multimodal export khi có.
10. Electrode geometry/IED/order/fibre alignment và raw propagation evidence nếu muốn MFCV.

## 7. Quyết định Day 25

```text
GO:
- catalog/manifest/schema engineering;
- subject-safe split;
- site audit package;
- parser scaffolding;
- Task A/B/C contract design.

NO-GO:
- training/tuning;
- final Noraxon parser schema;
- MFCV enablement;
- clinical performance claims;
- restricted dataset access không qua governance.
```
