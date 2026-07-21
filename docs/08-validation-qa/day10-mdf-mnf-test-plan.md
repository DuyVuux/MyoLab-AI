# Kế hoạch kiểm thử MDF/MNF Day 10

## Known-answer tests

- Uniform PSD 20–400 Hz → MDF = MNF = 210 Hz.
- Single-bin PSD tại 80 Hz → MDF = MNF = 80 Hz.
- Trọng số 1:2:1 tại 50/100/150 Hz → MNF = 100 Hz.
- Nhân PSD với hằng số dương → MDF/MNF không đổi.

## Negative tests

- PSD âm;
- PSD toàn 0;
- axis không đều;
- spectral stage bị block;
- spectral config/schema mismatch;
- band-power mismatch.

## E2E

Golden synthetic phải tạo 119 MDF/MNF rows và deterministic hash.
