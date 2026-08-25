# MyoLab-AI Frontend Architecture As Built

Discovery date: 2026-08-25.

## 1. Stack

- App root: `apps/web-portal`
- Framework: Next.js 14 App Router, React 18, TypeScript.
- Package manager: pnpm workspace (`pnpm-lock.yaml`, `pnpm-workspace.yaml`).
- Icons: `lucide-react`.
- Styling: CSS Modules plus global CSS variables in `src/styles/tokens.css` and `src/styles/global.css`.
- Charting/signal visualization: local SVG/custom React components. No Recharts, D3, Plotly, Canvas, or WebGL dependency in `package.json`.
- State: React local state, React context for mock auth, browser `sessionStorage` for deterministic mock workflow persistence.
- Server-state/cache: no TanStack Query/SWR. Fetch calls are wrapped in local clients and page effects.

## 2. Build/Tooling

- `pnpm --dir apps/web-portal type-check`: PASS.
- `pnpm --dir apps/web-portal build`: PASS, 29 static pages generated and dynamic routes traced.
- `pnpm --dir apps/web-portal exec jest --runInBand`: PASS, 16 tests.
- E2E: Playwright, Chromium only, `apps/web-portal/e2e`.
- Lint: Next ESLint config (`next/core-web-vitals`).

## 3. Directory Architecture

```text
apps/web-portal/
  src/app/                 Next App Router pages and legacy page modules
  src/components/          layout, UI primitives, clinical/review/data-intake widgets
  src/features/            focused Day56-59 features: qc-dashboard, signal-viewer, metric-evidence, review-queue
  src/hooks/               UC1 replay and analysis polling hooks
  src/lib/                 auth, permissions, HTTP clients, latency utilities
  src/schemas/             frontend runtime/domain contract TypeScript modules
  src/services/mock/       deterministic session workflow services
  src/styles/              global styles, tokens, animations
  e2e/                     Playwright regression/stress tests
  tests/                   node/Jest feature tests
```

Actual architecture is mixed: page-oriented Next routes for the main portal, feature-sliced modules for late-stage evidence features, and mock service modules as a browser-side repository.

## 4. Runtime Architecture

```mermaid
flowchart TD
  Root[Next RootLayout] --> Auth[AuthProvider]
  Auth --> Login[/login]
  Auth --> Group[(authenticated layout)]
  Group --> Guard[canAccessRoute + redirect/403 UX]
  Guard --> Shell[AppShell sidebar/mobile header]
  Shell --> Pages[App Router pages]
  Pages --> UI[UI primitives and feature components]
  Pages --> Clients[HTTP clients when NEXT_PUBLIC_API_BASE_URL exists]
  Pages --> MockRepo[MockWorkflowRepository sessionStorage]
```

## 5. Provider Tree

`RootLayout` imports global CSS and wraps all children in `AuthProvider`. The authenticated route group wraps pages in `AppShell` after checking mock auth readiness and route access. No global query, theme, form, or i18n provider exists.

## 6. Router Tree

Routing is filesystem-driven. `src/config/useCaseRoutes.ts` is a canonical route manifest, but it is not the router itself. `AppRouter.tsx` only centralizes compatibility route constants.

## 7. State Architecture

- Auth source of truth: `AuthProvider` plus `sessionStorage` key `myolab-ai.mock-role`.
- Workflow source of truth: `MockWorkflowRepository` plus `sessionStorage` key `myolab_workflow_state`.
- View state: mostly component `useState`; UC2 longitudinal uses URL `scenario`.
- Mutation safety is strongest in UC1 replay: abort controllers, generation guards, idempotency keys, and stale replay checks.

## 8. API Architecture

HTTP clients:

- `HttpUC1ReplayClient`: `/v1/uc1/sessions/{sessionId}/replays`, `/v1/uc1/replays/{replayId}/advance`, `/v1/uc1/replays/{replayId}/feedback`.
- `UC2AssessmentClient`: `/v1/uc2/assessments`, with local mock fallback.
- `ReviewReportClient`: `/v1/review-cases`, `/v1/reports/preview`, `/v1/reports/finalize`, `/v1/reports/{reportId}`.

Most session/intake/QC/report pages use mock browser services directly. Contract validation exists for UC1 replay and selected schema modules; many mock pages trust TypeScript/static fixture shape.

## 9. Domain/Schema Architecture

Frontend schemas are defined under `src/schemas`. They cover sessions, import, mapping, preflight, calibration, quality, analysis, segment, review, report, feedback, UC1 replay, UC2 assessment, and Day56-59 evidence contracts. This is a frontend-owned schema layer, not an imported shared package from backend.

## 10. Component Architecture

Main component families:

- Layout: `AppShell`, `Breadcrumbs`, `RoleGuard`.
- UI primitives: `Alert`, `Badge`, `Button`, `Card`, `Input`.
- Workflow: session/intake/calibration/QC/analysis/review/report components.
- Evidence features: QC dashboard, signal viewer, metric evidence, review queue.
- UC-specific: UC1 replay workspace and UC2 quantitative panels.

## 11. Styling/Design System

Design system is partially centralized. Tokens define color, typography, spacing, radius, transitions, z-index, and layout widths. CSS Modules implement most production pages. Some late feature components contain Tailwind-like utility class strings, but Tailwind is not installed or configured, so those styles are inert.

## 12. Chart/Signal Architecture

Signal visualization uses custom SVG polylines in `SignalViewer.tsx`. `utils.ts` validates window identity, enforces RAW/PROCESSED separation, checks time alignment, converts samples to points, and applies min/max decimation for large series.

## 13. Testing

Tests include Jest/unit tests for UC2 client and signal-viewer utilities, feature stress tests, and Playwright E2E for UC1/UC2/review/report workflows. No axe/accessibility package, visual regression baseline, Firefox/WebKit Playwright projects, or formal performance budget exists.

## 14. Deployment

Next production build succeeds. `apps/web-portal/Dockerfile` exists. Build output first-load JS is roughly 87-103 kB by route.

## 15. Current Strengths

- Strong deterministic demo posture, especially UC1.
- Clear research-only guardrails in UC1, QC, signal, and metric evidence features.
- Lightweight dependency surface.
- Good token foundation and reusable primitives.
- Build and type-check are green.

## 16. Technical Debt

- Visible clinical-use language conflicts with Phase 7R research-only claim boundary.
- Canonical route manifest diverges from filesystem routes.
- Mixed schema ownership; no shared backend contract package.
- No server-state cache/deduplication layer.
- Tailwind-like classes exist without Tailwind.
- Accessibility and performance verification are mostly manual or implicit.
