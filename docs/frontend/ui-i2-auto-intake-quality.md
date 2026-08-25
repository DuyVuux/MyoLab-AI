# UI-I2 — Automated Intake + Quality Integration

## Objective

Turn the existing session/intake/QC UI from mock/sessionStorage-centric behavior
into a real, fail-closed Auto-Data path while preserving UC1–UC4 and fatigue use cases.

## Critical path

```text
Noraxon source
  -> hash/provenance
  -> format detection
  -> parse/canonicalize
  -> preflight
  -> auto mapping
  -> mapping exception only when needed
  -> QC
  -> READY / REVIEW_REQUIRED / BLOCKED
```

## Important boundary

UI-I2 does not duplicate the ingestion or QC engines. It provides:

1. frontend contracts and consumers;
2. a FastAPI adapter boundary;
3. explicit backend binding audit;
4. route contract promotion;
5. fail-closed verification.

The live integration agent must bind `AutoDataBackend` to canonical repository
services if verified routes do not already exist.

## INPUT

- UI-I1 = `AUTO_DATA_CONTRACT_READY`
- existing Next.js portal
- existing ingestion/QC cores
- existing analysis job API
- existing UC1–UC4 preserved

## OUTPUT

- real-mode endpoint catalog for UI-I2 critical routes;
- automated intake workspace;
- preflight/mapping/QC contracts;
- API adapter boundary;
- targeted tests;
- one gate verifier.

## PASS CONDITION

`bash scripts/dev/verify_ui_i2_auto_intake_quality.sh .`

must end with:

```text
PASS: AUTO_DATA_INGEST_QC_READY
```

A build/test PASS while backend contracts remain unverified is NOT enough.

## FAIL/BLOCK CONDITIONS

- backend binding missing;
- route contract missing;
- upload/import response cannot preserve source hash;
- preflight FAIL can proceed;
- unresolved mapping silently auto-advances;
- QC FAIL treated as downstream success;
- protected UC regression.

## Additional final gate

Route existence is insufficient. `ui-i2-live-backend-binding.json` must PASS and prove a real-mode smoke against canonical services, not a demo/fake backend.
