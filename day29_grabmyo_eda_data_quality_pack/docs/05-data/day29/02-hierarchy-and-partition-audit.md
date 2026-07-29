# Hierarchy và partition audit

## Rule

```text
split registry
→ partition seal
→ segment/window bên trong mỗi partition
```

Không được:

```text
window toàn bộ data
→ random train/test
```

## Required checks

- duplicate `record_id`;
- duplicate natural key;
- hash xuất hiện ở nhiều partition;
- subject/day/session/repetition thiếu;
- subject thiếu ngày;
- gesture thiếu theo subject/day;
- test signal path bị lộ vào EDA.

Hierarchy `PARTIAL` có thể vẫn đi tiếp nếu thiếu ngày là đặc tính dataset và được ghi rõ; hierarchy `CONFLICTING` phải block.
