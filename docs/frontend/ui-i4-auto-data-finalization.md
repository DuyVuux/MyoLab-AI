# UI-I4 — Auto-Data Finalization & UI Freeze

## INPUT
- `AUTO_DATA_CONTRACT_READY`
- `AUTO_DATA_INGEST_QC_READY`
- `AUTO_DATA_EVIDENCE_READY`
- existing detailed Next.js UI
- existing UC1–UC4/fatigue use cases preserved

## ACTION
1. Bind existing dashboard to canonical operational counts.
2. Close real browser Noraxon single-CSV path using canonical services.
3. Run final real browser Auto-Data E2E without route interception.
4. Re-run type/build/tests/regressions.
5. Freeze frontend source hashes.

## OUTPUT
- canonical operations summary
- operational dashboard component
- real browser E2E evidence
- final frontend freeze manifest
- final readiness evidence

## PASS CONDITION
`bash scripts/dev/verify_ui_i4_finalization.sh .`

must end with:

`PASS: UI_PORTFOLIO_READY`

## HARD RULES
- no fatigue/clinical KPI in the core dashboard;
- no page.route API mocks in final real browser E2E;
- browser single CSV must reach real quality evidence;
- UI-I3 signal/metric/review/audit semantics remain intact;
- UC1–UC4 regression must remain green;
- no new ML/SSL/research scope;
- no clinical validation claim.
