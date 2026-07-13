# KẾ HOẠCH BRAINSTORM + PHÁT TRIỂN DỰ ÁN sEMG/MFCV FATIGUE CLINICAL INTELLIGENCE LAYER

**Team:** Duy (Solo)  
**Bản:** 1.0  
**Ngày lập:** 09/07/2026  
**Giả định lịch:** Day 1 bắt đầu ngày 10/07/2026; nếu lịch thực tế khác, giữ nguyên thứ tự dependency và dịch ngày tương ứng.  

## Assumptions vận hành

- Làm việc theo nhịp 6 giờ deep work/ngày + 30 phút daily sync. Ngày 7/14/21/30 là review/risk/planning.
- Chưa có dữ liệu thật ở ngày đầu; synthetic/CSV là baseline để chứng minh pipeline. Motion Lab/Noraxon audit quyết định raw/processed/MFCV.
- Mọi output lâm sàng là decision-support, có human-in-the-loop, có abstention khi dữ liệu không đủ điều kiện.
- Toàn bộ kiến trúc, core technical, AI, product, UI/UX, dashboard, QA, report, workflow và vận hành đều do 1 người (Duy) đảm nhiệm.

## 1. Executive Summary

Mục tiêu dự án là xây dựng một lớp **Clinical Intelligence** tương thích với dữ liệu sEMG/Motion Lab/Noraxon để kiểm tra chất lượng tín hiệu, trích xuất fatigue evidence, diễn giải theo use case phục hồi/y học thể thao/longitudinal/return-to-play, và sinh báo cáo cho bác sĩ/KTV review. Sản phẩm **không** phải thiết bị EMG mới, không thay thế Noraxon/myoRESEARCH, không tự động chẩn đoán bệnh, không tự động quyết định dừng tập hoặc return-to-play.

Chiến lược ưu tiên là **Motion Lab/Noraxon-first → audit dữ liệu thật → offline signal pipeline MVP → dashboard/report pitch-ready → pilot protocol nhỏ → local validation → workflow pilot**. Không claim realtime clinical trước khi có dữ liệu, latency, safety và validation đủ.

Tất cả các module từ technical architecture, signal pipeline, QC/abstention, preprocessing, feature extraction, FRS, inference, routing, clinical interpretation, UI/UX dashboard, và documentation đều do Duy thực hiện.

Vì là dự án solo, self-review bằng automated test và strict adherence to schema được áp dụng.

## 2. Nguyên tắc brainstorm chuẩn quốc tế

| Bước | Mục tiêu | Input | Hoạt động cụ thể | Câu hỏi cần trả lời | Output | Owner chính | Reviewer | Thời lượng |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0. Pre-read & evidence board | Đưa cả hai vào cùng bối cảnh | Implementation Plan Final, demo HTML, quy trình vận hành, định vị chương, paper sEMG | Đọc nhanh; tạo board: Facts / Assumptions / Risks / Questions | Sản phẩm là gì, không là gì? Có claim nào nguy hiểm? | evidence-board.md; assumption-log.md | Duy | N/A | 2 giờ |
| 1. Double Diamond — Discover | Mở rộng hiểu biết người dùng và workflow | Persona bác sĩ/KTV/Motion Lab; use case rehab/RTP/gait | Map stakeholder journey từ chỉ định → đo → QC → report → review | Ai dùng? Quyết định nào cần hỗ trợ? Pain nào Noraxon chưa xử lý? | clinical-workflow-map.md; JTBD draft | Duy | N/A | 3 giờ |
| 2. Design Thinking — Empathize/Define | Chốt problem statement an toàn | User pain, demo hiện tại, product boundary | Viết intended use, non-intended use, clinical safety claim | Có thay bác sĩ không? Có thay Noraxon không? Output được phép nói gì? | intended-use-statement.md; product-boundaries.md | Duy | N/A | 3 giờ |
| 3. Divergent ideation | Sinh nhiều hướng sản phẩm nhưng không overbuild | Use case list, technical options | Brainstorm 20 use cases/module; không đánh giá trong 30 phút đầu | Use case nào có evidence, workflow fit, demo được trong 30 ngày? | idea-backlog.md | Duy | N/A | 2 giờ |
| 4. Convergent selection bằng MoSCoW | Cắt scope cho team 2 người | Idea backlog | Phân loại Must/Should/Could/Won’t | Cái gì phải có để pitch? Cái gì đẩy sau pilot? | prioritization-matrix.md | Duy | N/A | 2 giờ |
| 5. RICE/ICE scoring | Ưu tiên theo impact và effort | MoSCoW list | Score Reach/Impact/Confidence/Effort hoặc Impact/Confidence/Ease | Feature nào tăng khác biệt với Noraxon nhất? Feature nào block kỹ thuật? | rice-scoring.xlsx hoặc md table | Duy | N/A | 2 giờ |
| 6. Risk-first planning | Bắt risk lớn lên trước roadmap | Risk list: raw EMG, MFCV, synthetic demo, overclaim | Risk storming; pre-mortem; define early warning + contingency | Điều gì giết dự án trong 2 tuần? Gate nào phát hiện sớm? | risk-register.md | Duy | N/A | 2 giờ |
| 7. WBS | Chuyển ý tưởng thành module thực thi | Prioritized scope, architecture | Breakdown epics → tasks → outputs → AC → dependencies | Task có đủ nhỏ để bắt tay làm chưa? Ai owner? | wbs.md | Duy | N/A | 3 giờ |
| 8. RACI-lite | Tránh nhập nhằng trách nhiệm | WBS, team capacity | Gán R/A/C/I cho 20 hạng mục | Ai quyết định cuối? Ai review? Module nào không được làm một mình? | raci-matrix.md | Duy | N/A | 1.5 giờ |
| 9. Decision gates | Đặt cửa kiểm soát trước khi scale | Risk register, WBS | Định nghĩa Gate 1–8 với pass/fail/owner | Đi tiếp hay pivot khi không có raw/MFCV/report readable? | decision-gates.md | Duy | N/A | 2 giờ |
| 10. Sprint planning | Đóng gói roadmap thành execution rhythm | WBS, RACI, gates | Sprint 0–5; sprint goal; demo cuối sprint; go/no-go | Cuối sprint demo cái gì? Fail thì cắt gì? | sprint-plan.md | Duy | N/A | 2 giờ |
| 11. Retrospective loop | Tạo cơ chế học nhanh | Sprint board, daily notes | Retro weekly: start/stop/continue; update risk; re-score backlog | Cái gì đang chậm? Có bị thắt cổ chai không? | weekly-retro.md | Duy | N/A | 45 phút/tuần |

## 3. Work Breakdown Structure toàn dự án

| Epic/Module | Mục tiêu | Task con | Owner chính | Reviewer | Dependency | Output | Acceptance criteria | Priority | Phase | Risk nếu làm sai |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Product Strategy | Chốt định vị khác Noraxon, intended use, non-claims | intended use; product boundary; differentiation; pricing/pitch hypothesis | Duy | N/A | Pre-read docs | executive-blueprint.md, product-boundaries.md | Không claim thiết bị mới; không diagnosis; có narrative 30s/2min | P0 | Phase 0 | Bị xem là dashboard generic hoặc copy Noraxon |
| Clinical Workflow | Luồng order→đo→QC→review→report có human-in-loop | workflow map; KTV checklist; review status; escalation | Duy | N/A | Intended use | clinical-workflow.md, human-review-policy.md | Có bước abstention; bác sĩ/KTV quyết định cuối | P0 | Phase 0/4 | Output bypass clinician hoặc không fit KTV |
| Motion Lab/Noraxon Audit | Biết dữ liệu thật lấy được gì | audit checklist; export format; sampling; sync; raw/processed; MFCV | Duy | N/A | Product boundary | audit-checklist.md, technical-audit-memo.md | Chốt scenario A/B/C/D; biết MFCV eligibility | P0 | Phase 1 | Build pipeline sai format, overclaim raw/MFCV |
| Data Ingestion | Đọc synthetic/CSV/Noraxon export | CSV parser; metadata validator; channel map; unit normalization | Duy | N/A | Audit sơ bộ, signal-import-spec | signal-import-spec.md, importer.py | Đọc được 3 file mẫu; lỗi format có message rõ | P0 | Phase 2 | File import sai channel/unit làm feature sai |
| Signal Quality Gate | Không phân tích khi tín hiệu kém | noise; clipping; dropout; contact; motion artifact; usable window | Duy | N/A | Ingestion, protocol | quality-gate-spec.md, qc_v0.1.yaml, tests | Fail phải abstain; warning phải explain; reason code chuẩn | P0 | Phase 2 | Tín hiệu xấu vẫn ra kết luận mỏi/không mỏi |
| Preprocessing | Chuẩn hóa filter/window trước feature | bandpass; notch optional; rectification; smoothing; baseline | Duy | N/A | QC pass/warning | preprocessing-spec.md, preprocessing.py | Deterministic trên golden signal; versioned config | P0 | Phase 2 | Filter sai gây méo MDF/MNF/RMS |
| Feature Extraction | Tạo fatigue evidence explainable | RMS, MAV, MDF, MNF, slopes, onset, entropy optional | Duy | N/A | Preprocessing | feature-extraction-spec.md, features.py | Feature khớp expected output ± tolerance; có units | P0 | Phase 2 | Feature black-box/không reproducible |
| Fatigue Resistance Score | Điểm 0–100 dùng cho trend, không phải chuẩn y khoa | FRS_freq; FRS_onset; amplitude; symmetry; MFCV optional | Duy | N/A | Feature extraction | frs-formula.md, fatigue_rules.py | Không tính FRS khi QC fail; threshold ghi là demo/pilot-tuned | P0 | Phase 2 | Score bị hiểu là diagnostic score cố định |
| Inference/Rule Engine | Ra fatigue status + confidence + evidence basis | rule v0.1; KNN/SVM/LDA baseline option; confidence; abstain | Duy | N/A | FRS, QC | fatigue-rule-engine-spec.md, inference.py | Output có reason codes; không chỉ nhãn 0/1 | P0 | Phase 2 | Overfit, leakage, AI black-box |
| Use Case Routing | Map evidence vào rehab/post-op/RTP/gait/longitudinal | metadata router; routing reason; fallback general | Duy | N/A | Output schema, metadata | use-case-routing-spec.md | Primary/secondary use case có lý do; không đoán thiếu metadata | P1 | Phase 3 | Cùng một fatigue flag bị diễn giải sai bối cảnh |
| Clinical Interpretation | Viết kết luận chức năng có guardrail | summary_vi; meaning_vi; recommended_review; disclaimer | Duy | N/A | Inference, routing | clinical-interpretation-spec.md | Không dùng chẩn đoán; có “KTV/bác sĩ xem xét” | P0 | Phase 3 | Report wording sai tạo rủi ro lâm sàng |
| Dashboard | Pitch-ready workflow 6 màn hình | Import; QC; Evidence; Routing; Report; Longitudinal | Duy | N/A | Output schema, mock API | dashboard-v1.html hoặc React prototype | Có synthetic + sample CSV mode; hiển thị abstention | P0 | Phase 3 | Demo đẹp nhưng overclaim/không có safety |
| Report Generation | Xuất report HTML/PDF/Markdown | report template; technical appendix; sign-off; disclaimer | Duy | N/A | Clinical interpretation | clinical_report_v0.1.md/html | Có reviewer sign-off; report fail nếu thiếu review trong pilot | P1 | Phase 3/6 | Báo cáo không đọc được hoặc sai claim |
| Backend/API | Contract cho dashboard và pipeline | OpenAPI; /import; /quality; /analyze; /report; /longitudinal | Duy | N/A | Data model, output schema | openapi.yaml, FastAPI mock | Contract stable; error schemas; versioned analysis_id | P1 | Phase 2/3 | Frontend/backend lệch schema, khó tích hợp |
| Data Model | Lưu session/feature/report/audit có version | session; muscle; protocol; feature rows; analysis run; audit | Duy | N/A | Output schema | data-model.md, output-schema.json | Mỗi report truy ngược được protocol/config/model version | P0 | Phase 2 | Không reproducible, không audit được |
| Security/Audit | On-prem, PHI tối thiểu, audit actions | RBAC-lite; audit log; raw data policy; de-id | Duy | N/A | Clinical workflow | security-audit-baseline.md | Không commit raw PHI; audit upload/analyze/review/export | P1 | Phase 3/6 | Dữ liệu y tế rò rỉ hoặc không trace được |
| QA/Validation | Chứng minh pipeline đúng và không leakage | golden tests; QC fail tests; subject split plan; UAT | Duy | N/A | Pipeline modules | test-plan.md, validation-plan.md | Pass golden tests; có leakage checklist; clinician feedback form | P0 | Phase 2/5 | Metric ảo, demo fail trước stakeholder |
| Pilot Operations | Thiết kế pilot nhỏ thực tế | muscle target; tasks; labels; metadata; training; schedule | Duy | N/A | Dashboard/report v1 | pilot-protocol.md, ktv-checklist.md | Protocol có inclusion/exclusion, label, repeatability | P1 | Phase 4 | Pilot thu data unusable hoặc quá nặng workflow |
| Business/Pitch Materials | Bán đúng narrative và decision gates | deck; one-page memo; demo script; FAQ; competitor comparison | Duy | N/A | Product strategy, dashboard | executive-memo.md, pitch-deck-outline.md | Sếp hiểu Noraxon là nền, không là đối thủ trực diện | P1 | Phase 0/3 | Stakeholder từ chối vì trùng Noraxon hoặc quá risky |

## 4. Kế hoạch theo ngày — 30 ngày đầu


### Day 1 — 2026-07-10 — Product Boundary & Intended Use

- Sáng: viết intended-use v0.1, non-intended-use, users bác sĩ/KTV/Motion Lab.
- Chiều: chốt product boundary: không thiết bị EMG, không thay Noraxon, không diagnosis.
- Cuối ngày: tạo decision record D1 và list claim cấm.


- Sáng: audit demo HTML hiện tại, đánh dấu câu overclaim/realtime/stop exercise.
- Chiều: tạo product-boundaries.md v0.1 và bảng “allowed/prohibited wording”.
- Cuối ngày: mở sprint-board.md với cột Backlog/Doing/Review/Done.


**Output:** intended-use-statement.md, product-boundaries.md, sprint-board.md  

**Done criteria:** Intended use có user, context, output, claim cấm; demo wording risk đã đánh dấu.  

**Quyết định / risk:** Chốt non-diagnosis, human-in-loop, offline-first. Risk: overclaim clinical/realtime.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 2 — 2026-07-11 — Differentiation & Executive Narrative

- Sáng: viết positioning 30s/2min, Noraxon as acquisition layer vs our clinical intelligence.
- Chiều: định nghĩa 5 giá trị: QC, fatigue evidence, routing, longitudinal, report.
- Cuối ngày: owner map 65/35 core technical.


- Sáng: làm competitor matrix: Noraxon/myoRESEARCH vs sản phẩm.
- Chiều: chuyển thành executive-blueprint.md và FAQ stakeholder.
- Cuối ngày: cập nhật risk Noraxon fatigue report.


**Output:** executive-blueprint.md, differentiation.md, FAQ.md  

**Done criteria:** Có câu chuyện rõ: “Noraxon đo; chúng ta diễn giải phục hồi”. Workload phân bổ sơ bộ.  

**Quyết định / risk:** Chốt pitch boundary. Risk: bị coi là copy Noraxon.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 3 — 2026-07-12 — Audit Checklist & Brainstorm Convergence

- Sáng: tạo audit checklist kỹ thuật: raw/processed, sampling, sync, MFCV, export.
- Chiều: risk-first pre-mortem và scenario A/B/C/D.
- Cuối ngày: chốt Gate 1–3 draft.


- Sáng: tạo JTBD và user journey bác sĩ/KTV.
- Chiều: MoSCoW + RICE scoring backlog demo.
- Cuối ngày: sprint-board cập nhật WIP limit và deadlines.


**Output:** audit-checklist.md, JTBD.md, prioritization-matrix.md, decision-gates-draft.md  

**Done criteria:** Mỗi task backlog có owner, output, AC, dependency.  

**Quyết định / risk:** Dependency: audit checklist chặn Motion Lab meeting. Risk: scope creep.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 4 — 2026-07-13 — Motion Lab/Noraxon Audit Prep & Data Contract

- Sáng: soạn danh sách câu hỏi technical deep-dive cho Motion Lab.
- Chiều: define output-schema v0.1 gồm QC/features/FRS/interpretation.
- Cuối ngày: review schema .


- Sáng: soạn email/slide audit meeting và sample-data request.
- Chiều: tạo CSV sample template và metadata form.
- Cuối ngày: kiểm tra schema có đủ cho dashboard.


**Output:** audit-meeting-pack.md, output-schema.json v0.1, sample_csv_template.csv  

**Done criteria:** Output schema validate được, CSV template có timestamp/channel/unit/metadata.  

**Quyết định / risk:** Dependency: schema chặn backend/dashboard mock. Risk: thiếu metadata cơ/side/protocol.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 5 — 2026-07-14 — Architecture Core & Repo Skeleton

- Sáng: vẽ architecture: ingestion→metadata→QC→preprocess→feature→FRS→routing→report.
- Chiều: data model analysis_run, config versioning, audit event.
- Cuối ngày: ADR offline-first, signal-first, abstention-first.


- Sáng: dựng repo skeleton tối thiểu docs/packages/data/reports.
- Chiều: tạo README, Makefile draft, folders semg-core/tests.
- Cuối ngày: kiểm tra naming conventions.


**Output:** high-level-architecture.md, data-model.md, repo skeleton, ADRs  

**Done criteria:** Repo có cấu trúc chạy 30 ngày; kiến trúc có module boundary và version IDs.  

**Quyết định / risk:** Dependency: architecture chặn implementation. Risk: single point of failure nếu Duy không document.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 6 — 2026-07-15 — Synthetic Data Generator & Ingestion Adapter

- Sáng: define signal assumptions: Fs, band, MVC/protocol, fatigue trend.
- Chiều: review generator design để không giả lập quá “đẹp”.
- Cuối ngày: viết expected feature behavior cho golden signals.


- Sáng: code generate_synthetic_semg.py với fresh/fatigue/noise/dropout/clipping.
- Chiều: code csv_importer.py + metadata_validator.py.
- Cuối ngày: xuất 5 sample files và manifest.


**Output:** generate_synthetic_semg.py, csv_importer.py, synthetic manifest  

**Done criteria:** Importer đọc sample; generator tạo pass/fail cases reproducible bằng seed.  

**Quyết định / risk:** Dependency: importer chặn QC. Risk: synthetic quá ảo.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 7 — 2026-07-16 — Weekly Review 1 & Audit Decision

- Sáng: review tất cả artifacts Days 1–6, fix schema gaps.
- Chiều: chốt Gate 1 question list và audit decision memo template.
- Cuối ngày: approve Sprint 1 start.


- Sáng: chạy demo narrative dry-run 5 phút.
- Chiều: cập nhật sprint board, burndown, blocker list.
- Cuối ngày: viết weekly-review-1.md.


**Output:** weekly-review-1.md, updated risk register, audit-decision-memo-template.md  

**Done criteria:** Tuần 1 có decision log, risk updated, Sprint 1 backlog locked.  

**Quyết định / risk:** Weekly review/risk review/planning. Risk: workload không cân bằng.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 8 — 2026-07-17 — Signal Quality Gate v0.1

- Sáng: define QC checks: sampling, duration, clipping, dropout, noise floor, powerline, motion artifact.
- Chiều: thresholds v0.1 + reason codes + abstention policy.
- Cuối ngày: review QC outputs with dashboard needs.


- Sáng: implement qc.py skeleton và tests for clipping/dropout/noise.
- Chiều: tạo qc-result schema + UI copy for fail/warning/pass.
- Cuối ngày: chạy QC trên 5 synthetic samples.


**Output:** quality-gate-spec.md, qc_v0.1.yaml, qc.py, qc tests  

**Done criteria:** QC fail không cho FRS; mỗi fail có reason và action.  

**Quyết định / risk:** Dependency: QC chặn feature/inference. Risk: threshold quá cứng/quá lỏng.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 9 — 2026-07-18 — Preprocessing Pipeline

- Sáng: define filter/window config: bandpass, notch optional, rectification, smoothing.
- Chiều: implement preprocessing.py core hoặc pair-code .
- Cuối ngày: compare plots raw vs processed.


- Sáng: viết preprocessing unit tests và config loader.
- Chiều: tạo chart preview raw/processed cho dashboard.
- Cuối ngày: document parameter defaults.


**Output:** preprocessing-spec.md, preprocessing.py, config tests, raw-vs-processed plot  

**Done criteria:** Golden signal preprocessing deterministic; config version recorded.  

**Quyết định / risk:** Dependency: preprocessing chặn features. Risk: filter làm méo phổ.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 10 — 2026-07-19 — Feature Extraction Core I

- Sáng: implement RMS/MAV, windowing, usable window ratio.
- Chiều: implement MDF/MNF bằng Welch/FFT + unit tests.
- Cuối ngày: generate expected_features.json.


- Sáng: hỗ trợ windowing tests, tolerance specs.
- Chiều: build feature table CSV export và chart data contract.
- Cuối ngày: review feature names/units.


**Output:** features.py, windowing.py, feature_table_spec.md, expected_features.json  

**Done criteria:** RMS/MAV/MDF/MNF chạy trên 3 sessions; có units và tolerance.  

**Quyết định / risk:** Dependency: features chặn FRS/inference. Risk: MDF/MNF sai do PSD implementation.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 11 — 2026-07-20 — Feature Extraction Core II — Slopes & Onset

- Sáng: implement MDF/MNF slope, RMS slope, fatigue onset heuristics.
- Chiều: define confidence of slope based on usable windows/R².
- Cuối ngày: write feature-extraction-spec.md v1.


- Sáng: create test cases for stable vs fatigued trend.
- Chiều: generate plots for fatigue evidence panel.
- Cuối ngày: verify dashboard data arrays.


**Output:** trend_features.py, feature-extraction-spec.md, evidence plots  

**Done criteria:** Slope/onset có reason basis; no onset nếu confidence thấp.  

**Quyết định / risk:** Dependency: slope chặn FRS. Risk: onset quá nhạy noise.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 12 — 2026-07-21 — FRS Formula & Dashboard Wireframe

- Sáng: define FRS_freq, FRS_onset, FRS_amplitude, symmetry optional.
- Chiều: implement FRS v0.1 with abstain guard.
- Cuối ngày: document thresholds as demo-only/pilot-tuned.


- Sáng: wireframe 6 màn hình: Import, QC, Evidence, Routing, Report, Trend.
- Chiều: map output schema to UI components.
- Cuối ngày: review FRS visual labels.


**Output:** frs-formula.md, fatigue_rules.py v0.1, dashboard-wireframe.md  

**Done criteria:** FRS không tính khi QC fail; UI label không gọi là diagnosis.  

**Quyết định / risk:** Dependency: FRS chặn report/demo. Risk: score 0–100 bị hiểu sai.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 13 — 2026-07-22 — MFCV Eligibility & Audit Follow-up

- Sáng: write mfcv-eligibility-spec: linear array, IED, orientation, Fs, correlation.
- Chiều: prepare fallback logic “MFCV unavailable”.
- Cuối ngày: update Gate 3 pass/fail.


- Sáng: implement cv_eligibility_check.py stub and schema fields.
- Chiều: update metadata form for electrode geometry.
- Cuối ngày: test UI abstain/optional state.


**Output:** mfcv-eligibility-spec.md, cv_eligibility_check.py, metadata form v0.2  

**Done criteria:** MFCV không bao giờ được report nếu thiếu cấu hình.  

**Quyết định / risk:** Dependency: Motion Lab audit data. Risk: MFCV overclaim.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 14 — 2026-07-23 — Inference/Rule Engine v0.1

- Sáng: define fatigue_status states: no_evidence, fatigue_evidence, inconclusive, abstained.
- Chiều: implement rule_engine + confidence + decision_basis.
- Cuối ngày: review output wording .


- Sáng: write inference tests: QC fail, weak features, strong fatigue, low confidence.
- Chiều: build JSON report fixture.
- Cuối ngày: update API contract draft.


**Output:** inference.py, confidence.py, abstention.py, inference fixtures  

**Done criteria:** Output không chỉ nhãn; có basis, confidence, requires_review.  

**Quyết định / risk:** Dependency: feature/FRS. Risk: rule quá black-box hoặc overfit threshold.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 15 — 2026-07-24 — Offline Pipeline Integration

- Sáng: integrate importer→QC→preprocess→features→FRS→inference.
- Chiều: implement run_offline_analysis.py CLI.
- Cuối ngày: run 5 synthetic sessions and compare output.


- Sáng: build CLI help, config file, output folder structure.
- Chiều: implement regression script and logs.
- Cuối ngày: collect bugs and assign fixes.


**Output:** run_offline_analysis.py, outputs/*.json, bug list  

**Done criteria:** End-to-end succeeds on pass/warn/fail samples; fail produces abstention report.  

**Quyết định / risk:** Dependency: all core modules. Risk: integration mismatch.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 16 — 2026-07-25 — Weekly Review 2 & Gate 4 Dry Run

- Sáng: technical review offline outputs; verify version metadata.
- Chiều: Gate 4 dry-run: Offline Pipeline Works.
- Cuối ngày: decide fixes for Sprint 2 hardening.


- Sáng: demo CLI to Duy; collect UX pain.
- Chiều: weekly risk review + sprint replanning.
- Cuối ngày: update validation evidence.


**Output:** weekly-review-2.md, gate4-dryrun.md, updated validation evidence  

**Done criteria:** At least 3 pass sessions + 2 fail sessions documented with expected behavior.  

**Quyết định / risk:** Weekly review/risk review. Risk: false confidence if only synthetic pass.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 17 — 2026-07-26 — API Contract & Backend Mock

- Sáng: define OpenAPI schemas for session/QC/features/report.
- Chiều: review API semantics: sync vs async analysis, errors, versioning.
- Cuối ngày: approve v0.1.


- Sáng: implement FastAPI mock endpoints /import /quality /analyze /report.
- Chiều: connect endpoints to offline pipeline or fixture mode.
- Cuối ngày: API smoke tests.


**Output:** openapi.yaml, FastAPI mock, API smoke tests  

**Done criteria:** Dashboard can call mock API; errors standardized.  

**Quyết định / risk:** Dependency: output schema. Risk: API drift.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 18 — 2026-07-27 — Clinical Report Template v0.1

- Sáng: define report sections and clinical phrase bank.
- Chiều: write interpretation rules for longitudinal/post-op/general.
- Cuối ngày: review prohibited claims.


- Sáng: build clinical_report_template.md/html.
- Chiều: add reviewer sign-off, limitations, QC summary.
- Cuối ngày: render sample report from JSON.


**Output:** clinical_report_template.md/html, phrase-bank.md, sample report  

**Done criteria:** Report readable, no diagnosis, includes evidence and “requires review”.  

**Quyết định / risk:** Dependency: inference output. Risk: wording unsafe.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 19 — 2026-07-28 — Dashboard v1 — Import & QC Screens

- Sáng: define UI states and evidence hierarchy.
- Chiều: review Import/Context and QC screen .
- Cuối ngày: adjust schema fields if needed.


- Sáng: build Import/Context screen with synthetic/CSV selector.
- Chiều: build Signal Quality screen with pass/warn/fail and reason codes.
- Cuối ngày: integrate API mock.


**Output:** dashboard import screen, QC screen, UI state screenshots  

**Done criteria:** User can load session and see QC; fail blocks next analysis visually.  

**Quyết định / risk:** Dependency: API/QC. Risk: UI lets user ignore critical fail.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 20 — 2026-07-29 — Dashboard v1 — Evidence & FRS Screens

- Sáng: define chart interpretation labels for RMS/MDF/MNF/slope.
- Chiều: validate FRS card copy and confidence display.
- Cuối ngày: review evidence screen.


- Sáng: implement Feature Evidence charts.
- Chiều: implement FRS/confidence/decision_basis cards.
- Cuối ngày: connect to sample JSON.


**Output:** evidence screen, FRS card, confidence component  

**Done criteria:** Evidence screen explains why, not just status.  

**Quyết định / risk:** Dependency: feature output. Risk: chart misleads due normalization.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 21 — 2026-07-30 — Use Case Routing & Clinical Interpretation UI

- Sáng: implement route_use_case logic from metadata.
- Chiều: define interpretation templates for longitudinal/post-op/RTP/general.
- Cuối ngày: review safety wording.


- Sáng: implement Use Case Routing panel.
- Chiều: implement Clinical Interpretation panel with “KTV/bác sĩ xem xét”.
- Cuối ngày: create 4 metadata scenarios.


**Output:** use_case_router.py, interpretation templates, routing UI  

**Done criteria:** Each route has reasons; missing metadata triggers general/inconclusive.  

**Quyết định / risk:** Dependency: metadata. Risk: routing đoán sai clinical context.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 22 — 2026-07-31 — Longitudinal Trend & Side-to-side Demo

- Sáng: define longitudinal comparison rules: same muscle, protocol, normalization.
- Chiều: implement trend delta calculations.
- Cuối ngày: write guardrail: no compare if mismatch.


- Sáng: build longitudinal trend chart.
- Chiều: build side-to-side comparison card with asymmetry.
- Cuối ngày: test mismatch protocol warning.


**Output:** longitudinal module, side-to-side card, compare guardrails  

**Done criteria:** Trend only shown when same protocol/muscle/side metadata valid.  

**Quyết định / risk:** Dependency: data model. Risk: invalid longitudinal comparison.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 23 — 2026-08-01 — Report Export & Review Workflow

- Sáng: define human review statuses: draft, KTV_reviewed, clinician_signed, exported.
- Chiều: define audit events for review/export.
- Cuối ngày: approve report gating.


- Sáng: implement Review screen checklist and comments.
- Chiều: implement Report preview/export markdown/html.
- Cuối ngày: connect sample report.


**Output:** review screen, report preview, audit event spec  

**Done criteria:** Report export shows reviewer/sign-off state; pilot mode blocks final without review.  

**Quyết định / risk:** Dependency: report template. Risk: missing human-in-loop.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 24 — 2026-08-02 — Weekly Review 3 & Demo Freeze Candidate

- Sáng: end-to-end technical walkthrough dashboard + CLI.
- Chiều: Gate 5 dry-run: Clinical Report Readability.
- Cuối ngày: list freeze blockers.


- Sáng: run 7-minute pitch script draft.
- Chiều: weekly risk review, QA bug triage.
- Cuối ngày: update demo-script.md.


**Output:** weekly-review-3.md, gate5-dryrun.md, demo-script.md v0.1  

**Done criteria:** Demo candidate has no P0 bugs; report readable by non-engineer.  

**Quyết định / risk:** Weekly review/risk review. Risk: too many UI bugs before demo.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 25 — 2026-08-03 — Hardening: QA, Golden Tests, Error States

- Sáng: review golden test failures and define tolerance.
- Chiều: fix core pipeline bugs and version metadata.
- Cuối ngày: approve analytical_validation_mvp0 draft.


- Sáng: create QA test-cases.csv for import/QC/features/inference/report.
- Chiều: implement run_golden_signal_tests.py.
- Cuối ngày: run regression and log results.


**Output:** test-cases.csv, golden test script, analytical_validation_mvp0.md  

**Done criteria:** All P0 tests pass or have documented exception.  

**Quyết định / risk:** Dependency: pipeline stable. Risk: regressions hidden.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 26 — 2026-08-04 — Pitch Materials & Stakeholder FAQ

- Sáng: create technical decision memo: rule vs ML, MFCV optional, offline-first.
- Chiều: prepare answers to hard questions: Noraxon, raw EMG, synthetic, validation.
- Cuối ngày: review pitch deck outline.


- Sáng: build executive memo and pitch-deck-outline.
- Chiều: update demo script with objections and transitions.
- Cuối ngày: run 15-minute mock pitch.


**Output:** executive-memo.md, pitch-deck-outline.md, stakeholder-FAQ.md  

**Done criteria:** FAQ answers Noraxon/realtime/MFCV/raw EMG clearly.  

**Quyết định / risk:** Dependency: product narrative. Risk: sếp hiểu sai scope.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 27 — 2026-08-05 — Pilot Protocol Design I

- Sáng: choose candidate protocol: quad isometric 60s / biceps 60s; define metadata.
- Chiều: define labels: RPE, MVC/force if available, KTV onset, pain/fatigue notes.
- Cuối ngày: write protocol draft.


- Sáng: create KTV measurement checklist and eForm fields.
- Chiều: create pilot data collection sheet.
- Cuối ngày: review workflow time burden.


**Output:** pilot-protocol.md v0.1, ktv-checklist.md, pilot-data-sheet.csv  

**Done criteria:** Protocol has muscle, task, duration, rest, labels, metadata, exclusion criteria.  

**Quyết định / risk:** Dependency: clinical feedback. Risk: protocol too hard to repeat.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 28 — 2026-08-06 — Pilot Protocol Design II & Validation Plan

- Sáng: define validation metrics: QC pass rate, feature reliability, sensitivity-first, clinician usefulness.
- Chiều: define leakage-free split and sample size hypothesis.
- Cuối ngày: write local validation design.


- Sáng: build clinician/KTV feedback form and UAT script.
- Chiều: update validation automation plan.
- Cuối ngày: risk review pilot readiness.


**Output:** validation-plan.md, UAT-script.md, feedback-form.md  

**Done criteria:** Validation plan includes analytical, clinical usefulness, operational metrics.  

**Quyết định / risk:** Dependency: pilot protocol. Risk: validation claims too strong.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 29 — 2026-08-07 — Security/Audit & Operational Readiness

- Sáng: define minimal RBAC and audit events: upload/analyze/review/export/config change.
- Chiều: data handling: raw on-prem, de-id features, no raw in repo.
- Cuối ngày: review release checklist.


- Sáng: write security-audit-baseline.md.
- Chiều: create release-checklist.md and operational readiness checklist.
- Cuối ngày: verify demo artifacts storage.


**Output:** security-audit-baseline.md, release-checklist.md, ops-readiness.md  

**Done criteria:** All user-visible report/export actions have audit plan; no PHI in repo.  

**Quyết định / risk:** Dependency: workflow. Risk: pilot not approvable due audit/security.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 30 — 2026-08-08 — Final Demo Rehearsal & Gate 6 Readiness

- Sáng: full technical audit: pipeline, schema, report, risk, gates.
- Chiều: Gate 6 Pilot Readiness self-assessment.
- Cuối ngày: approve Day-30 final package or assign blockers.


- Sáng: run final demo rehearsal, record issues.
- Chiều: polish dashboard/report copies and demo script.
- Cuối ngày: package artifacts and changelog.


**Output:** final-demo-package, gate6-self-assessment.md, changelog.md  

**Done criteria:** Demo can be run from clean repo; all P0 artifacts linked.  

**Quyết định / risk:** Dependency: all modules. Risk: integration bugs in final demo.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


### Day 31 — 2026-08-09 — Day-30 Executive Review & Roadmap Lock

- Sáng: present technical architecture, pipeline evidence, risk register, gates.
- Chiều: lock 60–90 day roadmap and Phase 4–6 pilot plan.
- Cuối ngày: final decision log: go/no-go/conditional go.


- Sáng: present dashboard/report demo and operational readiness.
- Chiều: collect stakeholder feedback, update backlog and owners.
- Cuối ngày: archive artifacts and next sprint tasks.


**Output:** day30-executive-review.md, 60-90-day-roadmap.md, final decision log  

**Done criteria:** Stakeholder can decide: proceed audit/pilot, revise scope, or hold. Next 2 sprints ready.  

**Quyết định / risk:** Final review/risk review/planning. Risk: feedback creates scope creep without gate.  

**Daily sync:** 15 phút đầu ngày để xác nhận blocker, 15 phút cuối ngày để cập nhật artifact và task chuyển ngày sau.


## Roadmap 60–90 ngày sau 30 ngày đầu

| Giai đoạn | Ngày | Mục tiêu | Duy | N/A | Output/Gate |
| --- | --- | --- | --- | --- | --- |
| Days 31–45 | Phase 4 mở rộng | Hoàn thiện pilot protocol với clinical/Motion Lab feedback | Finalize protocol, MFCV decision, feature/rule update | Training pack, data sheet, dashboard fixes | Gate 6 chính thức |
| Days 46–60 | Phase 5 Local Validation I | Thu 10–20 session đầu, kiểm tra QC/feature reliability | Analyze QC pass, feature distributions, threshold tuning | Run QA/UAT, synthesize clinician/KTV feedback | Validation interim report |
| Days 61–75 | Phase 5 Local Validation II | Kiểm tra FRS/rule/usefulness và leakage-safe metrics | Rule/model comparison, confidence calibration | Report improvements, dashboard/report iterations | Gate 7 Local Validation |
| Days 76–90 | Phase 6 Workflow Pilot Prep | Chuẩn bị workflow pilot có audit/human review/report export | Technical go/no-go, deployment constraints | Pilot ops, training, support, release checklist | Gate 8 Workflow Pilot Go/No-Go |

## 6. Sprint Plan

| Sprint | Thời gian | Sprint goal | Backlog & task | Deliverables | Demo cuối sprint | Acceptance criteria | Risks | Go/No-Go |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sprint 0: Alignment & Repositioning | Days 1–3 | Chốt định vị, boundary, brainstorming, risk-first plan | intended use, boundary, risk, differentiation, demo audit, JTBD, sprint board, MoSCoW. | executive-blueprint, product-boundaries, risk-register, sprint-board | Narrative 7 phút + risk review | Không overclaim; có WBS và owner rõ | Noraxon overlap; realtime wording | Gate 1 Product Differentiation |
| Sprint 1: Audit & Core Signal Feasibility | Days 4–9 | Chuẩn bị audit, schema, skeleton, synthetic/ingestion/QC/preprocessing | audit checklist, architecture, QC, preprocessing, CSV/importer, synthetic generator, tests, repo. | audit pack, output-schema, importer, QC v0.1, preprocessing v0.1 | CLI đọc sample và QC pass/fail | Biết data cần gì; QC fail abstain | Thiếu raw, MFCV unclear | Gate 2 Technical Feasibility prep; Gate 3 MFCV prep |
| Sprint 2: Offline Pipeline MVP | Days 10–17 | Feature extraction, FRS, inference, offline E2E | features, slopes, FRS, inference, integration, tests, plots, CLI, regression. | features.py, frs, rule engine, run_offline_analysis.py, JSON outputs | Offline pipeline trên 5 sessions | 3 pass + 2 fail; reason codes; version metadata | Feature wrong, thresholds arbitrary | Gate 4 Offline Pipeline Works |
| Sprint 3: Dashboard & Report MVP | Days 18–25 | API mock, dashboard v1, report, review workflow | API schema, interpretation, routing, review gates, FastAPI mock, UI screens, report preview/export. | openapi, dashboard, clinical report, review screen | 7-minute pitch demo | Import→QC→Evidence→Report→Trend chạy được | UI overclaim, report unreadable | Gate 5 Clinical Report Readability |
| Sprint 4: Pilot Protocol & Validation Setup | Days 26–35 | Pitch pack, pilot protocol, validation, ops readiness | technical decision memo, validation metrics, Gate 6, deck, KTV checklist, UAT, security/audit. | pilot-protocol, validation-plan, release-checklist, executive memo | Pilot readiness review | Protocol repeatable; validation plan leakage-safe | Pilot burden, weak labels | Gate 6 Pilot Readiness |
| Sprint 5+: Local Validation / Workflow Pilot | Days 36–90 | Thu data nhỏ, validate feature/report usefulness, workflow pilot | validation analysis, threshold tuning, model/rule decisions, pilot ops, QA, dashboard fixes, training/report export. | local validation report, revised thresholds, pilot closeout | Clinician/KTV feedback demo | QC pass target, usefulness ≥4/5, unsafe conclusion =0 | Dataset nhỏ, adoption low | Gate 7 Local Validation; Gate 8 Workflow Pilot Go/No-Go |

## 7. RACI Matrix

| Hạng mục | Duy | N/A |
| --- | --- | --- |
| Intended Use | A/R | C |
| Product Boundary | A/R | C |
| Clinical Workflow | C | A/R |
| Technical Architecture | A/R | C |
| Signal Import | C | A/R |
| Quality Gate | A/R | C/R test |
| Preprocessing | A/R | C/R test |
| Feature Extraction | A/R | R support |
| FRS Formula | A/R | C |
| Inference Rule | A/R | C/R test |
| Use Case Routing | A/R | C |
| Dashboard | C | A/R |
| Report Template | C/A wording | R/A |
| API Contract | A/C | R |
| Data Model | A/R | C |
| Security/Audit | C | A/R |
| Validation Plan | A/C | R |
| Pilot Protocol | C | A/R |
| Pitch Deck / Executive Memo | C | A/R |

**Cách dùng RACI-lite cho team 2 người:** RACI không dùng để tăng thủ tục, mà để tránh mơ hồ. Mỗi hạng mục chỉ cần một người Accountable cuối cùng. Người còn lại luôn là reviewer hoặc consulted. Với các mục clinical safety như intended use, abstention, report wording, product boundary, cả hai phải cùng review dù chỉ một người accountable.

## 8. Decision Gates

| Gate | Câu hỏi cần trả lời | Dữ liệu cần có | Pass criteria | Fail criteria | Quyết định nếu pass/fail | Phụ trách | - |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gate 1 — Product Differentiation | Sản phẩm có khác Noraxon generic fatigue/report không? | Positioning, competitor matrix, demo narrative | Stakeholder hiểu “clinical intelligence layer”; không thiết bị mới; không diagnosis | Pitch vẫn là RMS/MDF fatigue dashboard generic | Pass: tiếp tục demo spec; Fail: rewrite positioning, bỏ feature trùng | quyết định boundary/differentiation competitor slide/demo copy | - |
| Gate 2 — Technical Feasibility | Có đọc/nhận được dữ liệu usable không? | Audit checklist, sample export, format, sampling, metadata | Biết raw/processed, format, Fs, sync, metadata tối thiểu | Không sample, không export path, không metadata | Pass: build adapter; Fail: processed metrics mode hoặc pilot riêng | audit technical, scenario A/B/C/D sample import template và data request | - |
| Gate 3 — MFCV Feasibility | Có đủ cấu hình tính MFCV không? | Electrode geometry, IED, orientation, Fs, adjacent channel quality | Linear array/IED/placement/Fs đủ; correlation acceptable | Sensor rời, thiếu IED, sampling thấp, placement không chuẩn | Pass: MFCV module; Fail: không report MFCV, chuyển sEMG feature-based | MFCV eligibility rules metadata form, UI unavailable state | - |
| Gate 4 — Offline Pipeline Works | Pipeline offline có chạy đúng và abstain đúng không? | Synthetic/CSV sessions, test outputs | 3 pass + 2 fail; QC fail abstain; features explainable | Crash, feature inconsistent, fail vẫn ra score | Pass: dashboard integration; Fail: hardening Sprint 2 | fix core pipeline regression tests, CLI logs | - |
| Gate 5 — Clinical Report Readability | Bác sĩ/KTV đọc hiểu và không overclaim không? | Report template, sample report, phrase bank | Summary chức năng, evidence basis, disclaimer, human review | Có diagnosis/treatment command/return-to-play decision | Pass: demo to stakeholder; Fail: rewrite copy, clinical review | interpretation guardrails report template and UX wording | - |
| Gate 6 — Pilot Readiness | Có đủ protocol, ops, security, validation để pilot nhỏ không? | Pilot protocol, checklist, validation, audit, release checklist | Protocol repeatable; metadata/labels; human review; audit plan | Workflow mơ hồ, thiếu consent/training/audit | Pass: start local pilot; Fail: tabletop simulation only | technical go/no-go ops readiness and training checklist | - |
| Gate 7 — Local Validation | Feature/FRS/rule có đủ tin trên dữ liệu local không? | Pilot dataset, QC stats, reliability, clinician feedback | Usable ratio đạt target; report usefulness ≥4/5; no unsafe conclusion | QC fail quá nhiều; clinician không thấy useful; leakage | Pass: workflow pilot; Fail: retune protocol/QC/report | validation analysis, threshold decisions QA/UAT, feedback synthesis | - |
| Gate 8 — Workflow Pilot Go/No-Go | Có đưa vào workflow thử nghiệm được không? | Validation report, ops metrics, support plan, audit logs | Không làm chậm KTV quá mức; review/export/audit hoạt động | Adoption thấp, unsafe wording, support burden cao | Pass: limited workflow pilot; Fail: continue offline research/demo | final technical risk pilot ops and stakeholder comms | - |

## 9. Risk Register

| Risk | Severity | Probability | Impact | Mitigation | Owner | Early warning signal | Contingency plan |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Noraxon đã có fatigue report | High | High | Demo RMS/MDF generic bị coi là trùng sản phẩm có sẵn | Định vị Clinical Intelligence; use case routing; longitudinal; Vinmec workflow; report tiếng Việt | Duy | Stakeholder hỏi “Noraxon đã có rồi?” trong 5 phút đầu | Chuẩn bị slide “Noraxon đo gì vs chúng ta diễn giải gì” |
| Không lấy được raw EMG | High | Medium | Không validate feature/model sâu | Audit export/API/license; hỗ trợ processed metrics adapter | Duy | Motion Lab chỉ xuất PDF/report ảnh | Scenario C: dùng processed metrics; xin sample export; pilot riêng |
| Synthetic demo bị coi là ảo | High | High | Không thuyết phục triển khai | Thêm Import/Context màn hình; synthetic disclaimer; sample CSV mode | Duy | Người xem hỏi “data thật đâu?” | Ngày 4–8 ưu tiên xin 1–3 sample export hoặc tạo CSV format giả Noraxon |
| Realtime claim quá sớm | High | Medium | Bị hỏi latency/safety/regulatory | Offline-first; near-real-time demo; realtime chỉ sau validation | Duy | Demo title dùng “real-time clinical warning” | Đổi wording: “near-real-time / offline clinical MVP” |
| Tín hiệu sEMG nhiễu | High | High | False fatigue hoặc miss fatigue | QC gate; artifact flags; bad channel; abstention | Duy | Usable window ratio <70% | Yêu cầu đo lại; chỉnh electrode/skin prep; chỉ report QC |
| MFCV không đủ cấu hình | High | Medium | Overclaim MFCV | MFCV eligibility; chỉ report MFCV khi có linear array/IED/sampling | Duy | Không biết inter-electrode distance hoặc sensor rời | MVP không MFCV; làm sEMG feature fatigue trước |
| Label fatigue yếu | Medium | High | Model học nhãn nhiễu | RPE + force/MVC + KTV annotation + protocol endpoint | Duy | Clinician label không đồng thuận | Rule-based evidence trước; model chỉ exploratory |
| Dataset nhỏ | High | High | Overfit, metric không generalize | Classical/rule first; leave-subject/session-out; confidence interval | Duy | F1 cao nhưng ít subject/session | Không public claim performance; báo validation local |
| Model overfit | High | Medium | Sai khi triển khai | Feature simplicity, regularization, external validation | Duy | Train accuracy >> validation | Quay về rule engine + feature trend |
| Window leakage | High | Medium | Metric ảo cực cao | Split theo subject/session trước windowing; leakage checklist | Duy | Random split windows cùng session | Rewrite validation; invalid metric report |
| Dashboard overclaim | High | Medium | Rủi ro lâm sàng/regulatory | Approved wording; disclaimer; human review status | Duy | UI nói “diagnosis/stop immediately/fit to play” | Block release; sửa copy; clinical review |
| Report wording sai | High | Medium | Bác sĩ/KTV hiểu nhầm | Report phrase bank; Duy tự review; clinical reviewer sign-off | Duy | Report có câu quyết định điều trị tự động | Fail Gate 5; dùng “gợi ý review” |
| Workflow không fit KTV | Medium | High | Không adoption | Co-design; 5-click path; checklist giấy/online | Duy | KTV mất >10 phút nhập metadata | Cắt fields, dùng templates, batch import |
| Thiếu audit/human review | High | Medium | Không pilot clinical được | Audit upload/analyze/review/export; reviewer sign-off | Duy | Không biết ai phê duyệt report | Block workflow pilot; implement audit first |
| Scope creep | Medium | High | Quá tải (solo developer) | MoSCoW; WIP limit chặt chẽ; defer EMR/FHIR/DL/realtime | Duy | Backlog tăng >20%/tuần | Cut to Day-30 demo: import-QC-feature-report |
| Quá tải công việc solo | High | High | Chậm, lỗi core | Sử dụng automated tests; checklist nghiêm ngặt; daily WIP | Duy | Chậm tiến độ, block >3 modules | Rebalance weekly; giảm scope những feature không cốt lõi |

## 10. Output template cho từng ngày

```markdown
# Daily Execution Note — Day X — YYYY-MM-DD

## 1. Mục tiêu hôm nay
- Mục tiêu 1:
- Mục tiêu 2:

## 2. File/tài liệu/code phải tạo
| Artifact | Owner | Reviewer | Trạng thái | Link/commit |
|---|---|---|---|---|

## 3. Task Duy
- Sáng:
- Chiều:
- Cuối ngày:
- Output:
- Done criteria:

