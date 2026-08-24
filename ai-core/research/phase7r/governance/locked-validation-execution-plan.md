# Phase 7R Locked Validation Execution Plan

## Objective
Freeze and execute final research validation without tuning on locked outcomes.

## STEP 1 — Phase entry
**INPUT:** M6-R, Gate F-R, Phase 6R leakage/claim audits, Phase 6R handoff.  
**ACTION:** Verify `RESEARCH_ML_NOT_JUSTIFIED`, leakage PASS, claims PASS, ML OFF.  
**OUTPUT:** `qa-validation/evidence/phase7r-entry-preflight.json`.  
**PASS:** all critical upstream conditions resolve.  
**BLOCK:** missing/conflicting evidence.

## STEP 2 — Locked evaluation freeze
**INPUT:** public/synthetic evidence manifests, frozen splits/configs/contracts.  
**ACTION:** hash eligible evidence/config/split artifacts without inspecting outcomes for tuning.  
**OUTPUT:** `qa-validation/evidence/final-locked-evaluation-cohort-v1.0.yaml` and lock JSON.  
**PASS:** lock set non-empty, hashes resolve, no mutable/forbidden path.  
**BLOCK:** missing source/split/config identity.

## STEP 3 — Parser / integrity final validation
**INPUT:** locked research shapes + synthetic corruption fixtures.  
**ACTION:** run parser/integrity regression and fail-closed tests.  
**OUTPUT:** `qa-validation/validation-reports/final-parser-integrity-validation-v1.0.md`.  
**PASS:** no silent parser success on invalid data.

## STEP 4 — QC final research evaluation
**INPUT:** locked synthetic/public evidence with valid evidence tiers.  
**ACTION:** run frozen QC only; stratify by evidence tier/domain; no threshold update.  
**OUTPUT:** `qa-validation/validation-reports/final-qc-locked-evaluation-v1.0.md`.  
**PASS:** results trace to fixed config/splits; unsupported metrics omitted.

## STEP 5 — Processing/metric final validation
**INPUT:** frozen processing/metric engine + locked eligible windows.  
**ACTION:** known-answer, reproducibility, eligibility/null+reason and provenance replay.  
**OUTPUT:** `qa-validation/validation-reports/final-processing-metric-validation-v1.0.md`.  
**PASS:** core metrics reproducible within declared tolerance.

## STEP 6 — Workflow safety final campaign
**INPUT:** review state machine, RBAC, audit/event store, evidence bundle.  
**ACTION:** model/property tests and failure injection.  
**OUTPUT:** `qa-validation/validation-reports/final-workflow-safety-v1.0.md`.  
**PASS:** all critical invariants PASS; no final-looking false success.

## STEP 7 — Non-clinical workflow evidence
**INPUT:** event store/workbench and volunteer technical reviewers when available.  
**ACTION:** measure scripted task durations/process variants. If no participants, execute deterministic process simulation only.  
**OUTPUT:** `clinical/studies/nonclinical-time-on-task-v1.0.md`, process-mining report/CSV.  
**PASS:** evidence correctly labeled `NON_CLINICAL_REVIEW` or `SIMULATED_WORKFLOW_ONLY`.

## STEP 8 — Consolidated validation report
**INPUT:** validated evidence from previous steps.  
**ACTION:** aggregate only supported KPIs with denominators and source references.  
**OUTPUT:** `docs/00-executive/M7-R-final-research-validation-report.md`, `ai-core/metrics/final-kpi-snapshot-v1.0.json`.  
**BLOCK:** any estimated/unsupported KPI.

## STEP 9 — Documentation/release hardening
**INPUT:** frozen code/docs/evidence.  
**ACTION:** public redaction, quick-start, deterministic demo, security/integrity scans, clean-room reproduction.  
**OUTPUT:** portfolio docs, runbook, release manifest, hashes.  
**PASS:** fresh environment can reproduce documented core demo with ML OFF.

## STEP 10 — Final-R / M7-R
**INPUT:** all prior evidence.  
**ACTION:** choose exactly one final status.  
**OUTPUT:** Final-R decision + M7-R release milestone.  
**PASS:** `PORTFOLIO_RESEARCH_READY` only when all critical gates PASS.  
**LIMITED:** `READY_WITH_LIMITATIONS` for non-critical gaps.  
**BLOCK:** safety/provenance/reproducibility/confidentiality/claim failure.
