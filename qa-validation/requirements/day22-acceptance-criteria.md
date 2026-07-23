# Tiêu chí nghiệm thu Day 22 — UC1 biofeedback cử chỉ

> Day 22 là deterministic offline replay để kiểm chứng contract, tích hợp và
> usability. Đây không phải classifier đã được xác thực lâm sàng, không phải
> live Noraxon streaming và không được điều khiển actuator.
>
> Các kiểm soát dưới đây định hướng theo software lifecycle/risk/usability
> engineering của IEC 62304, ISO 14971, IEC 62366-1 và WCAG 2.2 AA. Việc đạt
> checklist không đồng nghĩa sản phẩm đã được chứng nhận hoặc clinical validation.

## AC-D22-01 — Prerequisite và phạm vi trung thực

- [ ] Checker Day 21 và regression liên quan vẫn PASS.
- [ ] Replay ghi rõ `sourceType=synthetic_replay`.
- [ ] Model/replay ghi `modelValidationStatus=not_validated`.
- [ ] Không có claim real-time clinical, accuracy/F1 giả hoặc probability lâm sàng.
- [ ] Không có chẩn đoán, khuyến nghị điều trị, quyết định dừng tập tự động hoặc
      physical actuation.

## AC-D22-02 — Protocol có phiên bản và có thể thực thi

- [ ] Protocol upper-limb gesture dùng convention/versioning của protocol library
      hiện tại và validate bằng JSON Schema Draft 2020-12.
- [ ] Tất cả object schema cụ thể đặt `additionalProperties=false`.
- [ ] Sampling rate, window, hop, activity-gate parameters, calibration,
      vocabulary và safety fields có constraint thực, không chỉ `type: object`.
- [ ] `hop_duration_ms <= window_duration_ms`.
- [ ] `0 < release_ratio < 1`, uncertainty band hợp lệ và engineering `k > 0`.
- [ ] Vocabulary v0.1 được khóa: `rest`, `hand_open`, `hand_close`,
      `wrist_flexion`, `wrist_extension`; active prediction không dùng giá trị
      ngoài vocabulary.
- [ ] Protocol ghi clinical use disabled, human review bắt buộc, không automated
      stop/treatment và không physical actuation.

## AC-D22-03 — Activity Gate và latency

- [ ] Known answer `4.2 + 3 × 0.8 = 6.6 µV` PASS.
- [ ] Ba cửa sổ chuẩn: `4.5 → inactive`, `6.1 → uncertain`, `7.0 → active`.
- [ ] Hysteresis sequence giữ active tại `5.5 µV` và release khi thấp hơn
      `5.28 µV`.
- [ ] Boundary tại activation/release threshold được định nghĩa và kiểm thử.
- [ ] NaN, ±Inf, RMS âm, sigma âm, `k <= 0`, release ratio/uncertainty band sai
      đều bị từ chối bằng reason/error code ổn định.
- [ ] Gate là pure/deterministic và replay thực sự truyền previous state giữa
      các window.
- [ ] Total latency bằng đúng tổng component; known answer là `270 ms`.
- [ ] Python và TypeScript dùng cùng nearest-rank: p50=`200`, p95=`400` cho
      `[100, 200, 300, 400]`.
- [ ] Empty/non-finite/negative input và percentile ngoài miền bị từ chối.
- [ ] Session telemetry có count, p50, p95, dropped windows và disconnect timeout.

## AC-D22-04 — Contract inference và replay strict

- [ ] Có bốn schema Draft 2020-12: protocol, gesture inference,
      gesture feedback context và UC1 replay session.
- [ ] Mỗi nested concrete object trong bốn schema đặt
      `additionalProperties=false`.
- [ ] Confidence dùng vocabulary canonical:
      `engineering_high|engineering_moderate|engineering_low|engineering_very_low|not_available`.
- [ ] Quality context và fatigue overlay là hai object riêng, mỗi object có
      status, reason codes và provenance cần thiết.
- [ ] `qualityContext` luôn có `source` và `qualityResultId`; provenance QC không
      được tái sử dụng như bằng chứng fatigue.
- [ ] `fatigueOverlay.source` chỉ nhận
      `scenario_fixture|analysis_summary|not_available`; `evidenceSummaryVi`,
      `counterevidenceVi`, `limitationsVi` là các mảng diễn giải ngắn, không chứa
      raw samples hoặc direct identifier.
- [ ] Window có `modelVersion` và `resultHashSha256` SHA-256 canonical do server
      tạo; client không tự chế hash/version.
- [ ] Hash dùng 64 ký tự lowercase hex; channel IDs unique; ID không rỗng;
      sample/time ranges tăng nghiêm ngặt.
- [ ] `latency.totalMs` khớp tổng component.
- [ ] Các predicate sau bắt buộc `predictedGesture=null` và confidence
      `not_available`: activity `inactive|uncertain`, QC `fail`, device
      `disconnected|reconnecting`, fatigue `abstain`.
- [ ] Prediction khác null chỉ được phép khi activity active, QC pass/warning,
      device connected và fatigue không abstain.
- [ ] Fatigue warning có reason code, đánh dấu adjustment và chỉ được giữ hoặc hạ
      confidence theo policy đã định; không bao giờ tăng confidence.
- [ ] Electrode shift chỉ nằm trong quality context; fatigue overlay giữ
      `source=not_available`, không warning/abstain và không có fatigue evidence
      được suy diễn từ Day 17 signal-quality result.
- [ ] Replay-session response chỉ có `currentWindow` và revealed `history`; không
      trả future inference windows.
- [ ] `totalWindows`, `currentIndex`, `revision`, `state`, history/current window
      và latency summary nhất quán ở Pydantic semantic validation.

## AC-D22-05 — Provenance và exact-window feedback

- [ ] Engine nhận calibration/import/mapping/repetition context từ Day 20; không
      hardcode rest RMS, sigma, source hash, channel IDs hoặc calibration ID.
- [ ] Source hash nhất quán xuyên suốt Day 20 import → Day 21 job → Day 22 window.
- [ ] Sample/time range dùng tên explicit half-open:
      `[startSample, endSampleExclusive)` và
      `[startTimeS, endTimeExclusiveS)`; time range khớp sampling rate.
- [ ] Feedback context giữ nguyên analysis/session/window ID, raw-signal ref,
      source hash, `startSample`, `endSampleExclusive`, `startTimeS`,
      `endTimeExclusiveS`, channels, repetition, calibration,
      `modelVersion` và exact `resultHashSha256`.
- [ ] Action `correct` bắt buộc có corrected gesture hợp lệ và khác prediction gốc.
- [ ] `accept|uncertain|remeasure` không được giả thành correction.
- [ ] Không tạo training candidate tự động; consent/adjudication vẫn là gate riêng.
- [ ] Feedback action được bảo vệ theo role ở UI và backend boundary.

## AC-D22-06 — Deterministic replay và state machine

- [ ] Registry có chính xác bảy scenario:
      `uc1_golden_correct`, `uc1_ambiguous_prediction`, `uc1_no_activity`,
      `uc1_fatigue_confidence_drop`, `uc1_electrode_shift_warning`,
      `uc1_qc_fail_abstention`, `uc1_device_disconnect`.
- [ ] Scenario không biết bị từ chối; không silent fallback sang golden.
- [ ] Cùng input/version tạo cùng replay ID, window payload và result hashes.
- [ ] Upstream Day 21 `abstained` tạo replay abstained với zero history/current
      window; tuyệt đối không chứa prediction ẩn.
- [ ] State/cursor/revision chỉ tiến theo transition hợp lệ; terminal state không
      quay lại running.
- [ ] Concurrent/stale advance không bỏ qua window hoặc advance hai lần.

## AC-D22-07 — API, idempotency và lỗi

- [ ] `POST /v1/uc1/sessions/{session_id}/replays` bắt buộc
      `Idempotency-Key`.
- [ ] Cùng key + cùng payload trả cùng replay ID/payload.
- [ ] Dùng lại key với payload khác trả HTTP 409
      `IDEMPOTENCY_KEY_REUSED`.
- [ ] Missing analysis/replay trả 404 với Problem Details; invalid body trả 422.
- [ ] Session/use-case mismatch trả 409.
- [ ] Analysis queued/running trả 409 `ANALYSIS_NOT_TERMINAL`.
- [ ] Analysis failed/cancelled trả 409 `ANALYSIS_NOT_REPLAYABLE`.
- [ ] Completed job chưa có result cần thiết trả 409 `ANALYSIS_RESULT_NOT_READY`.
- [ ] Advance nhận `expectedCurrentIndex` và `expectedRevision`; stale request trả
      409, terminal advance là idempotent.
- [ ] `/advance` được ghi rõ là deterministic dev/test endpoint, không phải
      production streaming API.
- [ ] OpenAPI 3.1 có operationId unique, examples hợp lệ và local refs resolve.

## AC-D22-08 — UI và usability safety

- [ ] Tích hợp vào Next.js 14 App Router thật tại UC1 session route; không thêm
      `react-router-dom` hoặc route placeholder.
- [ ] Reuse AppShell, design tokens, Card/Alert/Badge/Button và route/RBAC hiện có.
- [ ] Không còn `Date.now()`-generated inference, `% Conf`, `fatigueIndex` giả,
      fake hash/model hoặc câu “phát hiện mỏi cao, bệnh nhân phải nghỉ”.
- [ ] Idle không hiển thị trước future prediction.
- [ ] Inactive, uncertain, QC fail, fatigue abstain, disconnected và technical
      failure có copy/CTA khác nhau.
- [ ] “No activity” không bị diễn giải là model fail hoặc bệnh nhân không cố gắng.
- [ ] State không chỉ truyền đạt bằng màu; status có text/icon/reason code.
- [ ] Interactive controls có accessible name, focus state và action handler thật.
- [ ] Bảng history có caption/header semantics, empty state và responsive overflow.
- [ ] Patient-facing text đạt tối thiểu 16 px; keyboard và screen-reader flow đạt
      WCAG 2.2 AA target trong audit.

## AC-D22-09 — Verification và evidence

- [ ] JSON Schema meta-validation, valid/invalid fixture tests và Pydantic semantic
      tests PASS.
- [ ] Unit tests Activity Gate/latency và Python↔TypeScript parity PASS.
- [ ] API tests bao phủ bảy scenario, error matrix, idempotency, stale cursor,
      terminal idempotency và feedback correction conditions.
- [ ] Full frontend type-check dùng dependency thật của app, không chỉ vendor stub.
- [ ] Day 22 evidence được sinh từ code đã merge, không copy từ starter pack.
- [ ] Evidence chứa cả bảy scenario và feedback trace; mỗi payload validate schema.
- [ ] Hai lần sinh sau reset cho byte/canonical-hash giống nhau; thứ tự chạy
      scenario không ảnh hưởng output.
- [ ] Result hash được recompute và khớp; feedback original hash trỏ đúng window.
- [ ] Recursive privacy/safety scan không thấy raw sample array, direct identifier,
      probability field, diagnosis/treatment claim hoặc actuation enabled.
- [ ] `scripts/dev/run_day22_checks.sh` dùng `.venv` và local TypeScript binary,
      cleanup build bằng trap, và kết thúc PASS.
- [ ] Không có test skip/xfail để che invariant Day 22.
