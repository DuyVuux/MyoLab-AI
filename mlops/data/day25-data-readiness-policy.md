# Day 25 Data Readiness Policy v0.2

## Chính sách mặc định

```text
implementationAllowed = true
trainingAllowed = false
```

## Điều kiện để tạo model-ready dataset

- source/version/license đã khóa;
- archive và file hashes đã khóa;
- hierarchy subject/session/trial/repetition tồn tại;
- labels có provenance;
- privacy screening pass;
- DUA/IRB hoàn tất nếu cần;
- group-safe split được seal;
- test set chưa mở;
- derivative dataset purpose phù hợp license.

## Cấm

- auto-download restricted datasets;
- random-window split;
- tự map unknown thành rest;
- dùng direct identifiers;
- train từ feedback chưa adjudicate;
- model training chỉ để tạo metric demo;
- gọi public healthy benchmark là clinical validation.
