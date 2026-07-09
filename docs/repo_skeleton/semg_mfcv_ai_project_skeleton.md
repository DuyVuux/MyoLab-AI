# AI sEMG/MFCV Muscle Fatigue Assessment Platform — Project Skeleton

> **Mục đích tài liệu**: Đây là skeleton thư mục/file khuyến nghị cho một startup/system xây dựng nền tảng AI phân tích mỏi cơ dựa trên sEMG/MFCV, phục vụ phục hồi chức năng, y học thể thao và Motion Lab.  
> **Triết lý thiết kế**: clinical workflow trước, signal quality trước, explainable AI trước, production governance trước khi scale.

---

## 0. Cách đọc skeleton

### Ký hiệu ưu tiên

| Tag | Ý nghĩa |
|---|---|
| `[MVP-0]` | Technical feasibility/offline prototype, cần để chứng minh pipeline chạy được. |
| `[MVP-1]` | Offline/Web MVP có workflow cơ bản, có thể demo nội bộ hoặc design partner. |
| `[MVP-2]` | Workflow pilot tại site thật, cần RBAC/audit/monitoring/clinical ops tốt hơn. |
| `[MVP-3]` | Scalable product/commercial beta, multi-site, integration sâu, governance đầy đủ. |
| `[MUST]` | Không nên thiếu trong phase tương ứng. |
| `[SHOULD]` | Nên có nếu đủ nguồn lực. |
| `[LATER]` | Trì hoãn để tránh scope creep. |
| `[CLINICAL]` | Liên quan trực tiếp đến workflow/interpretation lâm sàng. |
| `[AI]` | Liên quan pipeline signal processing/ML. |
| `[SEC]` | Liên quan security/privacy/compliance. |
| `[OPS]` | Liên quan vận hành/pilot/customer success. |
| `[BIZ]` | Liên quan startup/business/fundraising. |

### Nguyên tắc tổ chức repo

- **Monorepo được khuyến nghị ở giai đoạn đầu** để team nhỏ nhìn được toàn bộ sản phẩm, API, AI engine, docs, validation và deployment.
- **Raw signal không commit vào repo**. Repo chỉ lưu sample synthetic, manifest, schema và script tạo dữ liệu test.
- **Clinical protocol, preprocessing config, feature extractor và model/rule phải versioned** ngay từ đầu.
- **Report lâm sàng chỉ xuất sau human review**; report template cũng phải có version.
- **MFCV/CV là optional capability** nếu hardware/electrode setup chưa đủ điều kiện.

---

## 1. Full recommended project skeleton

```text
semg-fatigue-platform/                                      # [ROOT] Monorepo cho product, AI core, backend, frontend, docs, infra, validation
├── README.md                                               # [MVP-0][MUST] Tổng quan sản phẩm, intended use, cách chạy local, link docs chính
├── CHANGELOG.md                                            # [MVP-1][MUST] Ghi thay đổi app/model/config theo release; cần cho audit/release
├── LICENSE                                                 # [MVP-1][SHOULD] License nội bộ hoặc commercial; cần rõ khi mở cho partner
├── CONTRIBUTING.md                                         # [MVP-1][SHOULD] Quy tắc branch, PR, code review, test, commit message
├── CODEOWNERS                                              # [MVP-1][SHOULD] Ai approve phần clinical/AI/security/backend/frontend
├── Makefile                                                # [MVP-0][SHOULD] Lệnh chuẩn: test, lint, run-api, run-web, run-pipeline
├── docker-compose.yml                                      # [MVP-1][MUST] Chạy local stack: API, DB, object storage, web portal
├── .env.example                                            # [MVP-1][MUST] Biến môi trường mẫu, không chứa secret thật
├── .gitignore                                              # [MVP-0][MUST] Loại bỏ data raw, secret, cache, model artifact lớn
├── .gitattributes                                          # [MVP-1][SHOULD] Chuẩn hóa line endings, Git LFS nếu cần artifact lớn
├── pyproject.toml                                          # [MVP-0][MUST] Python package config cho signal/AI/backend nếu dùng Python
├── package.json                                            # [MVP-1][MUST] JS/TS dependencies cho web portal nếu dùng React/Next.js
├── pnpm-workspace.yaml                                     # [MVP-1][SHOULD] Workspace JS/TS nếu dùng monorepo frontend
├── openapi.yaml                                            # [MVP-1][MUST] API contract versioned cho backend/frontend/integration
│
├── .github/                                                # [MVP-1][SHOULD] CI/CD automation nếu dùng GitHub
│   ├── workflows/                                          # Pipeline test/build/security scan
│   │   ├── ci.yml                                          # [MVP-1][MUST] Run unit test, lint, type check cho mỗi PR
│   │   ├── docker-build.yml                                # [MVP-1][SHOULD] Build Docker images cho API/web/services
│   │   ├── security-scan.yml                               # [MVP-2][MUST] Dependency/container secret scan
│   │   ├── model-validation.yml                            # [MVP-2][SHOULD] Validate feature/model artifact trước release
│   │   └── docs-check.yml                                  # [MVP-2][SHOULD] Check link/schema docs để tránh docs drift
│   ├── ISSUE_TEMPLATE/                                     # Chuẩn hóa bug/feature/risk/clinical feedback
│   │   ├── bug_report.md                                   # [MVP-1][SHOULD] Bug template kỹ thuật
│   │   ├── clinical_feedback.md                            # [MVP-2][MUST] Feedback từ bác sĩ/KTV trong pilot
│   │   ├── data_quality_issue.md                           # [MVP-1][MUST] Báo lỗi QC/tín hiệu/electrode/device
│   │   └── safety_incident.md                              # [MVP-2][MUST] Ghi nhận incident/safety concern
│   └── pull_request_template.md                            # [MVP-1][SHOULD] Checklist test, audit impact, migration, model version
│
├── docs/                                                   # [MVP-0][MUST] Tài liệu điều phối product/clinical/engineering/regulatory
│   ├── 00-executive/                                       # Tài liệu cho stakeholder/sếp/investor/clinical champion
│   │   ├── executive-blueprint.md                          # [MVP-0][MUST] 15 dòng: sản phẩm là gì, không là gì, use case đầu tiên
│   │   ├── stakeholder-decision-log.md                     # [MVP-0][MUST] 5 quyết định cần chốt: intended use, protocol, hardware, deployment, success metric
│   │   ├── assumptions-and-open-questions.md               # [MVP-0][MUST] Các điểm cần xác nhận, tránh team tự đoán
│   │   └── glossary.md                                     # [MVP-0][SHOULD] Giải thích RMS/MNF/MDF/MFCV/QC/abstention/reviewer
│   │
│   ├── 01-product/                                         # Product skeleton, PRD, personas, journey, backlog
│   │   ├── product-vision.md                               # [MVP-0][MUST] Vision/mission/product boundaries
│   │   ├── intended-use-statement.md                       # [MVP-0][MUST][CLINICAL] Intended use draft, claim boundaries, human-in-the-loop
│   │   ├── icp-and-personas.md                             # [MVP-0][MUST] ICP, bác sĩ, KTV, Motion Lab, researcher, admin
│   │   ├── jobs-to-be-done.md                              # [MVP-0][SHOULD] JTBD mapping với feature/backlog
│   │   ├── user-journey.md                                 # [MVP-1][MUST] End-to-end flow từ order đến report
│   │   ├── product-boundaries.md                           # [MVP-0][MUST] Làm gì/không làm gì; tránh overclaim
│   │   ├── mvp-definition-of-done.md                       # [MVP-0][MUST] Checklist DoD cho MVP-0/1/2
│   │   ├── release-scope-mvp0.md                           # [MVP-0][MUST] Scope feasibility trong 2-4 tuần
│   │   ├── release-scope-mvp1.md                           # [MVP-1][MUST] Scope offline/web prototype
│   │   ├── release-scope-mvp2.md                           # [MVP-2][MUST] Scope workflow pilot
│   │   └── backlog/                                        # Backlog có thể import vào Jira/Linear
│   │       ├── epics.md                                    # [MVP-0][MUST] Epics: QC, feature, report, review, audit
│   │       ├── user-stories.csv                            # [MVP-1][SHOULD] User stories dạng CSV để import tool quản lý
│   │       ├── acceptance-criteria.md                      # [MVP-1][MUST] AC theo screen/API/service
│   │       └── prioritization-matrix.md                    # [MVP-1][SHOULD] Must/Should/Later và dependency
│   │
│   ├── 02-clinical/                                        # Clinical workflow/protocol/report/validation
│   │   ├── clinical-workflow.md                            # [MVP-1][MUST][CLINICAL] Order, prep, electrode, acquisition, QC, review, report
│   │   ├── assessment-order-template.md                    # [MVP-1][SHOULD] Form chỉ định assessment
│   │   ├── patient-preparation-checklist.md                # [MVP-1][MUST] Consent, contraindication, skin prep, instruction
│   │   ├── electrode-placement-guide.md                    # [MVP-1][MUST] Placement theo muscle/side; nên align SENIAM khi phù hợp
│   │   ├── target-muscle-catalog.md                        # [MVP-1][MUST] Danh sách muscle support trong MVP
│   │   ├── protocol-library.md                             # [MVP-1][MUST] Protocol versioned: isometric 30/60s, repeated contraction
│   │   ├── quality-escalation-policy.md                    # [MVP-1][MUST] Khi nào đo lại, khi nào abstain, khi nào bác sĩ quyết định
│   │   ├── human-review-policy.md                          # [MVP-1][MUST] Ai được review/ký, override policy, sign-off
│   │   ├── report-interpretation-guide.md                  # [MVP-1][MUST] Cách đọc fatigue status/confidence/feature trend
│   │   ├── clinical-validation-plan.md                     # [MVP-2][MUST] Analytical/clinical validity/usefulness plan
│   │   ├── pilot-site-training-manual.md                   # [MVP-2][MUST] Training KTV/bác sĩ cho pilot site
│   │   └── clinical-advisory-notes/                        # [MVP-2][SHOULD] Lưu feedback/advice của clinical advisors
│   │       └── yyyy-mm-dd-advisor-meeting.md               # [MVP-2][SHOULD] Biên bản từng buổi review
│   │
│   ├── 03-architecture/                                    # Architecture decision, diagrams, service specs
│   │   ├── system-context.md                               # [MVP-1][MUST] Actor, external systems, data boundary
│   │   ├── high-level-architecture.md                      # [MVP-1][MUST] Web/API/services/storage/MLOps/monitoring
│   │   ├── module-dependency-map.md                        # [MVP-1][MUST] Dependency từ protocol -> ingestion -> QC -> feature -> inference -> report
│   │   ├── deployment-architecture-onprem.md               # [MVP-2][MUST] On-prem/hybrid deployment diagram
│   │   ├── data-flow-diagram.md                            # [MVP-1][MUST][SEC] Raw signal, metadata, features, report, audit flow
│   │   ├── sequence-upload-to-report.md                    # [MVP-1][SHOULD] Sequence diagram upload -> QC -> analysis -> review -> report
│   │   ├── adr/                                            # Architecture Decision Records
│   │   │   ├── ADR-0001-monorepo.md                        # [MVP-0][SHOULD] Vì sao dùng monorepo giai đoạn đầu
│   │   │   ├── ADR-0002-onprem-raw-signal-storage.md       # [MVP-1][MUST] Raw signal ưu tiên on-prem
│   │   │   ├── ADR-0003-rule-based-before-deep-learning.md # [MVP-0][MUST][AI] Baseline explainable trước deep learning
│   │   │   ├── ADR-0004-version-everything.md              # [MVP-1][MUST] Version protocol/preprocess/feature/model/report
│   │   │   └── ADR-0005-abstention-as-first-class-output.md# [MVP-1][MUST] Abstain là output hợp lệ, không phải lỗi hệ thống
│   │   └── threat-model-architecture.md                    # [MVP-2][SHOULD][SEC] Threat model high-level cho pilot
│   │
│   ├── 04-api/                                             # API contract và integration docs
│   │   ├── api-overview.md                                 # [MVP-1][MUST] Auth, patient/session, signal, QC, analysis, review, report
│   │   ├── auth-api.md                                     # [MVP-1][MUST] Login/logout/token/roles
│   │   ├── patient-session-api.md                          # [MVP-1][MUST] Patient/session/order/target muscle endpoints
│   │   ├── signal-upload-api.md                            # [MVP-1][MUST] Multipart upload, metadata mapping, hash
│   │   ├── quality-check-api.md                            # [MVP-1][MUST] QC endpoint, pass/fail/warning schema
│   │   ├── feature-extraction-api.md                       # [MVP-1][MUST] Trigger feature extraction, analysis id
│   │   ├── inference-api.md                                # [MVP-1][MUST] Fatigue status/confidence/abstain
│   │   ├── human-review-api.md                             # [MVP-1][MUST] Review/sign-off/override
│   │   ├── report-api.md                                   # [MVP-1][MUST] Preview/export/final PDF
│   │   ├── admin-config-api.md                             # [MVP-2][SHOULD] Protocol/model/device config
│   │   ├── audit-log-api.md                                # [MVP-2][MUST] Search audit events by resource/user/time
│   │   └── examples/                                       # Sample requests/responses
│   │       ├── create-session.request.json                 # [MVP-1][SHOULD] Example request tạo session
│   │       ├── upload-signal.response.json                 # [MVP-1][SHOULD] Example response upload file
│   │       ├── qc-fail.response.json                       # [MVP-1][MUST] Example QC fail để frontend xử lý đúng
│   │       ├── inference-abstain.response.json             # [MVP-1][MUST] Example abstention response
│   │       └── report-final.response.json                  # [MVP-1][SHOULD] Example final report response
│   │
│   ├── 05-data/                                            # Data dictionary, ERD, retention, de-identification
│   │   ├── data-model.md                                   # [MVP-1][MUST] Entity: patient/session/muscle/protocol/signal/feature/result/review/report/audit
│   │   ├── erd.puml                                        # [MVP-1][SHOULD] PlantUML ERD hoặc Mermaid ERD
│   │   ├── data-dictionary.csv                             # [MVP-1][MUST] Field, type, required, relationship, PHI flag
│   │   ├── raw-signal-storage-policy.md                    # [MVP-1][MUST][SEC] Storage path, checksum, immutability, no PHI in filename
│   │   ├── feature-table-spec.md                           # [MVP-1][MUST][AI] Feature schema, unit, version, windowing
│   │   ├── label-annotation-spec.md                        # [MVP-2][SHOULD] Reviewer label, RPE, force drop, notes
│   │   ├── de-identification-spec.md                       # [MVP-2][MUST][SEC] Hash MRN, date shift, study ID, PHI removal
│   │   ├── retention-and-backup-policy.md                  # [MVP-2][MUST][SEC] Retention configurable theo site/jurisdiction
│   │   └── sample-manifests/                               # Không chứa raw clinical data thật
│   │       ├── synthetic-session-manifest.json             # [MVP-0][MUST] Manifest cho dữ liệu synthetic/golden
│   │       ├── pilot-data-manifest.template.json           # [MVP-2][SHOULD] Template quản lý dữ liệu pilot
│   │       └── dataset-card-template.md                    # [MVP-2][SHOULD] Dataset card cho training/validation
│   │
│   ├── 06-ai-signal-processing/                            # Signal processing và ML design docs
│   │   ├── ai-core-overview.md                             # [MVP-0][MUST][AI] Pipeline import -> QC -> preprocess -> features -> inference -> report
│   │   ├── signal-import-spec.md                           # [MVP-0][MUST] Supported formats, channel map, unit normalization
│   │   ├── signal-validation-spec.md                       # [MVP-0][MUST] Sampling rate, duration, channels, unit, metadata required
│   │   ├── preprocessing-spec.md                           # [MVP-0][MUST] Bandpass/notch/detrend/resample configs
│   │   ├── segmentation-windowing-spec.md                  # [MVP-0][MUST] Window size, overlap, valid-window criteria
│   │   ├── feature-extraction-spec.md                      # [MVP-0][MUST] RMS/MAV/MNF/MDF/slope/CV optional
│   │   ├── mfcv-cv-calculation-spec.md                     # [MVP-1][SHOULD] Điều kiện tính CV/MFCV; block nếu hardware không đủ
│   │   ├── fatigue-rule-engine-spec.md                     # [MVP-0][MUST] Rule-based fatigue index, confidence, abstention
│   │   ├── classical-ml-baseline-spec.md                   # [MVP-1][SHOULD] Logistic/RF/GBM khi có label đủ
│   │   ├── confidence-and-abstention-spec.md               # [MVP-1][MUST] Low confidence/QC fail/missing metadata behavior
│   │   ├── explainability-spec.md                          # [MVP-1][MUST] Feature slope, chart, thresholds, reason codes
│   │   ├── versioning-policy.md                            # [MVP-1][MUST] Version preprocessing/feature/model/rule/report
│   │   └── golden-signal-test-plan.md                      # [MVP-0][MUST] Test reproducibility trên signal mẫu
│   │
│   ├── 07-security-compliance/                             # Privacy, security, regulatory, safety governance
│   │   ├── security-overview.md                            # [MVP-1][MUST][SEC] Data classification, RBAC, encryption, audit
│   │   ├── data-classification.md                          # [MVP-1][MUST] PHI/pseudonymized/de-identified/log/system config
│   │   ├── rbac-matrix.md                                  # [MVP-1][MUST] Doctor/KTV/admin/researcher/ML/QA permissions
│   │   ├── audit-trail-policy.md                           # [MVP-1][MUST] Events to log, immutability, retention
│   │   ├── encryption-policy.md                            # [MVP-1][MUST] TLS, at-rest encryption, key management assumptions
│   │   ├── consent-management.md                           # [MVP-2][MUST] Clinical use, research use, model training consent
│   │   ├── incident-response-plan.md                       # [MVP-2][MUST] Security/safety incident handling
│   │   ├── backup-restore-plan.md                          # [MVP-2][MUST] Backup schedule, restore test
│   │   ├── regulatory-risk-assessment.md                   # [MVP-1][SHOULD] SaMD/MDSW risk hypothesis, intended use, claims
│   │   ├── medical-disclaimer.md                           # [MVP-1][MUST] Human-in-loop, not replacement, limitation
│   │   ├── risk-management-file.md                         # [MVP-2][MUST] Hazard log, mitigations, residual risk
│   │   ├── usability-engineering-notes.md                  # [MVP-2][SHOULD] Use error, reviewer confirmation, QC warning design
│   │   └── supplier-and-third-party-risk.md                # [MVP-3][SHOULD] Device/vendor/cloud dependency risk
│   │
│   ├── 08-validation-qa/                                   # Testing, verification, validation, release evidence
│   │   ├── validation-master-plan.md                       # [MVP-2][MUST] Analytical/software/clinical usability validation
│   │   ├── software-test-plan.md                           # [MVP-1][MUST] Unit/integration/E2E/security/regression tests
│   │   ├── signal-processing-test-plan.md                  # [MVP-0][MUST] Feature correctness, noise cases, deterministic rerun
│   │   ├── clinical-usability-test-plan.md                 # [MVP-2][MUST] KTV/bác sĩ task success, time, comprehension
│   │   ├── model-evaluation-plan.md                        # [MVP-1][SHOULD] Metrics, cohort split, reviewer agreement
│   │   ├── test-cases.csv                                  # [MVP-1][MUST] Test case inventory
│   │   ├── traceability-matrix.csv                         # [MVP-2][MUST] Requirement -> test -> result -> risk mitigation
│   │   ├── release-checklist.md                            # [MVP-1][MUST] Functional/security/clinical/model/data gates
│   │   └── known-limitations.md                            # [MVP-1][MUST] Những gì MVP chưa làm/không claim
│   │
│   ├── 09-mlops-devops/                                    # MLOps/DevOps standards
│   │   ├── dev-staging-prod-strategy.md                    # [MVP-1][MUST] Environment, data allowed, access control
│   │   ├── ci-cd-strategy.md                               # [MVP-1][SHOULD] Build/test/deploy flow
│   │   ├── model-registry-spec.md                          # [MVP-2][MUST] Artifact, metrics, approval, rollback
│   │   ├── experiment-tracking-spec.md                     # [MVP-1][SHOULD] MLflow/equivalent tracking
│   │   ├── data-versioning-spec.md                         # [MVP-1][MUST] Dataset manifest, file hashes, versioning
│   │   ├── monitoring-observability-spec.md                # [MVP-2][MUST] Logs, metrics, tracing, alerting
│   │   ├── drift-detection-plan.md                         # [MVP-3][SHOULD] Feature distribution, device/site drift
│   │   └── rollback-plan.md                                # [MVP-2][MUST] Rollback app/config/model/report template
│   │
│   ├── 10-business-fundraising/                            # Startup, GTM, investor, partnership docs
│   │   ├── problem-statement.md                            # [MVP-0][MUST][BIZ] Pain point và why now
│   │   ├── market-segmentation.md                          # [MVP-0][SHOULD] Rehab, sports med, Motion Lab, research, OEM
│   │   ├── beachhead-market.md                             # [MVP-0][MUST] Rehab/Motion Lab có sẵn sEMG và clinical champion
│   │   ├── value-proposition.md                            # [MVP-0][MUST] Value cho bác sĩ/KTV/site/researcher/vendor
│   │   ├── differentiation.md                              # [MVP-0][SHOULD] So với MATLAB script, EMG software, wearable analytics
│   │   ├── pricing-hypotheses.md                           # [MVP-1][SHOULD] Paid pilot, per-site, per-assessment, OEM
│   │   ├── go-to-market-plan.md                            # [MVP-1][SHOULD] Discovery, design partner, paid pilot, reference site
│   │   ├── partnership-strategy.md                         # [MVP-2][SHOULD] Device vendor, rehab network, university lab
│   │   ├── investor-narrative.md                           # [MVP-1][SHOULD] Pitch story, wedge, moat, evidence roadmap
│   │   ├── metrics-dashboard-spec.md                       # [MVP-2][SHOULD] Business/pilot/clinical metrics for board/investor
│   │   └── fundraising-data-room-checklist.md              # [MVP-2][SHOULD] Docs cần cho investor/partner due diligence
│   │
│   └── 11-operations/                                      # Team, process, pilot operations, support
│       ├── team-operating-model.md                         # [MVP-0][MUST] Roles, responsibilities, cadence, decision rights
│       ├── raci-matrix.md                                  # [MVP-1][SHOULD] RACI cho product/clinical/AI/backend/frontend/QA/regulatory
│       ├── pilot-operations-plan.md                        # [MVP-2][MUST] Site onboarding, training, feedback, support SLA
│       ├── customer-support-playbook.md                    # [MVP-2][SHOULD] Ticket triage: data quality, account, report, device issue
│       ├── implementation-checklist.md                     # [MVP-2][MUST] Checklist triển khai tại site
│       ├── weekly-status-template.md                       # [MVP-1][SHOULD] Template cập nhật sếp/stakeholder
│       └── meeting-notes/                                  # Biên bản họp vận hành
│           └── yyyy-mm-dd-weekly-sync.md                   # [MVP-1][SHOULD] Notes theo tuần
│
├── product/                                                # [MVP-0][MUST] Artefact product dùng để chuyển thành backlog/UI/acceptance criteria
│   ├── prd/                                                # Product Requirement Documents
│   │   ├── PRD-001-core-assessment-workflow.md             # [MVP-1][MUST] Create session -> upload -> QC -> analysis -> review -> report
│   │   ├── PRD-002-signal-quality-gate.md                  # [MVP-0][MUST] QC rules, failure messages, user decisions
│   │   ├── PRD-003-fatigue-analysis-result.md              # [MVP-1][MUST] Fatigue status, confidence, feature summary
│   │   ├── PRD-004-human-review-and-signoff.md             # [MVP-1][MUST] Review roles, comments, approve/reject/repeat
│   │   ├── PRD-005-longitudinal-tracking.md                # [MVP-2][SHOULD] Compare same patient/muscle/protocol over time
│   │   └── PRD-006-admin-model-config.md                   # [MVP-2][SHOULD] Admin config for protocol/model/device
│   ├── ux/                                                 # Wireframe, flow, UI copy
│   │   ├── screen-map.md                                   # [MVP-1][MUST] Login, dashboard, session, upload, QC, result, review, report
│   │   ├── user-flows.mmd                                  # [MVP-1][SHOULD] Mermaid user flow diagram
│   │   ├── wireframes/                                     # Low/mid fidelity design assets
│   │   │   ├── login.md                                    # [MVP-1][MUST] Login state/error/session timeout
│   │   │   ├── dashboard.md                                # [MVP-1][MUST] Pending sessions/reviews/QC failures
│   │   │   ├── create-assessment.md                        # [MVP-1][MUST] Patient/protocol/muscle setup form
│   │   │   ├── signal-upload.md                            # [MVP-1][MUST] Upload file + metadata mapping
│   │   │   ├── signal-quality-check.md                     # [MVP-1][MUST] QC chart, warnings, remeasure action
│   │   │   ├── analysis-result.md                          # [MVP-1][MUST] Feature trend, fatigue score, confidence
│   │   │   ├── human-review.md                             # [MVP-1][MUST] Checklist, comments, sign-off
│   │   │   ├── report-preview.md                           # [MVP-1][MUST] Final report preview/export
│   │   │   ├── longitudinal-tracking.md                    # [MVP-2][SHOULD] Timeline comparison
│   │   │   └── admin-settings.md                           # [MVP-2][SHOULD] Users/roles/protocol/model versions
│   │   ├── copy/                                           # Clinical-safe UI wording
│   │   │   ├── qc-error-messages.md                        # [MVP-1][MUST] Messages cho clipping/dropout/noise/metadata missing
│   │   │   ├── inference-result-wording.md                 # [MVP-1][MUST] Không overclaim; “supporting evidence”
│   │   │   ├── disclaimer-copy.md                          # [MVP-1][MUST] Medical disclaimer in app/report
│   │   │   └── empty-states.md                             # [MVP-1][SHOULD] UX khi chưa có session/result
│   │   └── design-system/                                  # UI component rules
│   │       ├── components.md                               # [MVP-1][SHOULD] Badge, alert, chart, table, modal
│   │       └── accessibility-notes.md                      # [MVP-2][SHOULD] Contrast, keyboard nav, readable clinical UI
│   └── analytics/                                          # Product analytics spec
│       ├── event-taxonomy.md                               # [MVP-2][SHOULD] App events: session created, QC fail, report signed
│       ├── funnel-metrics.md                               # [MVP-2][SHOULD] Upload -> QC pass -> result -> review -> report
│       └── pilot-dashboard-requirements.md                 # [MVP-2][SHOULD] Dashboard cho pilot success metrics
│
├── clinical/                                               # [CLINICAL] Protocol, workflows, review, labels, training
│   ├── protocols/                                          # Versioned exercise/assessment protocols
│   │   ├── quad-isometric-60s.v0.1.yaml                    # [MVP-0][MUST] Protocol đầu tiên khuyến nghị: quadriceps isometric 60s
│   │   ├── hamstring-isometric-60s.v0.1.yaml               # [MVP-1][SHOULD] Protocol thứ hai nếu có data/site need
│   │   ├── calf-isometric-60s.v0.1.yaml                    # [MVP-2][SHOULD] Mở rộng cơ mục tiêu
│   │   ├── repeated-contraction-template.v0.1.yaml         # [MVP-2][SHOULD] Template dynamic/repeated contraction, chưa ưu tiên MVP đầu
│   │   └── protocol-schema.json                            # [MVP-1][MUST] Schema validate protocol version/duration/muscle/device requirement
│   ├── muscle-catalog/                                     # Danh mục muscle supported và placement metadata
│   │   ├── muscles.yaml                                    # [MVP-1][MUST] muscle_name, body_side, anatomical region, supported protocols
│   │   ├── placement-guides/                               # Hướng dẫn đặt điện cực theo muscle
│   │   │   ├── vastus-lateralis.md                         # [MVP-1][MUST] Placement guide cho muscle đầu tiên
│   │   │   ├── rectus-femoris.md                           # [MVP-1][SHOULD] Nếu chọn quadriceps nhóm rộng
│   │   │   ├── biceps-femoris.md                           # [MVP-2][SHOULD] Hamstring expansion
│   │   │   └── gastrocnemius-medialis.md                   # [MVP-2][SHOULD] Calf expansion
│   │   └── electrode-config-schema.json                    # [MVP-1][MUST] Spacing, orientation, channel map, array config nếu tính CV
│   ├── review-templates/                                   # Human review form/template
│   │   ├── technical-review-checklist.yaml                 # [MVP-1][MUST] KTV xác nhận signal/setup/QC
│   │   ├── clinical-review-checklist.yaml                  # [MVP-1][MUST] Bác sĩ xác nhận interpretation/final sign-off
│   │   ├── override-reason-codes.yaml                      # [MVP-1][MUST] Lý do override QC warning/result
│   │   └── escalation-reason-codes.yaml                    # [MVP-1][MUST] Đo lại/không đủ dữ liệu/chuyển bác sĩ review
│   ├── labels/                                             # Annotation/label definitions cho ML/validation
│   │   ├── label-taxonomy.yaml                             # [MVP-2][SHOULD] fatigue_label, inconclusive, artifact, protocol deviation
│   │   ├── rpe-scale.md                                    # [MVP-2][SHOULD] RPE capture nếu dùng
│   │   ├── force-drop-labeling.md                          # [MVP-2][SHOULD] Label dựa trên force drop nếu có force sensor
│   │   └── annotation-guidelines.md                        # [MVP-2][MUST] Hướng dẫn reviewer label để giảm noise
│   └── training/                                           # Training material cho pilot site
│       ├── ktv-training-deck.md                            # [MVP-2][MUST] Training KTV workflow và data quality
│       ├── doctor-review-guide.md                          # [MVP-2][MUST] Cách đọc result/report và sign-off
│       ├── quick-start-checklist.md                        # [MVP-2][MUST] Checklist 1 trang cho mỗi assessment
│       └── troubleshooting-guide.md                        # [MVP-2][MUST] Nhiễu, clipping, dropout, wrong channel, metadata missing
│
├── apps/                                                   # User-facing applications
│   ├── web-portal/                                         # [MVP-1][MUST] Web app cho KTV/bác sĩ/admin/researcher
│   │   ├── README.md                                       # Cách chạy web portal local
│   │   ├── package.json                                    # Frontend dependencies
│   │   ├── tsconfig.json                                   # TypeScript config
│   │   ├── next.config.js                                  # Nếu dùng Next.js; có thể thay bằng Vite config
│   │   ├── public/                                         # Static assets
│   │   │   ├── logo.svg                                    # [MVP-1][SHOULD] Logo/product identity
│   │   │   └── report-watermark.svg                        # [MVP-2][SHOULD] Watermark cho report preview nếu cần
│   │   └── src/                                            # Source code web
│   │       ├── app/                                        # Routing/pages
│   │       │   ├── login/page.tsx                          # [MVP-1][MUST] Login UI
│   │       │   ├── dashboard/page.tsx                      # [MVP-1][MUST] Work queue: pending QC/review/report
│   │       │   ├── patients/page.tsx                       # [MVP-1][MUST] Patient/session list
│   │       │   ├── patients/[patientId]/page.tsx           # [MVP-1][MUST] Patient detail + sessions timeline
│   │       │   ├── sessions/new/page.tsx                   # [MVP-1][MUST] Create new assessment
│   │       │   ├── sessions/[sessionId]/setup/page.tsx     # [MVP-1][MUST] Protocol/muscle/electrode setup
│   │       │   ├── sessions/[sessionId]/upload/page.tsx    # [MVP-1][MUST] Signal upload/import
│   │       │   ├── sessions/[sessionId]/quality/page.tsx   # [MVP-1][MUST] Signal quality check
│   │       │   ├── sessions/[sessionId]/analysis/page.tsx  # [MVP-1][MUST] Analysis result charts
│   │       │   ├── sessions/[sessionId]/review/page.tsx    # [MVP-1][MUST] Human review/sign-off
│   │       │   ├── sessions/[sessionId]/report/page.tsx    # [MVP-1][MUST] Report preview/export
│   │       │   ├── patients/[patientId]/trends/page.tsx    # [MVP-2][SHOULD] Longitudinal tracking
│   │       │   ├── admin/users/page.tsx                    # [MVP-2][SHOULD] User/role management
│   │       │   ├── admin/protocols/page.tsx                # [MVP-2][SHOULD] Protocol config/versioning
│   │       │   ├── admin/models/page.tsx                   # [MVP-2][SHOULD] Model/feature version monitoring
│   │       │   └── audit/page.tsx                          # [MVP-2][MUST] Audit log viewer cho admin/QA
│   │       ├── components/                                 # Reusable UI components
│   │       │   ├── charts/                                 # Signal/feature charts
│   │       │   │   ├── SignalPreviewChart.tsx              # [MVP-1][MUST] Hiển thị raw/processed signal preview
│   │       │   │   ├── FeatureTrendChart.tsx               # [MVP-1][MUST] RMS/MNF/MDF/CV trend
│   │       │   │   ├── QualityTimeline.tsx                 # [MVP-1][SHOULD] QC flags theo thời gian/window
│   │       │   │   └── LongitudinalTrendChart.tsx          # [MVP-2][SHOULD] So sánh phiên trước
│   │       │   ├── clinical/                               # Clinical-specific UI components
│   │       │   │   ├── FatigueStatusBadge.tsx              # [MVP-1][MUST] No/mild/moderate/high/inconclusive
│   │       │   │   ├── ConfidenceIndicator.tsx             # [MVP-1][MUST] Confidence + explanation
│   │       │   │   ├── ReviewChecklist.tsx                 # [MVP-1][MUST] Technical/clinical review checklist
│   │       │   │   ├── DisclaimerPanel.tsx                 # [MVP-1][MUST] Limitation/human-in-loop disclaimer
│   │       │   │   └── ProtocolSummaryCard.tsx             # [MVP-1][MUST] Protocol/muscle/electrode/device summary
│   │       │   ├── forms/                                  # Form components
│   │       │   │   ├── PatientForm.tsx                     # [MVP-1][MUST] Patient metadata form
│   │       │   │   ├── SessionForm.tsx                     # [MVP-1][MUST] Create assessment/session form
│   │       │   │   ├── ProtocolSetupForm.tsx               # [MVP-1][MUST] Protocol/muscle/side setup
│   │       │   │   ├── ElectrodeConfigForm.tsx             # [MVP-1][MUST] Electrode spacing/orientation/channel map
│   │       │   │   ├── SignalUploadForm.tsx                # [MVP-1][MUST] Upload file + metadata mapping
│   │       │   │   └── ReviewSignoffForm.tsx               # [MVP-1][MUST] Approve/reject/request repeat
│   │       │   ├── layout/                                 # App layout/navigation
│   │       │   │   ├── AppShell.tsx                        # [MVP-1][MUST] Navigation/sidebar/topbar
│   │       │   │   ├── RoleGuard.tsx                       # [MVP-1][MUST] Hide/guard UI by role
│   │       │   │   └── Breadcrumbs.tsx                     # [MVP-1][SHOULD] Context navigation
│   │       │   └── feedback/                               # Alerts/error states
│   │       │       ├── QcFailureAlert.tsx                  # [MVP-1][MUST] Block analysis when critical fail
│   │       │       ├── AbstentionAlert.tsx                 # [MVP-1][MUST] Display “not enough data” clearly
│   │       │       └── ValidationErrorSummary.tsx          # [MVP-1][SHOULD] Form validation summary
│   │       ├── lib/                                        # Frontend client utilities
│   │       │   ├── api-client.ts                           # [MVP-1][MUST] Typed API client from OpenAPI
│   │       │   ├── auth.ts                                 # [MVP-1][MUST] Token/session handling
│   │       │   ├── permissions.ts                          # [MVP-1][MUST] Role-based permission helper
│   │       │   ├── validators.ts                           # [MVP-1][MUST] Client-side validation mirrors backend
│   │       │   └── date-format.ts                          # [MVP-1][SHOULD] Consistent timestamp display
│   │       ├── schemas/                                    # Frontend shared schemas
│   │       │   ├── session.schema.ts                       # [MVP-1][SHOULD] Zod/type schema for session
│   │       │   ├── qc.schema.ts                            # [MVP-1][SHOULD] QC response schema
│   │       │   ├── inference.schema.ts                     # [MVP-1][SHOULD] Inference/abstain schema
│   │       │   └── report.schema.ts                        # [MVP-1][SHOULD] Report schema
│   │       └── tests/                                      # Frontend tests
│   │           ├── unit/                                   # Component/unit tests
│   │           └── e2e/                                    # [MVP-1][SHOULD] Upload -> QC -> report user flow tests
│   │
│   └── clinician-report-viewer/                            # [MVP-3][LATER] Standalone lightweight report viewer if needed
│       └── README.md                                       # Not needed until product expands beyond main web portal
│
├── services/                                               # Backend/service layer; có thể chạy modular monolith trước, split microservice sau
│   ├── api-server/                                         # [MVP-1][MUST] Main backend API gateway/application server
│   │   ├── README.md                                       # Cách chạy API server
│   │   ├── Dockerfile                                      # Container build
│   │   ├── alembic.ini                                     # Nếu dùng SQLAlchemy/Alembic migrations
│   │   ├── src/                                            # API source
│   │   │   ├── main.py                                     # [MVP-1][MUST] App entrypoint
│   │   │   ├── config.py                                   # [MVP-1][MUST] Environment config, secrets from env
│   │   │   ├── dependencies.py                             # [MVP-1][SHOULD] DB/auth/service dependencies
│   │   │   ├── routes/                                     # REST API routes
│   │   │   │   ├── auth.py                                 # [MVP-1][MUST] Login/logout/token refresh
│   │   │   │   ├── patients.py                             # [MVP-1][MUST] Patient CRUD scoped by site
│   │   │   │   ├── sessions.py                             # [MVP-1][MUST] Session/order/target endpoints
│   │   │   │   ├── signals.py                              # [MVP-1][MUST] Upload/import signal endpoints
│   │   │   │   ├── quality.py                              # [MVP-1][MUST] Trigger/read QC result
│   │   │   │   ├── analysis.py                             # [MVP-1][MUST] Feature extraction/inference endpoints
│   │   │   │   ├── reviews.py                              # [MVP-1][MUST] Human review/sign-off endpoints
│   │   │   │   ├── reports.py                              # [MVP-1][MUST] Report preview/export endpoints
│   │   │   │   ├── admin.py                                # [MVP-2][SHOULD] Users/protocol/model/device admin
│   │   │   │   └── audit.py                                # [MVP-2][MUST] Audit log search endpoint
│   │   │   ├── models/                                     # ORM/domain models
│   │   │   │   ├── patient.py                              # Patient metadata entity
│   │   │   │   ├── session.py                              # Assessment session entity
│   │   │   │   ├── protocol.py                             # Protocol config/version entity
│   │   │   │   ├── muscle_target.py                        # Target muscle/body side entity
│   │   │   │   ├── electrode_config.py                     # Electrode setup entity
│   │   │   │   ├── device.py                               # Device metadata entity
│   │   │   │   ├── raw_signal.py                           # Raw signal reference/checksum entity
│   │   │   │   ├── analysis_run.py                         # Analysis run + versions entity
│   │   │   │   ├── feature.py                              # Feature table metadata entity
│   │   │   │   ├── inference_result.py                     # Fatigue result/confidence/abstain entity
│   │   │   │   ├── review.py                               # Human review/sign-off entity
│   │   │   │   ├── report.py                               # Report artifact/reference entity
│   │   │   │   └── audit_event.py                          # Audit log entity
│   │   │   ├── schemas/                                    # Request/response DTOs
│   │   │   │   ├── auth_schema.py                          # Token/login schemas
│   │   │   │   ├── patient_schema.py                       # Patient DTO validation
│   │   │   │   ├── session_schema.py                       # Session DTO validation
│   │   │   │   ├── signal_schema.py                        # Upload/metadata schema
│   │   │   │   ├── qc_schema.py                            # QC response schema
│   │   │   │   ├── analysis_schema.py                      # Feature/inference schema
│   │   │   │   ├── review_schema.py                        # Review/sign-off schema
│   │   │   │   └── report_schema.py                        # Report schema
│   │   │   ├── services/                                   # Business logic orchestration
│   │   │   │   ├── auth_service.py                         # Auth and token issuing
│   │   │   │   ├── patient_service.py                      # Patient/session business rules
│   │   │   │   ├── signal_service.py                       # Upload, storage, checksum, parser dispatch
│   │   │   │   ├── qc_service.py                           # Calls quality gate service/library
│   │   │   │   ├── analysis_service.py                     # Orchestrates preprocess/features/inference
│   │   │   │   ├── review_service.py                       # Enforces reviewer permission and sign-off workflow
│   │   │   │   ├── report_service.py                       # Calls report generator and stores artifact
│   │   │   │   ├── longitudinal_service.py                 # Same protocol/device comparison logic
│   │   │   │   └── audit_service.py                        # Writes immutable audit events for write/read-sensitive actions
│   │   │   ├── repositories/                               # DB access layer
│   │   │   │   ├── patient_repo.py                         # Patient queries
│   │   │   │   ├── session_repo.py                         # Session queries
│   │   │   │   ├── analysis_repo.py                        # Analysis/result queries
│   │   │   │   ├── report_repo.py                          # Report queries
│   │   │   │   └── audit_repo.py                           # Audit event queries
│   │   │   ├── auth/                                       # Auth/RBAC internals
│   │   │   │   ├── password_hashing.py                     # Password hashing utility
│   │   │   │   ├── jwt.py                                  # JWT creation/verification
│   │   │   │   ├── rbac.py                                 # Role/permission matrix enforcement
│   │   │   │   └── policy.py                               # Resource-level access rules
│   │   │   ├── db/                                         # DB engine/session/migrations helpers
│   │   │   │   ├── base.py                                 # ORM base
│   │   │   │   ├── session.py                              # DB session lifecycle
│   │   │   │   └── migrations/                             # DB schema migrations
│   │   │   ├── jobs/                                       # Async/background-style jobs run by worker in current deployment
│   │   │   │   ├── run_qc_job.py                           # QC computation job
│   │   │   │   ├── run_analysis_job.py                     # Feature/inference job
│   │   │   │   └── generate_report_job.py                  # PDF report generation job
│   │   │   └── utils/                                      # Shared helpers
│   │   │       ├── file_hash.py                            # SHA-256 checksum
│   │   │       ├── time.py                                 # Timezone/timestamp utilities
│   │   │       ├── error_codes.py                          # Standard API error code constants
│   │   │       └── logging.py                              # Structured logging setup
│   │   └── tests/                                          # Backend tests
│   │       ├── unit/                                       # Unit tests for services/policies
│   │       ├── integration/                                # DB/API integration tests
│   │       └── fixtures/                                   # Test fixtures excluding raw PHI data
│   │
│   ├── signal-ingestion-service/                           # [MVP-0][MUST] Parser/normalizer cho signal files
│   │   ├── README.md                                       # Supported formats and assumptions
│   │   ├── src/                                            # Source
│   │   │   ├── importers/                                  # File/device importers
│   │   │   │   ├── base_importer.py                        # Common importer interface
│   │   │   │   ├── csv_importer.py                         # [MVP-0][MUST] CSV importer first
│   │   │   │   ├── edf_importer.py                         # [MVP-1][SHOULD] EDF/BDF support if site uses it
│   │   │   │   ├── vendor_x_importer.py                    # [MVP-1][SHOULD] Specific device format adapter
│   │   │   │   └── matlab_importer.py                      # [MVP-2][SHOULD] .mat support for research/Motion Lab
│   │   │   ├── normalizers/                                # Convert to internal representation
│   │   │   │   ├── unit_normalizer.py                      # Normalize uV/mV units
│   │   │   │   ├── channel_mapper.py                       # Map device channels to muscle/electrode positions
│   │   │   │   └── metadata_extractor.py                   # Extract sampling rate/duration/channel count
│   │   │   └── validators/                                 # Ingestion-time validation
│   │   │       ├── file_format_validator.py                # Unsupported/corrupt file detection
│   │   │       └── metadata_validator.py                   # Required metadata enforcement
│   │   └── tests/                                          # Ingestion tests using synthetic/sample files
│   │
│   ├── quality-gate-service/                               # [MVP-0][MUST][AI] Data quality gate, critical safety module
│   │   ├── README.md                                       # QC philosophy and reason codes
│   │   ├── configs/                                        # Versioned QC thresholds
│   │   │   ├── qc_v0.1.yaml                                # [MVP-0][MUST] MVP thresholds for clipping/dropout/duration/noise
│   │   │   └── qc_v0.2.yaml                                # [MVP-2][SHOULD] Pilot-tuned thresholds
│   │   ├── src/                                            # QC source code
│   │   │   ├── quality_gate.py                             # Main QC orchestration
│   │   │   ├── checks/                                     # Individual QC checks
│   │   │   │   ├── duration_check.py                       # Minimum duration per protocol
│   │   │   │   ├── sampling_rate_check.py                  # Sampling rate compatibility
│   │   │   │   ├── channel_completeness_check.py           # Missing channel/dropout
│   │   │   │   ├── clipping_saturation_check.py            # Saturation/clipping detection
│   │   │   │   ├── noise_floor_check.py                    # Baseline noise level
│   │   │   │   ├── powerline_noise_check.py                # 50/60Hz powerline noise flag
│   │   │   │   ├── motion_artifact_check.py                # Low-frequency artifact heuristic
│   │   │   │   ├── stationarity_check.py                   # Window stability check
│   │   │   │   └── cv_eligibility_check.py                 # Whether MFCV/CV can be computed
│   │   │   ├── scoring.py                                  # QC score aggregation and critical/warning status
│   │   │   ├── reason_codes.py                             # Standard QC reason codes for API/UI/report
│   │   │   └── result_schema.py                            # QC result schema
│   │   └── tests/                                          # QC unit/golden tests
│   │
│   ├── preprocessing-service/                              # [MVP-0][MUST][AI] Filtering/preprocessing pipeline
│   │   ├── README.md                                       # Preprocessing assumptions
│   │   ├── configs/                                        # Versioned preprocessing configs
│   │   │   ├── preprocess_v0.1.yaml                        # [MVP-0][MUST] Bandpass/notch/window default
│   │   │   └── preprocess_v0.2.yaml                        # [MVP-2][SHOULD] Pilot tuning
│   │   ├── src/                                            # Source
│   │   │   ├── pipeline.py                                 # Main preprocessing pipeline
│   │   │   ├── filters.py                                  # Bandpass/notch/detrend utilities
│   │   │   ├── resampling.py                               # Optional resampling utilities
│   │   │   ├── normalization.py                            # MVC/baseline normalization if available
│   │   │   ├── artifact_masking.py                         # Mark/remove invalid windows based on QC flags
│   │   │   └── config_schema.py                            # Validate preprocessing config
│   │   └── tests/                                          # Tests for deterministic preprocessing output
│   │
│   ├── feature-extraction-service/                         # [MVP-0][MUST][AI] Feature extraction engine
│   │   ├── README.md                                       # Feature list and formula references
│   │   ├── configs/                                        # Feature extraction configs
│   │   │   ├── features_semg_v0.1.yaml                     # [MVP-0][MUST] RMS/MAV/MNF/MDF/slope
│   │   │   └── features_semg_cv_v0.1.yaml                  # [MVP-1][SHOULD] Adds CV/MFCV if eligible
│   │   ├── src/                                            # Source
│   │   │   ├── extractor.py                                # Main feature extraction orchestration
│   │   │   ├── windowing.py                                # Fixed-size windows, overlap, valid-window filtering
│   │   │   ├── time_domain.py                              # RMS, MAV, optional ZC/SSC/WL
│   │   │   ├── frequency_domain.py                         # PSD, MNF, MDF
│   │   │   ├── conduction_velocity.py                      # CV/MFCV estimation if electrode array meets requirements
│   │   │   ├── trend_features.py                           # Slopes over time, normalized change, confidence of slope
│   │   │   ├── feature_schema.py                           # Feature row schema and units
│   │   │   └── feature_version.py                          # Feature extractor version metadata
│   │   └── tests/                                          # Feature correctness/golden tests
│   │
│   ├── inference-service/                                  # [MVP-1][MUST][AI] Fatigue scoring/inference/confidence/abstention
│   │   ├── README.md                                       # Inference behavior and model/rule versioning
│   │   ├── rules/                                          # Rule-based baseline, preferred for MVP
│   │   │   ├── fatigue_rule_v0.1.yaml                      # [MVP-0][MUST] Initial thresholds/reasoning
│   │   │   ├── fatigue_rule_v0.2.yaml                      # [MVP-2][SHOULD] Pilot-updated thresholds after review
│   │   │   └── rule_schema.json                            # [MVP-1][MUST] Validate rule config
│   │   ├── models/                                         # Classical ML artifacts only when data/labels đủ
│   │   │   ├── README.md                                   # Do not store large models in Git; use registry/artifact store
│   │   │   ├── logistic_baseline/                          # [MVP-1][SHOULD] Logistic regression baseline if labels exist
│   │   │   │   ├── model-card.md                           # Model intended use, data, metrics, limitations
│   │   │   │   └── metrics.json                            # Validation metrics snapshot
│   │   │   └── random_forest_baseline/                     # [MVP-2][SHOULD] Optional classical ML comparison
│   │   │       ├── model-card.md                           # Model card for RF baseline
│   │   │       └── metrics.json                            # Validation metrics snapshot
│   │   ├── src/                                            # Source
│   │   │   ├── inference.py                                # Main inference entrypoint
│   │   │   ├── rule_engine.py                              # Rule-based fatigue score/status
│   │   │   ├── classical_ml.py                             # Classical ML model wrapper
│   │   │   ├── confidence.py                               # QC-weighted confidence scoring
│   │   │   ├── abstention.py                               # Critical: no-analysis logic
│   │   │   ├── explainability.py                           # Feature contribution/reason codes
│   │   │   ├── result_formatter.py                         # API/report friendly result schema
│   │   │   └── model_compatibility.py                      # Check feature version vs model version
│   │   └── tests/                                          # Inference and abstention tests
│   │
│   ├── report-generation-service/                          # [MVP-1][MUST] PDF/HTML report generator
│   │   ├── README.md                                       # Report generation process
│   │   ├── templates/                                      # Versioned report templates
│   │   │   ├── clinical_report_v0.1.html                   # [MVP-1][MUST] Initial clinical report template
│   │   │   ├── technical_report_v0.1.html                  # [MVP-1][SHOULD] Technical appendix template
│   │   │   ├── research_export_summary_v0.1.html           # [MVP-2][SHOULD] Research summary template
│   │   │   └── operational_report_v0.1.html                # [MVP-2][SHOULD] Operational dashboard/report template
│   │   ├── src/                                            # Source
│   │   │   ├── generator.py                                # Main report generation entrypoint
│   │   │   ├── render_html.py                              # Render HTML from template/context
│   │   │   ├── render_pdf.py                               # Convert HTML to PDF
│   │   │   ├── chart_renderer.py                           # Generate feature trend charts for report
│   │   │   ├── disclaimer.py                               # Inject correct disclaimer by intended use
│   │   │   ├── report_hash.py                              # Hash final report for integrity
│   │   │   └── report_schema.py                            # Report data contract
│   │   └── tests/                                          # Snapshot tests for report content
│   │
│   └── integration-service/                                # [MVP-2][SHOULD] Device/EHR/LIS/HL7/FHIR integration layer
│       ├── README.md                                       # Integration strategy: file import first, SDK/EHR later
│       ├── device-adapters/                                # Device import/SDK adapters
│       │   ├── generic-csv-adapter.py                      # [MVP-1][MUST] Generic adapter first
│       │   ├── edf-bdf-adapter.py                          # [MVP-1][SHOULD] EDF/BDF adapter if needed
│       │   └── vendor-sdk-adapter-template.py              # [MVP-3][LATER] Template for future device SDK integration
│       ├── ehr/                                            # EHR integration, not MVP-first
│       │   ├── fhir-mapping.md                             # [MVP-3][LATER] Map patient/session/report to FHIR resources
│       │   ├── hl7-message-mapping.md                      # [MVP-3][LATER] HL7 mapping if hospital requires
│       │   └── ehr-sync-worker.py                          # [MVP-3][LATER] Sync final report/status to EHR
│       └── exports/                                        # Export utilities
│           ├── csv-feature-export.py                       # [MVP-2][SHOULD] Export de-identified features for research
│           ├── parquet-feature-export.py                   # [MVP-2][SHOULD] Efficient research export
│           └── report-batch-export.py                      # [MVP-3][LATER] Batch report export for enterprise sites
│
├── packages/                                               # Shared internal packages used by apps/services
│   ├── common-schemas/                                     # [MVP-1][MUST] Shared JSON/OpenAPI/Pydantic/Zod schemas
│   │   ├── README.md                                       # Schema package usage
│   │   ├── json/                                           # JSON schema shared across services
│   │   │   ├── patient.schema.json                         # Patient metadata schema
│   │   │   ├── session.schema.json                         # Session schema
│   │   │   ├── protocol.schema.json                        # Protocol schema
│   │   │   ├── electrode-config.schema.json                # Electrode config schema
│   │   │   ├── raw-signal-ref.schema.json                  # Raw signal reference schema
│   │   │   ├── qc-result.schema.json                       # QC result schema
│   │   │   ├── feature-row.schema.json                     # Feature table row schema
│   │   │   ├── inference-result.schema.json                # Inference/confidence/abstain schema
│   │   │   ├── review.schema.json                          # Human review schema
│   │   │   └── report.schema.json                          # Report schema
│   │   └── generated/                                      # Generated TS/Python clients/types
│   │       ├── python/                                     # Generated Python models
│   │       └── typescript/                                 # Generated TypeScript types
│   ├── semg-core/                                          # [MVP-0][MUST] Pure Python signal processing core, importable by services/notebooks
│   │   ├── README.md                                       # Core library overview
│   │   ├── semg_core/                                      # Python package
│   │   │   ├── __init__.py                                 # Package init
│   │   │   ├── io.py                                       # Load normalized signal arrays
│   │   │   ├── validation.py                               # Signal and metadata validation
│   │   │   ├── preprocessing.py                            # Filtering/preprocessing functions
│   │   │   ├── windowing.py                                # Segment/window helpers
│   │   │   ├── features.py                                 # RMS/MNF/MDF/MAV APIs
│   │   │   ├── cv.py                                       # CV/MFCV helpers, optional
│   │   │   ├── qc.py                                       # QC helper functions
│   │   │   ├── fatigue_rules.py                            # Rule engine helpers
│   │   │   ├── explainability.py                           # Reason codes and feature summary
│   │   │   └── version.py                                  # Core package version
│   │   └── tests/                                          # Unit/golden tests for core library
│   └── clinical-protocols/                                 # [MVP-1][MUST] Reusable protocol definitions as package/data
│       ├── README.md                                       # Protocol package usage
│       ├── schemas/                                        # Protocol/electrode schemas
│       └── protocols/                                      # Packaged YAML protocols used by app/services
│
├── ai-core/                                                # [MVP-0][MUST] Research-to-production AI workspace; code promoted to packages/services
│   ├── README.md                                           # How to run offline experiments safely
│   ├── notebooks/                                          # Exploration only; not production source of truth
│   │   ├── 00_data_inventory.ipynb                         # [MVP-0][MUST] Inspect available files/device/formats
│   │   ├── 01_signal_qc_exploration.ipynb                  # [MVP-0][MUST] Explore QC thresholds and artifact cases
│   │   ├── 02_feature_extraction_baseline.ipynb            # [MVP-0][MUST] RMS/MNF/MDF/slope exploration
│   │   ├── 03_fatigue_rule_baseline.ipynb                  # [MVP-0][MUST] First fatigue rule and plots
│   │   ├── 04_cv_mfcv_feasibility.ipynb                    # [MVP-1][SHOULD] Check if hardware supports CV/MFCV
│   │   └── 05_reviewer_agreement_analysis.ipynb            # [MVP-2][SHOULD] Compare AI vs human labels
│   ├── pipelines/                                          # Reproducible scripts, not ad-hoc notebooks
│   │   ├── run_offline_analysis.py                         # [MVP-0][MUST] Batch pipeline raw -> QC -> features -> result
│   │   ├── generate_golden_features.py                     # [MVP-0][MUST] Generate deterministic golden outputs
│   │   ├── train_classical_baseline.py                     # [MVP-1][SHOULD] Train logistic/RF when labels are available
│   │   ├── evaluate_model.py                               # [MVP-1][SHOULD] Evaluate model against labels/reviewer
│   │   └── export_research_features.py                     # [MVP-2][SHOULD] De-identified feature export
│   ├── configs/                                            # AI experiment configs
│   │   ├── offline_analysis_mvp0.yaml                      # [MVP-0][MUST] Config for feasibility run
│   │   ├── feature_extraction_mvp1.yaml                    # [MVP-1][MUST] Feature config for MVP-1
│   │   ├── model_training_baseline.yaml                    # [MVP-1][SHOULD] Classical ML training config
│   │   └── evaluation_pilot.yaml                           # [MVP-2][SHOULD] Pilot evaluation config
│   ├── metrics/                                            # Model/signal metric definitions and outputs
│   │   ├── metric_definitions.md                           # [MVP-1][MUST] QC/model/clinical usefulness metrics
│   │   ├── baseline_metrics.template.json                  # [MVP-1][SHOULD] Metrics snapshot template
│   │   └── pilot_metrics.template.json                     # [MVP-2][SHOULD] Pilot metrics snapshot template
│   ├── model-cards/                                        # Model/rule documentation
│   │   ├── fatigue_rule_v0.1_model_card.md                 # [MVP-1][MUST] Intended use/data/metrics/limitations for rule model
│   │   ├── logistic_baseline_model_card.md                 # [MVP-1][SHOULD] Classical ML model card
│   │   └── random_forest_baseline_model_card.md            # [MVP-2][SHOULD] RF baseline card if used
│   └── validation-reports/                                 # Locked validation outputs
│       ├── analytical_validation_mvp0.md                   # [MVP-0][MUST] Feature reproducibility/golden test result
│       ├── offline_validation_mvp1.md                      # [MVP-1][MUST] Offline validation summary
│       └── pilot_validation_mvp2.md                        # [MVP-2][MUST] Pilot validation summary
│
├── data-platform/                                          # [MVP-1][MUST] Data schemas, migrations, storage policies, seed data
│   ├── README.md                                           # Data architecture overview
│   ├── migrations/                                         # DB migrations
│   │   ├── 0001_create_core_tables.sql                     # [MVP-1][MUST] Patient/session/signal/analysis/result/review/report/audit
│   │   ├── 0002_add_rbac_tables.sql                        # [MVP-1][MUST] Users/roles/permissions
│   │   ├── 0003_add_protocol_versioning.sql                # [MVP-1][MUST] Protocol/config version tables
│   │   ├── 0004_add_feature_tables.sql                     # [MVP-1][MUST] Feature rows and analysis_run relation
│   │   └── 0005_add_longitudinal_indexes.sql               # [MVP-2][SHOULD] Indexes for trend comparison
│   ├── seeds/                                              # Non-PHI seed data
│   │   ├── roles.seed.sql                                  # [MVP-1][MUST] doctor/technician/admin/researcher/qa roles
│   │   ├── protocols.seed.sql                              # [MVP-1][MUST] Initial protocol versions
│   │   ├── devices.seed.sql                                # [MVP-1][SHOULD] Known test devices/devices used in pilot
│   │   └── synthetic_patients.seed.sql                     # [MVP-1][SHOULD] Demo data only, no real PHI
│   ├── object-storage/                                     # Object storage structure and scripts
│   │   ├── storage-layout.md                               # [MVP-1][MUST] raw/processed/reports/research-exports directory policy
│   │   ├── minio-init.sh                                   # [MVP-1][SHOULD] Local object storage init script
│   │   └── lifecycle-policy.template.json                  # [MVP-2][SHOULD] Retention/lifecycle policy template
│   ├── schemas/                                            # Database/schema docs
│   │   ├── feature_table.sql                               # [MVP-1][MUST] Feature table DDL if separate from migrations
│   │   ├── audit_log.sql                                   # [MVP-1][MUST] Audit table DDL if separate
│   │   ├── research_export_view.sql                        # [MVP-2][SHOULD] De-identified research view
│   │   └── longitudinal_view.sql                           # [MVP-2][SHOULD] Same protocol/device trend view
│   ├── synthetic-data/                                     # Synthetic/golden data only
│   │   ├── README.md                                       # Explain synthetic data purpose
│   │   ├── generate_synthetic_semg.py                      # [MVP-0][MUST] Generate synthetic sEMG-like signals for tests/demo
│   │   ├── golden_signal_01.csv                            # [MVP-0][MUST] Small synthetic golden signal
│   │   ├── golden_signal_01.expected_features.json         # [MVP-0][MUST] Expected output for regression tests
│   │   ├── qc_fail_clipping.csv                            # [MVP-0][MUST] Synthetic clipping failure sample
│   │   ├── qc_fail_dropout.csv                             # [MVP-0][MUST] Synthetic dropout failure sample
│   │   └── qc_fail_noise.csv                               # [MVP-0][MUST] Synthetic high-noise failure sample
│   └── privacy/                                            # Privacy utilities/specs
│       ├── deidentify_export.py                            # [MVP-2][MUST] De-identify feature/report exports
│       ├── hash_identifiers.py                             # [MVP-1][MUST] Hash MRN/external IDs
│       └── date_shift.py                                   # [MVP-2][SHOULD] Date shifting for research exports
│
├── reports/                                                # [MVP-1][MUST] Report templates, schemas, example outputs
│   ├── README.md                                           # Report structure and versioning rules
│   ├── templates/                                          # Report source templates
│   │   ├── clinical_report_v0.1.md                         # [MVP-1][MUST] Markdown source for clinical report template
│   │   ├── clinical_report_v0.1.html                       # [MVP-1][MUST] Renderable HTML template
│   │   ├── technical_appendix_v0.1.md                      # [MVP-1][SHOULD] Technical details for KTV/researcher
│   │   ├── operational_summary_v0.1.md                     # [MVP-2][SHOULD] QC/pass/review throughput summary
│   │   └── research_export_readme_v0.1.md                  # [MVP-2][SHOULD] Explain research export fields and limitations
│   ├── schemas/                                            # Report data contracts
│   │   ├── clinical_report_context.schema.json             # [MVP-1][MUST] Data required to render clinical report
│   │   ├── feature_summary.schema.json                     # [MVP-1][MUST] Feature summary schema
│   │   └── reviewer_signoff.schema.json                    # [MVP-1][MUST] Reviewer/signature schema
│   ├── examples/                                           # Example reports; no real PHI
│   │   ├── example_clinical_report_mvp1.pdf                # [MVP-1][SHOULD] PDF sample for clinicians/investors
│   │   ├── example_qc_fail_report.pdf                      # [MVP-1][SHOULD] Example “not enough data” report
│   │   └── example_longitudinal_report.pdf                 # [MVP-2][SHOULD] Trend comparison sample
│   └── wording/                                            # Guardrails for report language
│       ├── clinical-interpretation-phrases.md              # [MVP-1][MUST] Approved clinical wording templates
│       ├── limitation-disclaimer.md                        # [MVP-1][MUST] Limitation/disclaimer text
│       └── prohibited-claims.md                            # [MVP-1][MUST] Phrases not allowed in MVP/report/sales
│
├── integrations/                                           # [MVP-2][SHOULD] Integration specs and adapters
│   ├── README.md                                           # Integration roadmap: import file first, SDK/EHR later
│   ├── devices/                                            # Device-specific integration docs
│   │   ├── generic-csv/                                    # [MVP-0][MUST] Generic CSV support
│   │   │   ├── format-spec.md                              # Required columns: time/channel/unit/sampling metadata
│   │   │   ├── sample_file.csv                             # Synthetic sample only
│   │   │   └── adapter-config.yaml                         # Mapping config for generic CSV
│   │   ├── edf-bdf/                                        # [MVP-1][SHOULD] EDF/BDF import if site uses it
│   │   │   ├── format-notes.md                             # Channel/unit metadata assumptions
│   │   │   └── adapter-config.yaml                         # Importer config
│   │   └── vendor-x/                                       # [MVP-1/2][SHOULD] Replace with actual device vendor
│   │       ├── vendor-format-notes.md                      # Vendor-specific quirks and metadata mapping
│   │       ├── sample_manifest.json                        # Manifest for vendor sample files
│   │       └── adapter-config.yaml                         # Vendor adapter config
│   ├── ehr/                                                # EHR integration later
│   │   ├── fhir/                                           # FHIR integration specs
│   │   │   ├── mapping-patient.md                          # [MVP-3][LATER] Patient mapping
│   │   │   ├── mapping-observation.md                      # [MVP-3][LATER] Fatigue metrics as observations
│   │   │   ├── mapping-diagnostic-report.md                # [MVP-3][LATER] Final report mapping
│   │   │   └── integration-test-plan.md                    # [MVP-3][LATER] EHR integration testing
│   │   └── hl7/                                            # HL7 integration specs if needed
│   │       └── message-mapping.md                          # [MVP-3][LATER] HL7 message mapping
│   └── exports/                                            # Export specs
│       ├── feature-export-spec.md                          # [MVP-2][SHOULD] CSV/Parquet feature export columns
│       ├── audit-export-spec.md                            # [MVP-2][SHOULD] Audit export for compliance
│       └── report-export-spec.md                           # [MVP-1][MUST] PDF/HTML export behavior
│
├── mlops/                                                  # [MVP-2][MUST] Model/data/version tracking and monitoring
│   ├── README.md                                           # MLOps lifecycle overview
│   ├── registry/                                           # Model/rule/feature registry metadata
│   │   ├── model_registry_schema.json                      # [MVP-2][MUST] Artifact metadata schema
│   │   ├── registered_models.yaml                          # [MVP-2][SHOULD] Approved/staged/archived models list
│   │   ├── feature_extractors.yaml                         # [MVP-1][MUST] Feature extractor versions and compatibility
│   │   ├── preprocessing_configs.yaml                      # [MVP-1][MUST] Preprocessing config versions
│   │   └── report_templates.yaml                           # [MVP-1][MUST] Report template versions
│   ├── experiments/                                        # Experiment tracking configs
│   │   ├── mlflow_config.yaml                              # [MVP-1][SHOULD] MLflow config if used
│   │   ├── experiment_naming_convention.md                 # [MVP-1][SHOULD] Naming pattern
│   │   └── experiment_review_checklist.md                  # [MVP-2][SHOULD] Before promoting model
│   ├── monitoring/                                         # Model/signal/workflow monitoring
│   │   ├── feature_drift_metrics.yaml                      # [MVP-3][SHOULD] Feature distribution drift
│   │   ├── data_quality_metrics.yaml                       # [MVP-2][MUST] QC pass/fail/artifact metrics
│   │   ├── model_performance_metrics.yaml                  # [MVP-2][SHOULD] Agreement, calibration, abstention
│   │   ├── clinical_workflow_metrics.yaml                  # [MVP-2][MUST] Time/session, pending review, repeat measurement
│   │   └── alert_rules.yaml                                # [MVP-2][SHOULD] Alert thresholds
│   ├── release/                                            # Model/config release governance
│   │   ├── model_release_checklist.md                      # [MVP-2][MUST] Data, metrics, clinical review, QA sign-off
│   │   ├── rollback_checklist.md                           # [MVP-2][MUST] Rollback model/config safely
│   │   └── model_change_log.md                             # [MVP-2][MUST] Why/when model changed
│   └── scripts/                                            # Automation scripts
│       ├── register_model.py                               # [MVP-2][SHOULD] Register approved model artifact
│       ├── compare_feature_versions.py                     # [MVP-2][SHOULD] Detect feature extractor changes
│       ├── compute_drift_report.py                         # [MVP-3][SHOULD] Generate drift report
│       └── promote_model.py                                # [MVP-3][SHOULD] Promote model after approvals
│
├── infra/                                                  # [MVP-1][MUST] Local/on-prem/cloud infrastructure as code/config
│   ├── README.md                                           # Deployment modes and prerequisites
│   ├── local/                                              # Local development stack
│   │   ├── docker-compose.local.yml                        # [MVP-1][MUST] API/web/Postgres/MinIO local
│   │   ├── init-db.sh                                      # [MVP-1][MUST] Initialize local DB
│   │   └── init-object-store.sh                            # [MVP-1][SHOULD] Initialize local object storage buckets
│   ├── onprem/                                             # Pilot site on-prem deployment
│   │   ├── docker-compose.onprem.yml                       # [MVP-2][MUST] On-prem deployment compose
│   │   ├── nginx.conf                                      # [MVP-2][MUST] Reverse proxy/TLS termination
│   │   ├── backup-cron.example                             # [MVP-2][MUST] Backup schedule example
│   │   ├── storage-mounts.md                               # [MVP-2][MUST] NAS/object storage mounting assumptions
│   │   └── installation-runbook.md                         # [MVP-2][MUST] Step-by-step site install guide
│   ├── cloud/                                              # Hybrid/private cloud option
│   │   ├── terraform/                                      # [MVP-3][SHOULD] Terraform for cloud deployment
│   │   ├── kubernetes/                                     # [MVP-3][SHOULD] K8s manifests/helm charts
│   │   └── cloud-security-baseline.md                      # [MVP-3][SHOULD] VPC/IAM/KMS/logging baseline
│   ├── monitoring/                                         # Observability stack configs
│   │   ├── prometheus.yml                                  # [MVP-2][SHOULD] Metrics scrape config
│   │   ├── grafana-dashboard.json                          # [MVP-2][SHOULD] System/data/workflow dashboard
│   │   ├── loki-config.yml                                 # [MVP-2][SHOULD] Log aggregation config
│   │   └── alertmanager.yml                                # [MVP-2][SHOULD] Alert routing
│   └── secrets/                                            # Secret handling docs only, never actual secret
│       ├── secret-management.md                            # [MVP-1][MUST] How secrets are stored/rotated
│       └── .gitkeep                                        # Placeholder; no real secrets committed
│
├── security-compliance/                                    # [MVP-1/2][MUST] Files supporting privacy/compliance/governance
│   ├── README.md                                           # Security/compliance folder overview
│   ├── policies/                                           # Policies
│   │   ├── access-control-policy.md                        # [MVP-1][MUST] RBAC, least privilege, account lifecycle
│   │   ├── password-mfa-policy.md                          # [MVP-2][SHOULD] Password/MFA requirements
│   │   ├── data-handling-policy.md                         # [MVP-1][MUST] Raw signal, PHI, feature, report handling
│   │   ├── audit-log-policy.md                             # [MVP-1][MUST] Required events and retention
│   │   ├── backup-retention-policy.md                      # [MVP-2][MUST] Backup/restore/retention
│   │   ├── incident-response-policy.md                     # [MVP-2][MUST] Security/safety incident response
│   │   └── acceptable-use-policy.md                        # [MVP-2][SHOULD] User responsibilities in clinical site
│   ├── risk/                                               # Risk management artifacts
│   │   ├── hazard-log.csv                                  # [MVP-2][MUST] Hazard, cause, harm, mitigation, residual risk
│   │   ├── risk-control-matrix.csv                         # [MVP-2][MUST] Risk -> control -> test mapping
│   │   ├── clinical-safety-case.md                         # [MVP-2][SHOULD] Why product is safe enough for pilot
│   │   └── usability-risk-analysis.md                      # [MVP-2][SHOULD] Use error analysis
│   ├── regulatory/                                         # Regulatory planning
│   │   ├── intended-use-and-claims.md                      # [MVP-1][MUST] Claims allowed/prohibited
│   │   ├── regulatory-pathway-options.md                   # [MVP-2][SHOULD] RUO/CDS/SaMD/MDSW options by geography
│   │   ├── standards-mapping.md                            # [MVP-2][SHOULD] IEC 62304, ISO 14971, usability, cybersecurity mapping
│   │   ├── software-lifecycle-procedure.md                 # [MVP-2][SHOULD] Development/change control procedure
│   │   └── clinical-evaluation-plan.md                     # [MVP-2][MUST] Clinical evaluation/evidence plan
│   ├── privacy/                                            # Privacy documentation
│   │   ├── data-processing-inventory.md                    # [MVP-2][MUST] What data, purpose, processor/controller, retention
│   │   ├── consent-forms/                                  # Consent templates
│   │   │   ├── clinical-use-consent-template.md            # [MVP-2][MUST] Clinical consent template, site-specific review needed
│   │   │   ├── research-use-consent-template.md            # [MVP-2][MUST] Research/model training consent
│   │   │   └── data-sharing-consent-template.md            # [MVP-3][SHOULD] Cross-site data sharing consent
│   │   ├── deidentification-sop.md                         # [MVP-2][MUST] De-identification standard operating procedure
│   │   └── data-subject-request-sop.md                     # [MVP-3][SHOULD] Access/delete/export request handling if applicable
│   └── cybersecurity/                                      # Cybersecurity program
│       ├── threat-model.md                                 # [MVP-2][SHOULD] Assets, threats, mitigations
│       ├── vulnerability-management.md                     # [MVP-2][SHOULD] Dependency scanning, patching, severity handling
│       ├── sbom/                                           # Software Bill of Materials
│       │   └── sbom-template.json                          # [MVP-2][SHOULD] SBOM output template
│       └── penetration-test-plan.md                        # [MVP-3][SHOULD] Pre-commercial security testing plan
│
├── qa-validation/                                          # [MVP-1/2][MUST] Test automation, fixtures, evidence, validation reports
│   ├── README.md                                           # QA/validation overview
│   ├── requirements/                                       # Requirements under test
│   │   ├── product-requirements.csv                        # [MVP-1][MUST] Requirement ID, statement, priority, owner
│   │   ├── clinical-requirements.csv                       # [MVP-1][MUST] Clinical workflow and safety requirements
│   │   ├── security-requirements.csv                       # [MVP-2][MUST] RBAC/audit/encryption/backup requirements
│   │   └── ai-signal-requirements.csv                      # [MVP-0][MUST] QC/features/abstention requirements
│   ├── test-plans/                                         # Test plans
│   │   ├── unit-test-plan.md                               # [MVP-1][SHOULD] Unit testing scope
│   │   ├── integration-test-plan.md                        # [MVP-1][MUST] API/service/storage integration tests
│   │   ├── e2e-test-plan.md                                # [MVP-1][SHOULD] Web flow tests
│   │   ├── signal-golden-test-plan.md                      # [MVP-0][MUST] Golden signal regression tests
│   │   ├── security-test-plan.md                           # [MVP-2][MUST] Auth/RBAC/audit/security tests
│   │   └── user-acceptance-test-plan.md                    # [MVP-2][MUST] KTV/bác sĩ UAT for pilot
│   ├── test-data/                                          # Synthetic/de-identified test data only
│   │   ├── synthetic/                                      # Synthetic signals
│   │   ├── deidentified-samples/                           # Approved de-identified sample files if available
│   │   └── manifests/                                      # Dataset manifests and expected outputs
│   ├── automated-tests/                                    # Additional test automation scripts
│   │   ├── run_golden_signal_tests.py                      # [MVP-0][MUST] Validate QC/features deterministic outputs
│   │   ├── run_api_contract_tests.py                       # [MVP-1][MUST] API contract tests against openapi.yaml
│   │   ├── run_rbac_tests.py                               # [MVP-2][MUST] Permission matrix tests
│   │   └── run_report_snapshot_tests.py                    # [MVP-1][SHOULD] Report output snapshot tests
│   ├── evidence/                                           # Validation evidence snapshots
│   │   ├── mvp0-feasibility-evidence.md                    # [MVP-0][MUST] Screenshots/tables/feature outputs
│   │   ├── mvp1-release-evidence.md                        # [MVP-1][MUST] Test results and known limitations
│   │   └── mvp2-pilot-readiness-evidence.md                # [MVP-2][MUST] Release and site readiness evidence
│   └── traceability/                                       # Traceability matrix
│       ├── requirement-test-traceability.csv               # [MVP-2][MUST] Requirement -> test -> result -> risk
│       └── risk-control-traceability.csv                   # [MVP-2][MUST] Hazard -> mitigation -> verification
│
├── ops/                                                    # [OPS] Startup operating model, pilot ops, support, release process
│   ├── README.md                                           # Operations overview
│   ├── cadence/                                            # Meeting cadence and templates
│   │   ├── weekly-product-clinical-review.md               # [MVP-1][SHOULD] Product/clinical alignment
│   │   ├── weekly-engineering-sync.md                      # [MVP-1][SHOULD] Engineering execution
│   │   ├── biweekly-risk-review.md                         # [MVP-2][MUST] Safety/regulatory risk review
│   │   └── monthly-pilot-steering.md                       # [MVP-2][MUST] Site champion + team steering
│   ├── pilot/                                              # Pilot operations
│   │   ├── site-selection-criteria.md                      # [MVP-1][SHOULD] What makes a good pilot site
│   │   ├── pilot-kickoff-checklist.md                      # [MVP-2][MUST] Before pilot starts
│   │   ├── site-onboarding-runbook.md                      # [MVP-2][MUST] Install/training/data governance steps
│   │   ├── pilot-success-metrics.md                        # [MVP-2][MUST] QC pass, report usefulness, adoption, safety
│   │   ├── pilot-feedback-form.md                          # [MVP-2][MUST] Structured clinician/KTV feedback
│   │   └── pilot-closeout-template.md                      # [MVP-2][SHOULD] Pilot summary for business/investor
│   ├── support/                                            # Customer support and incident triage
│   │   ├── support-sla.md                                  # [MVP-2][SHOULD] Support response targets
│   │   ├── troubleshooting-qc-failures.md                  # [MVP-2][MUST] How support handles QC failures
│   │   ├── troubleshooting-upload-errors.md                # [MVP-1][SHOULD] File format/import issues
│   │   ├── troubleshooting-report-errors.md                # [MVP-2][SHOULD] Report generation/sign-off issues
│   │   └── escalation-matrix.md                            # [MVP-2][MUST] Who handles clinical/security/technical escalations
│   └── release/                                            # Release operations
│       ├── release-calendar.md                             # [MVP-2][SHOULD] Planned releases and freezes
│       ├── release-notes-template.md                       # [MVP-1][SHOULD] Release note template
│       ├── go-no-go-checklist.md                           # [MVP-2][MUST] Release gate checklist
│       └── rollback-runbook.md                             # [MVP-2][MUST] App/model/config rollback steps
│
├── business/                                               # [BIZ] Startup, fundraising, GTM, investor materials
│   ├── README.md                                           # Business folder overview
│   ├── strategy/                                           # Business strategy docs
│   │   ├── problem-solution-fit.md                         # [MVP-0][MUST] Problem, current alternatives, why product matters
│   │   ├── beachhead-market-analysis.md                    # [MVP-0][MUST] First market: rehab/Motion Lab/sports med
│   │   ├── competitive-landscape.md                        # [MVP-1][SHOULD] Competitors/alternatives and differentiation
│   │   ├── moat-strategy.md                                # [MVP-1][SHOULD] Data/protocol/workflow/evidence moat
│   │   └── risk-register-business.md                       # [MVP-1][SHOULD] Business risks: sales cycle, regulatory, hardware dependency
│   ├── customer-discovery/                                 # User/customer interviews
│   │   ├── interview-script-doctor.md                      # [MVP-0][MUST] Doctor discovery questions
│   │   ├── interview-script-ktv.md                         # [MVP-0][MUST] KTV/operator discovery questions
│   │   ├── interview-script-motion-lab.md                  # [MVP-0][SHOULD] Motion Lab discovery questions
│   │   ├── interview-notes/                                # Raw notes, de-identified if needed
│   │   └── insights-synthesis.md                           # [MVP-1][MUST] Patterns from discovery
│   ├── pricing/                                            # Pricing hypotheses
│   │   ├── paid-pilot-pricing.md                           # [MVP-1][SHOULD] Setup + monthly support hypothesis
│   │   ├── per-site-license-pricing.md                     # [MVP-2][SHOULD] Annual site license hypothesis
│   │   ├── per-assessment-pricing.md                       # [MVP-2][SHOULD] Usage-based pricing hypothesis
│   │   └── oem-partnership-pricing.md                      # [MVP-3][SHOULD] Device vendor OEM/revenue share
│   ├── gtm/                                                # Go-to-market
│   │   ├── design-partner-plan.md                          # [MVP-1][MUST] Identify and manage design partners
│   │   ├── sales-deck-outline.md                           # [MVP-1][SHOULD] Sales deck structure
│   │   ├── pilot-proposal-template.md                      # [MVP-1][MUST] Proposal for clinical pilot
│   │   ├── procurement-checklist.md                        # [MVP-2][SHOULD] Hospital procurement requirements
│   │   └── reference-site-case-study-template.md           # [MVP-2][SHOULD] Case study after pilot
│   ├── fundraising/                                        # Investor materials
│   │   ├── investor-narrative.md                           # [MVP-1][MUST] Story: clinical workflow layer for sEMG fatigue assessment
│   │   ├── pitch-deck-outline.md                           # [MVP-1][SHOULD] 10-12 slide deck outline
│   │   ├── data-room-index.md                              # [MVP-2][SHOULD] Docs investor will request
│   │   ├── traction-metrics.md                             # [MVP-2][SHOULD] Pilot usage, usefulness, QC pass, revenue
│   │   ├── use-of-funds.md                                 # [MVP-2][SHOULD] Hiring, validation, product, regulatory, GTM
│   │   └── investor-faq.md                                 # [MVP-2][SHOULD] Expected investor questions and answers
│   └── partnerships/                                       # Strategic partnerships
│       ├── device-vendor-partnership-plan.md               # [MVP-2][SHOULD] EMG hardware vendor partnership logic
│       ├── rehab-network-partnership-plan.md               # [MVP-2][SHOULD] Multi-site clinical partner plan
│       ├── university-lab-collaboration.md                 # [MVP-1][SHOULD] Research/validation collaboration
│       └── partnership-mou-template.md                     # [MVP-2][SHOULD] MOU template, legal review needed
│
├── scripts/                                                # Utility scripts for developers/operators
│   ├── README.md                                           # Script usage
│   ├── dev/                                                # Developer utilities
│   │   ├── setup_dev_env.sh                                # [MVP-1][MUST] Install/setup local dev
│   │   ├── seed_local_db.sh                                # [MVP-1][MUST] Seed local DB with synthetic data
│   │   └── reset_local_stack.sh                            # [MVP-1][SHOULD] Reset local containers/data
│   ├── data/                                               # Data utilities
│   │   ├── validate_signal_file.py                         # [MVP-0][MUST] CLI validate file before upload
│   │   ├── compute_file_hash.py                            # [MVP-1][MUST] SHA-256 utility
│   │   ├── deidentify_dataset.py                           # [MVP-2][MUST] De-identify dataset for research/ML
│   │   └── generate_dataset_manifest.py                    # [MVP-2][SHOULD] Create dataset manifest
│   ├── ops/                                                # Operational scripts
│   │   ├── backup_db.sh                                    # [MVP-2][MUST] DB backup script
│   │   ├── restore_db.sh                                   # [MVP-2][MUST] DB restore script
│   │   ├── export_audit_log.py                             # [MVP-2][SHOULD] Audit export
│   │   └── health_check.py                                 # [MVP-2][MUST] System health check
│   └── release/                                            # Release automation
│       ├── create_release_manifest.py                      # [MVP-2][MUST] App/model/config/report versions in one manifest
│       ├── verify_release_artifacts.py                     # [MVP-2][MUST] Check hashes/tests before release
│       └── rollback_release.py                             # [MVP-2][MUST] Rollback helper
│
└── tools/                                                  # Developer tools/configs
    ├── lint/                                               # Lint/type/static analysis configs
    │   ├── ruff.toml                                       # [MVP-1][SHOULD] Python lint config
    │   ├── mypy.ini                                        # [MVP-1][SHOULD] Python type checking config
    │   └── eslint.config.js                                # [MVP-1][SHOULD] Frontend lint config
    ├── openapi/                                            # API generation tools
    │   ├── generate_clients.sh                             # [MVP-1][SHOULD] Generate TS/Python clients from OpenAPI
    │   └── validate_openapi.sh                             # [MVP-1][MUST] Validate OpenAPI contract
    └── diagrams/                                           # Diagram generation tools
        ├── render_mermaid.sh                               # [MVP-1][SHOULD] Render Mermaid diagrams
        └── render_plantuml.sh                              # [MVP-1][SHOULD] Render PlantUML diagrams
```

---

## 2. Minimal tree nên build trước trong 30 ngày đầu

> Mục tiêu: chứng minh **technical feasibility + clinical readability** trước khi build hệ thống lớn.

```text
semg-fatigue-platform/
├── README.md                                               # Project overview và intended use conservative
├── docs/
│   ├── 00-executive/
│   │   ├── executive-blueprint.md                          # Chốt sản phẩm là gì/không là gì
│   │   └── stakeholder-decision-log.md                     # Chốt use case, protocol, hardware, deployment
│   ├── 01-product/
│   │   ├── intended-use-statement.md                       # Bắt buộc để không overclaim
│   │   └── mvp-definition-of-done.md                       # DoD cho MVP-0/MVP-1
│   ├── 02-clinical/
│   │   ├── protocol-library.md                             # Protocol đầu tiên
│   │   ├── electrode-placement-guide.md                    # Hướng dẫn setup để tín hiệu có nghĩa
│   │   └── quality-escalation-policy.md                    # Khi nào đo lại/abstain
│   └── 06-ai-signal-processing/
│       ├── signal-validation-spec.md                       # Required metadata và signal constraints
│       ├── preprocessing-spec.md                           # Filter/window default
│       ├── feature-extraction-spec.md                      # RMS/MNF/MDF/slope
│       └── fatigue-rule-engine-spec.md                     # Rule-based score + abstention
├── clinical/
│   └── protocols/
│       ├── quad-isometric-60s.v0.1.yaml                    # Protocol đầu tiên
│       └── protocol-schema.json                            # Validate protocol
├── packages/
│   └── semg-core/
│       ├── semg_core/
│       │   ├── io.py                                       # Load signal
│       │   ├── validation.py                               # Validate metadata/signal
│       │   ├── preprocessing.py                            # Filter/preprocess
│       │   ├── windowing.py                                # Segment windows
│       │   ├── features.py                                 # RMS/MNF/MDF/slope
│       │   ├── qc.py                                       # QC checks
│       │   └── fatigue_rules.py                            # Fatigue rule baseline
│       └── tests/                                          # Golden unit tests
├── ai-core/
│   ├── notebooks/
│   │   ├── 00_data_inventory.ipynb                         # Hiểu file/device/data
│   │   ├── 01_signal_qc_exploration.ipynb                  # Chọn QC thresholds
│   │   └── 02_feature_extraction_baseline.ipynb            # Feature trend đầu tiên
│   ├── pipelines/
│   │   └── run_offline_analysis.py                         # Chạy raw -> QC -> features -> report JSON
│   └── validation-reports/
│       └── analytical_validation_mvp0.md                   # Evidence MVP-0
├── data-platform/
│   └── synthetic-data/
│       ├── generate_synthetic_semg.py                      # Tạo dữ liệu test không PHI
│       ├── golden_signal_01.csv                            # Golden signal
│       └── golden_signal_01.expected_features.json         # Expected feature output
└── reports/
    └── templates/
        └── clinical_report_v0.1.md                         # Report mẫu cho clinician review
```

---

## 3. Minimal tree cho MVP-1 web/offline prototype

> Mục tiêu: KTV có thể **upload → QC → analysis → review → report** trong một web workflow cơ bản.

```text
semg-fatigue-platform/
├── openapi.yaml                                            # API contract chính
├── docker-compose.yml                                      # Local stack API/Web/Postgres/Object store
├── apps/
│   └── web-portal/
│       └── src/
│           ├── app/
│           │   ├── login/page.tsx                          # Login
│           │   ├── dashboard/page.tsx                      # Work queue
│           │   ├── sessions/new/page.tsx                   # Create assessment
│           │   ├── sessions/[sessionId]/upload/page.tsx    # Upload signal
│           │   ├── sessions/[sessionId]/quality/page.tsx   # QC result
│           │   ├── sessions/[sessionId]/analysis/page.tsx  # Analysis result
│           │   ├── sessions/[sessionId]/review/page.tsx    # Human review
│           │   └── sessions/[sessionId]/report/page.tsx    # Report preview/export
│           ├── components/
│           │   ├── charts/FeatureTrendChart.tsx            # RMS/MNF/MDF trend chart
│           │   ├── clinical/FatigueStatusBadge.tsx         # Clinical status display
│           │   ├── clinical/ConfidenceIndicator.tsx        # Confidence and reason
│           │   └── feedback/AbstentionAlert.tsx            # Not enough data state
│           └── lib/api-client.ts                           # API client
├── services/
│   ├── api-server/
│   │   └── src/
│   │       ├── routes/                                     # Auth, patients, sessions, signals, QC, analysis, review, report
│   │       ├── models/                                     # Patient/session/signal/analysis/result/review/report/audit
│   │       ├── services/                                   # Business logic
│   │       └── auth/rbac.py                                # Permission matrix
│   ├── signal-ingestion-service/                           # File import and normalization
│   ├── quality-gate-service/                               # QC gate
│   ├── preprocessing-service/                              # Filtering and preprocessing
│   ├── feature-extraction-service/                         # RMS/MNF/MDF/slope
│   ├── inference-service/                                  # Rule-based fatigue and abstention
│   └── report-generation-service/                          # PDF/HTML report
├── data-platform/
│   ├── migrations/0001_create_core_tables.sql              # Core DB tables
│   ├── migrations/0002_add_rbac_tables.sql                 # RBAC tables
│   └── seeds/roles.seed.sql                                # Seed roles
└── security-compliance/
    ├── policies/access-control-policy.md                   # RBAC policy
    ├── policies/audit-log-policy.md                        # Audit policy
    └── regulatory/intended-use-and-claims.md               # Prevent overclaim
```

---

## 4. Modules nên trì hoãn để tránh scope creep

```text
semg-fatigue-platform/
├── apps/
│   └── clinician-report-viewer/                            # [LATER] Chỉ cần khi report viewer độc lập khỏi web portal
├── integrations/
│   └── ehr/                                                # [LATER] FHIR/HL7 sau khi workflow/report có traction
├── services/
│   └── integration-service/
│       └── ehr/                                            # [LATER] EHR sync không cần cho MVP feasibility
├── mlops/
│   └── monitoring/feature_drift_metrics.yaml               # [LATER] Drift detection khi có multi-site volume
├── infra/
│   └── cloud/kubernetes/                                   # [LATER] K8s chỉ cần khi scale multi-site/cloud
└── ai-core/
    └── notebooks/advanced_deep_learning.ipynb              # [AVOID EARLY] Không dùng deep learning khi data/label nhỏ
```

---

## 5. Dependency map giữa các folder chính

```text
docs/01-product/intended-use-statement.md
    -> clinical/protocols/*.yaml
        -> services/signal-ingestion-service/
            -> services/quality-gate-service/
                -> services/preprocessing-service/
                    -> services/feature-extraction-service/
                        -> services/inference-service/
                            -> services/report-generation-service/
                                -> apps/web-portal/
                                    -> qa-validation/
                                        -> security-compliance/
                                            -> ops/pilot/
                                                -> business/fundraising/
```

### Dependency chi tiết

| Upstream | Downstream | Lý do |
|---|---|---|
| Intended use | Report wording, regulatory risk, product scope | Claim quyết định output được phép nói gì. |
| Protocol | QC, segmentation, feature extraction, longitudinal comparison | Không có protocol thì feature/trend mất ngữ cảnh. |
| Electrode config | CV/MFCV eligibility, channel map, signal interpretation | MFCV/CV phụ thuộc electrode array/spacing/orientation. |
| Raw signal storage policy | Ingestion, audit, re-analysis | Cần lưu raw immutable và có checksum. |
| QC gate | Feature extraction, inference, report | QC fail phải block hoặc cảnh báo trước analysis/report. |
| Feature extractor version | Inference model, report, validation | Model/result phải biết feature version đã dùng. |
| Inference result | Human review, report | AI output không final nếu chưa có reviewer. |
| Human review | Final report | Reviewer sign-off là governance/safety gate. |
| Audit policy | Backend write actions | Mọi action quan trọng cần traceability. |
| Validation plan | Release checklist | Không release pilot nếu không có evidence tối thiểu. |

---

## 6. Naming/versioning conventions

### Protocol

```text
{muscle-or-region}-{test-type}-{duration}.v{major}.{minor}.yaml
quad-isometric-60s.v0.1.yaml
hamstring-isometric-60s.v0.1.yaml
```

### Preprocessing config

```text
preprocess_v{major}.{minor}.yaml
preprocess_v0.1.yaml
```

### Feature extractor

```text
features_semg_v{major}.{minor}.yaml
features_semg_v0.1.yaml
features_semg_cv_v0.1.yaml
```

### Rule/model

```text
fatigue_rule_v{major}.{minor}.yaml
logistic_baseline_v{major}.{minor}/model-card.md
random_forest_baseline_v{major}.{minor}/model-card.md
```

### Report template

```text
clinical_report_v{major}.{minor}.html
technical_report_v{major}.{minor}.html
```

### Analysis run metadata bắt buộc

```json
{
  "analysis_id": "uuid",
  "raw_signal_id": "uuid",
  "protocol_version": "quad-isometric-60s.v0.1",
  "preprocess_config_version": "preprocess_v0.1",
  "feature_extractor_version": "features_semg_v0.1",
  "model_or_rule_version": "fatigue_rule_v0.1",
  "report_template_version": "clinical_report_v0.1",
  "created_at": "ISO-8601 timestamp"
}
```

---

## 7. Backlog-ready epics từ skeleton

| Epic | Folder/file liên quan | MVP phase | Exit criteria |
|---|---|---|---|
| E1. Clinical protocol v0.1 | `clinical/protocols/`, `docs/02-clinical/` | MVP-0 | Protocol được clinical lead approve. |
| E2. Signal importer | `services/signal-ingestion-service/` | MVP-0 | Import được file mẫu, normalize channel/unit. |
| E3. Data quality gate | `services/quality-gate-service/` | MVP-0 | QC pass/fail/warning và reason codes hoạt động. |
| E4. Feature extraction | `services/feature-extraction-service/`, `packages/semg-core/` | MVP-0 | RMS/MNF/MDF/slope deterministic trên golden signal. |
| E5. Fatigue rule baseline | `services/inference-service/rules/` | MVP-0/1 | Fatigue status/confidence/abstain output ổn định. |
| E6. Report v0.1 | `reports/templates/`, `report-generation-service/` | MVP-1 | Xuất PDF/HTML có limitation và reviewer sign-off. |
| E7. Web workflow | `apps/web-portal/` | MVP-1 | Upload -> QC -> analysis -> review -> report chạy end-to-end. |
| E8. Backend/API | `services/api-server/`, `openapi.yaml` | MVP-1 | API contract ổn định, có auth/session/audit cơ bản. |
| E9. Data platform | `data-platform/migrations/` | MVP-1 | Core tables + raw signal reference + feature table. |
| E10. Security/compliance baseline | `security-compliance/` | MVP-1/2 | RBAC, audit, encryption, intended-use/claims docs. |
| E11. Pilot operations | `ops/pilot/`, `clinical/training/` | MVP-2 | Site onboarding/training/success metrics sẵn sàng. |
| E12. MLOps/model governance | `mlops/` | MVP-2 | Registry, release checklist, rollback, monitoring baseline. |

---

## 8. Rủi ro nếu thiếu các folder/module trọng yếu

| Thiếu phần | Rủi ro |
|---|---|
| `clinical/protocols/` | Không chuẩn hóa measurement, feature/trend không so sánh được. |
| `quality-gate-service/` | Tín hiệu xấu vẫn ra kết quả, tăng rủi ro clinical safety. |
| `feature-extraction-service/` | Không có explainable output; AI thành black box hoặc demo rỗng. |
| `inference-service/abstention.py` | System bị ép phải kết luận cả khi dữ liệu không đủ. |
| `human-review-policy.md` | Không rõ ai chịu trách nhiệm final clinical report. |
| `audit-log-policy.md` | Không điều tra được ai upload/sửa/review/export gì. |
| `data-dictionary.csv` | Team hiểu khác nhau về patient/session/signal/feature/result. |
| `versioning-policy.md` | Không reproducible; không biết result được tạo bởi model/config nào. |
| `release-checklist.md` | Pilot dễ release lỗi chưa test hoặc wording overclaim. |
| `pilot-operations-plan.md` | Sản phẩm chạy được nhưng site không vận hành được. |
| `business/fundraising/` | Có kỹ thuật nhưng thiếu narrative, pricing, proof để gọi vốn/bán pilot. |

---

## 9. Definition of Done cho repo skeleton này

Repo skeleton được xem là đủ để bắt đầu engineering khi có:

1. `docs/01-product/intended-use-statement.md` đã được clinical lead và product owner review.  
2. `clinical/protocols/quad-isometric-60s.v0.1.yaml` có schema hợp lệ.  
3. `packages/semg-core/` có ít nhất validation, preprocessing, feature extraction và unit test.  
4. `data-platform/synthetic-data/` có golden signal và expected features.  
5. `services/quality-gate-service/` có QC reason codes và critical fail behavior.  
6. `services/inference-service/` có fatigue rule v0.1 và abstention logic.  
7. `reports/templates/clinical_report_v0.1.md` có disclaimer và reviewer sign-off.  
8. `openapi.yaml` có API contract tối thiểu cho upload/QC/analysis/review/report.  
9. `security-compliance/policies/audit-log-policy.md` định nghĩa audit events.  
10. `qa-validation/test-plans/signal-golden-test-plan.md` định nghĩa golden tests.  

---

## 10. Checklist triển khai tuần đầu tiên từ skeleton

| Ngày | Việc | File/folder cần tạo/cập nhật | Owner |
|---|---|---|---|
| Day 1 | Chốt intended use và product boundary | `docs/01-product/intended-use-statement.md`, `product-boundaries.md` | CPO + Clinical Lead |
| Day 2 | Chốt protocol/muscle đầu tiên | `clinical/protocols/quad-isometric-60s.v0.1.yaml` | Clinical Lead + Signal Engineer |
| Day 3 | Chuẩn hóa data/file input | `docs/06-ai-signal-processing/signal-import-spec.md` | Signal Engineer |
| Day 4 | Viết QC spec và reason codes | `services/quality-gate-service/configs/qc_v0.1.yaml` | Signal Engineer + Clinical Lead |
| Day 5 | Viết feature extraction core | `packages/semg-core/semg_core/features.py` | Signal Engineer |
| Day 6 | Tạo report template đầu tiên | `reports/templates/clinical_report_v0.1.md` | Product + Clinical Lead |
| Day 7 | Tạo backlog sprint 1 | `docs/01-product/backlog/epics.md` | Product Owner + CTO |

---

## 11. Ghi chú quan trọng cho team

- **Đừng đưa dữ liệu bệnh nhân thật vào repo**. Dùng object storage được kiểm soát và chỉ commit manifest/hash/schema.
- **Đừng build deep learning ở MVP nếu chưa có label đáng tin**. Rule-based + classical ML đủ để chứng minh workflow và clinical usefulness.
- **Đừng claim “diagnosis” hoặc “treatment recommendation” ở MVP**. Chỉ dùng ngôn ngữ hỗ trợ đánh giá và human-in-the-loop.
- **Đừng tính MFCV/CV nếu hardware/electrode setup không đủ**. System phải trả về “không đủ điều kiện tính CV/MFCV”.
- **Đừng bỏ qua report wording**. Một câu chữ sai có thể biến product từ decision-support thành overclaim regulatory.
- **Đừng để notebooks trở thành production**. Notebook dùng khám phá; code production phải vào `packages/semg-core/` hoặc `services/`.
- **Đừng so sánh longitudinal giữa protocol/device khác nhau** nếu chưa có calibration/normalization được clinical lead approve.

