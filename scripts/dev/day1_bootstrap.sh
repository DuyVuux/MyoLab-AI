#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-semg-fatigue-platform}"
TODAY="${TODAY:-$(date +%F)}"

mkdir -p "$ROOT"
cd "$ROOT"

write_if_missing() {
  local file="$1"
  local dir
  dir="$(dirname "$file")"
  mkdir -p "$dir"
  if [[ -f "$file" ]]; then
    echo "SKIP existing: $file"
  else
    cat > "$file"
    echo "CREATE: $file"
  fi
}

mkdir -p \
  docs/00-executive \
  docs/01-product/backlog \
  docs/03-architecture/adr \
  docs/07-security-compliance \
  product/ux/copy \
  reports/wording \
  ops/cadence \
  qa-validation/requirements \
  scripts/dev

write_if_missing README.md <<'MD'
# sEMG/MFCV Fatigue Clinical Intelligence Layer

## Positioning
This repository contains an offline-first Clinical Intelligence layer for sEMG/MFCV fatigue evidence. It is designed to work with Motion Lab/Noraxon-style exports, synthetic data, and later validated clinical workflows.

## MVP principles
- Signal quality before AI.
- Explainable rules before black-box models.
- Human-in-the-loop before clinical workflow pilot.
- Abstention before unsafe conclusion.
- MFCV/CV only when electrode geometry and sampling eligibility are confirmed.

## Not intended to be
- A new EMG acquisition device.
- A replacement for Noraxon/myoRESEARCH.
- An automated disease diagnosis system.
- A generic binary fatigue/no-fatigue dashboard.
MD

write_if_missing docs/00-executive/executive-blueprint.md <<'MD'
# Executive Blueprint — v0.1 Draft

## One-line definition
A Clinical Intelligence layer that transforms quality-checked sEMG/MFCV and Motion Lab/Noraxon-compatible data into fatigue evidence, use-case-specific interpretation, longitudinal tracking, and clinician/KTV-reviewed reports.

## Product is
- Signal quality gate for sEMG sessions.
- Fatigue evidence extraction from RMS/MAV/MDF/MNF slopes and optional MFCV/CV when eligible.
- Use-case routing for rehabilitation, post-op, sports medicine, Motion Lab, longitudinal tracking, and return-to-play support.
- Human-in-the-loop report workflow.
- Abstention behavior when data quality or metadata are insufficient.

## Product is not
- Not an EMG hardware product.
- Not a replacement for Noraxon/myoRESEARCH.
- Not an automated disease diagnosis tool.
- Not a fully autonomous treatment or return-to-play decision system.

## Day 1 decision status
- Intended use: DRAFT.
- Product boundary: DRAFT.
- Clinical claims: RESTRICTED.
- Realtime claim: DEMO ONLY / NEAR-REAL-TIME wording preferred.
- MFCV claim: OPTIONAL, only if electrode geometry and sampling are confirmed.

## Next gate
Gate 1 — Product Differentiation passes only if the narrative clearly says “clinical intelligence on top of Motion Lab/Noraxon data,” not “replacement EMG software.”
MD

write_if_missing docs/00-executive/stakeholder-decision-log.md <<'MD'
# Stakeholder Decision Log

| ID | Date | Decision | Options considered | Current decision | Owner mode | Reviewer mode | Status | Follow-up |
|---|---|---|---|---|---|---|---|---|
| D-001 | YYYY-MM-DD | Product positioning | Device / Noraxon replacement / Clinical Intelligence Layer | Clinical Intelligence Layer | Duy | Quân | Draft | Validate with stakeholder |
| D-002 | YYYY-MM-DD | Initial MVP mode | Realtime clinical / near-real-time demo / offline-first | Offline-first + near-real-time demo wording | Duy | Quân | Draft | Confirm with demo narrative |
| D-003 | YYYY-MM-DD | MFCV claim | Always report / optional / remove | Optional only when eligible | Duy | Quân | Draft | Audit electrode geometry |
| D-004 | YYYY-MM-DD | Output wording | Diagnosis / decision support / technical metrics only | Decision-support language with human review | Duy | Quân | Draft | Review report wording |
| D-005 | YYYY-MM-DD | First protocol focus | Upper limb / lower limb / both | TBD Day 2 | Duy | Quân | Open | Choose muscle/protocol |
| D-006 | YYYY-MM-DD | Data source priority | Synthetic / CSV / Noraxon export / C3D/MAT | Synthetic + CSV first; Noraxon audit next | Quân | Duy | Draft | Build audit checklist |
MD

write_if_missing docs/00-executive/assumptions-and-open-questions.md <<'MD'
# Assumptions and Open Questions — Day 1

## Assumptions
| ID | Assumption | Why it matters | Risk if false | Owner mode | Validation plan |
|---|---|---|---|---|---|
| A-001 | MVP starts offline-first using synthetic/CSV/Noraxon export files. | Reduces premature realtime clinical claims. | Demo may feel limited. | Duy | Confirm in demo script. |
| A-002 | MFCV/CV is optional until linear electrode array, inter-electrode distance, orientation, and sampling are confirmed. | Prevents overclaim. | Cannot advertise MFCV in MVP. | Duy | Motion Lab/Noraxon audit. |
| A-003 | Human review is required before final clinical report. | Clinical safety and workflow fit. | Product may look like autonomous diagnosis. | Quân | Report wording review. |
| A-004 | No real patient raw data will be committed to repo. | Privacy/security baseline. | Data governance incident. | Quân | Gitignore + data policy. |

## Open questions for Day 2+
1. Which first protocol should be used: quadriceps isometric 60s, biceps isometric, or repeated squat?
2. Which data format is most likely available from Motion Lab/Noraxon: CSV, TXT, MAT, C3D, or processed report?
3. Is the first pitch aimed at Motion Lab director, rehabilitation clinician, KTV, or executive sponsor?
4. Is return-to-play included in MVP-1 or only in roadmap/demo narrative?
5. What exact wording is acceptable for “fatigue detected,” “review suggested,” and “not enough data”?
MD

write_if_missing docs/01-product/intended-use-statement.md <<'MD'
# Intended Use Statement — v0.1 Draft

## Intended use
The sEMG/MFCV Fatigue Clinical Intelligence Layer is intended to support clinicians and rehabilitation/motion-lab technicians by analyzing quality-checked sEMG-derived fatigue evidence from standardized sessions. The system summarizes signal quality, fatigue-related features, fatigue resistance trends, use-case routing, and clinician-review-ready interpretations for rehabilitation, sports medicine, Motion Lab assessment, longitudinal rehab tracking, and return-to-play support.

## Intended users
- Rehabilitation physician.
- Sports medicine / orthopedic clinician.
- Motion Lab technician.
- Rehabilitation technician.
- Research/clinical AI team during validation.

## Intended data sources
- Synthetic sEMG demo files.
- CSV/TXT sEMG export files.
- Noraxon/myoRESEARCH-compatible exports when available.
- Optional Motion Lab synchronized data when export/sync are confirmed.
- MFCV/CV-related inputs only when electrode geometry and sampling eligibility are confirmed.

## Non-intended use
- Not for automated disease diagnosis.
- Not for autonomous treatment prescription.
- Not for automatic return-to-play clearance.
- Not for replacing clinical judgement, Motion Lab technicians, Noraxon/myoRESEARCH, or existing acquisition workflow.
- Not for reporting MFCV/CV when electrode geometry and sampling eligibility are not confirmed.

## Human-in-the-loop rule
A final clinical-facing report requires review/sign-off by qualified clinical or technical staff. AI/rule output is supporting evidence, not final medical decision.

## Abstention rule
If signal quality, metadata, protocol consistency, or MFCV eligibility is insufficient, the system must return “data not sufficient for analysis” with reason codes rather than forcing a fatigue conclusion.
MD

write_if_missing docs/01-product/product-boundaries.md <<'MD'
# Product Boundaries — v0.1 Draft

## Safety baseline
The product requires human review and uses abstention when data quality, metadata, or MFCV eligibility is insufficient.

## Allowed claims
| Claim | Allowed wording |
|---|---|
| Product category | Clinical Intelligence layer compatible with sEMG/Motion Lab/Noraxon-style data exports. |
| Signal quality | The system checks whether data is sufficient for fatigue evidence extraction. |
| Fatigue evidence | The system extracts fatigue-related evidence such as RMS/MAV/MDF/MNF trends and optional MFCV/CV when eligible. |
| Clinical interpretation | The system supports clinician/KTV review by summarizing evidence in use-case-specific language. |
| Longitudinal tracking | The system can compare sessions only when protocol, muscle, side, and normalization are compatible. |

## Prohibited claims
| Claim | Why prohibited | Safer wording |
|---|---|---|
| “Diagnoses muscle disease” | Overclaim; not the product scope. | “Supports functional fatigue assessment.” |
| “Replaces Noraxon/myoRESEARCH” | Wrong competitive positioning. | “Works on top of Motion Lab/Noraxon-compatible data.” |
| “Automatically decides return-to-play” | Clinical safety risk. | “Provides supporting evidence for return-to-play review.” |
| “Realtime clinical alert is validated” | Not validated at MVP-0. | “Near-real-time demo; offline-first MVP.” |
| “Always computes MFCV” | Needs electrode array/geometry/sampling. | “Computes MFCV only when eligible.” |
MD

write_if_missing docs/01-product/mvp-definition-of-done.md <<'MD'
# MVP Definition of Done — Draft

## MVP-0 Done
- Product boundary and intended use documented.
- Repo skeleton created without real patient raw data.
- Signal import/QC/preprocessing/feature specs drafted.
- Synthetic/golden data plan drafted.
- Output schema contains quality, abstention, fatigue evidence, and human review fields.
- Report wording avoids diagnosis/treatment overclaim.

## Day 1 Done
- Executive blueprint exists.
- Intended use statement exists.
- Product boundaries exist.
- Decision log exists.
- Assumptions/open questions exist.
- Demo wording audit exists.
- Day 1 acceptance criteria exists.
- Self-review notes exist.
MD

write_if_missing docs/01-product/backlog/day1-backlog.md <<'MD'
# Day 1 Backlog

| ID | Task | Owner mode | Reviewer mode | Output | Status |
|---|---|---|---|---|---|
| D1-001 | Draft intended use | Duy | Quân | `docs/01-product/intended-use-statement.md` | Draft |
| D1-002 | Draft product boundaries | Duy | Quân | `docs/01-product/product-boundaries.md` | Draft |
| D1-003 | Bootstrap repo skeleton | Quân | Duy | folders/files created | Draft |
| D1-004 | Create decision log | Quân | Duy | `docs/00-executive/stakeholder-decision-log.md` | Draft |
| D1-005 | Audit demo wording | Quân | Duy | `product/ux/copy/demo-rewrite-notes.md` | Draft |
| D1-006 | Create Day 1 acceptance criteria | Quân | Duy | `qa-validation/requirements/day1-acceptance-criteria.md` | Draft |
MD

write_if_missing docs/03-architecture/high-level-architecture.md <<'MD'
# High-Level Architecture — Day 1 Draft

```text
Motion Lab / Noraxon export / Synthetic CSV
        ↓
Data Ingestion Adapter
        ↓
Session Metadata & Protocol Mapper
        ↓
Signal Quality Gate
        ↓
Preprocessing Pipeline
        ↓
Windowing & Feature Extraction
        ↓
Fatigue Evidence Engine
        ↓
Explainable Rule Engine / Classical ML later
        ↓
Use Case Routing Engine
        ↓
Clinical Interpretation Engine
        ↓
Dashboard / Report / Review Workflow
```

## Day 1 architecture decisions
- Offline-first for MVP-0.
- Near-real-time wording only for demo.
- Rule engine first; classical ML only after usable local labels.
- Quality gate blocks unsafe analysis.
- MFCV/CV module remains optional until eligibility is confirmed.
MD

write_if_missing docs/03-architecture/adr/ADR-0001-clinical-intelligence-not-device.md <<'MD'
# ADR-0001 — Clinical Intelligence Layer, Not an EMG Device

## Status
Draft

## Context
Motion Lab/Noraxon-style systems already cover acquisition and general EMG review. The project should create value through signal quality, fatigue evidence, use-case routing, longitudinal tracking, and clinician/KTV-reviewed interpretation.

## Decision
Position the product as a Clinical Intelligence layer, not hardware and not replacement acquisition software.

## Consequences
- Prioritize import/export compatibility.
- Avoid hardware roadmap in MVP-0.
- Avoid “replacement for Noraxon/myoRESEARCH” wording.
MD

write_if_missing docs/03-architecture/adr/ADR-0002-offline-first-before-realtime.md <<'MD'
# ADR-0002 — Offline-First Before Realtime Clinical Claims

## Status
Draft

## Context
Realtime clinical claims require streaming integration, latency control, safety validation, workflow validation, and human-review design. MVP-0 should prove the pipeline with files first.

## Decision
MVP-0 will process synthetic/CSV/Noraxon-style exports offline. Demo may show near-real-time visualization but must not claim validated realtime clinical operation.

## Consequences
- First pipeline target: file → QC → features → fatigue evidence → JSON/report.
- Realtime is roadmap, not Day 1 build target.
MD

write_if_missing docs/07-security-compliance/medical-disclaimer.md <<'MD'
# Medical Disclaimer — v0.1 Draft

This system provides decision-support information based on quality-checked sEMG-derived fatigue evidence. It does not diagnose disease, prescribe treatment, replace clinical judgement, or independently clear a patient/athlete for return-to-play. Results must be reviewed in the context of the full clinical assessment by qualified professionals.
MD

write_if_missing reports/wording/prohibited-claims.md <<'MD'
# Prohibited Claims — v0.1

Do not use these phrases in demo, report, dashboard, pitch, or API output:

- “Diagnosed fatigue disease.”
- “Automatically stops the exercise.”
- “Patient is cleared for return-to-play.”
- “Replaces Noraxon/myoRESEARCH.”
- “Realtime clinical alert validated.”
- “MFCV is always available.”
- “No fatigue detected” when QC fails.

Preferred alternatives:

- “Fatigue-related evidence observed.”
- “KTV/clinician review suggested.”
- “Supporting evidence for return-to-play review.”
- “Compatible with Motion Lab/Noraxon-style data.”
- “Near-real-time demo; offline-first MVP.”
- “MFCV unavailable because eligibility is not confirmed.”
- “Data not sufficient for analysis.”
MD

write_if_missing reports/wording/clinical-interpretation-phrases.md <<'MD'
# Clinical Interpretation Phrases — v0.1 Draft

## Safe phrases
- “Dữ liệu đủ điều kiện để trích xuất bằng chứng mỏi cơ.”
- “Ghi nhận xu hướng giảm tần số trung vị/trung bình theo thời gian.”
- “Ghi nhận xu hướng tăng biên độ RMS/MAV trong protocol hiện tại.”
- “Kết quả gợi ý cần KTV/bác sĩ xem xét trong bối cảnh lâm sàng tổng thể.”
- “Không đủ dữ liệu để phân tích; đề xuất kiểm tra lại điện cực/protocol và đo lại nếu cần.”

## Avoid
- “Chẩn đoán bệnh.”
- “Bắt buộc dừng tập.”
- “Đủ điều kiện thi đấu.”
- “Không mỏi” khi QC fail hoặc metadata thiếu.
MD

write_if_missing product/ux/copy/demo-rewrite-notes.md <<'MD'
# Demo Rewrite Notes — Day 1

## Current demo risks to fix
| Existing pattern | Risk | Rewrite |
|---|---|---|
| “Realtime clinical fatigue detection” | Premature realtime claim | “Near-real-time demo; offline-first clinical MVP.” |
| “Stop exercise now” | Autonomous treatment action | “KTV/clinician review suggested; consider rest/load adjustment if clinically appropriate.” |
| Synthetic only | May look artificial | Add import/context panel and Noraxon export path placeholder. |
| Fatigue score without QC | Unsafe | Add Signal Quality Gate before score. |
| Binary fatigue/no fatigue | Too generic | Add evidence, use-case routing, clinical report, longitudinal trend. |

## Must-have new screens
1. Import & Session Context.
2. Signal Quality Gate.
3. Fatigue Evidence.
4. Use Case Routing.
5. Clinical Report / Review Workflow.
6. Longitudinal Trend.
MD

write_if_missing ops/cadence/day1-self-review.md <<'MD'
# Day 1 Self-Review

## Duy-mode review
- [ ] Intended use avoids diagnosis/treatment/replacement claims.
- [ ] MFCV/CV is marked optional and eligibility-gated.
- [ ] Architecture starts with data quality and abstention.
- [ ] No realtime clinical claim is made.

## Quân-mode review
- [ ] Repo files are in skeleton-compatible locations.
- [ ] Demo wording avoids overclaim.
- [ ] Day 1 docs are readable for a beginner/stakeholder.
- [ ] Acceptance criteria and next blockers are recorded.

## Joint decision log
| Decision | Final today? | Next action |
|---|---|---|
| Product positioning | Draft | Validate with stakeholder |
| First protocol | No | Choose Day 2 |
| Data source priority | Draft | Audit checklist Day 2 |
| MFCV eligibility | Draft | Motion Lab audit |
MD

write_if_missing qa-validation/requirements/day1-acceptance-criteria.md <<'MD'
# Day 1 Acceptance Criteria

## File-level criteria
- `README.md` exists and states product positioning.
- `docs/00-executive/executive-blueprint.md` exists.
- `docs/01-product/intended-use-statement.md` exists.
- `docs/01-product/product-boundaries.md` exists.
- `docs/00-executive/stakeholder-decision-log.md` exists.
- `docs/00-executive/assumptions-and-open-questions.md` exists.
- `product/ux/copy/demo-rewrite-notes.md` exists.
- `reports/wording/prohibited-claims.md` exists.
- `ops/cadence/day1-self-review.md` exists.

## Content criteria
- No claim that the product replaces Noraxon/myoRESEARCH.
- No autonomous diagnosis/treatment/return-to-play wording.
- Quality gate and abstention are mentioned.
- MFCV/CV is optional and eligibility-gated.
- Human review is required before clinical-facing report.

## Beginner criteria
- Key terms are understandable enough to explain verbally: sEMG, RMS, MAV, MDF, MNF, MFCV/CV, QC, abstention, FRS.
MD

write_if_missing scripts/dev/check_day1_artifacts.py <<'PY'
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
required_files = [
    "README.md",
    "docs/00-executive/executive-blueprint.md",
    "docs/00-executive/stakeholder-decision-log.md",
    "docs/00-executive/assumptions-and-open-questions.md",
    "docs/01-product/intended-use-statement.md",
    "docs/01-product/product-boundaries.md",
    "docs/01-product/mvp-definition-of-done.md",
    "docs/01-product/backlog/day1-backlog.md",
    "docs/03-architecture/high-level-architecture.md",
    "docs/03-architecture/adr/ADR-0001-clinical-intelligence-not-device.md",
    "docs/03-architecture/adr/ADR-0002-offline-first-before-realtime.md",
    "docs/07-security-compliance/medical-disclaimer.md",
    "reports/wording/prohibited-claims.md",
    "reports/wording/clinical-interpretation-phrases.md",
    "product/ux/copy/demo-rewrite-notes.md",
    "ops/cadence/day1-self-review.md",
    "qa-validation/requirements/day1-acceptance-criteria.md",
]

must_include = [
    "Clinical Intelligence",
    "not",
    "quality",
    "abstention",
    "human",
    "MFCV",
]

missing = []
weak_content = []
for rel in required_files:
    path = ROOT / rel
    if not path.exists():
        missing.append(rel)
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if rel in {
        "README.md",
        "docs/00-executive/executive-blueprint.md",
        "docs/01-product/intended-use-statement.md",
        "docs/01-product/product-boundaries.md",
    }:
        absent = [term for term in must_include if term.lower() not in text.lower()]
        if absent:
            weak_content.append((rel, absent))

if missing:
    print("MISSING FILES:")
    for item in missing:
        print(f" - {item}")
if weak_content:
    print("\nWEAK CONTENT:")
    for rel, absent in weak_content:
        print(f" - {rel}: missing terms {absent}")

if missing or weak_content:
    raise SystemExit(1)

print("Day 1 artifact check PASSED.")
print(f"Checked {len(required_files)} required files under: {ROOT}")
PY

chmod +x scripts/dev/check_day1_artifacts.py

echo "\nDay 1 bootstrap finished under: $(pwd)"
echo "Next: python scripts/dev/check_day1_artifacts.py"
