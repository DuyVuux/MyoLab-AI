# Day 22 — Questions

## 1. Câu hỏi đã chốt trong Day 22

| Câu hỏi | Trả lời |
| --- | --- |
| Public range dùng inclusive hay exclusive end? | Half-open: `endSampleExclusive`, `endTimeExclusiveS`. |
| Activation equality là gì? | Active tại `rms >= T_activation`. |
| Release equality là gì? | Nếu previous active, vẫn active tại `rms >= T_release`. |
| Uncertainty lower equality là gì? | Uncertain khi không held/activated và `rms >= T_uncertain`. |
| Percentile dùng interpolation nào? | Nearest-rank, `ceil(pn)`, không interpolation. |
| Confidence vocabulary/order? | high > moderate > low > very low; N/A là absence. |
| Fatigue warning có được giữ nguyên confidence? | Public contract yêu cầu hạ bậc nghiêm ngặt; fixture high → moderate. |
| Electrode shift có phải fatigue evidence? | Không; chỉ thuộc quality provenance. |
| Hash tính trên payload nào? | Public camelCase window, bỏ duy nhất `resultHashSha256`. |
| Client có gửi full feedback context? | Không; gửi expected window/revision, server derive context. |
| Replay có trả toàn bộ window không? | Không; chỉ current + revealed history. |
| Có bao nhiêu scenario? | Chính xác 7; unknown scenario bị từ chối. |

## 2. Câu hỏi mở cho Day 23+

1. Production identity provider và token claims nào thay cho
   `X-Actor-Role` mock header?
2. Record-level authorization cho dynamic UC1 session route được enforce ở BFF,
   API hay policy service nào?
3. `qualityResultId` khi quality source `not_available` sẽ dùng object provenance
   nào thay vì sentinel khó audit?
4. Day 21 analysis summary sẽ phát fatigue evidence schema/version nào để thay
   scenario fixture?
5. Có cần áp dụng RFC 8785/JCS thay project canonical JSON để cross-language
   signing dài hạn không? Nếu có, migration/version strategy là gì?
6. Floating-point public serialization được freeze/test giữa Python và
   TypeScript ra sao?
7. Raw-signal reference retention và access policy theo tenant/session là gì?
8. Live streaming sẽ xử lý dropped/out-of-order windows, reconnect và
   backpressure thế nào?
9. Threshold/window/protocol parameters nào cần clinical governance và change
   control trước study?
10. Human-factor study sẽ đo hiểu nhầm no-activity/fatigue/confidence ra sao?
11. Feedback adjudication, consent và training-candidate promotion workflow do
   role nào sở hữu?
12. Evidence artifact sẽ được ký, lưu immutable và gắn commit/build provenance
   thế nào trong CI?

## 3. Nguyên tắc xử lý câu hỏi mở

Không tự điền câu trả lời bằng dữ liệu giả để làm demo trông hoàn chỉnh. Nếu
quyết định thay đổi public alias, hash boundary, feedback concurrency hoặc
clinical/safety semantics thì phải version contract và bổ sung RED test trước.
