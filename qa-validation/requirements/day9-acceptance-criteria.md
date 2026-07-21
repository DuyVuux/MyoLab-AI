# Tiêu chí nghiệm thu Day 9

## A. Kiến thức

- [ ] Giải thích được DFT và FFT.
- [ ] Tính được Nyquist, bin spacing và Rayleigh resolution.
- [ ] Phân biệt amplitude spectrum, power spectrum và PSD.
- [ ] Nêu đúng đơn vị `uV²/Hz`.
- [ ] Giải thích spectral leakage và Hann.
- [ ] Giải thích Welch v0.1 chỉ có một segment.
- [ ] Giải thích weighted Parseval reference.
- [ ] Phân biệt công thức MDF và MNF.

## B. Code

- [ ] Có `semg_core/spectral.py`.
- [ ] Có one-sided frequency axis.
- [ ] Có periodogram/Welch PSD.
- [ ] Có band selection và power integration.
- [ ] Có input guards cho NaN/Inf/tham số sai.
- [ ] Có service config/result/estimator.
- [ ] Không tính MDF/MNF.

## C. Golden E2E

- [ ] Status `completed`.
- [ ] 119 total rows.
- [ ] 119 computed rows.
- [ ] 0 not-computed rows.
- [ ] Shared axis 20–400 Hz.
- [ ] 381 bins.
- [ ] Bin spacing 1 Hz.
- [ ] Rerun có cùng result hash.

## D. Negative behavior

- [ ] QC flatline fail block spectral stage.
- [ ] Blocked result không có rows.
- [ ] Invalid window không được impute.
- [ ] Low-power window không tạo fake PSD.

## E. Schema và provenance

- [ ] Result schema pass.
- [ ] Row schema pass.
- [ ] Verification schema pass.
- [ ] PSD row khớp shared axis.
- [ ] Có config/window/preprocess/source hashes.
- [ ] Không có raw samples trong JSON.

## F. Safety

- [ ] Không fatigue status.
- [ ] Không FRS.
- [ ] Không ML.
- [ ] Không clinical recommendation.
- [ ] Peak frequency ghi rõ QA only.
- [ ] `clinical_validation_status = not_validated`.
- [ ] Synthetic data không được gọi là clinical evidence.

## G. Documentation

- [ ] Tất cả Markdown Day 9 bằng tiếng Việt.
- [ ] Math primer đã đọc và ghi chú.
- [ ] Spec/data contract/test plan/ADR hoàn chỉnh.
- [ ] Notes Day 9 đã điền.
- [ ] Day 10 handoff rõ ràng.
