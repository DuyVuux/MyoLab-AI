# Data Readiness Gate Policy v0.2

## Trạng thái

### `READY`

Chỉ khi một dataset cụ thể có:

```text
canonical source/version
+ verified access/license
+ immutable archive/file hashes
+ complete data dictionary
+ subject/session grouping
+ label provenance
+ privacy approval
+ group-safe split
```

và site-specific workstream có boundary rõ.

### `CONDITIONAL_READY`

Research landscape đủ, nhưng còn một hoặc nhiều điều:

- site export chưa được kiểm;
- exact field schema chưa khóa;
- dataset version/license chưa chốt;
- MFCV chưa được xác minh;
- model-ready derivative chưa được phê duyệt.

### `BLOCKED`

- legal/access không thể xác định cho dataset định dùng;
- không có subject/session grouping;
- direct identifiers chưa được xử lý;
- source provenance không tồn tại;
- random-window-only split;
- raw site interface hoàn toàn speculative.

## Hai quyền tách biệt

```text
implementationAllowed
trainingAllowed
```

Day 25 kỳ vọng:

```text
implementationAllowed = true
trainingAllowed = false
```

## Training unlock requirements

1. Exact dataset/version đã chọn.
2. Official source và license được lưu.
3. Download/file hashes được khóa.
4. Data dictionary và label mapping được xác minh.
5. Subject/session grouping đầy đủ.
6. Split manifest được seal.
7. No direct identifier.
8. DUA/IRB hoàn tất khi áp dụng.
9. Test set chưa mở.
10. Site deployment claim vẫn tách khỏi public baseline.
