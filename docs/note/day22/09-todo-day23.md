# Day 23 — Todo từ Day 22

## P0 — Chốt integration và evidence

- [ ] Re-run full Day 21 + Day 22 suite từ source state cuối, không skip/xfail.
- [ ] Sinh lại deterministic Day 22 evidence; validate đủ 7 scenario, exact
      feedback trace và recompute mọi public hash.
- [ ] Lưu command, commit SHA, dependency versions, exit codes và artifact
      SHA-256.
- [ ] Xác minh response không có `windows`/future payload ở mọi lifecycle/error
      path.
- [ ] Xác minh feedback stale `expectedWindowId`/`expectedRevision` không ghi
      record.
- [ ] Chạy full frontend type-check với dependency thật và Playwright route
      `/uc1/session/{sessionId}`.

## P0 — Security boundary

- [ ] Thay mock `X-Actor-Role` bằng principal từ authentication layer hoặc ghi
      explicit dev-only guard nếu chưa thể.
- [ ] Enforce backend action + session/tenant ownership cho create/advance/
      feedback.
- [ ] Bổ sung dynamic UC1 route policy và test direct URL access.
- [ ] Audit logs không chứa raw/direct identifier và bind actor/replay/window/
      revision bất biến.

## P1 — Contract hardening

- [ ] Quyết định provenance cho `qualityResultId` khi source `not_available`.
- [ ] Freeze/test float serialization và canonical hash parity Python/TypeScript.
- [ ] Đánh giá RFC 8785/JCS cho contract version tiếp theo; không đổi v0.1 âm
      thầm.
- [ ] Sinh OpenAPI 3.1 examples từ valid schema fixtures và kiểm local refs/
      unique operation IDs.
- [ ] Contract-test mọi field alias half-open và unknown-field rejection.

## P1 — Signal/streaming readiness

- [ ] Định nghĩa live window clock, dropped/out-of-order policy, reconnect,
      timeout và backpressure.
- [ ] Phân biệt measured latency với injected replay latency; thêm benchmark plan
      trước khi đặt SLO.
- [ ] Định nghĩa schema/version cho Day 21 fatigue analysis summary và
      counterevidence/limitations.
- [ ] Không dùng `MDF_DECLINE_OBSERVED` như measured evidence cho đến khi DSP
      pipeline và provenance tồn tại.

## P1 — Usability và clinical governance

- [ ] Audit keyboard, screen reader, contrast và mobile overflow theo WCAG 2.2
      AA target; lưu evidence.
- [ ] User-test copy cho no activity, uncertain, QC fail, fatigue abstain,
      disconnect và technical failure.
- [ ] Xác định owner/change control cho threshold, window, gesture vocabulary và
      fatigue policy trước clinical study.
- [ ] Thiết kế feedback adjudication/consent/training-candidate workflow; tiếp
      tục giữ automatic candidate disabled.

## P2 — Documentation hygiene

- [ ] Cập nhật docs khi final API/frontend shapes thay đổi; không sửa schema mà
      bỏ quên hash/test/docs.
- [ ] Link evidence manifest từ validation docs sau khi artifact được sinh.
- [ ] Archive hoặc dán nhãn rõ starter pack để tránh bị hiểu là production
      source.

Day 23 không được mở rộng sang clinical claims hoặc physical-device control khi
chưa có authorization, risk review và verification evidence tương ứng.
