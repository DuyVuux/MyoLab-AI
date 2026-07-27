# Checklist bằng chứng site — Noraxon Ultium / myoRESEARCH

> Mục tiêu: biến các claim `NOT_VERIFIED` thành `SITE_VERIFIED` bằng artifact cụ thể, không bằng xác nhận miệng.

## A. Hardware inventory

- [ ] Ảnh model/SKU receiver.
- [ ] Serial được hash hoặc che một phần theo policy.
- [ ] Ảnh model/SKU từng loại sensor.
- [ ] Số sensor thực dùng cho protocol.
- [ ] Firmware receiver.
- [ ] Firmware sensors.
- [ ] SmartLead/adapter được dùng.

## B. Software inventory

- [ ] Ảnh About dialog.
- [ ] Exact myoRESEARCH/MR3 version.
- [ ] Installed module/license list.
- [ ] Export menu screenshot.
- [ ] Sync/plugin list.
- [ ] Database/storage location policy.

## C. De-identified exports

### C1 — Rest export

- [ ] 10–30 giây rest.
- [ ] Không tên/MRN/email/phone/video-face.
- [ ] Có sampling rate và unit hoặc tài liệu đi kèm.
- [ ] Có channel names/order.

### C2 — Five-gesture export

- [ ] `rest`.
- [ ] `hand_open`.
- [ ] `hand_close`.
- [ ] `wrist_flexion`.
- [ ] `wrist_extension`.
- [ ] Cue/marker hoặc trial timing.
- [ ] Repetition identity.

### C3 — Processed report/metric export

- [ ] Một report không chứa PHI.
- [ ] Report/module name và version.
- [ ] Filter/normalization settings nếu có.

### C4 — Synchronized multimodal export

- [ ] VICON/force/pressure/video/IMU modality list.
- [ ] Trigger/pulse test.
- [ ] Event/marker representation.
- [ ] Time base và offsets.

## D. MFCV evidence

- [ ] Linear array confirmed.
- [ ] Inter-electrode distance known.
- [ ] Electrode order known.
- [ ] Orientation along muscle fibres documented.
- [ ] Location relative to innervation zone documented.
- [ ] Compatible raw adjacent-channel signals.
- [ ] Sampling setting captured.
- [ ] Propagation/correlation evidence.

Nếu bất kỳ mục bắt buộc nào thiếu:

```text
mfcv.eligible = false
```

## E. Privacy and provenance

- [ ] `phi_screening=pass`.
- [ ] Source file hashes.
- [ ] Export date/time.
- [ ] Operator pseudonym/role.
- [ ] SOP version.
- [ ] Native vs converted representation.
