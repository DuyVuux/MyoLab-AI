# Bằng chứng Day 6 — Kiểm chứng preprocessing v0.1

- Config: `preprocess_v0.1`
- Config SHA-256: `844e19bb7da7161deadd51c3aeece0ddebf314e0c57b112f96bbf269454e56fa`
- Sampling rate kiểm chứng: `1000.0 Hz`
- Trạng thái kiểm chứng phân tích: **PASSED**
- Trạng thái xác nhận lâm sàng: **CHƯA XÁC NHẬN**

## Tiêu chí lý thuyết

| ID | Đường xử lý | Hz | Gain dB | Kết quả |
|---|---|---:|---:|---|
| TH_BP_5_STOP | bandpass | 5.0 | -97.7621 | PASS |
| TH_BP_30_PASS | bandpass | 30.0 | -0.2663 | PASS |
| TH_BP_80_PASS | bandpass | 80.0 | -0.0000 | PASS |
| TH_BP_200_PASS | bandpass | 200.0 | -0.0000 | PASS |
| TH_BP_350_PASS | bandpass | 350.0 | -0.1835 | PASS |
| TH_BP_450_STOP | bandpass | 450.0 | -51.0514 | PASS |
| TH_NOTCH_50_STOP | bandpass_plus_notch | 50.0 | -300.0021 | PASS |
| TH_NOTCH_80_COLLATERAL | bandpass_plus_notch | 80.0 | -0.0099 | PASS |

## Tiêu chí thực nghiệm

| ID | Đường xử lý | Hz | Gain dB | Kết quả |
|---|---|---:|---:|---|
| EM_BP_5_STOP | bandpass | 5.0 | -97.7667 | PASS |
| EM_BP_30_PASS | bandpass | 30.0 | -0.2663 | PASS |
| EM_BP_50_PRESERVED_WITHOUT_NOTCH | bandpass | 50.0 | -0.0021 | PASS |
| EM_BP_80_PASS | bandpass | 80.0 | -0.0000 | PASS |
| EM_BP_200_PASS | bandpass | 200.0 | -0.0000 | PASS |
| EM_BP_350_PASS | bandpass | 350.0 | -0.1835 | PASS |
| EM_BP_450_STOP | bandpass | 450.0 | -51.0514 | PASS |
| EM_NOTCH_50_STOP | bandpass_plus_notch | 50.0 | -57.6097 | PASS |
| EM_NOTCH_80_COLLATERAL | bandpass_plus_notch | 80.0 | -0.0099 | PASS |

## Pha bằng không

- Peak offset: `0 sample`.
- Normalized symmetry error: `3.304e-16`.
- Kết quả: **PASS**.

## Hành vi tại biên

- Interior RMSE: `6.59005e-06 uV`.
- Edge RMSE: `4.01763 uV`.
- Edge/interior ratio: `609651.521`.
- Edge guard: `0.25 s`.
- Kết quả: **PASS**.

## Tính xác định trong cùng môi trường

- Repeat count: `3`.
- Hashes giống nhau: `True`.
- Hash: `c7a996a480866fa3c654aa3cd8a63dc264916ebe3b263ca34c70ee182932e0f9`.

## Giới hạn

- Profile này chỉ là engineering acceptance cho MVP-0 offline.
- Chưa xác nhận trên Noraxon export thật hoặc dữ liệu lâm sàng.
- Chỉ kiểm chứng Fs=1000 Hz trong Day 6.
- Exact output hash được yêu cầu trong cùng environment; qua environment khác cần numerical tolerance.
- Không kiểm chứng electrode placement, crosstalk, protocol adherence hoặc clinical interpretation.
- Không kiểm chứng MFCV/CV preprocessing.

> Kết quả này là analytical verification cho MVP-0 offline trên fixture synthetic. Đây không phải xác nhận lâm sàng, không chứng minh hiệu quả chẩn đoán và không xác nhận realtime behavior.
