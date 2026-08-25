# Frontend Test Quality Audit

## Test Inventory

- Unit/component: Jest with jsdom.
- Current Jest passing baseline: 2 suites, 16 tests.
- E2E: Playwright Chromium only.
- Feature stress tests: QC dashboard, signal viewer, metric evidence, cross-feature.
- No visual regression snapshots.
- No axe/accessibility automated checks.
- No Firefox/WebKit Playwright projects.
- No contract test suite against a live backend in this audit.

## Strengths

- UC1 replay has unusually strong E2E coverage for fail-closed behavior, no-activity vs API failure, unsafe payload rejection, feedback provenance, and idempotency.
- Signal viewer utilities have unit tests around scientific safety semantics.
- UC2 client tests cover mock fallback and API success.
- Build and type-check pass.

## Gaps

| Gap | Severity | Evidence | Recommended action |
| --- | --- | --- | --- |
| No single golden demo E2E across QC, signal, metric, review, and provenance | P1 | existing tests are day-specific | add `golden-research-session.spec.ts` |
| Playwright browser matrix is Chromium-only | P2 | `playwright.config.ts` projects | document limitation or add browsers later |
| No automated accessibility smoke | P2 | no axe dependency/config | add keyboard smoke first; axe later if dependency accepted |
| Cross-feature stress test references `/dashboard/exceptions`, not a live route | P2 | Day59 spec | update or quarantine |
| Some feature tests live outside Jest `testMatch` | P2 | Jest only matches `src/**/*.test` | decide whether to include `tests/**/*.test` |

## Verification Baseline

- TypeScript: PASS.
- Production build: PASS.
- Jest: PASS.
