# sEMG/MFCV Fatigue Clinical Intelligence Layer

## Positioning
This repository contains an offline-first Clinical Intelligence layer for sEMG/MFCV fatigue evidence. It works on top of Motion Lab/Noraxon-style exports, synthetic data, and later validated clinical workflows. It is not an EMG acquisition device and not a replacement for Noraxon/myoRESEARCH.

## MVP principles
- Signal quality before AI or fatigue inference.
- Explainable rules before black-box models.
- Human review before any clinical-facing report.
- Abstention before unsafe or unsupported conclusions.
- MFCV/CV only when electrode geometry, channel ordering, sampling rate, and protocol eligibility are confirmed.

## What the product does
- Imports synthetic or exported sEMG session files.
- Validates metadata, protocol context, and signal quality.
- Extracts fatigue-related features such as RMS, MAV, MDF, MNF, slopes, and optional MFCV/CV when eligible.
- Produces structured evidence for technical and clinical review.
- Generates conservative report wording with limitations and reason codes.

## What the product does not do
- Not direct device control.
- Not autonomous diagnosis.
- Not automated treatment prescription.
- Not automatic return-to-play clearance.
- Not clinical-grade realtime alerting in MVP-0.
- Not storage of real patient raw signal in this repository.

## Day 1 status
Day 1 establishes the product boundary, intended use, safety language, quality gate, abstention behavior, and human-in-the-loop rule for MVP-0.

## Day 2 status
Day 2 establishes the data import contract (Generic CSV + JSON sidecar manifest) and the first versioned clinical protocol (`quad-isometric-60s`). It implements a multi-layer signal validation pipeline and quality gate (L0-L4) to explicitly block invalid data and separate basic sEMG eligibility from advanced MFCV analysis.

## Day 3 status
Day 3 implements the generic CSV ingestion pipeline and the canonical normalized signal contract (`NormalizedSignal`). It enforces read-only arrays after construction, strips raw data from the output JSON summary, and verifies file formats, metadata, and deterministic source hashing before moving to downstream processing.

## Day 4 status
Day 4 implements the Signal Quality Gate (QC) module to evaluate signals against invalidation criteria like Flatline, Clipping, Powerline Noise, and Motion Artifacts. It finalizes the data integration layer and implements a fail-fast abstention policy for unsafe data.

## Day 5 status
Day 5 builds the core signal preprocessing pipeline and service orchestration. It implements a multi-stage preprocessing flow including band-pass and dynamic notch filtering, integrating directly with the QC Gate to dynamically apply noise removal only when specific noise flags are present.

## Day 6 status
Day 6 focuses on the empirical verification of the multi-frequency signal preprocessing pipeline. It validates filter implementations using a deterministic sample array against theoretical expectations for spectral leakage and frequency response, finalizing the preprocessing verification work.

## Day 7 status
Day 7 implements protocol-aligned segmentation and windowing logic. It enforces strict alignment between clinical protocols and feature extraction configurations, explicitly rejecting execution on configuration mismatches.

## Day 8 status
Day 8 delivers the time-domain feature extraction module. It implements deterministic RMS and MAV feature extraction logic, associated schema definitions, and validation reports to ensure mathematical correctness.

## Day 9 status
Day 9 implements the spectral estimation pipeline using Welch's method. It establishes the robust calculation of Power Spectral Density (PSD) and handles frequency resolution bounds according to clinical protocols.

## Day 10 status
Day 10 introduces the frequency-domain feature extraction. It computes Median Frequency (MDF) and Mean Frequency (MNF) from the PSD, implementing standardized mathematical formulas and strict validation schemas.

## Day 11 status
Day 11 implements the Trend Feature extraction module. It calculates the linear regression slopes for RMS, MAV, MDF, and MNF over time windows. It strictly enforces a descriptive-only approach, stripping inferential statistics (like p-values or confidence intervals) to prevent premature clinical conclusions.

## Day 12 status
Day 12 implements the Fatigue Evidence Engine (`FatigueEvidenceEngine`). It transforms time, frequency, and trend metrics into structured evidence objects (`FatigueEvidenceResult v0.1`), explicitly separating observation/evidence from classification and clinical decision.

## Day 13 status
Day 13 implements the Explainable Rule Engine (`ExplainableRuleEngine`). It evaluates structured fatigue evidence against versioned rule mappings to produce deterministic rule results (`FatigueRuleResult v0.1`), multi-channel consensus, decision basis, counterevidence, and failure abstention.

## Day 14 status
Day 14 implements Engineering Confidence calculation (`EngineeringConfidenceCalculator`) and safety guardrails (`WordingGuard`). It rates internal pipeline quality, constructs explainability summaries, and strictly blocks unsafe or overclaiming wording.

## Day 15 status
Day 15 orchestrates the complete offline analysis pipeline (`run_offline_analysis.py`). It integrates Days 1–14 into an offline executable that produces 11 stage artifact files, provenance metadata, SHA-256 source hashing, and an offline analysis package.

## Day 16 status
Day 16 delivers Golden Regression & Analytical Validation (`day16-mvp0-regression-report.md`). It validates pipeline stability across a matrix of synthetic fixtures, locks safety behavior, and freezes baseline `mvp0_baseline_v0.1.json`.

## Day 17 status
Day 17 implements the Canonical Output Schema (`SessionAnalysisSummary v0.1`) and OpenAPI contract (`openapi.yaml`). It establishes a stable, versioned contract interface between offline analysis packages and downstream backend/frontend consumers.

## Day 18 status
Day 18 implements the UI/UX & Continuous Audit Frontend (`apps/web-portal`) using Next.js 14 App Router, TypeScript strict mode, and WCAG 2.2 AA accessibility standards. It features 4 Use Case workflows, human-in-the-loop clinical review sign-off, ML adjudication, data quality issue tracking, and an automated Playwright E2E spec suite with a 100/100 PASS audit verdict.

### 🚀 Hướng dẫn khởi chạy UI (Running the UI Portal)

#### Prerequisites
- Node.js >= 18.0.0
- npm or pnpm

#### Running Development Server
From the project root:
```bash
npm --prefix apps/web-portal run dev
```
Or directly inside the `apps/web-portal` directory:
```bash
cd apps/web-portal && npm run dev
```
Open [http://localhost:3100](http://localhost:3100) in your browser.

#### Running Production Build
From the project root:
```bash
# Build Next.js application
npm --prefix apps/web-portal run build

# Start Production Server
npm --prefix apps/web-portal run start
```
Open [http://localhost:3100](http://localhost:3100) in your browser.

#### Static Type-Check & Linting
```bash
npm --prefix apps/web-portal run type-check
npm --prefix apps/web-portal run lint
```

#### Demo User Roles & Credentials
When accessing the Login page (`/login`), click any quick-login persona:
- **Doctor (Bác sĩ):** Full clinical review sign-off & report export (`/sessions/[id]/review`).
- **Technician (KTV):** Session creation, file import, channel mapping, QC & Analysis run.
- **Researcher (Trọng tài ML):** Label feedback inbox & ML adjudication (`/feedback/inbox`).
- **Patient (Bệnh nhân):** Gesture biofeedback interface (`/uc1/session/[id]`).

