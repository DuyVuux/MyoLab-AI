# AI sEMG/MFCV Muscle Fatigue Assessment Platform — Project Skeleton

> **Mục đích tài liệu**: Đây là skeleton thư mục/file khuyến nghị cho một startup/system xây dựng nền tảng AI phân tích mỏi cơ dựa trên sEMG/MFCV, phục vụ phục hồi chức năng, y học thể thao và Motion Lab.  
> **Triết lý thiết kế**: clinical workflow trước, signal quality trước, explainable AI trước, production governance trước khi scale.

---

## 0. Cách đọc skeleton

### Ký hiệu ưu tiên

| Tag          | Ý nghĩa                                                                           |
| --------------| -----------------------------------------------------------------------------------|
| `[MVP-0]`    | Technical feasibility/offline prototype, cần để chứng minh pipeline chạy được.    |
| `[MVP-1]`    | Offline/Web MVP có workflow cơ bản, có thể demo nội bộ hoặc design partner.       |
| `[MVP-2]`    | Workflow pilot tại site thật, cần RBAC/audit/monitoring/clinical ops tốt hơn.     |
| `[MVP-3]`    | Scalable product/commercial beta, multi-site, integration sâu, governance đầy đủ. |
| `[MUST]`     | Không nên thiếu trong phase tương ứng.                                            |
| `[SHOULD]`   | Nên có nếu đủ nguồn lực.                                                          |
| `[LATER]`    | Trì hoãn để tránh scope creep.                                                    |
| `[CLINICAL]` | Liên quan trực tiếp đến workflow/interpretation lâm sàng.                         |
| `[AI]`       | Liên quan pipeline signal processing/ML.                                          |
| `[SEC]`      | Liên quan security/privacy/compliance.                                            |
| `[OPS]`      | Liên quan vận hành/pilot/customer success.                                        |
| `[BIZ]`      | Liên quan startup/business/fundraising.                                           |

### Nguyên tắc tổ chức repo

- **Monorepo được khuyến nghị ở giai đoạn đầu** để team nhỏ nhìn được toàn bộ sản phẩm, API, AI engine, docs, validation và deployment.
- **Raw signal không commit vào repo**. Repo chỉ lưu sample synthetic, manifest, schema và script tạo dữ liệu test.
- **Clinical protocol, preprocessing config, feature extractor và model/rule phải versioned** ngay từ đầu.
- **Report lâm sàng chỉ xuất sau human review**; report template cũng phải có version.
- **MFCV/CV là optional capability** nếu hardware/electrode setup chưa đủ điều kiện.

---

## 1. Full recommended project skeleton

```text
.
├── .agents
│   ├── rules
│   │   ├── common-agents.md
│   │   ├── common-code-review.md
│   │   ├── common-coding-style.md
│   │   ├── common-development-workflow.md
│   │   ├── common-git-workflow.md
│   │   ├── common-hooks.md
│   │   ├── common-patterns.md
│   │   ├── common-performance.md
│   │   ├── common-security.md
│   │   ├── common-testing.md
│   │   ├── core_workflow.md
│   │   ├── cpp-coding-style.md
│   │   ├── cpp-hooks.md
│   │   ├── cpp-patterns.md
│   │   ├── cpp-security.md
│   │   ├── cpp-testing.md
│   │   ├── csharp-coding-style.md
│   │   ├── csharp-hooks.md
│   │   ├── csharp-patterns.md
│   │   ├── csharp-security.md
│   │   ├── csharp-testing.md
│   │   ├── dart-coding-style.md
│   │   ├── dart-hooks.md
│   │   ├── dart-patterns.md
│   │   ├── dart-security.md
│   │   ├── dart-testing.md
│   │   ├── golang-coding-style.md
│   │   ├── golang-hooks.md
│   │   ├── golang-patterns.md
│   │   ├── golang-security.md
│   │   ├── golang-testing.md
│   │   ├── guess-or-certain.md
│   │   ├── idae_coding-standards.md
│   │   ├── idae_master-protocol.md
│   │   ├── idae_verification-protocol.md
│   │   ├── java-coding-style.md
│   │   ├── java-hooks.md
│   │   ├── java-patterns.md
│   │   ├── java-security.md
│   │   ├── java-testing.md
│   │   ├── JustScribe-security-guardrails.md
│   │   ├── kotlin-coding-style.md
│   │   ├── kotlin-hooks.md
│   │   ├── kotlin-patterns.md
│   │   ├── kotlin-security.md
│   │   ├── kotlin-testing.md
│   │   ├── perl-coding-style.md
│   │   ├── perl-hooks.md
│   │   ├── perl-patterns.md
│   │   ├── perl-security.md
│   │   ├── perl-testing.md
│   │   ├── php-coding-style.md
│   │   ├── php-hooks.md
│   │   ├── php-patterns.md
│   │   ├── php-security.md
│   │   ├── php-testing.md
│   │   ├── prr-code-review.md
│   │   ├── python-coding-style.md
│   │   ├── python-hooks.md
│   │   ├── python-patterns.md
│   │   ├── python-security.md
│   │   ├── python-testing.md
│   │   ├── rag_logging-protocol.md
│   │   ├── README.md
│   │   ├── rust-coding-style.md
│   │   ├── rust-hooks.md
│   │   ├── rust-patterns.md
│   │   ├── rust-security.md
│   │   ├── rust-testing.md
│   │   ├── swift-coding-style.md
│   │   ├── swift-hooks.md
│   │   ├── swift-patterns.md
│   │   ├── swift-security.md
│   │   ├── swift-testing.md
│   │   ├── typescript-coding-style.md
│   │   ├── typescript-hooks.md
│   │   ├── typescript-patterns.md
│   │   ├── typescript-security.md
│   │   ├── typescript-testing.md
│   │   ├── understand-anything-agent-protocol.md
│   │   ├── walkthrough_and_task.md
│   │   ├── web-coding-style.md
│   │   ├── web-design-quality.md
│   │   ├── web-hooks.md
│   │   ├── web-patterns.md
│   │   ├── web-performance.md
│   │   ├── web-security.md
│   │   ├── web-testing.md
│   │   ├── zh-agents.md
│   │   ├── zh-code-review.md
│   │   ├── zh-coding-style.md
│   │   ├── zh-development-workflow.md
│   │   ├── zh-git-workflow.md
│   │   ├── zh-hooks.md
│   │   ├── zh-patterns.md
│   │   ├── zh-performance.md
│   │   ├── zh-README.md
│   │   ├── zh-security.md
│   │   └── zh-testing.md
│   ├── skills
│   │   ├── agent-harness-construction
│   │   │   └── SKILL.md
│   │   ├── agentic-engineering
│   │   │   └── SKILL.md
│   │   ├── agent-introspection-debugging
│   │   │   └── SKILL.md
│   │   ├── agent-sort
│   │   │   └── SKILL.md
│   │   ├── ai-first-engineering
│   │   │   └── SKILL.md
│   │   ├── ai-regression-testing
│   │   │   └── SKILL.md
│   │   ├── android-clean-architecture
│   │   │   └── SKILL.md
│   │   ├── api-connector-builder
│   │   │   └── SKILL.md
│   │   ├── api-design
│   │   │   └── SKILL.md
│   │   ├── article-writing
│   │   │   └── SKILL.md
│   │   ├── automation-audit-ops
│   │   │   └── SKILL.md
│   │   ├── autonomous-loops
│   │   │   └── SKILL.md
│   │   ├── backend-patterns
│   │   │   └── SKILL.md
│   │   ├── blueprint
│   │   │   └── SKILL.md
│   │   ├── brandkit
│   │   │   └── SKILL.md
│   │   ├── brand-voice
│   │   │   ├── references
│   │   │   │   └── voice-profile-schema.md
│   │   │   └── SKILL.md
│   │   ├── carrier-relationship-management
│   │   │   └── SKILL.md
│   │   ├── claude-api
│   │   │   └── SKILL.md
│   │   ├── claude-devfleet
│   │   │   └── SKILL.md
│   │   ├── clickhouse-io
│   │   │   └── SKILL.md
│   │   ├── code-tour
│   │   │   └── SKILL.md
│   │   ├── coding-standards
│   │   │   └── SKILL.md
│   │   ├── compose-multiplatform-patterns
│   │   │   └── SKILL.md
│   │   ├── configure-ecc
│   │   │   └── SKILL.md
│   │   ├── connections-optimizer
│   │   │   └── SKILL.md
│   │   ├── content-engine
│   │   │   └── SKILL.md
│   │   ├── content-hash-cache-pattern
│   │   │   └── SKILL.md
│   │   ├── continuous-agent-loop
│   │   │   └── SKILL.md
│   │   ├── continuous-learning
│   │   │   ├── config.json
│   │   │   ├── evaluate-session.sh
│   │   │   └── SKILL.md
│   │   ├── continuous-learning-v2
│   │   │   ├── agents
│   │   │   │   ├── observer-loop.sh
│   │   │   │   ├── observer.md
│   │   │   │   ├── session-guardian.sh
│   │   │   │   └── start-observer.sh
│   │   │   ├── hooks
│   │   │   │   └── observe.sh
│   │   │   ├── scripts
│   │   │   │   ├── detect-project.sh
│   │   │   │   ├── instinct-cli.py
│   │   │   │   └── test_parse_instinct.py
│   │   │   ├── config.json
│   │   │   └── SKILL.md
│   │   ├── cost-aware-llm-pipeline
│   │   │   └── SKILL.md
│   │   ├── council
│   │   │   └── SKILL.md
│   │   ├── cpp-coding-standards
│   │   │   └── SKILL.md
│   │   ├── cpp-testing
│   │   │   └── SKILL.md
│   │   ├── crosspost
│   │   │   └── SKILL.md
│   │   ├── csharp-testing
│   │   │   └── SKILL.md
│   │   ├── customer-billing-ops
│   │   │   └── SKILL.md
│   │   ├── customs-trade-compliance
│   │   │   └── SKILL.md
│   │   ├── dart-flutter-patterns
│   │   │   └── SKILL.md
│   │   ├── dashboard-builder
│   │   │   └── SKILL.md
│   │   ├── database-migrations
│   │   │   └── SKILL.md
│   │   ├── data-scraper-agent
│   │   │   └── SKILL.md
│   │   ├── deep-research
│   │   │   └── SKILL.md
│   │   ├── defi-amm-security
│   │   │   └── SKILL.md
│   │   ├── deployment-patterns
│   │   │   └── SKILL.md
│   │   ├── design-taste-frontend
│   │   │   └── SKILL.md
│   │   ├── design-taste-frontend-v1
│   │   │   └── SKILL.md
│   │   ├── django-patterns
│   │   │   └── SKILL.md
│   │   ├── django-security
│   │   │   └── SKILL.md
│   │   ├── django-tdd
│   │   │   └── SKILL.md
│   │   ├── django-verification
│   │   │   └── SKILL.md
│   │   ├── docker-patterns
│   │   │   └── SKILL.md
│   │   ├── dotnet-patterns
│   │   │   └── SKILL.md
│   │   ├── e2e-testing
│   │   │   └── SKILL.md
│   │   ├── ecc-tools-cost-audit
│   │   │   └── SKILL.md
│   │   ├── email-ops
│   │   │   └── SKILL.md
│   │   ├── energy-procurement
│   │   │   └── SKILL.md
│   │   ├── enterprise-agent-ops
│   │   │   └── SKILL.md
│   │   ├── eval-harness
│   │   │   └── SKILL.md
│   │   ├── evm-token-decimals
│   │   │   └── SKILL.md
│   │   ├── exa-search
│   │   │   └── SKILL.md
│   │   ├── finance-billing-ops
│   │   │   └── SKILL.md
│   │   ├── flutter-theme-migration
│   │   │   └── SKILL.md
│   │   ├── foundation-models-on-device
│   │   │   └── SKILL.md
│   │   ├── frontend-design
│   │   │   └── SKILL.md
│   │   ├── frontend-patterns
│   │   │   └── SKILL.md
│   │   ├── frontend-slides
│   │   │   ├── SKILL.md
│   │   │   └── STYLE_PRESETS.md
│   │   ├── full-output-enforcement
│   │   │   └── SKILL.md
│   │   ├── github-ops
│   │   │   └── SKILL.md
│   │   ├── golang-patterns
│   │   │   └── SKILL.md
│   │   ├── golang-testing
│   │   │   └── SKILL.md
│   │   ├── google-workspace-ops
│   │   │   └── SKILL.md
│   │   ├── gpt-taste
│   │   │   └── SKILL.md
│   │   ├── healthcare-phi-compliance
│   │   │   └── SKILL.md
│   │   ├── high-end-visual-design
│   │   │   └── SKILL.md
│   │   ├── hipaa-compliance
│   │   │   └── SKILL.md
│   │   ├── hookify-rules
│   │   │   └── SKILL.md
│   │   ├── imagegen-frontend-mobile
│   │   │   └── SKILL.md
│   │   ├── imagegen-frontend-web
│   │   │   └── SKILL.md
│   │   ├── image-to-code
│   │   │   └── SKILL.md
│   │   ├── industrial-brutalist-ui
│   │   │   └── SKILL.md
│   │   ├── inventory-demand-planning
│   │   │   └── SKILL.md
│   │   ├── investor-materials
│   │   │   └── SKILL.md
│   │   ├── investor-outreach
│   │   │   └── SKILL.md
│   │   ├── iterative-retrieval
│   │   │   └── SKILL.md
│   │   ├── java-coding-standards
│   │   │   └── SKILL.md
│   │   ├── jira-integration
│   │   │   └── SKILL.md
│   │   ├── jpa-patterns
│   │   │   └── SKILL.md
│   │   ├── knowledge-ops
│   │   │   └── SKILL.md
│   │   ├── kotlin-coroutines-flows
│   │   │   └── SKILL.md
│   │   ├── kotlin-exposed-patterns
│   │   │   └── SKILL.md
│   │   ├── kotlin-ktor-patterns
│   │   │   └── SKILL.md
│   │   ├── kotlin-patterns
│   │   │   └── SKILL.md
│   │   ├── kotlin-testing
│   │   │   └── SKILL.md
│   │   ├── laravel-patterns
│   │   │   └── SKILL.md
│   │   ├── laravel-plugin-discovery
│   │   │   └── SKILL.md
│   │   ├── laravel-security
│   │   │   └── SKILL.md
│   │   ├── laravel-tdd
│   │   │   └── SKILL.md
│   │   ├── laravel-verification
│   │   │   └── SKILL.md
│   │   ├── lead-intelligence
│   │   │   ├── agents
│   │   │   │   ├── enrichment-agent.md
│   │   │   │   ├── mutual-mapper.md
│   │   │   │   ├── outreach-drafter.md
│   │   │   │   └── signal-scorer.md
│   │   │   └── SKILL.md
│   │   ├── liquid-glass-design
│   │   │   └── SKILL.md
│   │   ├── llm-trading-agent-security
│   │   │   └── SKILL.md
│   │   ├── local-xlsx-schema
│   │   │   ├── agents
│   │   │   │   └── openai.yaml
│   │   │   ├── scripts
│   │   │   │   └── inspect_workbook.py
│   │   │   └── SKILL.md
│   │   ├── logistics-exception-management
│   │   │   └── SKILL.md
│   │   ├── market-research
│   │   │   └── SKILL.md
│   │   ├── mcp-server-patterns
│   │   │   └── SKILL.md
│   │   ├── messages-ops
│   │   │   └── SKILL.md
│   │   ├── minimalist-ui
│   │   │   └── SKILL.md
│   │   ├── nanoclaw-repl
│   │   │   └── SKILL.md
│   │   ├── nestjs-patterns
│   │   │   └── SKILL.md
│   │   ├── nodejs-keccak256
│   │   │   └── SKILL.md
│   │   ├── nutrient-document-processing
│   │   │   └── SKILL.md
│   │   ├── perl-patterns
│   │   │   └── SKILL.md
│   │   ├── perl-security
│   │   │   └── SKILL.md
│   │   ├── perl-testing
│   │   │   └── SKILL.md
│   │   ├── plankton-code-quality
│   │   │   └── SKILL.md
│   │   ├── postgres-patterns
│   │   │   └── SKILL.md
│   │   ├── product-capability
│   │   │   └── SKILL.md
│   │   ├── production-scheduling
│   │   │   └── SKILL.md
│   │   ├── project-flow-ops
│   │   │   └── SKILL.md
│   │   ├── prompt-optimizer
│   │   │   └── SKILL.md
│   │   ├── python-patterns
│   │   │   └── SKILL.md
│   │   ├── python-testing
│   │   │   └── SKILL.md
│   │   ├── quality-nonconformance
│   │   │   └── SKILL.md
│   │   ├── ralphinho-rfc-pipeline
│   │   │   └── SKILL.md
│   │   ├── redesign-existing-projects
│   │   │   └── SKILL.md
│   │   ├── regex-vs-llm-structured-text
│   │   │   └── SKILL.md
│   │   ├── research-ops
│   │   │   └── SKILL.md
│   │   ├── returns-reverse-logistics
│   │   │   └── SKILL.md
│   │   ├── rust-patterns
│   │   │   └── SKILL.md
│   │   ├── rust-testing
│   │   │   └── SKILL.md
│   │   ├── search-first
│   │   │   └── SKILL.md
│   │   ├── security-bounty-hunter
│   │   │   └── SKILL.md
│   │   ├── security-review
│   │   │   ├── cloud-infrastructure-security.md
│   │   │   └── SKILL.md
│   │   ├── security-scan
│   │   │   └── SKILL.md
│   │   ├── seo
│   │   │   └── SKILL.md
│   │   ├── skill-stocktake
│   │   │   ├── scripts
│   │   │   │   ├── quick-diff.sh
│   │   │   │   ├── save-results.sh
│   │   │   │   └── scan.sh
│   │   │   └── SKILL.md
│   │   ├── social-graph-ranker
│   │   │   └── SKILL.md
│   │   ├── springboot-patterns
│   │   │   └── SKILL.md
│   │   ├── springboot-security
│   │   │   └── SKILL.md
│   │   ├── springboot-tdd
│   │   │   └── SKILL.md
│   │   ├── springboot-verification
│   │   │   └── SKILL.md
│   │   ├── stitch-design-taste
│   │   │   ├── DESIGN.md
│   │   │   └── SKILL.md
│   │   ├── strategic-compact
│   │   │   ├── SKILL.md
│   │   │   └── suggest-compact.sh
│   │   ├── swift-actor-persistence
│   │   │   └── SKILL.md
│   │   ├── swift-concurrency-6-2
│   │   │   └── SKILL.md
│   │   ├── swift-protocol-di-testing
│   │   │   └── SKILL.md
│   │   ├── swiftui-patterns
│   │   │   └── SKILL.md
│   │   ├── tdd-workflow
│   │   │   └── SKILL.md
│   │   ├── team-builder
│   │   │   └── SKILL.md
│   │   ├── terminal-ops
│   │   │   └── SKILL.md
│   │   ├── token-budget-advisor
│   │   │   └── SKILL.md
│   │   ├── understand-anything
│   │   │   └── SKILL.md
│   │   ├── unified-notifications-ops
│   │   │   └── SKILL.md
│   │   ├── verification-loop
│   │   │   └── SKILL.md
│   │   ├── visa-doc-translate
│   │   │   ├── README.md
│   │   │   └── SKILL.md
│   │   ├── workspace-surface-audit
│   │   │   └── SKILL.md
│   │   ├── x-api
│   │   │   └── SKILL.md
│   │   ├── architect.md
│   │   ├── build-error-resolver.md
│   │   ├── ccpm -> /home/duykhongngu28/massive/day04_2A202600337/references/ccpm/skill/ccpm
│   │   ├── chief-of-staff.md
│   │   ├── code-architect.md
│   │   ├── code-explorer.md
│   │   ├── code-reviewer.md
│   │   ├── code-simplifier.md
│   │   ├── comment-analyzer.md
│   │   ├── conversation-analyzer.md
│   │   ├── cpp-build-resolver.md
│   │   ├── cpp-reviewer.md
│   │   ├── csharp-reviewer.md
│   │   ├── dart-build-resolver.md
│   │   ├── database-reviewer.md
│   │   ├── docs-lookup.md
│   │   ├── doc-updater.md
│   │   ├── e2e-runner.md
│   │   ├── flutter-reviewer.md
│   │   ├── gan-evaluator.md
│   │   ├── gan-generator.md
│   │   ├── gan-planner.md
│   │   ├── go-build-resolver.md
│   │   ├── go-reviewer.md
│   │   ├── harness-optimizer.md
│   │   ├── healthcare-reviewer.md
│   │   ├── java-build-resolver.md
│   │   ├── java-reviewer.md
│   │   ├── kotlin-build-resolver.md
│   │   ├── kotlin-reviewer.md
│   │   ├── loop-operator.md
│   │   ├── opensource-forker.md
│   │   ├── opensource-packager.md
│   │   ├── opensource-sanitizer.md
│   │   ├── performance-optimizer.md
│   │   ├── planner.md
│   │   ├── pr-test-analyzer.md
│   │   ├── python-reviewer.md
│   │   ├── pytorch-build-resolver.md
│   │   ├── refactor-cleaner.md
│   │   ├── rust-build-resolver.md
│   │   ├── rust-reviewer.md
│   │   ├── security-reviewer.md
│   │   ├── seo-specialist.md
│   │   ├── silent-failure-hunter.md
│   │   ├── tdd-guide.md
│   │   ├── type-design-analyzer.md
│   │   └── typescript-reviewer.md
│   └── workflows
│       ├── agent-sort.md
│       ├── aside.md
│       ├── build-fix.md
│       ├── checkpoint.md
│       ├── claw.md
│       ├── code-review.md
│       ├── context-budget.md
│       ├── cpp-build.md
│       ├── cpp-review.md
│       ├── cpp-test.md
│       ├── devfleet.md
│       ├── docs.md
│       ├── e2e.md
│       ├── eval.md
│       ├── evolve.md
│       ├── feature-dev.md
│       ├── flutter-build.md
│       ├── flutter-review.md
│       ├── flutter-test.md
│       ├── gan-build.md
│       ├── gan-design.md
│       ├── go-build.md
│       ├── go-review.md
│       ├── go-test.md
│       ├── gradle-build.md
│       ├── harness-audit.md
│       ├── hookify-configure.md
│       ├── hookify-help.md
│       ├── hookify-list.md
│       ├── hookify.md
│       ├── instinct-export.md
│       ├── instinct-import.md
│       ├── instinct-status.md
│       ├── jira.md
│       ├── kotlin-build.md
│       ├── kotlin-review.md
│       ├── kotlin-test.md
│       ├── learn-eval.md
│       ├── learn.md
│       ├── loop-start.md
│       ├── loop-status.md
│       ├── model-route.md
│       ├── multi-backend.md
│       ├── multi-execute.md
│       ├── multi-frontend.md
│       ├── multi-plan.md
│       ├── multi-workflow.md
│       ├── orchestrate.md
│       ├── plan.md
│       ├── pm2.md
│       ├── projects.md
│       ├── promote.md
│       ├── prompt-optimize.md
│       ├── prp-commit.md
│       ├── prp-implement.md
│       ├── prp-plan.md
│       ├── prp-prd.md
│       ├── prp-pr.md
│       ├── prune.md
│       ├── python-review.md
│       ├── quality-gate.md
│       ├── refactor-clean.md
│       ├── resume-session.md
│       ├── review-pr.md
│       ├── rules-distill.md
│       ├── rust-build.md
│       ├── rust-review.md
│       ├── rust-test.md
│       ├── santa-loop.md
│       ├── save-session.md
│       ├── sessions.md
│       ├── setup-pm.md
│       ├── skill-create.md
│       ├── skill-health.md
│       ├── tdd.md
│       ├── test-coverage.md
│       ├── understand-anything-workflow.md
│       ├── update-codemaps.md
│       ├── update-docs.md
│       └── verify.md
├── ai-core
│   ├── calibration
│   │   ├── abstention.py
│   │   ├── calibration.py
│   │   ├── __init__.py
│   │   └── metrics.py
│   ├── configs
│   │   ├── abstention_reason_registry.v0.1.yaml
│   │   ├── dataset_research_v0.2.yaml
│   │   ├── day27_dataset_selection.research.yaml
│   │   ├── day27_training_authorization.research.yaml
│   │   ├── day28_eda.research.yaml
│   │   ├── day28_quality_rules.provisional.yaml
│   │   ├── day29_cross_day_drift.research.yaml
│   │   ├── day29_grabmyo_eda.research.yaml
│   │   ├── day29_grabmyo_quality_rules.provisional.yaml
│   │   ├── day30_channel_policy.research.yaml
│   │   ├── day30_dataset_views.research.yaml
│   │   ├── day30_experiment_eligibility.research.yaml
│   │   ├── day30_harmonization.research.yaml
│   │   ├── day30_normalization_policy.research.yaml
│   │   ├── day30_sampling_policy.research.yaml
│   │   ├── day30_training_authorization.research.yaml
│   │   ├── day30_windowing_policy.research.yaml
│   │   ├── day31_authorization.research.yaml
│   │   ├── day31_dataset_views.research.yaml
│   │   ├── day31_feature_arms.research.yaml
│   │   ├── day31_feature_contract.v1.yaml
│   │   ├── day31_feature_engineering.research.yaml
│   │   ├── day31_output_contract.research.yaml
│   │   ├── day31_quality_thresholds.provisional.yaml
│   │   ├── day31_spectral_contract.v1.yaml
│   │   ├── day32_baseline_protocol.research.yaml
│   │   ├── day32_compute_budget.research.yaml
│   │   ├── day32_core_models.research.yaml
│   │   ├── day32_execution_authorization.template.yaml
│   │   ├── day32_metrics_contract.research.yaml
│   │   ├── day32_optional_models.research.yaml
│   │   ├── day32_validation_protocol.research.yaml
│   │   ├── day33_bootstrap_protocol.research.yaml
│   │   ├── day33_comparison_protocol.research.yaml
│   │   ├── day33_evaluation_protocol.research.yaml
│   │   ├── day33_execution_authorization.template.yaml
│   │   ├── day33_failure_taxonomy.research.yaml
│   │   ├── day34_fewshot_protocol.research.yaml
│   │   ├── day34_personalization_gate.research.yaml
│   │   ├── day35_abstention_policy.research.yaml
│   │   ├── day35_calibration_protocol.research.yaml
│   │   ├── day36_fatigue_context_policy.yaml
│   │   ├── day37_taskc_metric_registry.yaml                     # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── environment-lock.research.yaml
│   │   ├── evaluation_pilot.yaml
│   │   ├── evaluation_regimes.research.yaml
│   │   ├── experiment_matrix.draft.yaml
│   │   ├── fatigue_experiments.research.yaml
│   │   ├── feature_extraction_mvp1.yaml
│   │   ├── feature_groups.research.yaml
│   │   ├── license-gate.research.yaml
│   │   ├── mendeley_4ch_label_map.template.json
│   │   ├── mendeley_4ch_mapping_profile.template.json
│   │   ├── mlflow-local.research.yaml
│   │   ├── model_ladder.research.yaml
│   │   ├── model_registry_states.research.yaml
│   │   ├── model_training_baseline.yaml
│   │   ├── offline_analysis_mvp0.yaml
│   │   ├── offline-pipeline-v0.1.yaml
│   │   ├── personalization_strategies.research.yaml
│   │   ├── registry-state-machine.research.yaml
│   │   ├── serialization-policy.research.yaml
│   │   ├── task_contracts.research.yaml
│   │   └── training_authorization.research.yaml
│   ├── context
│   │   ├── engine.py
│   │   └── schema.py
│   ├── data
│   │   ├── day27
│   │   │   ├── contracts.py
│   │   │   ├── engineering_gate.py
│   │   │   ├── group_split.py
│   │   │   ├── hashing.py
│   │   │   ├── __init__.py
│   │   │   ├── label_mapping.py
│   │   │   ├── profile_driven_csv_adapter.py
│   │   │   ├── safe_archive.py
│   │   │   └── source_record.py
│   │   ├── day28
│   │   │   ├── __init__.py
│   │   │   ├── label_audit.py
│   │   │   ├── manifest_io.py
│   │   │   ├── preflight.py
│   │   │   ├── quality_rules.py
│   │   │   ├── signal_quality.py
│   │   │   └── structural_eda.py
│   │   ├── day29
│   │   │   ├── contracts.py
│   │   │   ├── cross_day_drift.py
│   │   │   ├── descriptive_stats.py
│   │   │   ├── feature_eligibility.py
│   │   │   ├── hierarchy_audit.py
│   │   │   ├── __init__.py
│   │   │   ├── label_audit.py
│   │   │   ├── manifest_io.py
│   │   │   ├── partition_guard.py
│   │   │   ├── readiness.py
│   │   │   ├── signal_loader.py
│   │   │   └── signal_quality.py
│   │   ├── day30
│   │   │   ├── channel_policy.py
│   │   │   ├── contracts.py
│   │   │   ├── __init__.py
│   │   │   ├── normalization.py
│   │   │   ├── ontology.py
│   │   │   ├── policy_validation.py
│   │   │   ├── preflight.py
│   │   │   ├── readiness.py
│   │   │   ├── sample_rate.py
│   │   │   ├── storage_contract.py
│   │   │   ├── view_registry.py
│   │   │   └── windowing.py
│   │   ├── day31
│   │   │   ├── contracts.py
│   │   │   ├── __init__.py
│   │   │   ├── io.py
│   │   │   ├── pipeline.py
│   │   │   ├── preflight.py
│   │   │   └── readiness.py
│   │   ├── dataset_catalog.py
│   │   ├── evidence_catalog.py
│   │   ├── group_split.py
│   │   ├── group_split_v2.py
│   │   ├── __init__.py
│   │   └── readiness_gate_v2.py
│   ├── evaluation
│   │   └── day33
│   │       ├── aggregation.py
│   │       ├── bootstrap.py
│   │       ├── contracts.py
│   │       ├── cross_day.py
│   │       ├── day32_adapters.py
│   │       ├── failure_cases.py
│   │       ├── __init__.py
│   │       ├── io.py
│   │       ├── metrics.py
│   │       ├── prediction_gate.py
│   │       └── readiness.py
│   ├── experiments
│   │   ├── cross-dataset-transfer-handoff
│   │   │   ├── common-representation-manifest.json
│   │   │   ├── day38-transfer-protocol.json                     # [MVP-2][MUST] Day 38 Cross-Dataset Transfer
│   │   │   ├── day38-transfer-readiness.json                    # [MVP-2][MUST] Day 38 Cross-Dataset Transfer
│   │   │   ├── domain-classifier-results.json
│   │   │   ├── domain-gap-per-feature.csv
│   │   │   ├── domain-gap-summary.json
│   │   │   ├── per-class-transfer.csv
│   │   │   ├── per-subject-transfer.csv
│   │   │   ├── source-model-selection.csv
│   │   │   ├── transfer-bundles.joblib
│   │   │   ├── transfer-failure-cases.csv
│   │   │   └── zero-shot-results.csv
│   │   ├── grabmyo-primary4
│   │   │   ├── baseline-v1
│   │   │   │   ├── grabmyo-baseline-handoff
│   │   │   │   │   ├── grabmyo-baseline-evidence.json
│   │   │   │   │   ├── grabmyo-baseline-final-gate.json
│   │   │   │   │   ├── grabmyo-baseline-input-gate.json
│   │   │   │   │   ├── grabmyo-cv-fold-contract.json
│   │   │   │   │   ├── grabmyo-cv-fold-metrics.csv
│   │   │   │   │   ├── grabmyo-cv-leaderboard.csv
│   │   │   │   │   ├── grabmyo-cv-leaderboard.png
│   │   │   │   │   ├── grabmyo-cv-subject-fold-assignment.csv
│   │   │   │   │   ├── grabmyo-model-selection.json
│   │   │   │   │   ├── grabmyo-selected-model.joblib
│   │   │   │   │   ├── grabmyo-selected-model-metadata.json
│   │   │   │   │   ├── grabmyo-selected-oof-metrics.json
│   │   │   │   │   ├── grabmyo-selected-oof-session-metrics.csv
│   │   │   │   │   ├── grabmyo-selected-oof-subject-metrics.csv
│   │   │   │   │   ├── grabmyo-selected-oof-trial-predictions.csv
│   │   │   │   │   ├── grabmyo-validation-metrics.json
│   │   │   │   │   ├── grabmyo-validation-session-metrics.csv
│   │   │   │   │   ├── grabmyo-validation-subject-metrics.csv
│   │   │   │   │   ├── grabmyo-validation-subject-session-metrics.csv
│   │   │   │   │   ├── grabmyo-validation-trial-confusion-matrix.csv
│   │   │   │   │   ├── grabmyo-validation-trial-confusion-matrix.png
│   │   │   │   │   ├── grabmyo-validation-trial-predictions.csv
│   │   │   │   │   ├── grabmyo-validation-window-confusion-matrix.csv
│   │   │   │   │   └── grabmyo-validation-window-confusion-matrix.png
│   │   │   │   └── grabmyo-baseline-handoff.zip
│   │   │   ├── day34-personalization-v2
│   │   │   │   ├── day34-adapter-representation.json
│   │   │   │   ├── day34-final-gate.json
│   │   │   │   ├── day34-input-gate.json
│   │   │   │   ├── day34-p0-reproduction-audit.csv
│   │   │   │   ├── day34-p0-reproduction-audit.json
│   │   │   │   ├── day34-personalization-evidence.json
│   │   │   │   ├── few-shot-adapter-bundle.joblib
│   │   │   │   ├── few-shot-calibration-manifest.csv
│   │   │   │   ├── few-shot-class-summary.csv
│   │   │   │   ├── few-shot-policy-search.csv
│   │   │   │   ├── few-shot-policy-selection.json
│   │   │   │   ├── few-shot-protocol.json
│   │   │   │   ├── few-shot-results.csv
│   │   │   │   ├── few-shot-session-summary.csv
│   │   │   │   ├── few-shot-trial-predictions.csv.gz
│   │   │   │   ├── personalization-delta-distribution.png
│   │   │   │   ├── personalization-vs-global.csv
│   │   │   │   ├── personalization-vs-global.png
│   │   │   │   └── per-subject-improvement.csv
│   │   │   ├── day35-confidence-v2
│   │   │   │   ├── day35-abstention-policy.json
│   │   │   │   ├── day35-abstention-score-selection.csv
│   │   │   │   ├── day35-calibration-abstention-bundle.joblib
│   │   │   │   ├── day35-calibrator-candidate-metrics.csv
│   │   │   │   ├── day35-calibrator-selection.json
│   │   │   │   ├── day35-confidence-abstention-protocol.json
│   │   │   │   ├── day35-confidence-calibration-evidence.json
│   │   │   │   ├── day35-coverage-risk-k2-p0-cross_session.png
│   │   │   │   ├── day35-coverage-risk-k2-p1-cross_session.png
│   │   │   │   ├── day35-coverage-risk-k3-p0-cross_session.png
│   │   │   │   ├── day35-coverage-risk-k3-p1-cross_session.png
│   │   │   │   ├── day35-development-coverage-risk.csv
│   │   │   │   ├── day35-development-episode-manifest.csv
│   │   │   │   ├── day35-development-predictions.csv.gz
│   │   │   │   ├── day35-development-subject-partitions.csv
│   │   │   │   ├── day35-figure-manifest.json
│   │   │   │   ├── day35-final-gate.json
│   │   │   │   ├── day35-input-gate.json
│   │   │   │   ├── day35-reliability-k2-p0-cross_session.png
│   │   │   │   ├── day35-reliability-k2-p1-cross_session.png
│   │   │   │   ├── day35-reliability-k3-p0-cross_session.png
│   │   │   │   ├── day35-reliability-k3-p1-cross_session.png
│   │   │   │   ├── day35-validation-calibration-metrics.csv
│   │   │   │   ├── day35-validation-class-metrics.csv
│   │   │   │   ├── day35-validation-coverage-risk.csv
│   │   │   │   ├── day35-validation-predictions.csv.gz
│   │   │   │   ├── day35-validation-reliability-bins.csv
│   │   │   │   ├── day35-validation-selective-metrics.csv
│   │   │   │   ├── day35-validation-session-metrics.csv
│   │   │   │   └── day35-validation-subject-metrics.csv
│   │   │   └── day37-taskc-v2                                   # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   │       └── grabmyo-summary-report.md
│   │   ├── mendeley-primary
│   │   │   ├── day32-baseline-v1
│   │   │   │   ├── day32-baseline-evidence.json
│   │   │   │   ├── day32-cv-fold-contract.json
│   │   │   │   ├── day32-cv-fold-metrics.csv
│   │   │   │   ├── day32-cv-leaderboard.csv
│   │   │   │   ├── day32-cv-leaderboard.png
│   │   │   │   ├── day32-cv-subject-fold-assignment.csv
│   │   │   │   ├── day32-final-gate.json
│   │   │   │   ├── day32-model-selection.json
│   │   │   │   ├── day32-selected-model.joblib
│   │   │   │   ├── day32-selected-model-metadata.json
│   │   │   │   ├── day32-selected-oof-metrics.json
│   │   │   │   ├── day32-selected-oof-repetition-predictions.csv
│   │   │   │   ├── day32-selected-oof-subject-metrics.csv
│   │   │   │   ├── day32-selected-oof-window-predictions.csv.gz
│   │   │   │   ├── day32-training-summary.json
│   │   │   │   ├── day32-validation-metrics.json
│   │   │   │   ├── day32-validation-repetition-confusion-matrix.csv
│   │   │   │   ├── day32-validation-repetition-confusion-matrix.png
│   │   │   │   ├── day32-validation-repetition-predictions.csv
│   │   │   │   ├── day32-validation-subject-metrics.csv
│   │   │   │   ├── day32-validation-window-confusion-matrix.csv
│   │   │   │   ├── day32-validation-window-confusion-matrix.png
│   │   │   │   └── day32-validation-window-predictions.csv.gz
│   │   │   ├── day34-personalization-v2
│   │   │   │   ├── day34-adapter-representation.json
│   │   │   │   ├── day34-final-gate.json
│   │   │   │   ├── day34-input-gate.json
│   │   │   │   ├── day34-p0-reproduction-audit.csv
│   │   │   │   ├── day34-p0-reproduction-audit.json
│   │   │   │   ├── day34-personalization-evidence.json
│   │   │   │   ├── few-shot-adapter-bundle.joblib
│   │   │   │   ├── few-shot-calibration-manifest.csv
│   │   │   │   ├── few-shot-class-summary.csv
│   │   │   │   ├── few-shot-policy-search.csv
│   │   │   │   ├── few-shot-policy-selection.json
│   │   │   │   ├── few-shot-protocol.json
│   │   │   │   ├── few-shot-results.csv
│   │   │   │   ├── few-shot-session-summary.csv
│   │   │   │   ├── few-shot-trial-predictions.csv.gz
│   │   │   │   ├── personalization-delta-distribution.png
│   │   │   │   ├── personalization-vs-global.csv
│   │   │   │   ├── personalization-vs-global.png
│   │   │   │   └── per-subject-improvement.csv
│   │   │   ├── day35-confidence-v2
│   │   │   │   ├── day35-abstention-policy.json
│   │   │   │   ├── day35-abstention-score-selection.csv
│   │   │   │   ├── day35-calibration-abstention-bundle.joblib
│   │   │   │   ├── day35-calibrator-candidate-metrics.csv
│   │   │   │   ├── day35-calibrator-selection.json
│   │   │   │   ├── day35-confidence-abstention-protocol.json
│   │   │   │   ├── day35-confidence-calibration-evidence.json
│   │   │   │   ├── day35-coverage-risk-k2-p0-all_eval.png
│   │   │   │   ├── day35-coverage-risk-k2-p1-all_eval.png
│   │   │   │   ├── day35-coverage-risk-k3-p0-all_eval.png
│   │   │   │   ├── day35-coverage-risk-k3-p1-all_eval.png
│   │   │   │   ├── day35-development-coverage-risk.csv
│   │   │   │   ├── day35-development-episode-manifest.csv
│   │   │   │   ├── day35-development-predictions.csv.gz
│   │   │   │   ├── day35-development-subject-partitions.csv
│   │   │   │   ├── day35-figure-manifest.json
│   │   │   │   ├── day35-final-gate.json
│   │   │   │   ├── day35-input-gate.json
│   │   │   │   ├── day35-reliability-k2-p0-all_eval.png
│   │   │   │   ├── day35-reliability-k2-p1-all_eval.png
│   │   │   │   ├── day35-reliability-k3-p0-all_eval.png
│   │   │   │   ├── day35-reliability-k3-p1-all_eval.png
│   │   │   │   ├── day35-validation-calibration-metrics.csv
│   │   │   │   ├── day35-validation-class-metrics.csv
│   │   │   │   ├── day35-validation-coverage-risk.csv
│   │   │   │   ├── day35-validation-predictions.csv.gz
│   │   │   │   ├── day35-validation-reliability-bins.csv
│   │   │   │   ├── day35-validation-selective-metrics.csv
│   │   │   │   ├── day35-validation-session-metrics.csv
│   │   │   │   └── day35-validation-subject-metrics.csv
│   │   │   └── day37-taskc-v2                                   # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   │       ├── between-session-bland-altman.csv
│   │   │       ├── cocontraction-eligibility.json
│   │   │       ├── cocontraction-results.csv
│   │   │       ├── day37-day36-integration-report.json          # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   │       ├── day37-final-manifest.json                    # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   │       ├── repeatability-icc-results.csv
│   │   │       ├── repeatability-results.csv
│   │   │       ├── repeatability-subject-summary.csv
│   │   │       ├── similarity-results.csv
│   │   │       ├── similarity-subject-summary.csv
│   │   │       ├── taskc-metric-registry.yaml
│   │   │       ├── taskc-repetition-feature-manifest.json
│   │   │       ├── taskc-repetition-features.parquet
│   │   │       └── taskc-sensitivity-report.json
│   │   ├── offline-pipeline-handoff
│   │   │   ├── SYN-FAIL
│   │   │   │   ├── context
│   │   │   │   │   └── context-result.json
│   │   │   │   ├── features
│   │   │   │   ├── inference
│   │   │   │   │   └── prediction.json
│   │   │   │   ├── logs
│   │   │   │   ├── manifests
│   │   │   │   │   ├── artifact-ledger.json
│   │   │   │   │   ├── input-manifest.json
│   │   │   │   │   └── pipeline-run-manifest.json
│   │   │   │   ├── qc
│   │   │   │   │   └── quality-report.json
│   │   │   │   ├── report
│   │   │   │   │   ├── report.json
│   │   │   │   │   └── report.md
│   │   │   │   └── taskc
│   │   │   │       └── quantitative-summary.json
│   │   │   ├── SYN-PASS
│   │   │   │   ├── context
│   │   │   │   │   └── context-result.json
│   │   │   │   ├── features
│   │   │   │   │   └── feature-summary.json
│   │   │   │   ├── inference
│   │   │   │   │   └── prediction.json
│   │   │   │   ├── logs
│   │   │   │   ├── manifests
│   │   │   │   │   ├── artifact-ledger.json
│   │   │   │   │   ├── input-manifest.json
│   │   │   │   │   └── pipeline-run-manifest.json
│   │   │   │   ├── qc
│   │   │   │   │   └── quality-report.json
│   │   │   │   ├── report
│   │   │   │   │   ├── report.json
│   │   │   │   │   └── report.md
│   │   │   │   └── taskc
│   │   │   │       └── quantitative-summary.json
│   │   │   ├── SYN-RERUN-A
│   │   │   │   ├── context
│   │   │   │   │   └── context-result.json
│   │   │   │   ├── features
│   │   │   │   │   └── feature-summary.json
│   │   │   │   ├── inference
│   │   │   │   │   └── prediction.json
│   │   │   │   ├── logs
│   │   │   │   ├── manifests
│   │   │   │   │   ├── artifact-ledger.json
│   │   │   │   │   ├── input-manifest.json
│   │   │   │   │   └── pipeline-run-manifest.json
│   │   │   │   ├── qc
│   │   │   │   │   └── quality-report.json
│   │   │   │   ├── report
│   │   │   │   │   ├── report.json
│   │   │   │   │   └── report.md
│   │   │   │   └── taskc
│   │   │   │       └── quantitative-summary.json
│   │   │   ├── SYN-RERUN-B
│   │   │   │   ├── context
│   │   │   │   │   └── context-result.json
│   │   │   │   ├── features
│   │   │   │   │   └── feature-summary.json
│   │   │   │   ├── inference
│   │   │   │   │   └── prediction.json
│   │   │   │   ├── logs
│   │   │   │   ├── manifests
│   │   │   │   │   ├── artifact-ledger.json
│   │   │   │   │   ├── input-manifest.json
│   │   │   │   │   └── pipeline-run-manifest.json
│   │   │   │   ├── qc
│   │   │   │   │   └── quality-report.json
│   │   │   │   ├── report
│   │   │   │   │   ├── report.json
│   │   │   │   │   └── report.md
│   │   │   │   └── taskc
│   │   │   │       └── quantitative-summary.json
│   │   │   ├── SYN-UNSUPPORTED
│   │   │   │   ├── context
│   │   │   │   │   └── context-result.json
│   │   │   │   ├── features
│   │   │   │   │   └── feature-summary.json
│   │   │   │   ├── inference
│   │   │   │   │   └── prediction.json
│   │   │   │   ├── logs
│   │   │   │   ├── manifests
│   │   │   │   │   ├── artifact-ledger.json
│   │   │   │   │   ├── input-manifest.json
│   │   │   │   │   └── pipeline-run-manifest.json
│   │   │   │   ├── qc
│   │   │   │   │   └── quality-report.json
│   │   │   │   ├── report
│   │   │   │   │   ├── report.json
│   │   │   │   │   └── report.md
│   │   │   │   └── taskc
│   │   │   │       └── quantitative-summary.json
│   │   │   ├── SYN-WARN
│   │   │   │   ├── context
│   │   │   │   │   └── context-result.json
│   │   │   │   ├── features
│   │   │   │   │   └── feature-summary.json
│   │   │   │   ├── inference
│   │   │   │   │   └── prediction.json
│   │   │   │   ├── logs
│   │   │   │   ├── manifests
│   │   │   │   │   ├── artifact-ledger.json
│   │   │   │   │   ├── input-manifest.json
│   │   │   │   │   └── pipeline-run-manifest.json
│   │   │   │   ├── qc
│   │   │   │   │   └── quality-report.json
│   │   │   │   ├── report
│   │   │   │   │   ├── report.json
│   │   │   │   │   └── report.md
│   │   │   │   └── taskc
│   │   │   │       └── quantitative-summary.json
│   │   │   ├── day40-final-manifest.json
│   │   │   ├── pipeline-smoke-report.csv
│   │   │   └── rerun-comparison.json
│   │   ├── blueprint_contract.py
│   │   ├── experiment_matrix.py
│   │   ├── __init__.py
│   │   └── metric_contracts.py
│   ├── governance
│   │   └── day39                                                # [MVP-2][MUST] Day 39 Reproducibility & Governance
│   │       ├── environment.py
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── registry.py
│   │       └── rerun.py
│   ├── metrics
│   │   ├── baseline_metrics.template.json
│   │   ├── metric_definitions.md
│   │   └── pilot_metrics.template.json
│   ├── model-cards
│   │   ├── dummy.template.md
│   │   ├── fatigue_context.template.md
│   │   ├── fatigue_rule_v0.1_model_card.md
│   │   ├── lda.template.md
│   │   ├── linear_svm.template.md
│   │   ├── logistic_baseline_model_card.md
│   │   ├── logistic.template.md
│   │   ├── random_forest_baseline_model_card.md
│   │   └── random_forest.template.md
│   ├── modeling
│   │   └── day32
│   │       ├── aggregation.py
│   │       ├── authorization.py
│   │       ├── core_gate.py
│   │       ├── grouped_cv.py
│   │       ├── __init__.py
│   │       ├── matrix_gate.py
│   │       ├── metrics.py
│   │       ├── model_factory.py
│   │       └── smoke_runner.py
│   ├── notebooks
│   │   ├── 00_data_inventory.ipynb
│   │   ├── 00_gesture_data_inventory.ipynb
│   │   ├── 01_signal_qc_exploration.ipynb
│   │   ├── 02_feature_extraction_baseline.ipynb
│   │   ├── 03_fatigue_rule_baseline.ipynb
│   │   ├── 04_cv_mfcv_feasibility.ipynb
│   │   └── 05_reviewer_agreement_analysis.ipynb
│   ├── personalization
│   │   └── day34
│   │       ├── fewshot.py
│   │       ├── gate.py
│   │       └── __init__.py
│   ├── pipelines
│   │   ├── offline_pipeline_v0_1
│   │   │   ├── exceptions.py
│   │   │   ├── guards.py
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py
│   │   │   └── state.py
│   │   ├── analysis_manifest.py
│   │   ├── DAY15_IMPLEMENTATION_NOTES.md
│   │   ├── day32_materialize_matrix.py
│   │   ├── day32_run_core_baselines.py
│   │   ├── day32_run_optional_baselines.py
│   │   ├── day33_build_prediction_contract.py
│   │   ├── day33_run_evaluation.py
│   │   ├── day33_validate_predictions.py
│   │   ├── day37_finalize.py                                    # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── day37_quantitative_pipeline.py                       # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── evaluate_model.py
│   │   ├── export_research_features.py
│   │   ├── generate_golden_features.py
│   │   ├── offline_analysis.py
│   │   ├── run_offline_analysis.py
│   │   ├── run_offline_pipeline.py
│   │   └── train_classical_baseline.py
│   ├── quantitative
│   │   └── day37                                                # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │       ├── cocontraction.py
│   │       ├── __init__.py
│   │       ├── repeatability.py
│   │       ├── similarity.py
│   │       ├── supportability.py
│   │       └── types.py
│   ├── transfer
│   │   ├── domain_gap.py
│   │   ├── guards.py
│   │   ├── __init__.py
│   │   └── representation.py
│   ├── validation-reports
│   │   ├── analytical_validation_fatigue_evidence_v0.1.md
│   │   ├── analytical_validation_fatigue_rule_v0.1.md
│   │   ├── analytical_validation_frequency_features_v0.1.md
│   │   ├── analytical_validation_mvp0.md
│   │   ├── analytical_validation_mvp0.template.md
│   │   ├── analytical_validation_offline_pipeline_mvp0.md
│   │   ├── analytical_validation_preprocessing_v0.1.md
│   │   ├── analytical_validation_preprocessing_v0.1.template.md
│   │   ├── analytical_validation_spectral_estimation_v0.1.md
│   │   ├── analytical_validation_technical_confidence_v0.1.md
│   │   ├── analytical_validation_time_domain_features_v0.1.md
│   │   ├── analytical_validation_trend_features_v0.1.md
│   │   ├── offline_validation_mvp1.md
│   │   └── pilot_validation_mvp2.md
│   ├── README.md
│   ├── stress_test_day35.py
│   ├── stress_test_transfer.py
│   ├── test_calibration.py
│   └── test_transfer_logic.py
├── apps
│   ├── clinician-report-viewer
│   │   └── README.md
│   └── web-portal
│       ├── artifacts
│       │   └── font-check
│       ├── e2e
│       │   ├── day22-uc1-replay.spec.ts
│       │   ├── day23-uc2-regression.spec.ts
│       │   ├── day24-review-report-regression.spec.ts
│       │   └── workflow-e2e.spec.ts
│       ├── public
│       │   ├── logo.svg
│       │   ├── report-watermark.svg
│       │   └── VINMEC_logo.png
│       ├── src
│       │   ├── app
│       │   │   ├── analyses
│       │   │   │   ├── Day21AnalysisProcessingPage.tsx
│       │   │   │   └── Day21AnalysisRoutes.tsx
│       │   │   ├── (authenticated)
│       │   │   │   ├── admin
│       │   │   │   │   └── users
│       │   │   │   │       └── page.tsx
│       │   │   │   ├── analyses
│       │   │   │   │   ├── [analysisId]
│       │   │   │   │   │   └── processing
│       │   │   │   │   │       └── page.tsx
│       │   │   │   │   ├── analyses.module.css
│       │   │   │   │   └── page.tsx
│       │   │   │   ├── audit
│       │   │   │   │   ├── audit.module.css
│       │   │   │   │   └── page.tsx
│       │   │   │   ├── dashboard
│       │   │   │   │   ├── dashboard.module.css
│       │   │   │   │   └── page.tsx
│       │   │   │   ├── data-quality
│       │   │   │   │   └── issues
│       │   │   │   │       ├── data-quality.module.css
│       │   │   │   │       ├── issues.module.css
│       │   │   │   │       └── page.tsx
│       │   │   │   ├── devices
│       │   │   │   │   ├── [deviceId]
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   └── page.tsx
│       │   │   │   ├── feedback
│       │   │   │   │   ├── analytics
│       │   │   │   │   │   ├── analytics.module.css
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   ├── [feedbackId]
│       │   │   │   │   │   ├── adjudication.module.css
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   ├── inbox
│       │   │   │   │   │   ├── feedback.module.css
│       │   │   │   │   │   ├── inbox.module.css
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   └── training-candidates
│       │   │   │   │       └── page.tsx
│       │   │   │   ├── imports
│       │   │   │   │   ├── [importId]
│       │   │   │   │   │   ├── import-detail.module.css
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   ├── imports.module.css
│       │   │   │   │   └── page.tsx
│       │   │   │   ├── protocols
│       │   │   │   │   ├── [protocolId]
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   └── page.tsx
│       │   │   │   ├── reports
│       │   │   │   │   └── [reportId]
│       │   │   │   │       └── page.tsx
│       │   │   │   ├── reviews
│       │   │   │   │   └── [caseId]
│       │   │   │   │       └── page.tsx
│       │   │   │   ├── sessions
│       │   │   │   │   ├── new
│       │   │   │   │   │   ├── new-session.module.css
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   ├── [sessionId]
│       │   │   │   │   │   ├── acquisition
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── analysis
│       │   │   │   │   │   │   ├── analysis.module.css
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── calibration
│       │   │   │   │   │   │   ├── calibration.module.css
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── context
│       │   │   │   │   │   │   ├── context.module.css
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── data-source
│       │   │   │   │   │   │   ├── data-source.module.css
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── import
│       │   │   │   │   │   │   ├── import.module.css
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── mapping
│       │   │   │   │   │   │   ├── mapping.module.css
│       │   │   │   │   │   │   └── page.tsx
│       │   │   │   │   │   ├── preflight
│       │   │   │   │   │   │   ├── page.tsx
│       │   │   │   │   │   │   └── preflight.module.css
│       │   │   │   │   │   ├── quality
│       │   │   │   │   │   │   ├── page.tsx
│       │   │   │   │   │   │   └── quality.module.css
│       │   │   │   │   │   ├── report
│       │   │   │   │   │   │   ├── page.tsx
│       │   │   │   │   │   │   └── report.module.css
│       │   │   │   │   │   └── review
│       │   │   │   │   │       ├── page.tsx
│       │   │   │   │   │       └── review.module.css
│       │   │   │   │   ├── page.tsx
│       │   │   │   │   └── sessions.module.css
│       │   │   │   ├── uc1
│       │   │   │   │   ├── calibration
│       │   │   │   │   │   └── [sessionId]
│       │   │   │   │   │       └── page.tsx
│       │   │   │   │   ├── demo
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   ├── intro
│       │   │   │   │   │   ├── page.tsx
│       │   │   │   │   │   └── uc1-intro.module.css
│       │   │   │   │   ├── review
│       │   │   │   │   │   └── [sessionId]
│       │   │   │   │   │       ├── page.tsx
│       │   │   │   │   │       └── uc1-review.module.css
│       │   │   │   │   └── session
│       │   │   │   │       └── [sessionId]
│       │   │   │   │           ├── page.tsx
│       │   │   │   │           └── uc1-session.module.css
│       │   │   │   ├── uc2
│       │   │   │   │   ├── assessment
│       │   │   │   │   │   └── [sessionId]
│       │   │   │   │   │       ├── page.tsx
│       │   │   │   │   │       └── uc2-assessment.module.css
│       │   │   │   │   ├── demo
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   ├── intro
│       │   │   │   │   │   ├── page.tsx
│       │   │   │   │   │   └── uc2-intro.module.css
│       │   │   │   │   └── longitudinal
│       │   │   │   │       └── [subjectRef]
│       │   │   │   │           ├── page.tsx
│       │   │   │   │           └── uc2-longitudinal.module.css
│       │   │   │   ├── uc3
│       │   │   │   │   ├── feasibility
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   └── intro
│       │   │   │   │       ├── page.tsx
│       │   │   │   │       └── uc3-intro.module.css
│       │   │   │   ├── uc4
│       │   │   │   │   ├── feasibility
│       │   │   │   │   │   └── page.tsx
│       │   │   │   │   └── intro
│       │   │   │   │       ├── page.tsx
│       │   │   │   │       └── uc4-intro.module.css
│       │   │   │   ├── use-cases
│       │   │   │   │   ├── page.tsx
│       │   │   │   │   └── use-cases.module.css
│       │   │   │   └── layout.tsx
│       │   │   ├── login
│       │   │   │   ├── login.module.css
│       │   │   │   └── page.tsx
│       │   │   ├── reports
│       │   │   │   └── Day24ReportPreviewPage.tsx
│       │   │   ├── reviews
│       │   │   │   └── Day24ReviewPage.tsx
│       │   │   ├── sessions
│       │   │   │   ├── analysis
│       │   │   │   │   └── SessionAnalysisHandoffPage.tsx
│       │   │   │   ├── calibration
│       │   │   │   │   └── SessionCalibrationPage.tsx
│       │   │   │   ├── context
│       │   │   │   │   └── SessionContextPage.tsx
│       │   │   │   ├── data-source
│       │   │   │   │   └── SessionDataSourcePage.tsx
│       │   │   │   ├── import
│       │   │   │   │   └── SessionImportPage.tsx
│       │   │   │   ├── mapping
│       │   │   │   │   └── SessionMappingPage.tsx
│       │   │   │   ├── new
│       │   │   │   │   └── SessionCreatePage.tsx
│       │   │   │   ├── preflight
│       │   │   │   │   └── SessionPreflightPage.tsx
│       │   │   │   ├── quality
│       │   │   │   │   └── SessionQualityPage.tsx
│       │   │   │   └── Day20SessionRoutes.tsx
│       │   │   ├── uc2
│       │   │   │   ├── assessment
│       │   │   │   │   └── Day23UC2AssessmentPage.tsx
│       │   │   │   └── longitudinal
│       │   │   │       └── Day23UC2LongitudinalPage.tsx
│       │   │   ├── AppRouter.tsx
│       │   │   ├── layout.tsx
│       │   │   └── page.tsx
│       │   ├── components
│       │   │   ├── analysis
│       │   │   │   └── AnalysisJobTimeline.tsx
│       │   │   ├── auth
│       │   │   │   └── RoleGuard.tsx
│       │   │   ├── calibration
│       │   │   │   └── CalibrationWizard.tsx
│       │   │   ├── charts
│       │   │   │   ├── FeatureTrendChart.tsx
│       │   │   │   ├── LongitudinalTrendChart.tsx
│       │   │   │   ├── QualityTimeline.tsx
│       │   │   │   └── SignalPreviewChart.tsx
│       │   │   ├── clinical
│       │   │   │   ├── AnalysisHandoffPanel.tsx
│       │   │   │   ├── ConfidenceIndicator.tsx
│       │   │   │   ├── DisclaimerPanel.tsx
│       │   │   │   ├── FatigueStatusBadge.tsx
│       │   │   │   ├── ProtocolSummaryCard.tsx
│       │   │   │   ├── ReviewChecklist.tsx
│       │   │   │   └── SignalQualityGatePanel.tsx
│       │   │   ├── data-intake
│       │   │   │   ├── ChannelMappingTable.tsx
│       │   │   │   ├── DataSourceSelector.tsx
│       │   │   │   ├── ImportStatePanel.tsx
│       │   │   │   └── PreflightSummaryPanel.tsx
│       │   │   ├── feedback
│       │   │   │   ├── AbstentionAlert.tsx
│       │   │   │   ├── QcFailureAlert.tsx
│       │   │   │   └── ValidationErrorSummary.tsx
│       │   │   ├── forms
│       │   │   │   ├── ElectrodeConfigForm.tsx
│       │   │   │   ├── PatientForm.tsx
│       │   │   │   ├── ProtocolSetupForm.tsx
│       │   │   │   ├── ReviewSignoffForm.tsx
│       │   │   │   ├── SessionForm.tsx
│       │   │   │   └── SignalUploadForm.tsx
│       │   │   ├── layout
│       │   │   │   ├── AppShell.module.css
│       │   │   │   ├── AppShell.tsx
│       │   │   │   ├── Breadcrumbs.tsx
│       │   │   │   └── RoleGuard.tsx
│       │   │   ├── review
│       │   │   │   ├── ClinicalSignoffPanel.tsx
│       │   │   │   ├── FeedbackAdjudicationPanel.tsx
│       │   │   │   ├── ReportPreviewPanel.tsx
│       │   │   │   ├── ReviewStatusBadge.tsx
│       │   │   │   ├── ReviewTimeline.tsx
│       │   │   │   └── TechnicalReviewPanel.tsx
│       │   │   ├── uc1
│       │   │   │   ├── GestureHistoryTable.tsx
│       │   │   │   ├── UC1SessionWorkspace.module.css
│       │   │   │   └── UC1SessionWorkspace.tsx
│       │   │   ├── uc2
│       │   │   │   ├── AccessibleMetricChart.tsx
│       │   │   │   ├── FatigueEndurancePanel.tsx
│       │   │   │   ├── QuantitativeKpiRow.tsx
│       │   │   │   ├── RepeatabilityPanel.tsx
│       │   │   │   ├── SessionCompatibilityTable.tsx
│       │   │   │   └── SymmetryPanel.tsx
│       │   │   └── ui
│       │   │       ├── Alert.module.css
│       │   │       ├── Alert.tsx
│       │   │       ├── Badge.module.css
│       │   │       ├── Badge.tsx
│       │   │       ├── Button.module.css
│       │   │       ├── Button.tsx
│       │   │       ├── Card.module.css
│       │   │       ├── Card.tsx
│       │   │       ├── Input.module.css
│       │   │       └── Input.tsx
│       │   ├── config
│       │   │   ├── featureFlags.ts
│       │   │   ├── routePermissions.ts
│       │   │   └── useCaseRoutes.ts
│       │   ├── hooks
│       │   │   ├── useAnalysisJob.ts
│       │   │   └── useUC1Replay.ts
│       │   ├── lib
│       │   │   ├── analysis-client.ts
│       │   │   ├── api-client.ts
│       │   │   ├── auth.tsx
│       │   │   ├── date-format.ts
│       │   │   ├── latencyMetrics.ts
│       │   │   ├── mock-api-client.ts
│       │   │   ├── permissions.ts
│       │   │   ├── pollingSchedule.ts
│       │   │   ├── review-report-client.ts
│       │   │   ├── session-intake-client.ts
│       │   │   ├── uc1-replay-client.ts
│       │   │   ├── uc2-assessment-client.ts
│       │   │   └── validators.ts
│       │   ├── mocks
│       │   │   ├── day20ScenarioRegistry.ts
│       │   │   ├── mockDatabase.ts
│       │   │   └── scenarioRegistry.ts
│       │   ├── schemas
│       │   │   ├── analysis-envelope.schema.ts
│       │   │   ├── analysis-handoff.schema.ts
│       │   │   ├── analysis-job.schema.ts
│       │   │   ├── analysis.ts
│       │   │   ├── calibration.schema.ts
│       │   │   ├── calibration.ts
│       │   │   ├── channel-mapping.schema.ts
│       │   │   ├── common.ts
│       │   │   ├── feedback.ts
│       │   │   ├── gesture-feedback-context.schema.ts
│       │   │   ├── gesture-inference.schema.ts
│       │   │   ├── gesture-inference.type-test.ts
│       │   │   ├── import.ts
│       │   │   ├── import-workflow.schema.ts
│       │   │   ├── inference.schema.ts
│       │   │   ├── issue.ts
│       │   │   ├── mapping.ts
│       │   │   ├── preflight.schema.ts
│       │   │   ├── preflight.ts
│       │   │   ├── qc.schema.ts
│       │   │   ├── quality-gate.schema.ts
│       │   │   ├── quality.ts
│       │   │   ├── rbac.ts
│       │   │   ├── report.schema.ts
│       │   │   ├── report.ts
│       │   │   ├── review-report.schema.ts
│       │   │   ├── review.ts
│       │   │   ├── role.schema.ts
│       │   │   ├── segment.ts
│       │   │   ├── session-intake.schema.ts
│       │   │   ├── session.schema.ts
│       │   │   ├── session.ts
│       │   │   ├── uc2-assessment.schema.ts
│       │   │   └── work-queue.schema.ts
│       │   ├── services
│       │   │   └── mock
│       │   │       ├── fixtures.ts
│       │   │       ├── MockAnalysisService.ts
│       │   │       ├── MockCalibrationService.ts
│       │   │       ├── MockImportService.ts
│       │   │       ├── MockSessionService.ts
│       │   │       ├── MockSignalWorkflowService.ts
│       │   │       └── MockWorkflowRepository.ts
│       │   ├── styles
│       │   │   ├── animations.css
│       │   │   ├── global.css
│       │   │   └── tokens.css
│       │   ├── utils
│       │   │   ├── replayView.ts
│       │   │   └── uc1ReplayValidation.ts
│       │   └── workflows
│       │       ├── calibrationWorkflowReducer.ts
│       │       └── importWorkflowReducer.ts
│       ├── .eslintrc.json
│       ├── next.config.js
│       ├── next-env.d.ts
│       ├── package.json
│       ├── playwright.config.ts
│       ├── README.md
│       ├── tsconfig.json
│       └── tsconfig.tsbuildinfo
├── business
│   ├── customer-discovery
│   │   ├── interview-notes
│   │   ├── insights-synthesis.md
│   │   ├── interview-script-doctor.md
│   │   ├── interview-script-ktv.md
│   │   └── interview-script-motion-lab.md
│   ├── fundraising
│   │   ├── data-room-index.md
│   │   ├── investor-faq.md
│   │   ├── investor-narrative.md
│   │   ├── pitch-deck-outline.md
│   │   ├── traction-metrics.md
│   │   └── use-of-funds.md
│   ├── gtm
│   │   ├── design-partner-plan.md
│   │   ├── pilot-proposal-template.md
│   │   ├── procurement-checklist.md
│   │   ├── reference-site-case-study-template.md
│   │   └── sales-deck-outline.md
│   ├── partnerships
│   │   ├── device-vendor-partnership-plan.md
│   │   ├── partnership-mou-template.md
│   │   ├── rehab-network-partnership-plan.md
│   │   └── university-lab-collaboration.md
│   ├── pricing
│   │   ├── oem-partnership-pricing.md
│   │   ├── paid-pilot-pricing.md
│   │   ├── per-assessment-pricing.md
│   │   └── per-site-license-pricing.md
│   ├── strategy
│   │   ├── beachhead-market-analysis.md
│   │   ├── competitive-landscape.md
│   │   ├── moat-strategy.md
│   │   ├── problem-solution-fit.md
│   │   └── risk-register-business.md
│   └── README.md
├── clinical
│   ├── governance
│   │   ├── claim-language-policy.v0.1.yaml
│   │   └── task-portfolio.v0.1.yaml
│   ├── labels
│   │   ├── annotation-guidelines.md
│   │   ├── annotation-guidelines-v0.2.md
│   │   ├── fatigue-context-taxonomy.v0.1.yaml
│   │   ├── force-drop-labeling.md
│   │   ├── gesture-label-taxonomy.v0.2.yaml
│   │   ├── label-quality-policy-v0.2.md
│   │   ├── label-taxonomy.yaml
│   │   ├── quantitative-metric-status-taxonomy.v0.1.yaml
│   │   └── rpe-scale.md
│   ├── learning
│   │   └── lower-limb-acl
│   │       ├── pre-day41-01-medical-keywords.v0.1.yaml          # [MVP-2][MUST] Day 41 Portfolio Management
│   │       ├── pre-day41-01-medical-learning-guide.md           # [MVP-2][MUST] Day 41 Portfolio Management
│   │       ├── pre-day41-01-medical-source-notes.md             # [MVP-2][MUST] Day 41 Portfolio Management
│   │       └── pre-day41-01-self-check.md                       # [MVP-2][MUST] Day 41 Portfolio Management
│   ├── muscle-catalog
│   │   ├── placement-guides
│   │   │   ├── biceps-femoris.md
│   │   │   ├── gastrocnemius-medialis.md
│   │   │   ├── rectus-femoris.md
│   │   │   └── vastus-lateralis.md
│   │   ├── electrode-config-schema.json
│   │   └── muscles.yaml
│   ├── protocols
│   │   ├── calf-isometric-60s.v0.1.yaml
│   │   ├── gesture-protocol.v0.1.schema.json
│   │   ├── hamstring-isometric-60s.v0.1.yaml
│   │   ├── protocol-schema.json
│   │   ├── quad-isometric-60s.v0.1.yaml
│   │   ├── repeated-contraction-template.v0.1.yaml
│   │   └── upper-limb-gesture-biofeedback.v0.1.yaml
│   ├── review-templates
│   │   ├── clinical-review-checklist.v0.1.yaml
│   │   ├── clinical-review-checklist.yaml
│   │   ├── escalation-reason-codes.v0.1.yaml
│   │   ├── escalation-reason-codes.yaml
│   │   ├── override-reason-codes.v0.1.yaml
│   │   ├── override-reason-codes.yaml
│   │   ├── technical-review-checklist.v0.1.yaml
│   │   └── technical-review-checklist.yaml
│   └── training
│       ├── doctor-review-guide.md
│       ├── ktv-training-deck.md
│       ├── quick-start-checklist.md
│       └── troubleshooting-guide.md
├── data-platform
│   ├── configs
│   │   ├── day30
│   │   │   ├── common-ontology.yaml
│   │   │   ├── dataset-profiles.yaml
│   │   │   └── dataset-view-registry.yaml
│   │   ├── pre_day30_remote_eda.research.yaml
│   │   └── pre_day30_storage.local.yaml
│   ├── contracts
│   │   ├── day30
│   │   │   ├── feature-table-columns.csv
│   │   │   ├── storage-contract.yaml
│   │   │   └── window-index-columns.csv
│   │   ├── day31
│   │   │   ├── feature-arm-dimensions.csv
│   │   │   ├── feature-row-columns.csv
│   │   │   ├── qc-flags.yaml
│   │   │   └── storage-contract.yaml
│   │   ├── day33
│   │   │   ├── failure-case-columns.csv
│   │   │   ├── repetition-prediction-columns.csv
│   │   │   └── window-prediction-columns.csv
│   │   └── day37                                                # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │       ├── cocontraction-envelope.schema.json
│   │       └── taskc-repetition-feature.schema.json
│   ├── datasets
│   │   ├── external
│   │   │   ├── grabmyo-v1.1.0
│   │   │   │   ├── day29-manifest-index.yaml
│   │   │   │   └── remote-objects.input.template.csv
│   │   │   └── mendeley-4channel-hand-gesture-v2
│   │   │       ├── day28-manifest-index.yaml
│   │   │       └── remote-objects.input.template.csv
│   │   └── external-artifacts
│   │       ├── grabmyo-physionet-v1.1.0
│   │       │   ├── primary4-forearm16
│   │       │   ├── grabmyo-etl-evidence.json
│   │       │   ├── grabmyo-etl-final-gate.json
│   │       │   ├── grabmyo-feature-column-manifest.json
│   │       │   ├── grabmyo-primary4-forearm16-fall14.npz
│   │       │   └── grabmyo-subject-split-manifest.json
│   │       └── mendeley-4channel-hand-gesture-v2
│   │           └── day31-primary
│   │               ├── day31-colab-etl-evidence.json
│   │               ├── day31-feature-column-manifest.json
│   │               ├── day31-final-gate.json
│   │               ├── day31-mendeley-primary-fall14.npz
│   │               └── subject-split-manifest.csv
│   ├── manifests
│   │   ├── public-datasets
│   │   │   ├── grabmyo-canonical
│   │   │   │   ├── canonical-mapping-draft.yaml
│   │   │   │   ├── data-hierarchy.yaml
│   │   │   │   ├── dataset-source-record.yaml
│   │   │   │   ├── domain-gap-matrix.csv
│   │   │   │   ├── field-dictionary.csv
│   │   │   │   ├── file-inventory.csv
│   │   │   │   ├── label-dictionary.yaml
│   │   │   │   ├── license-record.yaml
│   │   │   │   └── readiness-decision.yaml
│   │   │   └── mendeley-4channel-hand-gesture-v2
│   │   │       ├── archive.sha256
│   │   │       ├── canonical-mapping-draft.yaml
│   │   │       ├── data-hierarchy.yaml
│   │   │       ├── data-quality-inventory.json
│   │   │       ├── dataset-source-record.yaml
│   │   │       ├── domain-gap-matrix.csv
│   │   │       ├── field-dictionary.csv
│   │   │       ├── file-inventory.csv
│   │   │       ├── label-dictionary.yaml
│   │   │       ├── license-record.yaml
│   │   │       └── readiness-decision.yaml
│   │   ├── public-dataset-manifest.template.json
│   │   └── research-dataset-manifest.template.json
│   ├── migrations
│   │   ├── 0001_create_core_tables.sql
│   │   ├── 0002_add_rbac_tables.sql
│   │   ├── 0003_add_protocol_versioning.sql
│   │   ├── 0004_add_feature_tables.sql
│   │   └── 0005_add_longitudinal_indexes.sql
│   ├── object-storage
│   │   ├── lifecycle-policy.template.json
│   │   ├── minio-init.sh
│   │   ├── pre-day30.gitignore.snippet
│   │   ├── pre-day30-storage-layout.md
│   │   └── storage-layout.md
│   ├── privacy
│   │   ├── date_shift.py
│   │   ├── deidentify_export.py
│   │   └── hash_identifiers.py
│   ├── raw
│   │   └── Vinmec
│   │       ├── Motion Lab Example Output csv files
│   │       │   ├── Noraxon MR4 csv exports
│   │       │   │   ├── Running on instrumented treadmill with EMG
│   │       │   │   │   ├── MR4_treadmill_running_pressure_and_EMG_separated_csv_file
│   │       │   │   │   │   ├── info.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── Ultium_EMG-LT_BICEPS_FEM..csv
│   │       │   │   │   │   ├── Ultium_EMG-LT_MED._GASTRO.csv
│   │       │   │   │   │   ├── Ultium_EMG-LT_RECTUS_FEM..csv
│   │       │   │   │   │   ├── Ultium_EMG-LT_SEMITEND..csv
│   │       │   │   │   │   ├── Ultium_EMG-LT_SOLEUS.csv
│   │       │   │   │   │   ├── Ultium_EMG-LT_TIB.ANT..csv
│   │       │   │   │   │   ├── Ultium_EMG-RT_BICEPS_FEM..csv
│   │       │   │   │   │   ├── Ultium_EMG-RT_MED._GASTRO.csv
│   │       │   │   │   │   ├── Ultium_EMG-RT_RECTUS_FEM..csv
│   │       │   │   │   │   ├── Ultium_EMG-RT_SEMITEND..csv
│   │       │   │   │   │   ├── Ultium_EMG-RT_SOLEUS.csv
│   │       │   │   │   │   └── Ultium_EMG-RT_TIB.ANT..csv
│   │       │   │   │   └── MR4_treadmill_running_pressure_and_EMG_single_csv_file.csv
│   │       │   │   ├── Walking on pressure plateform
│   │       │   │   │   ├── MR4_free_gait_pressure_platform_separated_csv_files
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 10_backward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 11_forward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 12_backward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 1_forward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 2_backward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 3_forward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 4_backward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 5_forward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 6_backward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 7_forward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 8_backward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_LT-LT_COP.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_LT-LT_Force.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_COP.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_LT-LT_Local_Pressure.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_LT-LT_Max_Pressure.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_RT-RT_COP.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_RT-RT_Force.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_COP.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Max_Load.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_RT-RT_Local_Pressure.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Contacts-Foot_RT-RT_Max_Pressure.csv
│   │       │   │   │   │   ├── 9_forward_Pressure_Platform-Pressure,_Gait_Mode.csv
│   │       │   │   │   │   └── info.csv
│   │       │   │   │   ├── free gait report.pdf
│   │       │   │   │   └── MR4_free_gait_pressure_platform_single_csv_files.csv
│   │       │   │   └── Mẫu kết quả phân tích vận động chuyên sâu.doc
│   │       │   ├── Vicon Nexus csv exports
│   │       │   │   ├── Nexus walking trial.csv
│   │       │   │   └── Nexus walking trial with EMG.csv
│   │       │   └── Chú thích.docx
│   │       └── Motion_Lab_CSV_Architecture.md
│   ├── schemas
│   │   ├── audit_log.sql
│   │   ├── feature_table.sql
│   │   ├── longitudinal_view.sql
│   │   └── research_export_view.sql
│   ├── seeds
│   │   ├── devices.seed.sql
│   │   ├── protocols.seed.sql
│   │   ├── roles.seed.sql
│   │   └── synthetic_patients.seed.sql
│   ├── synthetic-data
│   │   ├── generate_synthetic_semg.py
│   │   ├── golden_signal_01.csv
│   │   ├── golden_signal_01.expected_ingestion_summary.json
│   │   ├── golden_signal_01.generation.json
│   │   ├── golden_signal_01.manifest.json
│   │   ├── qc_fail_clipping.csv
│   │   ├── qc_fail_dropout.csv
│   │   ├── qc_fail_noise.csv
│   │   └── README.md
│   └── README.md
├── docs
│   ├── 00-executive
│   │   ├── pre-day41                                            # [MVP-2][MUST] Day 41 Portfolio Management
│   │   │   └── decision-log.md
│   │   ├── 00_Implementation_Plan_Realtime_Final.md
│   │   ├── 01_semg_mfcv_project_strategy_roadmap.md
│   │   ├── 01_semg_mfcv_project_strategy_roadmap_quan_duy.md
│   │   ├── assumptions-and-open-questions.md
│   │   ├── day10-decision-log-append.md
│   │   ├── day11-decision-log-append.md
│   │   ├── day12-decision-log-append.md
│   │   ├── day13-decision-log-append.md
│   │   ├── day14-decision-log-append.md
│   │   ├── day15-decision-log-append.md
│   │   ├── day16-decision-log-append.md
│   │   ├── day17-decision-log-append.md
│   │   ├── day3-decision-log-append.md
│   │   ├── day4-decision-log-append.md
│   │   ├── day5-decision-log-append.md
│   │   ├── day6-decision-log-append.md
│   │   ├── day7-decision-log-append.md
│   │   ├── day8-decision-log-append.md
│   │   ├── day9-decision-log-append.md
│   │   ├── executive-blueprint.md
│   │   ├── glossary.md
│   │   └── stakeholder-decision-log.md
│   ├── 01-product
│   │   ├── backlog
│   │   │   ├── acceptance-criteria.md
│   │   │   ├── day10-backlog.md
│   │   │   ├── day11-backlog.md
│   │   │   ├── day12-backlog.md
│   │   │   ├── day13-backlog.md
│   │   │   ├── day14-backlog.md
│   │   │   ├── day15-backlog.md
│   │   │   ├── day1-backlog.md
│   │   │   ├── day2-backlog.md
│   │   │   ├── day3-backlog.md
│   │   │   ├── day4-backlog.md
│   │   │   ├── day5-backlog.md
│   │   │   ├── day6-backlog.md
│   │   │   ├── day7-backlog.md
│   │   │   ├── day8-backlog.md
│   │   │   ├── day9-backlog.md
│   │   │   ├── epics.md
│   │   │   ├── prioritization-matrix.md
│   │   │   └── user-stories.csv
│   │   ├── icp-and-personas.md
│   │   ├── intended-use-statement.md
│   │   ├── jobs-to-be-done.md
│   │   ├── mvp-definition-of-done.md
│   │   ├── product-boundaries.md
│   │   ├── product-vision.md
│   │   ├── release-scope-mvp0.md
│   │   ├── release-scope-mvp1.md
│   │   ├── release-scope-mvp2.md
│   │   └── user-journey.md
│   ├── 02-clinical
│   │   ├── clinical-advisory-notes
│   │   │   └── yyyy-mm-dd-advisor-meeting.md
│   │   ├── pre-day41                                            # [MVP-2][MUST] Day 41 Portfolio Management
│   │   │   ├── parallel-intended-use.v0.1.md
│   │   │   ├── population-protocol-matrix.csv
│   │   │   ├── task-definitions.v0.1.md
│   │   │   └── unresolved-clinical-questions.md
│   │   ├── assessment-order-template.md
│   │   ├── clinical-validation-plan.md
│   │   ├── clinical-workflow.md
│   │   ├── day24-human-review-and-signoff-policy.md
│   │   ├── electrode-placement-guide.md
│   │   ├── human-review-policy.md
│   │   ├── patient-preparation-checklist.md
│   │   ├── pilot-site-training-manual.md
│   │   ├── protocol-library.md
│   │   ├── quality-escalation-policy.md
│   │   ├── report-interpretation-guide.md
│   │   └── target-muscle-catalog.md
│   ├── 03-architecture
│   │   ├── adr
│   │   │   ├── ADR-0001-clinical-intelligence-not-device.md
│   │   │   ├── ADR-0001-monorepo.md
│   │   │   ├── ADR-0002-offline-first-before-realtime.md
│   │   │   ├── ADR-0002-onprem-raw-signal-storage.md
│   │   │   ├── ADR-0003-rule-based-before-deep-learning.md
│   │   │   ├── ADR-0004-version-everything.md
│   │   │   ├── ADR-0005-abstention-as-first-class-output.md
│   │   │   ├── ADR-0008-freeze-preprocess-v0.1-after-analytical-verification.md
│   │   │   ├── ADR-0009-fixed-half-open-window-plan-v0.1.md
│   │   │   ├── ADR-0009-isolate-unknown-vendor-output-behind-adapters.md
│   │   │   ├── ADR-0010-time-domain-features-before-spectral-and-inference.md
│   │   │   ├── ADR-0011-hann-welch-spectral-foundation-before-mdf-mnf.md
│   │   │   ├── ADR-0012-canonical-mdf-mnf-definitions.md
│   │   │   ├── ADR-0013-descriptive-trends-without-inferential-statistics.md
│   │   │   ├── ADR-0014-evidence-before-rule-and-score.md
│   │   │   ├── ADR-0015-rule-engine-before-confidence-and-score.md
│   │   │   ├── ADR-0016-engineering-confidence-not-clinical-probability.md
│   │   │   └── ADR-0017-atomic-versioned-offline-analysis-package.md
│   │   ├── data-flow-diagram.md
│   │   ├── day19-route-and-shell-map.md
│   │   ├── day20-session-intake-sequence.md
│   │   ├── day21-analysis-runtime-integration.md
│   │   ├── deployment-architecture-onprem.md
│   │   ├── frontend-mock-integration-architecture.md
│   │   ├── high-level-architecture.md
│   │   ├── module-dependency-map.md
│   │   ├── offline-analysis-orchestration.md
│   │   ├── sequence-upload-to-report.md
│   │   ├── system-context.md
│   │   └── threat-model-architecture.md
│   ├── 04-api
│   │   ├── examples
│   │   │   ├── analysis-abstained.response.json
│   │   │   ├── analysis-completed.response.json
│   │   │   ├── analysis-job.response.json
│   │   │   ├── create-session.request.json
│   │   │   ├── inference-abstain.response.json
│   │   │   ├── problem-details.response.json
│   │   │   ├── qc-fail.response.json
│   │   │   ├── report-final.response.json
│   │   │   ├── session-import.response.json
│   │   │   └── upload-signal.response.json
│   │   ├── admin-config-api.md
│   │   ├── api-error-taxonomy.md
│   │   ├── api-overview.md
│   │   ├── audit-log-api.md
│   │   ├── auth-api.md
│   │   ├── day21-analysis-job-api.md
│   │   ├── day22-uc1-replay-api.md
│   │   ├── day24-review-report-api.md
│   │   ├── feature-extraction-api.md
│   │   ├── human-review-api.md
│   │   ├── inference-api.md
│   │   ├── offline-analysis-api-contract.md
│   │   ├── openapi-day19-ui-mock.fragment.yaml
│   │   ├── openapi-day20-session-intake.fragment.yaml
│   │   ├── openapi-day22-uc1-replay.fragment.yaml
│   │   ├── openapi-v0.1.yaml
│   │   ├── patient-session-api.md
│   │   ├── quality-check-api.md
│   │   ├── report-api.md
│   │   └── signal-upload-api.md
│   ├── 05-data
│   │   ├── day25-research
│   │   │   ├── canonical-research-dataset-contract.md
│   │   │   ├── data-readiness-gate-policy.md
│   │   │   ├── dataset-inventory-v0.2.csv
│   │   │   ├── dataset-license-access-register-v0.2.csv
│   │   │   ├── day25-decision-record.md
│   │   │   ├── domain-gap-register-v0.2.csv
│   │   │   ├── five-data-layer-separation.md
│   │   │   ├── free-first-research-stack.md
│   │   │   ├── noraxon-output-uncertainty-resolution-addendum.md
│   │   │   ├── pre-day25-gate.json
│   │   │   ├── pre-day25-research-synthesis.md
│   │   │   ├── repository-reuse-shortlist.md
│   │   │   ├── research-conflict-register.csv
│   │   │   ├── restricted-reference-register.md
│   │   │   ├── source-evidence-register.csv
│   │   │   ├── task-a-gesture-data-spec.md
│   │   │   ├── task-b-fatigue-context-data-spec.md
│   │   │   └── task-c-quantitative-metrics-data-spec.md
│   │   ├── day28
│   │   │   ├── 00-day28-scope-and-gates.md
│   │   │   ├── 01-day27-artifact-reconciliation.md
│   │   │   ├── 02-eda-policy.md
│   │   │   ├── 03-label-and-hierarchy-audit.md
│   │   │   ├── 04-signal-quality-audit.md
│   │   │   ├── 05-experiment-eligibility.md
│   │   │   └── 06-day29-handoff.md
│   │   ├── day29
│   │   │   ├── 00-day29-scope-and-gates.md
│   │   │   ├── 01-input-contract.md
│   │   │   ├── 02-hierarchy-and-partition-audit.md
│   │   │   ├── 03-signal-quality-audit.md
│   │   │   ├── 04-cross-day-drift-policy.md
│   │   │   ├── 05-feature-eligibility.md
│   │   │   ├── 06-experiment-eligibility.md
│   │   │   └── 07-readiness-and-handoff.md
│   │   ├── day30
│   │   │   ├── 00-pre-day30-input-report.md
│   │   │   ├── 01-harmonization-principles.md
│   │   │   ├── 02-normalization-and-dc-policy.md
│   │   │   ├── 03-sampling-rate-and-resampling-policy.md
│   │   │   ├── 04-channel-strategy-and-ch4-quarantine.md
│   │   │   ├── 05-label-ontology-and-dataset-views.md
│   │   │   ├── 06-windowing-and-segmentation-policy.md
│   │   │   ├── 07-output-storage-contract.md
│   │   │   ├── 08-experiment-eligibility-and-day31-handoff.md
│   │   │   ├── 09-full-coverage-gap-and-risk-register.md
│   │   │   ├── 10-day30-readiness-decision.md
│   │   │   └── day30-source-traceability.csv
│   │   ├── public-datasets
│   │   │   └── mendeley-4channel-hand-gesture-v2
│   │   │       ├── 00-day27-scope-and-gates.md
│   │   │       ├── 01-dataset-selection-decision.md
│   │   │       ├── 02-canonical-source-verification-sop.md
│   │   │       ├── 03-controlled-acquisition-and-hashing.md
│   │   │       ├── 04-archive-inventory-and-safe-extraction.md
│   │   │       ├── 05-adapter-and-mapping-profile.md
│   │   │       ├── 06-label-ontology-mapping.md
│   │   │       ├── 07-group-split-and-test-seal.md
│   │   │       ├── 08-engineering-data-gate.md
│   │   │       ├── 09-domain-gap-and-transfer-boundary.md
│   │   │       ├── 10-day28-handoff.md
│   │   │       ├── 11-external-dependencies.md
│   │   │       ├── dataset-experiment-eligibility-matrix.csv
│   │   │       ├── dataset-selection-scorecard.csv
│   │   │       ├── day27-final-manifest.json
│   │   │       └── day27-source-traceability.csv
│   │   ├── sample-manifests
│   │   │   ├── dataset-card-template.md
│   │   │   ├── pilot-data-manifest.template.json
│   │   │   └── synthetic-session-manifest.json
│   │   ├── canonical-gesture-dataset-contract.md
│   │   ├── data-dictionary.csv
│   │   ├── data-model.md
│   │   ├── data-readiness-checklist.md
│   │   ├── day20-session-intake-contract.md
│   │   ├── day21-analysis-job-contract.md
│   │   ├── day22-gesture-inference-contract.md
│   │   ├── day24-review-report-contract.md
│   │   ├── day25-gesture-dataset-research-plan.md
│   │   ├── de-identification-spec.md
│   │   ├── domain-gap-register.md
│   │   ├── erd.puml
│   │   ├── explainable-inference-result-contract.md
│   │   ├── fatigue-evidence-result-contract.md
│   │   ├── fatigue-rule-result-contract.md
│   │   ├── feature-table-spec.md
│   │   ├── frequency-domain-feature-result-contract.md
│   │   ├── KIEN_TRUC_HAI_VUNG_LUU_TRU.md
│   │   ├── label-annotation-spec.md
│   │   ├── normalized-signal-object.md
│   │   ├── offline-analysis-manifest-contract.md
│   │   ├── PRE_DAY30_HUONG_DAN_EDA_DU_LIEU_LON_REMOTE_FIRST.md
│   │   ├── PRE_DAY30_REASON_CODES.md
│   │   ├── preprocessing-result-contract.md
│   │   ├── public-dataset-inventory.csv
│   │   ├── qc-result-contract.md
│   │   ├── raw-signal-storage-policy.md
│   │   ├── retention-and-backup-policy.md
│   │   ├── session-analysis-summary-contract.md
│   │   ├── spectral-estimation-result-contract.md
│   │   ├── time-domain-feature-result-contract.md
│   │   ├── trend-feature-result-contract.md
│   │   └── windowing-result-contract.md
│   ├── 06-ai-signal-processing
│   │   ├── day31
│   │   │   ├── 01-feature-mathematical-contract.md
│   │   │   ├── 09-day31-readiness-and-day32-handoff.md
│   │   │   ├── 10-risk-register.md
│   │   │   └── README.md
│   │   ├── day32
│   │   │   ├── 01-model-scope.md
│   │   │   ├── 02-authorization-and-input-gate.md
│   │   │   ├── 03-matrix-materialization.md
│   │   │   ├── 04-grouped-validation.md
│   │   │   ├── 05-core-model-contract.md
│   │   │   ├── 06-optional-model-gates.md
│   │   │   ├── 07-metrics-and-aggregation.md
│   │   │   ├── 08-reporting-and-limitations.md
│   │   │   └── 09-day33-handoff.md
│   │   ├── references
│   │   │   └── matlab_scripts
│   │   │       ├── Feature_Extraction.m
│   │   │       ├── Feature_Selection.m
│   │   │       ├── Import.m
│   │   │       ├── KNNClassification.m
│   │   │       ├── LDAClassification.m
│   │   │       ├── README.md
│   │   │       ├── RFClassification.m
│   │   │       └── SVMClassification.m
│   │   ├── ai-core-overview.md
│   │   ├── classical-ml-baseline-spec.md
│   │   ├── confidence-and-abstention-spec.md
│   │   ├── data-ingestion-adapter-spec.md
│   │   ├── day22-activity-gate-and-gesture-replay-spec.md
│   │   ├── day26-feature-and-model-blueprint.md
│   │   ├── evidence-combination-math-primer.md
│   │   ├── explainability-spec.md
│   │   ├── explainable-rule-engine-math-primer.md
│   │   ├── explainable-rule-engine-spec.md
│   │   ├── fatigue-context-architecture.md
│   │   ├── fatigue-evidence-engine-spec.md
│   │   ├── fatigue-rule-engine-spec.md
│   │   ├── feature-extraction-spec.md
│   │   ├── filter-response-math-primer.md
│   │   ├── frequency-domain-feature-spec.md
│   │   ├── frequency-domain-math-primer.md
│   │   ├── golden-signal-test-plan.md
│   │   ├── mdf-mnf-math-primer.md
│   │   ├── mfcv-cv-calculation-spec.md
│   │   ├── mvp0-regression-and-validation-spec.md
│   │   ├── personalization-strategy.md
│   │   ├── preprocessing-spec.md
│   │   ├── preprocessing-verification-spec.md
│   │   ├── segmentation-windowing-spec.md
│   │   ├── signal-import-spec.md
│   │   ├── signal-quality-gate-spec.md
│   │   ├── signal-validation-spec.md
│   │   ├── spectral-estimation-spec.md
│   │   ├── technical-confidence-math-primer.md
│   │   ├── technical-confidence-spec.md
│   │   ├── time-domain-feature-math-primer.md
│   │   ├── trend-feature-math-primer.md
│   │   ├── trend-feature-spec.md
│   │   ├── versioning-policy.md
│   │   └── windowing-math-primer.md
│   ├── 07-evaluation
│   │   └── day33
│   │       ├── 01-day32-evidence-assessment.md
│   │       ├── 02-prediction-contract.md
│   │       ├── 03-repetition-aggregation.md
│   │       ├── 04-subject-level-metrics.md
│   │       ├── 05-bootstrap-protocol.md
│   │       ├── 06-failure-taxonomy.md
│   │       ├── 07-cross-day-analysis.md
│   │       ├── 08-model-comparison.md
│   │       ├── 09-report-template.md
│   │       ├── 10-day34-handoff.md
│   │       └── 11-day33-results-summary.md
│   ├── 07-security-compliance
│   │   ├── audit-trail-policy.md
│   │   ├── backup-restore-plan.md
│   │   ├── consent-management.md
│   │   ├── data-classification.md
│   │   ├── encryption-policy.md
│   │   ├── incident-response-plan.md
│   │   ├── medical-disclaimer.md
│   │   ├── rbac-matrix.md
│   │   ├── regulatory-risk-assessment.md
│   │   ├── risk-management-file.md
│   │   ├── security-overview.md
│   │   ├── supplier-and-third-party-risk.md
│   │   └── usability-engineering-notes.md
│   ├── 08-validation-qa
│   │   ├── clinical-usability-test-plan.md
│   │   ├── day10-mdf-mnf-test-plan.md
│   │   ├── day11-trend-feature-test-plan.md
│   │   ├── day12-fatigue-evidence-test-plan.md
│   │   ├── day13-rule-engine-test-plan.md
│   │   ├── day14-confidence-explainability-test-plan.md
│   │   ├── day15-offline-pipeline-test-plan.md
│   │   ├── day16-golden-regression-test-plan.md
│   │   ├── day17-api-contract-test-plan.md
│   │   ├── day19-frontend-foundation-test-plan.md
│   │   ├── day20-intake-quality-test-plan.md
│   │   ├── day21-analysis-runtime-test-plan.md
│   │   ├── day22-uc1-vertical-slice-test-plan.md
│   │   ├── day24-review-report-test-plan.md
│   │   ├── day25-data-readiness-test-plan.md
│   │   ├── day3-ingestion-test-plan.md
│   │   ├── day4-qc-test-plan.md
│   │   ├── day5-preprocessing-test-plan.md
│   │   ├── day6-preprocessing-verification-test-plan.md
│   │   ├── day7-windowing-test-plan.md
│   │   ├── day8-time-domain-feature-test-plan.md
│   │   ├── day9-spectral-estimation-test-plan.md
│   │   ├── gesture-model-evaluation-plan.md
│   │   ├── known-limitations.md
│   │   ├── leakage-prevention-plan.md
│   │   ├── model-evaluation-plan.md
│   │   ├── release-checklist.md
│   │   ├── signal-processing-test-plan.md
│   │   ├── software-test-plan.md
│   │   ├── test-cases.csv
│   │   ├── test-set-governance.md
│   │   ├── traceability-matrix.csv
│   │   └── validation-master-plan.md
│   ├── 09-mlops-devops
│   │   ├── ci-cd-strategy.md
│   │   ├── data-versioning-spec.md
│   │   ├── dev-staging-prod-strategy.md
│   │   ├── drift-detection-plan.md
│   │   ├── dsp-reproducibility-policy.md
│   │   ├── experiment-tracking-spec.md
│   │   ├── model-registry-spec.md
│   │   ├── monitoring-observability-spec.md
│   │   ├── reproducible-training-policy.md
│   │   └── rollback-plan.md
│   ├── 10-business-fundraising
│   │   ├── beachhead-market.md
│   │   ├── differentiation.md
│   │   ├── fundraising-data-room-checklist.md
│   │   ├── go-to-market-plan.md
│   │   ├── investor-narrative.md
│   │   ├── market-segmentation.md
│   │   ├── metrics-dashboard-spec.md
│   │   ├── partnership-strategy.md
│   │   ├── pricing-hypotheses.md
│   │   ├── problem-statement.md
│   │   └── value-proposition.md
│   ├── 11-operations
│   │   ├── meeting-notes
│   │   │   └── yyyy-mm-dd-weekly-sync.md
│   │   ├── customer-support-playbook.md
│   │   ├── day19-existing-ui-integration-guide.md
│   │   ├── day21-existing-code-integration-guide.md
│   │   ├── day22-existing-code-integration-guide.md
│   │   ├── day24-existing-code-integration-guide.md
│   │   ├── day25-existing-code-integration-guide.md
│   │   ├── day26-existing-code-integration-guide.md
│   │   ├── day26-rollback-and-handoff.md
│   │   ├── external-dependency-register.md
│   │   ├── implementation-checklist.md
│   │   ├── pilot-operations-plan.md
│   │   ├── raci-matrix.md
│   │   ├── team-operating-model.md
│   │   └── weekly-status-template.md
│   ├── architecture
│   │   ├── CODEBASE_ARCHITECTURE_AUDIT.md
│   │   └── DATA_PIPELINE_FLOW.md
│   ├── learning
│   │   ├── day28
│   │   │   ├── 01-thong-ke-mo-ta-cho-semG.md
│   │   │   ├── 02-pho-tan-so-va-psd.md
│   │   │   └── 03-leakage-trong-eda.md
│   │   └── TOAN_DSP_VA_HE_THONG_CAN_HOC.md
│   ├── note
│   │   ├── day01
│   │   │   └── reading-notes.md
│   │   ├── day02
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day03.md
│   │   ├── day03
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day04.md
│   │   ├── day04
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day05.md
│   │   ├── day05
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day06.md
│   │   ├── day06
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day07.md
│   │   ├── day07
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day08.md
│   │   ├── day08
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day09.md
│   │   ├── day09
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day10.md
│   │   ├── day10
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day11.md
│   │   ├── day11
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day12.md
│   │   ├── day12
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day13.md
│   │   ├── day13
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day14.md
│   │   ├── day14
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day15.md
│   │   ├── day15
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day16.md
│   │   ├── day16
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day17.md
│   │   ├── day17
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day18.md
│   │   ├── day19
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day20.md
│   │   ├── day20
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day21.md
│   │   ├── day21
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day22.md
│   │   ├── day22
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day23.md
│   │   ├── day24
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day25.md
│   │   ├── day25
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-data-engineering-notes.md
│   │   │   ├── 05-clinical-notes.md
│   │   │   ├── 06-questions.md
│   │   │   ├── 07-decisions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day26.md
│   │   ├── day26
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-model-notes.md
│   │   │   ├── 05-validation-notes.md
│   │   │   ├── 06-governance-notes.md
│   │   │   ├── 07-questions.md
│   │   │   ├── 08-decisions.md
│   │   │   ├── 09-daily-summary.md
│   │   │   └── 10-todo-day27.md
│   │   ├── day27
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-and-dsp-notes.md
│   │   │   ├── 04-data-provenance-notes.md
│   │   │   ├── 05-label-mapping-notes.md
│   │   │   ├── 06-leakage-notes.md
│   │   │   ├── 07-code-reading-guide.md
│   │   │   ├── 08-decisions.md
│   │   │   ├── 09-questions.md
│   │   │   ├── 10-daily-summary.md
│   │   │   └── 11-todo-day28.md
│   │   ├── day29
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-reading-notes.md
│   │   │   ├── 03-math-notes.md
│   │   │   ├── 04-signal-processing-notes.md
│   │   │   ├── 05-leakage-notes.md
│   │   │   ├── 06-decisions.md
│   │   │   ├── 07-questions.md
│   │   │   ├── 08-daily-summary.md
│   │   │   └── 09-todo-day30.md
│   │   ├── day30
│   │   │   ├── 01-learning-objectives.md
│   │   │   ├── 02-math-normalization.md
│   │   │   ├── 03-math-resampling.md
│   │   │   ├── 04-channel-and-ontology.md
│   │   │   ├── 05-leakage-notes.md
│   │   │   ├── 06-decisions.md
│   │   │   ├── 07-open-questions.md
│   │   │   ├── 08-daily-summary-template.md
│   │   │   └── 09-todo-day31.md
│   │   ├── day32
│   │   │   ├── 01-learning-roadmap.md
│   │   │   ├── 02-lda-and-qda.md
│   │   │   ├── 03-logistic-and-svm.md
│   │   │   ├── 04-tree-models.md
│   │   │   ├── 05-knn-dimensionality.md
│   │   │   ├── 06-grouped-cv.md
│   │   │   ├── 07-metrics.md
│   │   │   ├── 08-daily-summary-template.md
│   │   │   └── 09-open-questions.md
│   │   ├── day33
│   │   │   ├── 01-learning-roadmap.md
│   │   │   ├── 02-confusion-matrix.md
│   │   │   ├── 03-macro-f1.md
│   │   │   ├── 04-hierarchical-data.md
│   │   │   ├── 05-cluster-bootstrap.md
│   │   │   ├── 06-confidence-calibration.md
│   │   │   ├── 07-error-analysis.md
│   │   │   ├── 08-daily-summary-template.md
│   │   │   └── 09-open-questions.md
│   │   └── pre-day41-01                                         # [MVP-2][MUST] Day 41 Portfolio Management
│   │       └── learning-roadmap.md
│   ├── plans
│   │   ├── version01
│   │   │   ├── DAY10_EXECUTION_PLAN.md
│   │   │   ├── DAY11_EXECUTION_PLAN.md
│   │   │   ├── DAY12_EXECUTION_PLAN.md
│   │   │   ├── DAY13_EXECUTION_PLAN.md
│   │   │   ├── DAY14_EXECUTION_PLAN.md
│   │   │   ├── DAY15_EXECUTION_PLAN.md
│   │   │   ├── DAY16_EXECUTION_PLAN.md
│   │   │   ├── DAY17_EXECUTION_PLAN.md
│   │   │   ├── DAY18_EXECUTION_PLAN.md
│   │   │   ├── DAY19_EXECUTION_PLAN.md
│   │   │   ├── DAY20_EXECUTION_PLAN.md
│   │   │   ├── DAY21_EXECUTION_PLAN.md
│   │   │   ├── DAY22_EXECUTION_PLAN.md
│   │   │   ├── DAY23_EXECUTION_PLAN.md
│   │   │   ├── DAY24_EXECUTION_PLAN.md
│   │   │   ├── DAY25_EXECUTION_PLAN.md
│   │   │   ├── DAY25_EXTENDED.md
│   │   │   ├── DAY26_EXECUTION_PLAN.md
│   │   │   ├── DAY28_EXECUTION_PLAN.md
│   │   │   ├── DAY29_EXECUTION_PLAN.md
│   │   │   ├── DAY2_EXECUTION_PLAN.md
│   │   │   ├── DAY30_EXECUTION_PLAN.md
│   │   │   ├── DAY31_EXECUTION_PLAN.md
│   │   │   ├── DAY32_EXECUTION_PLAN.md
│   │   │   ├── DAY33_EXECUTION_PLAN.md
│   │   │   ├── DAY34_EXECUTION_PLAN.md
│   │   │   ├── DAY35_EXECUTION_PLAN.md
│   │   │   ├── DAY36_EXECUTION_PLAN.md
│   │   │   ├── DAY37_EXECUTION_PLAN.md                          # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   │   ├── DAY38_EXECUTION_PLAN.md                          # [MVP-2][MUST] Day 38 Cross-Dataset Transfer
│   │   │   ├── DAY39_EXECUTION_PLAN.md                          # [MVP-2][MUST] Day 39 Reproducibility & Governance
│   │   │   ├── DAY3_EXECUTION_PLAN.md
│   │   │   ├── DAY40_EXECUTION_PLAN.md
│   │   │   ├── DAY4_EXECUTION_PLAN.md
│   │   │   ├── DAY5_EXECUTION_PLAN.md
│   │   │   ├── DAY6_EXECUTION_PLAN.md
│   │   │   ├── DAY7_EXECUTION_PLAN.md
│   │   │   ├── DAY8_EXECUTION_PLAN.md
│   │   │   ├── DAY9_EXECUTION_PLAN.md
│   │   │   ├── Execution_Plans_Summary.md
│   │   │   ├── PRE_DAY30_EXECUTION_PLAN.md
│   │   │   ├── PRE_DAY41_01_EXECUTION_PLAN.md                   # [MVP-2][MUST] Day 41 Portfolio Management
│   │   │   ├── PROMPT_KIEM_THU_UI_FRONTEND_MyoLab_AI_CONTINUOUS_AUDIT_v1.0.md
│   │   │   └── PROMPT_UI_UX_MyoLab_AI_Hoan_Chinh_v2.0.md
│   │   └── version02
│   │       └── MotionLab_Data_Intelligence_90_Day_Rebaselined_Execution_Roadmap_v1.0.md
│   ├── repo_skeleton
│   │   ├── mammolab_ai_project_skeleton.md
│   │   ├── semg_mfcv_ai_project_skeleton_docs.md
│   │   └── semg_mfcv_ai_project_skeleton.md
│   └── research
│       ├── day26
│       │   ├── day26_deep_research
│       │   │   ├── 08-metrics-calibration-abstention.md
│       │   │   ├── 09-reproducibility-and-governance.md
│       │   │   ├── Classical Model Candidate Review cho Day 26 sEMG Clinical Intelligence.md
│       │   │   ├── Day 26 Personalization và Adaptation Strategy cho sEMG Clinical Intelligence.md
│       │   │   ├── Day 26 Research Protocol và Governance Framework cho sEMG Clinical Intelligence.md
│       │   │   ├── Day 26 sEMG Clinical Intelligence Feature Engineering Review.md
│       │   │   ├── Day 26 sEMG Clinical Intelligence về fatigue-induced distribution shift và experiment blueprint.md
│       │   │   ├── Day 26 Validation and Leakage Review for sEMG Clinical Intelligence.md
│       │   │   ├── evaluation_regimes.research.yaml
│       │   │   ├── experiment-tracking-spec.md
│       │   │   ├── gesture-model-evaluation-plan.md
│       │   │   ├── model-registry-spec.md
│       │   │   └── reproducible-training-policy.md
│       │   ├── governance
│       │   │   ├── evidence
│       │   │   │   ├── 09-decision-ledger.yaml
│       │   │   │   ├── 09-evidence-matrix.csv
│       │   │   │   └── 09-search-screening-log.csv
│       │   │   ├── examples
│       │   │   │   ├── experiment-manifest.example.yaml
│       │   │   │   ├── model-registry-record.example.yaml
│       │   │   │   ├── release-manifest.example.yaml
│       │   │   │   └── rollback-record.example.yaml
│       │   │   ├── fixtures
│       │   │   │   ├── abstention-policy.blueprint.yaml
│       │   │   │   ├── calibration-config.blueprint.yaml
│       │   │   │   ├── channel-mapping.blueprint.yaml
│       │   │   │   ├── class-ontology.blueprint.yaml
│       │   │   │   ├── dataset-manifest.blueprint.json
│       │   │   │   ├── feature-config.blueprint.yaml
│       │   │   │   ├── hash-ledger.blueprint.json
│       │   │   │   ├── model-config.blueprint.yaml
│       │   │   │   ├── preprocessing-config.blueprint.yaml
│       │   │   │   ├── raw-registry.blueprint.csv
│       │   │   │   ├── split-manifest.blueprint.json
│       │   │   │   ├── test-seal.blueprint.json
│       │   │   │   └── threshold-policy.blueprint.yaml
│       │   │   └── templates
│       │   │       ├── experiment-review-checklist.md
│       │   │       ├── model-card-template.md
│       │   │       ├── model-release-checklist.md
│       │   │       └── rollback-checklist.md
│       │   ├── 00-decision-ledger.md
│       │   ├── 00-evidence-schema.csv
│       │   ├── 00-paper-appraisal-template.csv
│       │   ├── 00-research-protocol.md
│       │   ├── 00-search-strategy.md
│       │   ├── 01-preprocessing-and-windowing-policy.md
│       │   ├── 02-feature-engineering-review.md
│       │   ├── 03-classical-model-candidate-review.md
│       │   ├── 04-validation-and-leakage-review.md
│       │   ├── 05-personalization-and-adaptation-strategy.md
│       │   ├── 06-fatigue-distribution-shift-blueprint.md
│       │   ├── 07-task-c-target-and-metric-framework.md
│       │   ├── 08-metrics-calibration-abstention.md
│       │   ├── 09-reproducibility-and-governance.md
│       │   ├── 10-master-experiment-blueprint.md
│       │   ├── 11-open-questions-and-dependencies.md
│       │   ├── 12-red-team-audit-findings.md
│       │   ├── 13-day26-readiness-gate.md
│       │   ├── day26-final-manifest.json
│       │   └── day26-source-traceability.csv
│       └── 08-metrics-calibration-abstention.md
├── environment
│   ├── day30-environment-notes.md
│   ├── day30-requirements.txt
│   ├── pre-day41-01-requirements.txt                            # [MVP-2][MUST] Day 41 Portfolio Management
│   ├── pyproject.toml
│   ├── README.md
│   ├── reference-runtime.env
│   ├── requirements-core.lock.txt
│   └── requirements-pre-day30.txt
├── .github
│   ├── ISSUE_TEMPLATE
│   │   ├── bug_report.md
│   │   ├── clinical_feedback.md
│   │   ├── data_quality_issue.md
│   │   └── safety_incident.md
│   ├── workflows
│   │   ├── ci.yml
│   │   ├── docker-build.yml
│   │   ├── docs-check.yml
│   │   ├── model-validation.yml
│   │   └── security-scan.yml
│   └── pull_request_template.md
├── infra
│   ├── cloud
│   │   ├── kubernetes
│   │   ├── terraform
│   │   └── cloud-security-baseline.md
│   ├── local
│   │   ├── docker-compose.local.yml
│   │   ├── init-db.sh
│   │   └── init-object-store.sh
│   ├── monitoring
│   │   ├── alertmanager.yml
│   │   ├── grafana-dashboard.json
│   │   ├── loki-config.yml
│   │   └── prometheus.yml
│   ├── onprem
│   │   ├── backup-cron.example
│   │   ├── docker-compose.onprem.yml
│   │   ├── installation-runbook.md
│   │   ├── nginx.conf
│   │   └── storage-mounts.md
│   ├── secrets
│   │   ├── .gitkeep
│   │   └── secret-management.md
│   └── README.md
├── integrations
│   ├── devices
│   │   ├── edf-bdf
│   │   │   ├── adapter-config.yaml
│   │   │   └── format-notes.md
│   │   ├── generic-csv
│   │   │   ├── adapter-config.yaml
│   │   │   ├── format-spec.md
│   │   │   ├── sample_file.csv
│   │   │   └── sample_file.manifest.json
│   │   ├── noraxon
│   │   │   ├── adapter-verification-policy.md
│   │   │   ├── export-format-register.csv
│   │   │   ├── __init__.py
│   │   │   ├── logical-field-dictionary-draft.csv
│   │   │   ├── mapping-profile.template.yaml
│   │   │   ├── motion-lab-questions-vi.md
│   │   │   ├── noraxon-support-questions-en.txt
│   │   │   ├── public-vs-site-capability-matrix.csv
│   │   │   ├── public-vs-site-readiness.md
│   │   │   ├── site-evidence-request-checklist.md
│   │   │   ├── site_export_audit.py
│   │   │   ├── site-export-evidence-bundle.template.json
│   │   │   └── site-export-onboarding-runbook.md
│   │   ├── vendor-x
│   │   │   ├── adapter-config.yaml
│   │   │   ├── sample_manifest.json
│   │   │   └── vendor-format-notes.md
│   │   └── __init__.py
│   ├── ehr
│   │   ├── fhir
│   │   │   ├── integration-test-plan.md
│   │   │   ├── mapping-diagnostic-report.md
│   │   │   ├── mapping-observation.md
│   │   │   └── mapping-patient.md
│   │   └── hl7
│   │       └── message-mapping.md
│   ├── exports
│   │   ├── audit-export-spec.md
│   │   ├── feature-export-spec.md
│   │   └── report-export-spec.md
│   ├── __init__.py
│   └── README.md
├── mlops
│   ├── data
│   │   └── day25-data-readiness-policy.md
│   ├── experiments
│   │   ├── experiment-manifest.template.yaml
│   │   ├── experiment_naming_convention.md
│   │   ├── experiment_review_checklist.md
│   │   ├── mlflow_config.yaml
│   │   └── test-seal-manifest.template.yaml
│   ├── monitoring
│   │   ├── alert_rules.yaml
│   │   ├── clinical_workflow_metrics.yaml
│   │   ├── data_quality_metrics.yaml
│   │   ├── feature_drift_metrics.yaml
│   │   └── model_performance_metrics.yaml
│   ├── registry
│   │   ├── analysis_pipelines.yaml
│   │   ├── confidence_engines.yaml
│   │   ├── evidence_engines.yaml
│   │   ├── feature_extractors.yaml
│   │   ├── model_registry_schema.json
│   │   ├── preprocessing_configs.yaml
│   │   ├── registered_models.yaml
│   │   ├── report_templates.yaml
│   │   └── rule_engines.yaml
│   ├── release
│   │   ├── model_change_log.md
│   │   ├── model_release_checklist.md
│   │   └── rollback_checklist.md
│   ├── scripts
│   │   ├── compare_feature_versions.py
│   │   ├── compute_drift_report.py
│   │   ├── promote_model.py
│   │   └── register_model.py
│   └── README.md
├── notebooks
│   ├── Cross_Dataset_Transfer_Standalone_v2.ipynb
│   ├── Day27_31_Colab_ETL_Pipeline.ipynb
│   ├── Day27_31_Colab_ETL_Pipeline.py
│   ├── Day27_31_Colab_ETL_Pipeline_ver02.ipynb
│   ├── Day32_Baseline_Modeling.ipynb
│   ├── Day32_Baseline_Modeling.py
│   ├── Day32_Baseline_Modeling_ver02.ipynb
│   ├── GRABMyo_Baseline_Modeling_Primary4_v1.ipynb
│   ├── GRABMyo_Confidence_Calibration_Abstention_Standalone_v2.ipynb
│   ├── GRABMyo_ETL_RemoteStreaming_Primary4_v1.ipynb
│   ├── GRABMyo_Personalization_FewShot_Standalone_v2.ipynb
│   ├── Medeley_Personalization_FewShot_Standalone_v2.ipynb
│   ├── Mendeley_Confidence_Calibration_Abstention_Standalone_v2.ipynb
│   ├── Mendeley_TaskC_Quantitative_Metrics_Standalone_v2.ipynb
│   └── Offline_Integrated_Pipeline_Walkthrough_Standalone_v2.ipynb
├── ops
│   ├── cadence
│   │   ├── biweekly-risk-review.md
│   │   ├── day1-self-review.md
│   │   ├── monthly-pilot-steering.md
│   │   ├── weekly-engineering-sync.md
│   │   └── weekly-product-clinical-review.md
│   ├── pilot
│   │   ├── pilot-closeout-template.md
│   │   ├── pilot-feedback-form.md
│   │   ├── pilot-kickoff-checklist.md
│   │   ├── pilot-success-metrics.md
│   │   ├── site-onboarding-runbook.md
│   │   └── site-selection-criteria.md
│   ├── release
│   │   ├── go-no-go-checklist.md
│   │   ├── release-calendar.md
│   │   ├── release-notes-template.md
│   │   └── rollback-runbook.md
│   ├── support
│   │   ├── escalation-matrix.md
│   │   ├── support-sla.md
│   │   ├── troubleshooting-qc-failures.md
│   │   ├── troubleshooting-report-errors.md
│   │   └── troubleshooting-upload-errors.md
│   └── README.md
├── packages
│   ├── clinical-governance
│   │   └── pre_day41_01                                         # [MVP-2][MUST] Day 41 Portfolio Management
│   │       ├── __init__.py
│   │       └── portfolio.py
│   ├── clinical-protocols
│   │   ├── protocols
│   │   ├── schemas
│   │   └── README.md
│   ├── common-schemas
│   │   ├── generated
│   │   │   ├── python
│   │   │   └── typescript
│   │   ├── json
│   │   │   ├── day39                                            # [MVP-2][MUST] Day 39 Reproducibility & Governance
│   │   │   │   ├── rerun-result.schema.json
│   │   │   │   └── run-manifest.schema.json
│   │   │   ├── analysis-job.schema.json
│   │   │   ├── analysis-job.v0.1.schema.json
│   │   │   ├── clinical-report-package.v0.1.schema.json
│   │   │   ├── data-readiness-gate.v0.2.schema.json
│   │   │   ├── dataset-adapter-profile.v1.schema.json
│   │   │   ├── day26-blueprint.schema.json
│   │   │   ├── day28-eda-summary.schema.json
│   │   │   ├── day28-readiness-decision.schema.json
│   │   │   ├── day29-cross-day-drift-row.v1.schema.json
│   │   │   ├── day29-eda-summary.v1.schema.json
│   │   │   ├── day29-preflight.v1.schema.json
│   │   │   ├── day29-readiness-decision.v1.schema.json
│   │   │   ├── day30-channel-decision.v1.schema.json
│   │   │   ├── day30-common-ontology.v1.schema.json
│   │   │   ├── day30-dataset-view-registry.v1.schema.json
│   │   │   ├── day30-harmonization-run.v1.schema.json
│   │   │   ├── day30-preflight.v1.schema.json
│   │   │   ├── day30-readiness-decision.v1.schema.json
│   │   │   ├── day30-window-index.v1.schema.json
│   │   │   ├── day31-feature-contract-validation.v1.schema.json
│   │   │   ├── day31-feature-manifest.v1.schema.json
│   │   │   ├── day31-feature-registry.v1.schema.json
│   │   │   ├── day31-feature-row.v1.schema.json
│   │   │   ├── day31-preflight.v1.schema.json
│   │   │   ├── day31-readiness-decision.v1.schema.json
│   │   │   ├── day31-stress-test.v1.schema.json
│   │   │   ├── day32-core-gate.v1.schema.json
│   │   │   ├── day32-execution-authorization.v1.schema.json
│   │   │   ├── day32-preflight.v1.schema.json
│   │   │   ├── day32-synthetic-core-smoke.v1.schema.json
│   │   │   ├── day33-evaluation-result.v1.schema.json
│   │   │   ├── day33-evaluation-run.v1.schema.json
│   │   │   ├── day33-prediction-gate.v1.schema.json
│   │   │   ├── day33-subject-cluster-bootstrap.v1.schema.json
│   │   │   ├── day40-input-manifest.schema.json
│   │   │   ├── day40-pipeline-run-manifest.schema.json
│   │   │   ├── day40-report.schema.json
│   │   │   ├── electrode-config.schema.json
│   │   │   ├── engineering-data-gate.v1.schema.json
│   │   │   ├── evaluation-summary.schema.json
│   │   │   ├── experiment-manifest.schema.json
│   │   │   ├── explainable-inference-result.schema.json
│   │   │   ├── fatigue-evidence-result.schema.json
│   │   │   ├── fatigue-evidence-verification.schema.json
│   │   │   ├── fatigue-rule-result.schema.json
│   │   │   ├── fatigue-rule-verification.schema.json
│   │   │   ├── feature-row.schema.json
│   │   │   ├── feedback-adjudication.v0.1.schema.json
│   │   │   ├── frequency-feature-extraction-result.schema.json
│   │   │   ├── frequency-feature-row.schema.json
│   │   │   ├── frequency-feature-verification.schema.json
│   │   │   ├── gesture-feedback-context.v0.1.schema.json
│   │   │   ├── gesture-inference.v0.1.schema.json
│   │   │   ├── inference-result.schema.json
│   │   │   ├── label-mapping.v1.schema.json
│   │   │   ├── longitudinal-compatibility.v0.1.schema.json
│   │   │   ├── model-registry-record.schema.json
│   │   │   ├── mvp0-regression-report.schema.json
│   │   │   ├── normalized-signal-summary.schema.json
│   │   │   ├── offline-analysis-manifest.schema.json
│   │   │   ├── offline-analysis-verification.schema.json
│   │   │   ├── patient.schema.json
│   │   │   ├── pre-day41-task-portfolio.schema.json             # [MVP-2][MUST] Day 41 Portfolio Management
│   │   │   ├── preprocessing-result.schema.json
│   │   │   ├── preprocessing-verification-report.schema.json
│   │   │   ├── problem-details.schema.json
│   │   │   ├── protocol.schema.json
│   │   │   ├── public-dataset-archive-inventory.v1.schema.json
│   │   │   ├── public-source-record.v1.schema.json
│   │   │   ├── qc-result.schema.json
│   │   │   ├── raw-signal-ref.schema.json
│   │   │   ├── release-manifest.schema.json
│   │   │   ├── report.schema.json
│   │   │   ├── research-dataset-manifest.v0.2.schema.json
│   │   │   ├── review.schema.json
│   │   │   ├── review-workflow.v0.1.schema.json
│   │   │   ├── rollback-record.schema.json
│   │   │   ├── session-analysis-summary.schema.json
│   │   │   ├── session-import-response.schema.json
│   │   │   ├── session.schema.json
│   │   │   ├── site-export-evidence-bundle.v0.1.schema.json
│   │   │   ├── site-export-inspection.v0.1.schema.json
│   │   │   ├── source-adapter-profile.v0.1.schema.json
│   │   │   ├── spectral-estimation-result.schema.json
│   │   │   ├── spectral-verification.schema.json
│   │   │   ├── spectral-window-row.schema.json
│   │   │   ├── subject-group-split.v0.2.schema.json
│   │   │   ├── subject-group-split.v1.schema.json
│   │   │   ├── taskc-metric-event.schema.json
│   │   │   ├── technical-confidence-verification.schema.json
│   │   │   ├── test-seal-manifest.schema.json
│   │   │   ├── time-domain-feature-extraction-result.schema.json
│   │   │   ├── time-domain-feature-result.schema.json
│   │   │   ├── time-domain-feature-verification.schema.json
│   │   │   ├── training-authorization.schema.json
│   │   │   ├── trend-feature-extraction-result.schema.json
│   │   │   ├── trend-feature-verification.schema.json
│   │   │   ├── uc1-replay-session.v0.1.schema.json
│   │   │   ├── uc2-quantitative-assessment.v0.1.schema.json
│   │   │   └── windowing-result.schema.json
│   │   ├── pre-day30
│   │   │   ├── pre-day30-dual-gate.schema.json
│   │   │   └── remote-catalog.schema.json
│   │   └── README.md
│   └── semg-core
│       ├── semg_core
│       │   ├── day31_features
│       │   │   ├── feature_set_14_v1.py
│       │   │   ├── __init__.py
│       │   │   ├── long_format.py
│       │   │   ├── quality.py
│       │   │   └── spectral_v1.py
│       │   ├── activity_gate.py
│       │   ├── cv.py
│       │   ├── explainability.py
│       │   ├── fatigue_evidence.py
│       │   ├── fatigue_rules.py
│       │   ├── features.py
│       │   ├── __init__.py
│       │   ├── io.py
│       │   ├── latency_metrics.py
│       │   ├── preprocessing.py
│       │   ├── qc.py
│       │   ├── quantitative_metrics.py
│       │   ├── safety_wording.py
│       │   ├── spectral_features.py
│       │   ├── spectral.py
│       │   ├── technical_confidence.py
│       │   ├── trend.py
│       │   ├── validation.py
│       │   ├── version.py
│       │   └── windowing.py
│       └── README.md
├── product
│   ├── analytics
│   │   ├── event-taxonomy.md
│   │   ├── funnel-metrics.md
│   │   └── pilot-dashboard-requirements.md
│   ├── prd
│   │   ├── PRD-001-core-assessment-workflow.md
│   │   ├── PRD-002-signal-quality-gate.md
│   │   ├── PRD-003-fatigue-analysis-result.md
│   │   ├── PRD-004-human-review-and-signoff.md
│   │   ├── PRD-005-longitudinal-tracking.md
│   │   └── PRD-006-admin-model-config.md
│   └── ux
│       ├── copy
│       │   ├── demo-rewrite-notes.md
│       │   ├── disclaimer-copy.md
│       │   ├── empty-states.md
│       │   ├── inference-result-wording.md
│       │   └── qc-error-messages.md
│       ├── design-system
│       │   ├── accessibility-notes.md
│       │   └── components.md
│       ├── wireframes
│       │   ├── admin-settings.md
│       │   ├── analysis-result.md
│       │   ├── create-assessment.md
│       │   ├── dashboard.md
│       │   ├── human-review.md
│       │   ├── login.md
│       │   ├── longitudinal-tracking.md
│       │   ├── report-preview.md
│       │   ├── signal-quality-check.md
│       │   └── signal-upload.md
│       ├── screen-map.md
│       └── user-flows.mmd
├── .pytest_cache
│   ├── v
│   │   └── cache
│   │       ├── lastfailed
│   │       └── nodeids
│   ├── CACHEDIR.TAG
│   ├── .gitignore
│   └── README.md
├── qa-validation
│   ├── automated-tests
│   │   ├── governance
│   │   │   └── test_day39_governance.py                         # [MVP-2][MUST] Day 39 Reproducibility & Governance
│   │   ├── conftest.py
│   │   ├── day20_workflow_runtime.test.cjs
│   │   ├── day21_polling_runtime.test.cjs
│   │   ├── day22_frontend_runtime.test.cjs
│   │   ├── day23_metric_display.test.cjs
│   │   ├── run_api_contract_tests.py
│   │   ├── run_golden_signal_tests.py
│   │   ├── run_rbac_tests.py
│   │   ├── run_report_snapshot_tests.py
│   │   ├── test_api_contract_day17.py
│   │   ├── test_context_engine.py
│   │   ├── test_day19_contracts.py
│   │   ├── test_day19_mock_api.py
│   │   ├── test_day20_frontend_contracts.py
│   │   ├── test_day20_mock_api.py
│   │   ├── test_day21_analysis_jobs.py
│   │   ├── test_day21_schema.py
│   │   ├── test_day22_evidence.py
│   │   ├── test_day22_frontend_contracts.py
│   │   ├── test_day22_schemas.py
│   │   ├── test_day22_uc1_api.py
│   │   ├── test_day23_metrics.py
│   │   ├── test_day23_schemas.py
│   │   ├── test_day23_service_api.py
│   │   ├── test_day24_api.py
│   │   ├── test_day24_feedback_adjudication.py
│   │   ├── test_day24_report_builder.py
│   │   ├── test_day24_review_workflow.py
│   │   ├── test_day24_schemas.py
│   │   ├── test_day25_conflict_register_v2.py
│   │   ├── test_day25_contract_schemas_v2.py
│   │   ├── test_day25_group_split_v2.py
│   │   ├── test_day25_readiness_gate_v2.py
│   │   ├── test_day25_research_catalog_v2.py
│   │   ├── test_day25_site_audit_v2.py
│   │   ├── test_day26_blueprint_contract.py
│   │   ├── test_day26_configs.py
│   │   ├── test_day26_metrics.py
│   │   ├── test_day26_safety_and_governance.py
│   │   ├── test_day26_schemas.py
│   │   ├── test_day27_adapter.py
│   │   ├── test_day27_archive_safety.py
│   │   ├── test_day27_engineering_gate.py
│   │   ├── test_day27_group_split.py
│   │   ├── test_day27_label_mapping.py
│   │   ├── test_day27_safety_policy.py
│   │   ├── test_day27_schemas.py
│   │   ├── test_day27_source_record.py
│   │   ├── test_day28_deep.py
│   │   ├── test_day28_preflight.py
│   │   ├── test_day28_statistics.py
│   │   ├── test_day29_drift.py
│   │   ├── test_day29_feature_readiness.py
│   │   ├── test_day29_hierarchy_labels.py
│   │   ├── test_day29_partition_guard.py
│   │   ├── test_day29_schemas.py
│   │   ├── test_day29_statistics.py
│   │   ├── test_day30_cli.py
│   │   ├── test_day30_delivery.py
│   │   ├── test_day30_governance.py
│   │   ├── test_day30_schemas.py
│   │   ├── test_day30_signal_contracts.py
│   │   ├── test_day30_stress.py
│   │   ├── test_day30_windowing_storage.py
│   │   ├── test_day31_cli.py
│   │   ├── test_day31_feature_math.py
│   │   ├── test_day31_governance.py
│   │   ├── test_day31_io.py
│   │   ├── test_day31_pipeline_safety.py
│   │   ├── test_day31_quality_and_arms.py
│   │   ├── test_day31_schemas.py
│   │   ├── test_day31_stress.py
│   │   ├── test_day32_aggregation.py
│   │   ├── test_day32_authorization.py
│   │   ├── test_day32_core_gate.py
│   │   ├── test_day32_grouped_cv.py
│   │   ├── test_day32_matrix_gate.py
│   │   ├── test_day32_models.py
│   │   ├── test_day32_schemas.py
│   │   ├── test_day33.py
│   │   ├── test_day34.py
│   │   ├── test_mvp0_regression_suite.py
│   │   ├── test_offline_analysis_pipeline.py
│   │   ├── test_pre_day41_01.py                                 # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── test_spectral_estimation_analytical.py
│   │   ├── test_time_domain_feature_analytical.py
│   │   └── test_windowing_analytical.py
│   ├── baselines
│   │   └── mvp0_baseline_v0.1.json
│   ├── configs
│   │   ├── day19_tsconfig.json
│   │   ├── day19_vendor_stubs.d.ts
│   │   ├── day20_tsconfig.json
│   │   ├── day20_vendor_stubs.d.ts
│   │   ├── day20_workflow_tsconfig.json
│   │   ├── day21_runtime_tsconfig.json
│   │   ├── day21_tsconfig.json
│   │   ├── day21_vendor_stubs.d.ts
│   │   ├── day22_runtime_tsconfig.json
│   │   ├── day22_tsconfig.json
│   │   ├── day23_runtime_tsconfig.json
│   │   ├── day23_tsconfig.json
│   │   ├── day23_vendor_stubs.d.ts
│   │   ├── day24_tsconfig.json
│   │   ├── day24_vendor_stubs.d.ts
│   │   ├── mvp0_regression_v0.1.yaml
│   │   └── preprocess_verification_v0.1.yaml
│   ├── evidence
│   │   ├── day15-abstained-run
│   │   │   ├── 00-ingestion-summary.json
│   │   │   ├── 01-qc-result.json
│   │   │   ├── 02-preprocessing-result.json
│   │   │   ├── 03-windowing-result.json
│   │   │   ├── 04-time-domain-features.json
│   │   │   ├── 05-spectral-estimation.json
│   │   │   ├── 06-frequency-features.json
│   │   │   ├── 07-trend-features.json
│   │   │   ├── 08-fatigue-evidence.json
│   │   │   ├── 09-fatigue-rule.json
│   │   │   ├── 10-explainable-inference.json
│   │   │   └── 11-analysis-manifest.json
│   │   ├── day15-golden-rerun
│   │   │   ├── 00-ingestion-summary.json
│   │   │   ├── 01-qc-result.json
│   │   │   ├── 02-preprocessing-result.json
│   │   │   ├── 03-windowing-result.json
│   │   │   ├── 04-time-domain-features.json
│   │   │   ├── 05-spectral-estimation.json
│   │   │   ├── 06-frequency-features.json
│   │   │   ├── 07-trend-features.json
│   │   │   ├── 08-fatigue-evidence.json
│   │   │   ├── 09-fatigue-rule.json
│   │   │   ├── 10-explainable-inference.json
│   │   │   └── 11-analysis-manifest.json
│   │   ├── day15-golden-run
│   │   │   ├── 00-ingestion-summary.json
│   │   │   ├── 01-qc-result.json
│   │   │   ├── 02-preprocessing-result.json
│   │   │   ├── 03-windowing-result.json
│   │   │   ├── 04-time-domain-features.json
│   │   │   ├── 05-spectral-estimation.json
│   │   │   ├── 06-frequency-features.json
│   │   │   ├── 07-trend-features.json
│   │   │   ├── 08-fatigue-evidence.json
│   │   │   ├── 09-fatigue-rule.json
│   │   │   ├── 10-explainable-inference.json
│   │   │   └── 11-analysis-manifest.json
│   │   ├── day15-warning-run
│   │   │   ├── 00-ingestion-summary.json
│   │   │   ├── 01-qc-result.json
│   │   │   ├── 02-preprocessing-result.json
│   │   │   ├── 03-windowing-result.json
│   │   │   ├── 04-time-domain-features.json
│   │   │   ├── 05-spectral-estimation.json
│   │   │   ├── 06-frequency-features.json
│   │   │   ├── 07-trend-features.json
│   │   │   ├── 08-fatigue-evidence.json
│   │   │   ├── 09-fatigue-rule.json
│   │   │   ├── 10-explainable-inference.json
│   │   │   └── 11-analysis-manifest.json
│   │   ├── day16-regression
│   │   │   ├── fail-flatline
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   ├── fail-nonfinite
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   ├── fail-short-duration
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   ├── golden-run-1
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   ├── golden-run-2
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   ├── warning-clipping
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   ├── warning-motion
│   │   │   │   ├── 00-ingestion-summary.json
│   │   │   │   ├── 01-qc-result.json
│   │   │   │   ├── 02-preprocessing-result.json
│   │   │   │   ├── 03-windowing-result.json
│   │   │   │   ├── 04-time-domain-features.json
│   │   │   │   ├── 05-spectral-estimation.json
│   │   │   │   ├── 06-frequency-features.json
│   │   │   │   ├── 07-trend-features.json
│   │   │   │   ├── 08-fatigue-evidence.json
│   │   │   │   ├── 09-fatigue-rule.json
│   │   │   │   ├── 10-explainable-inference.json
│   │   │   │   └── 11-analysis-manifest.json
│   │   │   └── warning-powerline
│   │   │       ├── 00-ingestion-summary.json
│   │   │       ├── 01-qc-result.json
│   │   │       ├── 02-preprocessing-result.json
│   │   │       ├── 03-windowing-result.json
│   │   │       ├── 04-time-domain-features.json
│   │   │       ├── 05-spectral-estimation.json
│   │   │       ├── 06-frequency-features.json
│   │   │       ├── 07-trend-features.json
│   │   │       ├── 08-fatigue-evidence.json
│   │   │       ├── 09-fatigue-rule.json
│   │   │       ├── 10-explainable-inference.json
│   │   │       └── 11-analysis-manifest.json
│   │   ├── day17-abstained-analysis
│   │   │   ├── 00-ingestion-summary.json
│   │   │   ├── 01-qc-result.json
│   │   │   ├── 02-preprocessing-result.json
│   │   │   ├── 03-windowing-result.json
│   │   │   ├── 04-time-domain-features.json
│   │   │   ├── 05-spectral-estimation.json
│   │   │   ├── 06-frequency-features.json
│   │   │   ├── 07-trend-features.json
│   │   │   ├── 08-fatigue-evidence.json
│   │   │   ├── 09-fatigue-rule.json
│   │   │   ├── 10-explainable-inference.json
│   │   │   └── 11-analysis-manifest.json
│   │   ├── day17-golden-analysis
│   │   │   ├── 00-ingestion-summary.json
│   │   │   ├── 01-qc-result.json
│   │   │   ├── 02-preprocessing-result.json
│   │   │   ├── 03-windowing-result.json
│   │   │   ├── 04-time-domain-features.json
│   │   │   ├── 05-spectral-estimation.json
│   │   │   ├── 06-frequency-features.json
│   │   │   ├── 07-trend-features.json
│   │   │   ├── 08-fatigue-evidence.json
│   │   │   ├── 09-fatigue-rule.json
│   │   │   ├── 10-explainable-inference.json
│   │   │   └── 11-analysis-manifest.json
│   │   ├── day30
│   │   │   ├── day30-artifact-check.json
│   │   │   ├── day30-channel-decision.json
│   │   │   ├── day30-check-run.log
│   │   │   ├── day30-common-ontology.json
│   │   │   ├── day30-dataset-view-registry.json
│   │   │   ├── day30-final-manifest.json
│   │   │   ├── day30-harmonization-report.md
│   │   │   ├── day30-harmonization-run.json
│   │   │   ├── day30-line-coverage.json
│   │   │   ├── day30-pre-day30-input-baseline.json
│   │   │   ├── day30-preflight.json
│   │   │   ├── day30-readiness-decision.json
│   │   │   ├── day30-sampling-policy-validation.json
│   │   │   ├── day30-source-hash-ledger.json
│   │   │   ├── day30-stress-test.json
│   │   │   ├── day30-tooling-validation.json
│   │   │   ├── day30-window-index.fixture.json
│   │   │   ├── input-git-commit.txt
│   │   │   └── input-working-tree.patch
│   │   ├── day31
│   │   │   ├── day31-artifact-check.json
│   │   │   ├── day31-check-run.log
│   │   │   ├── day31-coverage.json
│   │   │   ├── day31-feature-contract-validation.json
│   │   │   ├── day31-feature-manifest.json
│   │   │   ├── day31-feature-quality-smoke.json
│   │   │   ├── day31-feature-registry.json
│   │   │   ├── day31-golden-feature-results.json
│   │   │   ├── day31-preflight.json
│   │   │   ├── day31-readiness-decision.json
│   │   │   └── day31-stress-test.json
│   │   ├── day32
│   │   │   ├── day32-artifact-check.json
│   │   │   ├── day32-optional-eligibility.json
│   │   │   ├── day32-preflight.json
│   │   │   ├── day32-real-baseline-evidence.json
│   │   │   ├── day32-synthetic-core-smoke.json
│   │   │   └── day32-tooling-validation.json
│   │   ├── day33
│   │   │   ├── input-day32
│   │   │   │   ├── grabmyo-day32-input-ledger.json
│   │   │   │   └── mendeley-day32-input-ledger.json
│   │   │   ├── predictions
│   │   │   │   ├── grabmyo-day32-oof-trial-contract.csv
│   │   │   │   └── mendeley-day32-oof-window-contract.csv
│   │   │   ├── real-development
│   │   │   │   ├── grabmyo
│   │   │   │   │   ├── aggregation-audit.json
│   │   │   │   │   ├── bootstrap-primary-metric.json
│   │   │   │   │   ├── confusion-matrix.csv
│   │   │   │   │   ├── day-metrics.csv
│   │   │   │   │   ├── evaluation-metrics.json
│   │   │   │   │   ├── failure-cases.csv
│   │   │   │   │   ├── failure-summary.json
│   │   │   │   │   ├── fold-metrics.csv
│   │   │   │   │   ├── high-confidence-errors.csv
│   │   │   │   │   ├── high-disagreement-errors.csv
│   │   │   │   │   ├── per-class-metrics.csv
│   │   │   │   │   ├── prediction-gate.json
│   │   │   │   │   ├── qc-associated-errors.csv
│   │   │   │   │   ├── repetition-metrics.json
│   │   │   │   │   ├── repetition-predictions.csv
│   │   │   │   │   ├── run-summary.json
│   │   │   │   │   ├── subject-class-recall.csv
│   │   │   │   │   ├── subject-metrics.csv
│   │   │   │   │   ├── subject-summary.json
│   │   │   │   │   ├── top-confusion-pairs.csv
│   │   │   │   │   └── worst-subjects.csv
│   │   │   │   └── mendeley
│   │   │   │       ├── aggregation-audit.json
│   │   │   │       ├── bootstrap-primary-metric.json
│   │   │   │       ├── confusion-matrix.csv
│   │   │   │       ├── day-metrics.csv
│   │   │   │       ├── evaluation-metrics.json
│   │   │   │       ├── failure-cases.csv
│   │   │   │       ├── failure-summary.json
│   │   │   │       ├── fold-metrics.csv
│   │   │   │       ├── high-confidence-errors.csv
│   │   │   │       ├── high-disagreement-errors.csv
│   │   │   │       ├── per-class-metrics.csv
│   │   │   │       ├── prediction-gate.json
│   │   │   │       ├── qc-associated-errors.csv
│   │   │   │       ├── repetition-metrics.json
│   │   │   │       ├── repetition-predictions.csv
│   │   │   │       ├── run-summary.json
│   │   │   │       ├── subject-class-recall.csv
│   │   │   │       ├── subject-metrics.csv
│   │   │   │       ├── subject-summary.json
│   │   │   │       ├── top-confusion-pairs.csv
│   │   │   │       └── worst-subjects.csv
│   │   │   ├── synthetic-evaluation
│   │   │   │   ├── aggregation-audit.json
│   │   │   │   ├── bootstrap-primary-metric.json
│   │   │   │   ├── confusion-matrix.csv
│   │   │   │   ├── day-metrics.csv
│   │   │   │   ├── evaluation-metrics.json
│   │   │   │   ├── failure-cases.csv
│   │   │   │   ├── failure-summary.json
│   │   │   │   ├── fold-metrics.csv
│   │   │   │   ├── high-confidence-errors.csv
│   │   │   │   ├── high-disagreement-errors.csv
│   │   │   │   ├── per-class-metrics.csv
│   │   │   │   ├── prediction-gate.json
│   │   │   │   ├── qc-associated-errors.csv
│   │   │   │   ├── repetition-metrics.json
│   │   │   │   ├── repetition-predictions.csv
│   │   │   │   ├── run-summary.json
│   │   │   │   ├── subject-class-recall.csv
│   │   │   │   ├── subject-metrics.csv
│   │   │   │   ├── subject-summary.json
│   │   │   │   ├── top-confusion-pairs.csv
│   │   │   │   └── worst-subjects.csv
│   │   │   └── day33-synthetic-prediction-gate.json
│   │   ├── pre-day30
│   │   │   ├── grabmyo
│   │   │   │   ├── day29-readiness-decision.yaml
│   │   │   │   └── grabmyo-eda-summary.json
│   │   │   ├── mendeley
│   │   │   │   ├── day28-readiness-decision.yaml
│   │   │   │   └── mendeley-eda-summary.json
│   │   │   ├── smoke
│   │   │   │   ├── eda
│   │   │   │   │   ├── record-statistics.jsonl
│   │   │   │   │   └── streaming-eda-summary.json
│   │   │   │   ├── catalog.json
│   │   │   │   └── sample-plan.json
│   │   │   ├── pre-day30-final-manifest.template.json
│   │   │   └── README.md
│   │   ├── day10-frequency-features-blocked.json
│   │   ├── day10-frequency-features.csv
│   │   ├── day10-frequency-features.json
│   │   ├── day10-frequency-features-rerun.json
│   │   ├── day10-mdf-mnf-verification.json
│   │   ├── day10-mdf-mnf-verification.md
│   │   ├── day11-trends-blocked.json
│   │   ├── day11-trends.csv
│   │   ├── day11-trends.json
│   │   ├── day11-trends-rerun.json
│   │   ├── day11-trend-verification.json
│   │   ├── day11-trend-verification.md
│   │   ├── day12-evidence-verification.json
│   │   ├── day12-evidence-verification.md
│   │   ├── day12-fatigue-evidence-abstained.json
│   │   ├── day12-fatigue-evidence.json
│   │   ├── day12-fatigue-evidence-rerun.json
│   │   ├── day13-day12-regression.log
│   │   ├── day13-fatigue-rule-abstained.json
│   │   ├── day13-fatigue-rule.json
│   │   ├── day13-fatigue-rule-rerun.json
│   │   ├── day13-rule-verification.json
│   │   ├── day13-rule-verification.md
│   │   ├── day14-confidence-verification.json
│   │   ├── day14-confidence-verification.md
│   │   ├── day14-explainable-inference-abstained.json
│   │   ├── day14-explainable-inference.json
│   │   ├── day14-explainable-inference-rerun.json
│   │   ├── day14-explainable-inference-warning.json
│   │   ├── day15-package-verification.json
│   │   ├── day16-mvp0-regression-report.json
│   │   ├── day16-mvp0-regression-report.md
│   │   ├── day17-abstained-api-summary.json
│   │   ├── day17-golden-api-summary.json
│   │   ├── day19-mock-api-smoke.json
│   │   ├── day20-golden-intake-evidence.json
│   │   ├── day21-analysis-job-evidence.json
│   │   ├── day22-uc1-replay-evidence.json
│   │   ├── day23-uc2-assessment-evidence.json
│   │   ├── day24-report-draft.json
│   │   ├── day24-report-final.json
│   │   ├── day24-review-case.json
│   │   ├── day25-data-readiness-gate-v0.2.json
│   │   ├── day25-noraxon-site-audit.json
│   │   ├── day25-readiness-summary.md
│   │   ├── day25-subject-group-split-v0.2.json
│   │   ├── day26-blueprint-validation.json
│   │   ├── day26-check-run.log
│   │   ├── day26-experiment-matrix.csv
│   │   ├── day26-experiment-matrix.json
│   │   ├── day26-source-hash-ledger.json
│   │   ├── day26-test-set-seal.template.json
│   │   ├── day26-validation-run.md
│   │   ├── day27-check-run.log
│   │   ├── day27-real-dataset-gate.placeholder.json
│   │   ├── day27-source-fixture-verification.json
│   │   ├── day27-source-hash-ledger.json
│   │   ├── day27-source-template-negative-test.log
│   │   ├── day27-tooling-validation.json
│   │   ├── day27-validation-run.md
│   │   ├── day28-check-run.log
│   │   ├── day28-current-input-preflight.json
│   │   ├── day28-eda-report.NOT_RUN.md
│   │   ├── day28-final-manifest.json
│   │   ├── day28-preflight.json
│   │   ├── day28-tooling-validation.json
│   │   ├── day28-user-input-baseline-hash-ledger.json
│   │   ├── day29-artifact-check.json
│   │   ├── day29-check-run.log
│   │   ├── day29-eda-report.NOT_RUN.md
│   │   ├── day29-final-manifest.json
│   │   ├── day29-source-hash-ledger.json
│   │   ├── day29-tooling-validation.json
│   │   ├── day33-artifact-check.json
│   │   ├── day33-check-run.log
│   │   ├── day33-final-manifest.json
│   │   ├── day33-source-hash-ledger.json
│   │   ├── day37-day36-integration-report.json                  # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── day37-final-manifest.json                            # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── day37-input-gate.json                                # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── day37-synthetic-validation.json                      # [MVP-2][MUST] Day 37 Quantitative Metrics
│   │   ├── day3-check-output.txt
│   │   ├── day3-ingestion-evidence.template.md
│   │   ├── day3-normalized-summary.json
│   │   ├── day3-preflight-day2-regression.txt
│   │   ├── day4-qc-evidence.md
│   │   ├── day4-qc-evidence.template.md
│   │   ├── day4-qc-fail-flatline.json
│   │   ├── day4-qc-fail-nonfinite.json
│   │   ├── day4-qc-fail-short-duration.json
│   │   ├── day4-qc-pass.json
│   │   ├── day4-qc-warning-clipping.json
│   │   ├── day4-qc-warning-motion.json
│   │   ├── day4-qc-warning-powerline.json
│   │   ├── day5-frequency-response.json
│   │   ├── day5-preprocess-blocked.json
│   │   ├── day5-preprocess-golden.json
│   │   ├── day5-preprocess-golden.npz
│   │   ├── day5-preprocessing-evidence.md
│   │   ├── day5-preprocess-powerline.json
│   │   ├── day6-day5-regression.log
│   │   ├── day6-dsp-environment.json
│   │   ├── day6-filter-verification.md
│   │   ├── day6-filter-verification.template.md
│   │   ├── day6-preprocessing-verification.json
│   │   ├── day7-day6-regression.log
│   │   ├── day7-window-geometry.json
│   │   ├── day7-windowing-evidence.md
│   │   ├── day7-windowing-evidence.template.md
│   │   ├── day7-windowing-result.json
│   │   ├── day7-windowing-result-rerun.json
│   │   ├── day8-day7-regression.log
│   │   ├── day8-time-domain-features.csv
│   │   ├── day8-time-domain-features.json
│   │   ├── day8-time-domain-features-rerun.json
│   │   ├── day8-time-domain-feature-verification.json
│   │   ├── day8-time-domain-feature-verification.md
│   │   ├── day9-spectral-blocked.json
│   │   ├── day9-spectral-estimation.csv
│   │   ├── day9-spectral-estimation.json
│   │   ├── day9-spectral-estimation-rerun.json
│   │   ├── day9-spectral-verification.json
│   │   ├── day9-spectral-verification.md
│   │   ├── e2e_A_Golden.json
│   │   ├── e2e_B_Powerline.json
│   │   ├── e2e_C_Flatline.json
│   │   ├── mvp0-feasibility-evidence.md
│   │   ├── mvp1-release-evidence.md
│   │   ├── mvp2-pilot-readiness-evidence.md
│   │   ├── pre-day41-01-artifact-check.json                     # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── pre-day41-01-checks.log                              # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── pre-day41-01-final-manifest.json                     # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── pre-day41-01-source-hash-ledger.json                 # [MVP-2][MUST] Day 41 Portfolio Management
│   │   └── pre-day41-01-validation-report.json                  # [MVP-2][MUST] Day 41 Portfolio Management
│   ├── fixtures
│   │   ├── day30
│   │   │   └── metadata-index.fixture.csv
│   │   ├── pre_day30
│   │   │   ├── remote-objects.local.csv
│   │   │   └── tiny_signal.csv
│   │   ├── day31-readiness.fixture.json
│   │   ├── day32-synthetic-authorization.yaml
│   │   ├── day32-synthetic-matrix.npz
│   │   └── day33-synthetic-window-predictions.csv
│   ├── requirements
│   │   ├── ai-signal-requirements.csv
│   │   ├── clinical-requirements.csv
│   │   ├── day10-acceptance-criteria.md
│   │   ├── day11-acceptance-criteria.md
│   │   ├── day12-acceptance-criteria.md
│   │   ├── day13-acceptance-criteria.md
│   │   ├── day14-acceptance-criteria.md
│   │   ├── day15-acceptance-criteria.md
│   │   ├── day16-acceptance-criteria.md
│   │   ├── day17-acceptance-criteria.md
│   │   ├── day19-acceptance-criteria.md
│   │   ├── day1-acceptance-criteria.md
│   │   ├── day20-acceptance-criteria.md
│   │   ├── day21-acceptance-criteria.md
│   │   ├── day22-acceptance-criteria.md
│   │   ├── day24-acceptance-criteria.md
│   │   ├── day25-acceptance-criteria.md
│   │   ├── day25-research-grounded-requirements.csv
│   │   ├── day26-acceptance-criteria.md
│   │   ├── day26-research-blueprint-requirements.csv
│   │   ├── day27-acceptance-criteria.md
│   │   ├── day27-requirements.csv
│   │   ├── day28-acceptance-criteria.md
│   │   ├── day29-acceptance-criteria.md
│   │   ├── day29-red-team-checklist.md
│   │   ├── day29-requirements.csv
│   │   ├── day2-acceptance-criteria.md
│   │   ├── day30-acceptance-criteria.md
│   │   ├── day30-red-team-checklist.md
│   │   ├── day30-requirements.csv
│   │   ├── day31-acceptance-criteria.md
│   │   ├── day31-red-team-checklist.md
│   │   ├── day31-requirements.csv
│   │   ├── day32-acceptance-criteria.md
│   │   ├── day33-acceptance-criteria.md
│   │   ├── day3-acceptance-criteria.md
│   │   ├── day4-acceptance-criteria.md
│   │   ├── day5-acceptance-criteria.md
│   │   ├── day6-acceptance-criteria.md
│   │   ├── day7-acceptance-criteria.md
│   │   ├── day8-acceptance-criteria.md
│   │   ├── day9-acceptance-criteria.md
│   │   ├── pre-day41-01-acceptance-criteria.md                  # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── product-requirements.csv
│   │   └── security-requirements.csv
│   ├── test-data
│   │   ├── day27
│   │   │   ├── label-map.synthetic-verified.json
│   │   │   ├── profile.synthetic-verified.json
│   │   │   ├── README.md
│   │   │   ├── signal.synthetic.csv
│   │   │   ├── source-record.synthetic-invalid.json
│   │   │   └── source-record.synthetic-verified.json
│   │   ├── deidentified-samples
│   │   ├── frontend
│   │   │   └── day20
│   │   │       ├── fail_flatline.json
│   │   │       ├── golden_intake_pass.json
│   │   │       ├── import_missing_unit.json
│   │   │       └── warning_powerline.json
│   │   ├── manifests
│   │   └── synthetic
│   │       ├── day25-subject-session-metadata.json
│   │       ├── day4_qc_fixture_index.json
│   │       ├── generate_qc_fixtures.py
│   │       ├── qc_fail_flatline.csv
│   │       ├── qc_fail_flatline.manifest.json
│   │       ├── qc_fail_nonfinite.csv
│   │       ├── qc_fail_nonfinite.manifest.json
│   │       ├── qc_fail_short_duration.csv
│   │       ├── qc_fail_short_duration.manifest.json
│   │       ├── qc_warning_clipping.csv
│   │       ├── qc_warning_clipping.manifest.json
│   │       ├── qc_warning_motion_artifact.csv
│   │       ├── qc_warning_motion_artifact.manifest.json
│   │       ├── qc_warning_powerline.csv
│   │       └── qc_warning_powerline.manifest.json
│   ├── test-plans
│   │   ├── day29-grabmyo-eda-test-plan.md
│   │   ├── day30-harmonization-test-plan.md
│   │   ├── day31-feature-engineering-test-plan.md
│   │   ├── day32-test-plan.md
│   │   ├── day33-test-plan.md
│   │   ├── e2e-test-plan.md
│   │   ├── integration-test-plan.md
│   │   ├── pre-day41-01-test-plan.md                            # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── security-test-plan.md
│   │   ├── signal-golden-test-plan.md
│   │   ├── unit-test-plan.md
│   │   └── user-acceptance-test-plan.md
│   ├── traceability
│   │   ├── day16-requirement-test-traceability.csv
│   │   ├── day29-requirement-test-traceability.csv
│   │   ├── day30-requirement-test-traceability.csv
│   │   ├── day31-requirement-test-traceability.csv
│   │   ├── day32-requirement-test.csv
│   │   ├── pre-day41-01-requirement-test.csv                    # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── requirement-test-traceability.csv
│   │   └── risk-control-traceability.csv
│   ├── ui-audit
│   │   ├── screenshots
│   │   │   ├── .gitkeep
│   │   │   ├── mobile-drawer-450x714-firefox.png
│   │   │   ├── UIAUDIT-001-admin-created-report-without-prerequisites.png
│   │   │   ├── UIAUDIT-001-admin-finalized-invalid-report.png
│   │   │   ├── UIAUDIT-001-missing-prerequisites-admin-review.png
│   │   │   └── UIAUDIT-005-patient-audit-route-bypass.png
│   │   ├── 00-executive-summary.md
│   │   ├── 01-repo-inventory.md
│   │   ├── 02-route-coverage.csv
│   │   ├── 03-requirement-traceability.csv
│   │   ├── 04-findings.json
│   │   ├── 05-findings.md
│   │   ├── 06-e2e-results.md
│   │   ├── 07-accessibility-results.md
│   │   ├── 08-responsive-visual-results.md
│   │   ├── 09-performance-results.md
│   │   ├── 10-security-privacy-rbac-results.md
│   │   ├── 11-ai-safety-copy-results.md
│   │   ├── 12-test-command-log.md
│   │   ├── 13-remediation-plan.md
│   │   └── audit-ledger.csv
│   └── README.md
├── reports
│   ├── examples
│   │   ├── example_clinical_report_mvp1.pdf
│   │   ├── example_longitudinal_report.pdf
│   │   └── example_qc_fail_report.pdf
│   ├── schemas
│   │   ├── clinical_report_context.schema.json
│   │   ├── feature_summary.schema.json
│   │   └── reviewer_signoff.schema.json
│   ├── templates
│   │   ├── clinical_report_v0.1.html
│   │   ├── clinical_report_v0.1.md
│   │   ├── clinical_report_v0.2-review-workflow.md
│   │   ├── operational_summary_v0.1.md
│   │   ├── research_export_readme_v0.1.md
│   │   └── technical_appendix_v0.1.md
│   ├── wording
│   │   ├── clinical-interpretation-phrases.md
│   │   ├── day24-approved-phrases.md
│   │   ├── day24-prohibited-claims.md
│   │   ├── limitation-disclaimer.md
│   │   └── prohibited-claims.md
│   └── README.md
├── .ruff_cache
│   ├── 0.16.0
│   │   ├── 10656590239286997543
│   │   ├── 12657778968226520829
│   │   ├── 1638017197841394455
│   │   ├── 17199752757005378944
│   │   ├── 18217271609707301901
│   │   ├── 239105367297105599
│   │   ├── 3126472705764691367
│   │   ├── 498863909749480865
│   │   ├── 5510839132657840070
│   │   ├── 6218558126346713801
│   │   ├── 6625101780496566838
│   │   ├── 7422075558997016083
│   │   └── 9929350600193105711
│   ├── CACHEDIR.TAG
│   └── .gitignore
├── scripts
│   ├── data
│   │   ├── audit_dataset_readiness.py
│   │   ├── audit_noraxon_site_evidence.py
│   │   ├── audit_repo_no_raw_data.py
│   │   ├── build_analysis_api_summary.py
│   │   ├── build_day25_readiness_gate.py
│   │   ├── build_remote_catalog.py
│   │   ├── build_subject_group_split.py
│   │   ├── build_subject_group_split_v2.py
│   │   ├── check_reproducibility.py
│   │   ├── check_storage_capacity.py
│   │   ├── check_two_zone_contract.py
│   │   ├── _common.py
│   │   ├── compare_regression_runs.py
│   │   ├── compute_file_hash.py
│   │   ├── day27_acquire_public_dataset.py
│   │   ├── day27_build_group_split.py
│   │   ├── day27_build_metadata_index.py
│   │   ├── day27_convert_csv_smoke.py
│   │   ├── day27_inventory_archive.py
│   │   ├── day27_run_engineering_gate.py
│   │   ├── day27_verify_source_record.py
│   │   ├── day28_plot_eda.py
│   │   ├── day28_preflight.py
│   │   ├── day28_run_eda.py
│   │   ├── day29_audit_partition_visibility.py
│   │   ├── day29_plot_eda.py
│   │   ├── day29_preflight.py
│   │   ├── day29_run_eda.py
│   │   ├── day30_build_common_ontology.py
│   │   ├── day30_build_input_report.py
│   │   ├── day30_build_view_registry.py
│   │   ├── day30_build_window_index.py
│   │   ├── day30_preflight.py
│   │   ├── day30_render_harmonization_report.py
│   │   ├── day30_run_harmonization.py
│   │   ├── day30_validate_channel_policy.py
│   │   ├── day30_validate_sampling_policy.py
│   │   ├── day31_build_feature_manifest.py
│   │   ├── day31_build_readiness_decision.py
│   │   ├── day31_extract_features.py
│   │   ├── day31_extract_smoke.py
│   │   ├── day31_feature_quality_smoke.py
│   │   ├── day31_generate_feature_registry.py
│   │   ├── day31_preflight.py
│   │   ├── day31_validate_feature_contract.py
│   │   ├── day32_generate_synthetic_matrix.py
│   │   ├── day32_preflight.py
│   │   ├── day33_generate_synthetic_predictions.py
│   │   ├── day33_preflight.py
│   │   ├── deidentify_dataset.py
│   │   ├── generate_dataset_manifest.py
│   │   ├── generate_day24_review_evidence.py
│   │   ├── import_signal_session.py
│   │   ├── inspect_unknown_export.py
│   │   ├── pre_day30_dual_gate.py
│   │   ├── run_explainable_inference.py
│   │   ├── run_fatigue_evidence.py
│   │   ├── run_fatigue_rule.py
│   │   ├── run_frequency_features.py
│   │   ├── run_grabmyo_real_eda.py
│   │   ├── run_mendeley_real_eda.py
│   │   ├── run_mvp0_regression.py
│   │   ├── run_preprocessing_e2e.py
│   │   ├── run_signal_preprocessing.py
│   │   ├── run_signal_qc.py
│   │   ├── run_signal_windowing.py
│   │   ├── run_spectral_estimation.py
│   │   ├── run_time_domain_features.py
│   │   ├── run_trend_features.py
│   │   ├── select_remote_sample.py
│   │   ├── streaming_signal_eda.py
│   │   ├── update_notes.py
│   │   ├── validate_dataset_inventory.py
│   │   ├── validate_day25_research_inventory.py
│   │   ├── validate_signal_file.py
│   │   ├── verify_fatigue_evidence.py
│   │   ├── verify_fatigue_rule.py
│   │   ├── verify_mdf_mnf.py
│   │   ├── verify_offline_analysis_package.py
│   │   ├── verify_preprocessing_response.py
│   │   ├── verify_preprocess_v0_1.py
│   │   ├── verify_spectral_estimation.py
│   │   ├── verify_technical_confidence.py
│   │   ├── verify_time_domain_features.py
│   │   ├── verify_trend_features.py
│   │   └── verify_window_geometry.py
│   ├── dev
│   │   ├── bootstrap_pre_day30_storage.sh
│   │   ├── build_day30_manifest.py
│   │   ├── capture_dsp_environment.py
│   │   ├── check_day10_artifacts.py
│   │   ├── check_day11_artifacts.py
│   │   ├── check_day12_artifacts.py
│   │   ├── check_day13_artifacts.py
│   │   ├── check_day14_artifacts.py
│   │   ├── check_day15_artifacts.py
│   │   ├── check_day16_artifacts.py
│   │   ├── check_day17_artifacts.py
│   │   ├── check_day19_artifacts.py
│   │   ├── check_day1_artifacts.py
│   │   ├── check_day20_artifacts.py
│   │   ├── check_day21_artifacts.py
│   │   ├── check_day22_artifacts.py
│   │   ├── check_day23_artifacts.py
│   │   ├── check_day24_artifacts.py
│   │   ├── check_day25_artifacts.py
│   │   ├── check_day25_research_artifacts.py
│   │   ├── check_day26_research_artifacts.py
│   │   ├── check_day27_artifacts.py
│   │   ├── check_day29_artifacts.py
│   │   ├── check_day2_artifacts.py
│   │   ├── check_day30_artifacts.py
│   │   ├── check_day31_artifacts.py
│   │   ├── check_day32_artifacts.py
│   │   ├── check_day33_artifacts.py
│   │   ├── check_day3_artifacts.py
│   │   ├── check_day4_artifacts.py
│   │   ├── check_day5_artifacts.py
│   │   ├── check_day6_artifacts.py
│   │   ├── check_day7_artifacts.py
│   │   ├── check_day8_artifacts.py
│   │   ├── check_day9_artifacts.py
│   │   ├── day1_bootstrap.sh
│   │   ├── day29_tooling_smoke.py
│   │   ├── day30_tooling_smoke.py
│   │   ├── day32_tooling_smoke.py
│   │   ├── freeze_mvp0_baseline_v0_1.py
│   │   ├── freeze_preprocess_v0_1.py
│   │   ├── generate_day17_api_examples.py
│   │   ├── generate_day22_evidence.py
│   │   ├── register_fatigue_evidence_v0_1.py
│   │   ├── register_fatigue_rule_v0_1.py
│   │   ├── register_feature_extractor_v0_1.py
│   │   ├── register_frequency_features_v0_1.py
│   │   ├── register_offline_analysis_mvp0.py
│   │   ├── register_spectral_estimator_v0_1.py
│   │   ├── register_technical_confidence_v0_1.py
│   │   ├── register_trend_features_v0_1.py
│   │   ├── reset_local_stack.sh
│   │   ├── run_day10_checks.sh
│   │   ├── run_day11_checks.sh
│   │   ├── run_day12_checks.sh
│   │   ├── run_day13_checks.sh
│   │   ├── run_day14_checks.sh
│   │   ├── run_day15_checks.sh
│   │   ├── run_day16_checks.sh
│   │   ├── run_day17_checks.sh
│   │   ├── run_day19_checks.sh
│   │   ├── run_day19_mock_api.py
│   │   ├── run_day20_checks.sh
│   │   ├── run_day21_checks.sh
│   │   ├── run_day22_checks.sh
│   │   ├── run_day23_checks.sh
│   │   ├── run_day24_checks.sh
│   │   ├── run_day25_checks.sh
│   │   ├── run_day25_research_checks.sh
│   │   ├── run_day26_checks.sh
│   │   ├── run_day26_research_checks.sh
│   │   ├── run_day27_checks.sh
│   │   ├── run_day27_public_dataset_checks.sh
│   │   ├── run_day28_checks.sh
│   │   ├── run_day29_checks.sh
│   │   ├── run_day2_checks.sh
│   │   ├── run_day30_checks.sh
│   │   ├── run_day31_checks.sh
│   │   ├── run_day32_checks.sh
│   │   ├── run_day32_real_local_test.py
│   │   ├── run_day33_checks.sh
│   │   ├── run_day34_checks.sh
│   │   ├── run_day3_checks.sh
│   │   ├── run_day4_checks.sh
│   │   ├── run_day5_checks.sh
│   │   ├── run_day6_checks.sh
│   │   ├── run_day7_checks.sh
│   │   ├── run_day8_checks.sh
│   │   ├── run_day9_checks.sh
│   │   ├── run_pre_day30_checks.sh
│   │   ├── run_pre_day41_01_checks.sh                           # [MVP-2][MUST] Day 41 Portfolio Management
│   │   ├── seed_local_db.sh
│   │   ├── setup_dev_env.sh
│   │   ├── smoke_test_pre_day30_remote_eda.sh
│   │   ├── stress_test_day30.py
│   │   ├── stress_test_day31.py
│   │   ├── stress_test_day34.py
│   │   ├── sync_pre_day30_evidence_to_repo.sh
│   │   ├── test_skeleton.py
│   │   ├── update_skeleton.py
│   │   ├── validate_day10_outputs.py
│   │   ├── validate_day11_outputs.py
│   │   ├── validate_day12_outputs.py
│   │   ├── validate_day13_outputs.py
│   │   ├── validate_day14_outputs.py
│   │   ├── validate_day15_outputs.py
│   │   ├── validate_day16_outputs.py
│   │   ├── validate_day17_outputs.py
│   │   ├── validate_day9_outputs.py
│   │   ├── validate_openapi_contract.py
│   │   ├── validate_pre_day41_01.py                             # [MVP-2][MUST] Day 41 Portfolio Management
│   │   └── validate_protocol.py
│   ├── governance
│   │   ├── day39_generate_model_card.py                         # [MVP-2][MUST] Day 39 Reproducibility & Governance
│   │   └── generate_schemas.py
│   ├── ml
│   │   ├── capture_environment.py
│   │   ├── generate_hash_ledger.py
│   │   ├── hash_artifact.py
│   │   ├── render_day26_experiment_matrix.py
│   │   ├── seal_test_manifest.py
│   │   └── validate_day26_blueprint.py
│   ├── ops
│   │   ├── backup_db.sh
│   │   ├── export_audit_log.py
│   │   ├── health_check.py
│   │   └── restore_db.sh
│   ├── release
│   │   ├── create_release_manifest.py
│   │   ├── rollback_release.py
│   │   └── verify_release_artifacts.py
│   ├── README.md
│   ├── start_mlflow_local.sh
│   └── validate_day37_evidence.py                               # [MVP-2][MUST] Day 37 Quantitative Metrics
├── security-compliance                                          # [MVP-2][MUST] Day 37 Quantitative Metrics
│   ├── cybersecurity
│   │   ├── sbom
│   │   │   └── sbom-template.json
│   │   ├── penetration-test-plan.md
│   │   ├── threat-model.md
│   │   └── vulnerability-management.md
│   ├── policies
│   │   ├── acceptable-use-policy.md
│   │   ├── access-control-policy.md
│   │   ├── audit-log-policy.md
│   │   ├── backup-retention-policy.md
│   │   ├── data-handling-policy.md
│   │   ├── incident-response-policy.md
│   │   └── password-mfa-policy.md
│   ├── privacy
│   │   ├── consent-forms
│   │   │   ├── clinical-use-consent-template.md
│   │   │   ├── data-sharing-consent-template.md
│   │   │   └── research-use-consent-template.md
│   │   ├── data-processing-inventory.md
│   │   ├── data-subject-request-sop.md
│   │   └── deidentification-sop.md
│   ├── regulatory
│   │   ├── clinical-evaluation-plan.md
│   │   ├── intended-use-and-claims.md
│   │   ├── regulatory-pathway-options.md
│   │   ├── software-lifecycle-procedure.md
│   │   └── standards-mapping.md
│   ├── risk
│   │   ├── clinical-safety-case.md
│   │   ├── hazard-log.csv
│   │   ├── risk-control-matrix.csv
│   │   └── usability-risk-analysis.md
│   └── README.md
├── services
│   ├── api-server
│   │   ├── src
│   │   │   ├── auth
│   │   │   │   ├── jwt.py
│   │   │   │   ├── password_hashing.py
│   │   │   │   ├── policy.py
│   │   │   │   └── rbac.py
│   │   │   ├── db
│   │   │   │   ├── migrations
│   │   │   │   ├── base.py
│   │   │   │   └── session.py
│   │   │   ├── jobs
│   │   │   │   ├── generate_report_job.py
│   │   │   │   ├── run_analysis_job.py
│   │   │   │   └── run_qc_job.py
│   │   │   ├── mock_api
│   │   │   │   ├── day19_app.py
│   │   │   │   ├── day19_models.py
│   │   │   │   ├── day19_store.py
│   │   │   │   ├── day20_app.py
│   │   │   │   ├── day20_models.py
│   │   │   │   ├── day20_store.py
│   │   │   │   ├── day21_app.py
│   │   │   │   ├── day22_app.py
│   │   │   │   ├── day23_app.py
│   │   │   │   └── day24_app.py
│   │   │   ├── models
│   │   │   │   ├── analysis_run.py
│   │   │   │   ├── audit_event.py
│   │   │   │   ├── device.py
│   │   │   │   ├── electrode_config.py
│   │   │   │   ├── feature.py
│   │   │   │   ├── inference_result.py
│   │   │   │   ├── muscle_target.py
│   │   │   │   ├── patient.py
│   │   │   │   ├── protocol.py
│   │   │   │   ├── raw_signal.py
│   │   │   │   ├── report.py
│   │   │   │   ├── review.py
│   │   │   │   └── session.py
│   │   │   ├── repositories
│   │   │   │   ├── analysis_job_repo.py
│   │   │   │   ├── analysis_repo.py
│   │   │   │   ├── audit_repo.py
│   │   │   │   ├── patient_repo.py
│   │   │   │   ├── report_repo.py
│   │   │   │   ├── session_repo.py
│   │   │   │   └── uc1_replay_repo.py
│   │   │   ├── routes
│   │   │   │   ├── admin.py
│   │   │   │   ├── analysis_jobs.py
│   │   │   │   ├── analysis.py
│   │   │   │   ├── audit.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── patients.py
│   │   │   │   ├── quality.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── reviews.py
│   │   │   │   ├── sessions.py
│   │   │   │   ├── signals.py
│   │   │   │   └── uc1_replays.py
│   │   │   ├── schemas
│   │   │   │   ├── analysis_contract.py
│   │   │   │   ├── analysis_job_schema.py
│   │   │   │   ├── analysis_schema.py
│   │   │   │   ├── api_errors.py
│   │   │   │   ├── auth_schema.py
│   │   │   │   ├── day24_review_report_schema.py
│   │   │   │   ├── gesture_schema.py
│   │   │   │   ├── patient_schema.py
│   │   │   │   ├── qc_schema.py
│   │   │   │   ├── report_schema.py
│   │   │   │   ├── review_schema.py
│   │   │   │   ├── session_schema.py
│   │   │   │   ├── signal_schema.py
│   │   │   │   └── uc2_schema.py
│   │   │   ├── services
│   │   │   │   ├── analysis_job_service.py
│   │   │   │   ├── analysis_service.py
│   │   │   │   ├── audit_service.py
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── day24_feedback_adjudication_service.py
│   │   │   │   ├── day24_review_workflow_service.py
│   │   │   │   ├── longitudinal_service.py
│   │   │   │   ├── offline_analysis_runtime.py
│   │   │   │   ├── patient_service.py
│   │   │   │   ├── qc_service.py
│   │   │   │   ├── report_service.py
│   │   │   │   ├── review_service.py
│   │   │   │   ├── signal_service.py
│   │   │   │   └── uc1_replay_service.py
│   │   │   ├── utils
│   │   │   │   ├── error_codes.py
│   │   │   │   ├── file_hash.py
│   │   │   │   ├── logging.py
│   │   │   │   └── time.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   └── main.py
│   │   ├── alembic.ini
│   │   ├── Dockerfile
│   │   └── README.md
│   ├── feature-extraction-service
│   │   ├── configs
│   │   │   ├── features_semg_cv_v0.1.yaml
│   │   │   ├── features_semg_v0.1.yaml
│   │   │   ├── frequency_features_v0.1.yaml
│   │   │   ├── spectral_estimation_v0.1.yaml
│   │   │   ├── trend_features_v0.1.yaml
│   │   │   └── windowing_v0.1.yaml
│   │   ├── src
│   │   │   ├── conduction_velocity.py
│   │   │   ├── extractor.py
│   │   │   ├── feature_config.py
│   │   │   ├── feature_result_models.py
│   │   │   ├── feature_schema.py
│   │   │   ├── feature_version.py
│   │   │   ├── frequency_domain.py
│   │   │   ├── frequency_feature_config.py
│   │   │   ├── frequency_feature_extractor.py
│   │   │   ├── frequency_feature_result_models.py
│   │   │   ├── spectral_config.py
│   │   │   ├── spectral_estimator.py
│   │   │   ├── spectral_extractor.py
│   │   │   ├── spectral_result_models.py
│   │   │   ├── time_domain.py
│   │   │   ├── trend_feature_config.py
│   │   │   ├── trend_feature_extractor.py
│   │   │   ├── trend_feature_result_models.py
│   │   │   ├── trend_features.py
│   │   │   ├── window_config.py
│   │   │   ├── windowing.py
│   │   │   └── window_result_models.py
│   │   ├── DAY10_IMPLEMENTATION_NOTES.md
│   │   ├── DAY11_IMPLEMENTATION_NOTES.md
│   │   ├── DAY8_IMPLEMENTATION_NOTES.md
│   │   ├── DAY9_IMPLEMENTATION_NOTES.md
│   │   └── README.md
│   ├── inference-service
│   │   ├── confidence
│   │   │   └── technical_confidence_v0.1.yaml
│   │   ├── evidence
│   │   │   └── fatigue_evidence_v0.1.yaml
│   │   ├── models
│   │   │   ├── logistic_baseline
│   │   │   │   ├── metrics.json
│   │   │   │   └── model-card.md
│   │   │   ├── random_forest_baseline
│   │   │   │   ├── metrics.json
│   │   │   │   └── model-card.md
│   │   │   └── README.md
│   │   ├── rules
│   │   │   ├── fatigue_rule_v0.1.yaml
│   │   │   ├── fatigue_rule_v0.2.yaml
│   │   │   └── rule_schema.json
│   │   ├── src
│   │   │   ├── abstention.py
│   │   │   ├── classical_ml.py
│   │   │   ├── confidence_config.py
│   │   │   ├── confidence.py
│   │   │   ├── evidence_config.py
│   │   │   ├── evidence_engine.py
│   │   │   ├── evidence_result_models.py
│   │   │   ├── explainability.py
│   │   │   ├── gesture_replay_engine.py
│   │   │   ├── inference.py
│   │   │   ├── inference_result_models.py
│   │   │   ├── model_compatibility.py
│   │   │   ├── result_formatter.py
│   │   │   ├── rule_config.py
│   │   │   ├── rule_engine.py
│   │   │   └── rule_result_models.py
│   │   ├── DAY12_IMPLEMENTATION_NOTES.md
│   │   ├── DAY13_IMPLEMENTATION_NOTES.md
│   │   ├── DAY14_IMPLEMENTATION_NOTES.md
│   │   └── README.md
│   ├── integration-service
│   │   ├── device-adapters
│   │   │   ├── edf-bdf-adapter.py
│   │   │   ├── generic-csv-adapter.py
│   │   │   └── vendor-sdk-adapter-template.py
│   │   ├── ehr
│   │   │   ├── ehr-sync-worker.py
│   │   │   ├── fhir-mapping.md
│   │   │   └── hl7-message-mapping.md
│   │   ├── exports
│   │   │   ├── csv-feature-export.py
│   │   │   ├── parquet-feature-export.py
│   │   │   └── report-batch-export.py
│   │   └── README.md
│   ├── preprocessing-service
│   │   ├── configs
│   │   │   ├── preprocess_v0.1.yaml
│   │   │   └── preprocess_v0.2.yaml
│   │   ├── src
│   │   │   ├── artifact_masking.py
│   │   │   ├── config_schema.py
│   │   │   ├── filters.py
│   │   │   ├── normalization.py
│   │   │   ├── pipeline.py
│   │   │   ├── preprocess_config.py
│   │   │   ├── preprocess_result_models.py
│   │   │   └── resampling.py
│   │   └── README.md
│   ├── quality-gate-service
│   │   ├── configs
│   │   │   ├── qc_v0.1.yaml
│   │   │   └── qc_v0.2.yaml
│   │   ├── src
│   │   │   ├── checks
│   │   │   │   ├── baseline_noise_check.py
│   │   │   │   ├── channel_completeness_check.py
│   │   │   │   ├── clipping_saturation_check.py
│   │   │   │   ├── common.py
│   │   │   │   ├── cv_eligibility_check.py
│   │   │   │   ├── duration_check.py
│   │   │   │   ├── flatline_check.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── motion_artifact_check.py
│   │   │   │   ├── nonfinite_check.py
│   │   │   │   ├── powerline_noise_check.py
│   │   │   │   ├── protocol_compatibility_check.py
│   │   │   │   └── sampling_rate_check.py
│   │   │   ├── config_loader.py
│   │   │   ├── quality_gate.py
│   │   │   ├── reason_codes.py
│   │   │   ├── result_models.py
│   │   │   ├── result_schema.py
│   │   │   └── scoring.py
│   │   ├── DAY5_IMPLEMENTATION_NOTES.md
│   │   └── README.md
│   ├── report-generation-service
│   │   ├── src
│   │   │   ├── chart_renderer.py
│   │   │   ├── day24_report_builder.py
│   │   │   ├── day24_report_hash.py
│   │   │   ├── disclaimer.py
│   │   │   ├── generator.py
│   │   │   ├── render_html.py
│   │   │   ├── render_pdf.py
│   │   │   ├── report_hash.py
│   │   │   └── report_schema.py
│   │   ├── templates
│   │   │   ├── clinical_report_v0.1.html
│   │   │   ├── operational_report_v0.1.html
│   │   │   ├── research_export_summary_v0.1.html
│   │   │   └── technical_report_v0.1.html
│   │   └── README.md
│   └── signal-ingestion-service
│       ├── src
│       │   ├── importers
│       │   │   ├── base_importer.py
│       │   │   ├── csv_importer.py
│       │   │   └── __init__.py
│       │   ├── normalizers
│       │   │   ├── channel_mapper.py
│       │   │   ├── __init__.py
│       │   │   ├── metadata_extractor.py
│       │   │   └── unit_normalizer.py
│       │   ├── validators
│       │   │   ├── file_format_validator.py
│       │   │   ├── __init__.py
│       │   │   └── metadata_validator.py
│       │   └── __init__.py
│       └── README.md
├── tools
│   ├── diagrams
│   │   ├── render_mermaid.sh
│   │   └── render_plantuml.sh
│   ├── lint
│   │   ├── eslint.config.js
│   │   ├── mypy.ini
│   │   └── ruff.toml
│   └── openapi
│       ├── generate_clients.sh
│       └── validate_openapi.sh
├── .vscode
│   └── settings.json
├── CHANGELOG.md
├── CODEOWNERS
├── CONTRIBUTING.md
├── .coverage
├── dataset-inventory-v0.2.csv
├── docker-compose.yml
├── .env
├── .env.example
├── .gitattributes
├── .gitignore
├── json
├── LICENSE
├── Makefile
├── openapi.yaml
├── package.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
├── PRE_DAY41_01_EXECUTION_PLAN.md                               # [MVP-2][MUST] Day 41 Portfolio Management
├── public-vs-site-capability-matrix.csv
├── pyproject.toml
├── pytest.ini
├── README.md
├── README_VI.md
├── requirements.txt
├── update_skeleton.py
└── uv.lock

694 directories, 3670 files

```


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

