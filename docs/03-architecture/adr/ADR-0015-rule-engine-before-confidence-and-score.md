# ADR-0015 — Rule engine trước confidence và score

## Quyết định

Day 13 chỉ xây rule mapping có giải thích. Confidence aggregation được trì hoãn sang Day 14; FRS và ML tiếp tục bị vô hiệu hóa.

## Lý do

- tránh trộn logic kết luận với cách đo chất lượng kết luận;
- cho phép test từng lớp độc lập;
- ngăn một con số confidence che khuất evidence mâu thuẫn;
- giữ pipeline audit được.

## Hệ quả

`FatigueRuleResult v0.1` không có probability hoặc FRS. Mọi thay đổi mapping phải tăng version config.
