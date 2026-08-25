# UI-I1 Integration Foundation Package

This is an additive canonical overlay for the existing MyoLab-AI monorepo. It does **not** contain a replacement Next.js codebase.

## Scope

- typed auto-data contracts;
- fail-closed runtime validators;
- `AutomationRepository` abstraction;
- real/mock repository boundary;
- safe HTTP problem normalization;
- endpoint verification catalog;
- pipeline job hook;
- live backend route auditor;
- UC1–UC4 preservation contract;
- verification scripts/tests.

## Important

The supplied source material proves the existence of backend route modules and several historical/candidate endpoints, but it does not prove every current live decorator/payload. Therefore the built-in endpoint catalog marks them `CANDIDATE` or `UNAVAILABLE`. `RealAutomationRepository` refuses to call non-`VERIFIED` endpoints.

This is intentional. UI-I2 should only bind actual pages after the live-repo audit has promoted the required endpoint contracts to `VERIFIED`.

## Apply

```bash
rsync -av canonical-repo-overlay/ /path/to/MyoLab-AI/
cd /path/to/MyoLab-AI
bash scripts/dev/verify_ui_i1_foundation.sh .
```

## Expected gate

```text
AUTO_DATA_CONTRACT_READY
```

## UC preservation

No new overlay file is placed under `/uc1`, `/uc2`, `/uc3`, or `/uc4`. Their fatigue/gesture/business logic remains out of scope.
