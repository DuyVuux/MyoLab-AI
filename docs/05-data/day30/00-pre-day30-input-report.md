# Báo cáo đầu vào Pre-Day 30

Tài liệu này lưu lại các kết luận do người thực hiện cung cấp trước Day 30.

## Trạng thái

```yaml
overall_status: GO_FOR_DAY30_HARMONIZATION
test_set_opened: false
training_allowed: false
fatigue_inference_allowed: false
```

## GRABMyo

- 51/51 bản ghi EDA PASS;
- 29 subject unique trong phần đã EDA, 43 total được báo cáo;
- 28 kênh phân tích: F1–F16, W1–W12;
- U1–U4 ở noise floor và không thuộc analysis view;
- 2048 Hz, mV;
- ba session/cross-day;
- 17 gesture;
- không NaN/Inf.

## Mendeley

- 9/9 file EDA PASS trong phần sampled;
- 9 sampled subjects, 25 total được báo cáo;
- 2000 Hz, mV;
- CH1–CH3 có std khoảng 3–3.6 mV;
- CH4 std khoảng 0.039 mV và cần quarantine;
- 10 raw gesture;
- không NaN/Inf.

## Khác biệt chính

1. biên độ khác khoảng 40 lần;
2. sampling rate 2048/2000;
3. Mendeley có DC offset;
4. CH4 chưa rõ vai trò;
5. channel count 28 so với 3–4;
6. ontology 17 so với 10;
7. GRABMyo cross-day, Mendeley single-session.

Tài liệu Day 30 không tự sửa hoặc thay thế các số liệu này bằng nguồn bên ngoài.
