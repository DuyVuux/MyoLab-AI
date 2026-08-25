# Frontend Golden Demo Map

## Shortest Deterministic Path

Primary path: UC1 deterministic replay plus review-queue evidence pages.

```text
/login
  -> select KTV role
  -> verify skip-to-content keyboard path
/uc1/session/SESSION-GOLDEN-E2E?analysisId=ANALYSIS-GOLDEN-E2E&scenarioId=uc1_golden_correct
  -> see research-only/synthetic/not-validated/human-review badges
  -> start replay
  -> inspect QC/activity/fatigue reason codes
  -> inspect provenance hashes/model/calibration
  -> submit human feedback
/review-queue/CASE-GOLDEN/qc
  -> inspect UNKNOWN != PASS / QC evidence
/review-queue/CASE-GOLDEN/signal
  -> inspect RAW vs PROCESSED identity
/review-queue/CASE-GOLDEN/metrics
  -> inspect unsupported MFCV reason ELECTRODE_GEOMETRY_NOT_VERIFIED
```

## Desired Capability Mapping

| Golden screen | Existing route/component | Maturity |
| --- | --- | --- |
| Overview/session workspace | `/dashboard`, `/sessions`, UC1 workspace | DEMO_READY |
| Quality intelligence | `/sessions/[id]/quality`, `/qc`, `/review-queue/[caseId]/qc` | FUNCTIONAL/PARTIAL |
| Signal explorer | `SignalViewer`, `/review-queue/[caseId]/signal`, UC1 provenance | FUNCTIONAL |
| Metric evidence | `MetricEvidenceCard`, `/review-queue/[caseId]/metrics`, UC2 panels | FUNCTIONAL/PARTIAL |
| Human review | UC1 feedback controls, `/reviews/[caseId]`, `/sessions/[id]/review` | DEMO_READY_WITH_LIMITATIONS |
| Research evidence | UC1 provenance, reports/docs, Phase 7R docs | FUNCTIONAL |

## Determinism

The demo runs with Playwright route mocks and local deterministic fixtures. It does not require internet, private credentials, hospital data, or dataset download.

## Verification

`pnpm --dir apps/web-portal exec playwright test e2e/golden-research-session.spec.ts` passed on Chromium with `PLAYWRIGHT_BASE_URL=http://127.0.0.1:3101` and `PLAYWRIGHT_WEB_SERVER_COMMAND='next dev --port 3101'`.

## Current Status

`PASS` with documented limitations: Chromium-only automated run, no full screenshot matrix, and review-queue evidence subroutes are still lightweight stubs.
