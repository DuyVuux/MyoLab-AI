# Tiêu chí nghiệm thu Day 7

## A. Dependency

- [ ] Day 6 preprocessing verification đang PASS.
- [ ] `preprocess_v0.1` vẫn frozen/not clinically validated.
- [ ] QC/preprocessing block được propagate.

## B. Protocol alignment

- [ ] Target phase lấy từ protocol.
- [ ] Protocol ID/version phải khớp signal.
- [ ] Time-domain window đúng 500 ms.
- [ ] Frequency-domain window đúng 1000 ms.
- [ ] Cả hai overlap 50%.
- [ ] Mismatch bị block, không fallback.

## C. Geometry

- [ ] Half-open `[start,end)`.
- [ ] Time profile: L=500, H=250, K=239 tại Fs=1000/60s.
- [ ] Frequency profile: L=1000, H=500, K=119.
- [ ] First/last windows nằm trong active phase.
- [ ] Không có partial final window.
- [ ] Window indices liên tục từ 0 trong từng profile.

## D. Validity

- [ ] Đánh giá theo từng channel-window.
- [ ] Non-finite hoặc invalid mask làm window invalid.
- [ ] Không impute/pad.
- [ ] Case index 5750 tạo invalid `[2,3]` và `[0,1]` tương ứng.
- [ ] Nếu một required profile không còn valid window, run bị block.

## E. Output/provenance

- [ ] JSON không chứa raw samples.
- [ ] Có upstream preprocessing version/hash.
- [ ] Có windowing config ID.
- [ ] Có plan hash.
- [ ] Có geometry/validity của cả hai profile.
- [ ] JSON Schema pass.
- [ ] Hai lần chạy cho cùng plan hash.

## F. Safety

- [ ] Windowing completed không sinh fatigue result.
- [ ] Không gọi số window là số observation độc lập.
- [ ] Không claim clinical validation.
- [ ] Không dùng Hann cho RMS/MAV tại tầng này.
- [ ] Không có MFCV calculation.

## G. Documentation

- [ ] Toàn bộ Markdown mới bằng tiếng Việt.
- [ ] Math primer hoàn chỉnh.
- [ ] Spec, contract, ADR và test plan hoàn chỉnh.
- [ ] Notes Day 7 được điền thật.
- [ ] Handoff Day 8 rõ ràng.
