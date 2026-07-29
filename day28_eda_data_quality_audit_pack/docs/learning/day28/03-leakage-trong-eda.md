# Học kỹ: Leakage trong EDA

EDA có thể leak khi operator nhìn test distribution rồi chọn:

- outlier threshold;
- filter cutoff;
- feature family;
- normalization;
- class exclusions;
- narrative có lợi cho model.

Quy tắc: develop on train, audit on validation after freeze, keep test sealed.
