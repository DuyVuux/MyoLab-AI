# ADR-0010 — Triển khai và kiểm chứng RMS/MAV trước spectral features và inference

**Trạng thái:** Được chấp thuận cho MVP-0  
**Ngày:** Day 8  
**Phụ trách:** một người thực hiện — AI/Tín hiệu/Kiến trúc  
**Review ngoài cần có về sau:** chuyên gia xử lý tín hiệu y sinh và chuyên gia lâm sàng

## Bối cảnh

Sau Day 7, hệ thống đã có:

- ingestion;
- protocol mapping;
- quality gate;
- preprocessing v0.1 đã analytical verification;
- fixed half-open window plan v0.1;
- time-domain profile 500 ms;
- frequency-domain profile 1000 ms.

Bước tiếp theo có thể là:

1. triển khai toàn bộ RMS/MAV/MDF/MNF/slope cùng lúc;
2. đi thẳng vào classifier KNN/SVM;
3. triển khai feature family nhỏ nhất, kiểm chứng kỹ rồi mở rộng.

## Quyết định

Chọn phương án 3:

```text
Day 8:
RMS + MAV only
→ pure math tests
→ valid-window-only extraction
→ feature-row contract
→ deterministic evidence

Day 9+:
PSD/Welch/MDF/MNF
→ trend features
→ fatigue evidence
→ rule engine
→ classical ML only after usable local labels
```

## Quy tắc bắt buộc

- RMS/MAV chỉ tính trên `time_domain` valid windows.
- Không Hann taper.
- Không rectification trong feature layer.
- Không MVC/baseline normalization.
- Invalid windows tạo traceable `not_computed` rows.
- Không tạo fatigue status hoặc clinical interpretation.
- Output không chứa raw samples.
- Feature extractor/config/schema phải versioned.

## Lý do

### 1. Giảm blast radius

RMS/MAV có công thức đơn giản, dễ tính tay và tạo golden tests. Điều này giúp xác minh đầy đủ data lineage trước khi thêm spectral complexity.

### 2. Tách lỗi theo tầng

Nếu MDF/MNF sai ngay khi thêm cùng lúc, khó biết lỗi nằm ở:

- windowing;
- taper;
- PSD estimator;
- band selection;
- cumulative power;
- feature serialization.

RMS/MAV tạo checkpoint sạch cho amplitude path.

### 3. Clinical safety

Amplitude thay đổi không đủ để kết luận fatigue. Bằng cách chưa thêm rule/ML, team tránh biến feature kỹ thuật thành claim lâm sàng quá sớm.

### 4. Explainability and reproducibility

RMS/MAV có thể kiểm chứng bằng vector đóng, bất biến scale/sign và `RMS ≥ MAV`.

### 5. Phù hợp team một người

Giới hạn WIP giúp người mới học sâu từng khái niệm và giảm single-operator cognitive overload.

## Hệ quả tích cực

- Có deterministic feature table đầu tiên.
- Dashboard sau này có amplitude trend có provenance.
- Có schema/API-ready rows.
- Có nền cho slope nhưng chưa tạo slope vội.
- Dễ phát hiện unit/windowing bug.

## Trade-offs

- Chưa tạo được fatigue evidence đầy đủ.
- Chưa có spectral shift.
- Chưa có FRS/ML demo.
- Có thể cảm giác tiến độ chậm hơn nhưng giảm rework/risk.

## Phương án bị từ chối

### All features at once

Bị từ chối vì tăng complexity và khó trace lỗi.

### KNN-first

Bị từ chối vì chưa có local labels đủ dùng, chưa khóa feature contract và có nguy cơ leakage/overfit.

### Session-level RMS only

Bị từ chối vì làm mất temporal evolution và không khớp architecture windowed evidence.

## Điều kiện xem xét lại

ADR có thể mở rộng khi:

- PSD/Welch spec được approved;
- spectral golden tests pass;
- normalization policy được review;
- local data audit cho thấy feature khác cần ưu tiên.

Không được sửa `features_semg_v0.1` để thêm MDF/MNF; phải tăng version/config.
