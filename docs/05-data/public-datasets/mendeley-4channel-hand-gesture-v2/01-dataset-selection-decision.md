# Day 27 — Quyết định chọn dataset đầu tiên

## Primary

`MENDELEY_4CH_GESTURE` được preselect làm sparse-channel Task A adapter đầu tiên.

## Vì sao không chọn GRABMyo trước?

GRABMyo rất quan trọng cho cross-day robustness nhưng 32 channels và gesture-count conflict làm phạm vi adapter đầu tiên lớn hơn. Mendeley 4-channel phù hợp hơn để khóa một contract nhỏ, strict label mapper và canonical conversion trước. Đây là quyết định thứ tự thực hiện, không phải xếp hạng khoa học.

## Fallback

Chuyển sang `GRABMYO_V1_1` nếu canonical record/license/hierarchy của primary không thể xác minh theo stop rules.

## Decision status

```yaml
status: PRESELECTED_PENDING_CANONICAL_VERIFICATION
trainingAllowed: false
```
