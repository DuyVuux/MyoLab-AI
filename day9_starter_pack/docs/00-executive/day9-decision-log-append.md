# Nội dung bổ sung decision log — Day 9

## D9-01 — PSD là artifact trung gian độc lập

**Quyết định:** Chuẩn hóa PSD trước MDF/MNF.

**Lý do:** MDF/MNF phụ thuộc trực tiếp trục tần số, taper, scaling và integration convention.

## D9-02 — Welch full-window v0.1

**Quyết định:** `nperseg = outer frequency window`, `noverlap = 0`.

**Giới hạn:** Chưa có lợi ích averaging nhiều segment; cần tuning sau local data audit.

## D9-03 — Hann chỉ ở spectral stage

**Quyết định:** Không taper tại windowing và không taper RMS/MAV.

## D9-04 — Không zero-padding

**Quyết định:** `nfft = nperseg = 1000` trên fixture 1000 Hz.

**Lý do:** Tránh nhầm bin spacing với resolution.

## D9-05 — Peak frequency chỉ dùng QA

**Quyết định:** Không dùng peak frequency thay MDF/MNF hoặc làm fatigue conclusion.

## D9-06 — Clinical boundary

**Quyết định:** `clinical_validation_status = not_validated`; synthetic verification chỉ chứng minh software/DSP behavior.
