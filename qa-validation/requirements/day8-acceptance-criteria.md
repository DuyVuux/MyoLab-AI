# Tiêu chí nghiệm thu — Day 8 trích xuất RMS/MAV

## AC-01 — Công thức thuần

- [ ] RMS dùng `sqrt(mean(x²))` với mẫu số `N`.
- [ ] MAV dùng `mean(abs(x))` với mẫu số `N`.
- [ ] Empty/2-D/NaN/Inf bị reject.
- [ ] RMS/MAV finite và không âm.
- [ ] `RMS >= MAV` trong tolerance.

## AC-02 — Hợp đồng đầu vào

- [ ] Chỉ nhận `WindowingRunResult.downstream_allowed=true`.
- [ ] Chỉ nhận `windowing_v0.1`.
- [ ] Chỉ nhận `preprocess_v0.1`.
- [ ] Chỉ dùng profile `time_domain` purpose `rms_mav`.
- [ ] Input canonical unit là `uV`.
- [ ] Samples không taper, không rectify trong feature layer.

## AC-03 — Hành vi theo cửa sổ

- [ ] Chỉ tính trên valid windows.
- [ ] Invalid windows tạo `not_computed` rows.
- [ ] Không impute, zero-fill hoặc bỏ row im lặng.
- [ ] Geometry/provenance được giữ nguyên.

## AC-04 — Đầu ra golden

- [ ] Golden có 239 total rows.
- [ ] 239 computed rows.
- [ ] 0 not-computed rows.
- [ ] Usable ratio bằng 1.0.
- [ ] Result status là `completed`.

## AC-05 — Tích hợp trường hợp âm

- [ ] Một invalid sample tạo đúng hai excluded overlapping windows trong fixture.
- [ ] Upstream block được propagate.
- [ ] Preprocess/window/profile mismatch bị block.
- [ ] Không còn computed row → block.

## AC-06 — Schema và nguồn gốc dữ liệu

- [ ] Feature row schema pass.
- [ ] Result schema pass.
- [ ] Verification schema pass.
- [ ] Row có feature/window/preprocess IDs và hashes.
- [ ] Deterministic result hash pass.

## AC-07 — Tối thiểu hóa dữ liệu

- [ ] JSON không chứa raw signal samples.
- [ ] CSV không chứa PHI.
- [ ] Feature row ID không dùng tên/MRN.

## AC-08 — Kiểm soát phạm vi

- [ ] Không MDF/MNF/PSD/slope.
- [ ] Không MVC/baseline normalization.
- [ ] Không cross-session/subject amplitude comparison.
- [ ] Không cross-channel aggregate.
- [ ] Không fatigue status, FRS, ML hoặc recommendation.

## AC-09 — Tài liệu

- [ ] Tất cả Markdown mới bằng tiếng Việt.
- [ ] Math primer hoàn chỉnh.
- [ ] Feature spec hoàn chỉnh.
- [ ] Data contract hoàn chỉnh.
- [ ] Test plan hoàn chỉnh.
- [ ] Notes Day 8 đã điền.

## AC-10 — Quản trị

- [ ] Feature extractor được đăng ký với code/config/schema hashes.
- [ ] Analytical verification status là `passed`.
- [ ] Clinical validation status vẫn `not_validated`.
- [ ] Synthetic evidence không bị trình bày thành clinical evidence.

## Định nghĩa hoàn thành

Day 8 hoàn thành khi:

```text
all Day 8 tests pass
+ golden E2E pass
+ schemas pass
+ deterministic hash pass
+ artifact checker pass
+ registry pass
+ notes complete
+ no clinical/ML overclaim
```
