# Phase 6R Leakage Remediation & Continuation Execution Plan

## 1. Scope
Re-audit leakage safety and contextual claim boundaries on the live repository.

## 2. Step Sequence
1. Run evidence-based leakage auditor (`phase6r_leakage.py`).
2. Run context-aware claim auditor (`phase6r_claims.py`).
3. Evaluate starting ML decision and representation research question configuration.
4. If leakage PASS, claims PASS, and decision is ML_NO_GO with no distinct question, finalize M6-R as `RESEARCH_ML_NOT_JUSTIFIED`.
