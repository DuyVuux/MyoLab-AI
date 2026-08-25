# UI-I1 — Automation Integration Foundation

## Objective

Introduce a typed, fail-closed boundary between the mature Next.js frontend and the automatic data pipeline without rewriting existing pages or changing UC1–UC4 behavior.

## INPUT

- Existing `apps/web-portal` Next.js 14 application.
- Existing mock/sessionStorage workflows.
- Existing API server route modules.
- Existing Phase 7R research-only claim boundary.

## ACTION

1. Add domain-neutral automation contracts.
2. Add runtime payload validation for scientific invariants.
3. Add `AutomationRepository` as the UI data boundary.
4. Add Real/Mock repository implementations.
5. Add an endpoint verification catalog; candidate routes cannot be called in real mode.
6. Add shared safe HTTP problem handling.
7. Add a shared pipeline-job polling hook.
8. Add live-repo backend route discovery.
9. Add preservation contract for UC1–UC4.

## OUTPUT

- `AUTO_DATA_CONTRACT_READY` when live backend route/schema evidence has been audited and all verification commands pass.

## VERIFICATION

```bash
python scripts/dev/audit_ui_i1_backend_contracts.py .
python -m pytest qa-validation/automated-tests/test_ui_i1_integration_foundation.py -q
pnpm --dir apps/web-portal type-check
pnpm --dir apps/web-portal build
pnpm --dir apps/web-portal exec jest --runInBand
```

## PASS CONDITION

- Existing frontend baseline remains green.
- No UC1–UC4 behavior files are intentionally changed by this overlay.
- New automation contracts compile.
- Scientific validation tests pass.
- Backend route audit finds actual API route modules.
- Any endpoint used in `real` mode is explicitly VERIFIED from live repo evidence.

## FAIL/BLOCK CONDITION

- Existing UI regression.
- Fatigue/use-case logic changed.
- Candidate endpoint treated as verified.
- Processed signal accepted without processing manifest.
- Unsupported metric represented as numeric zero instead of `null + reason`.
- Raw backend error text is surfaced to the UI.
