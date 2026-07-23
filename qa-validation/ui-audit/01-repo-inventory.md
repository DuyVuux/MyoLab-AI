# DANH MỤC TÀI NGUYÊN REPOSITORY (REPO INVENTORY)

**Target App:** `apps/web-portal`  
**Framework:** Next.js 14.2.15 (App Router, React 18.3.1, TypeScript 5.6.3)  

---

## 1. CẤU TRÚC THƯ MỤC VÀ TỆP TIN CHÍNH

### Config & Environment
- `package.json` / `apps/web-portal/package.json`
- `tsconfig.json` / `apps/web-portal/tsconfig.json`
- `apps/web-portal/.eslintrc.json`
- `apps/web-portal/next.config.js`
- `apps/web-portal/src/config/featureFlags.ts`
- `apps/web-portal/src/config/useCaseRoutes.ts`

### Domain Schemas (`src/schemas/`)
- `session.ts` / `session.schema.ts` — Workflow session & context schemas
- `import.ts` — Import records & file integrity verification
- `mapping.ts` — Channel to muscle/electrode placement mapping
- `preflight.ts` — Signal validation & quality checks
- `calibration.ts` — MVC & baseline calibration wizard schemas
- `quality.ts` / `qc.schema.ts` — QC verdicts & structured acknowledgement reasons
- `analysis.ts` — Signal analysis job & engineering output
- `segment.ts` — Signal segment traceability contract
- `review.ts` — Technical & Clinical review sign-off & override policies
- `report.ts` — Report document lifecycle & watermarking
- `feedback.ts` — Feedback event & ML adjudication schemas
- `issue.ts` — Data quality issues tracking schema
- `rbac.ts` — Role permission matrix definition

### Services Layer (`src/services/mock/`)
- `MockWorkflowRepository.ts` — Central state persistence via `sessionStorage`
- `MockSessionService.ts` — Session creation & context management
- `MockImportService.ts` — File import & Web Crypto SHA-256 calculation
- `MockSignalWorkflowService.ts` — Preflight, QC, and Analysis processing pipeline
- `MockCalibrationService.ts` — Calibration wizard repetitions & MVC calculation
- `MockAnalysisService.ts` — Feature extraction & confidence rating
- `fixtures.ts` — Standardized clinical signal fixtures & test datasets

### UI & Layout Components (`src/components/`)
- `layout/AppShell.tsx` — Main application shell with navigation bar & user menu
- `layout/Breadcrumbs.tsx` — Accessible breadcrumb navigation component
- `auth/RoleGuard.tsx` — Role-based access control guard component
- `ui/Button.tsx`, `Card.tsx`, `Input.tsx`, `Badge.tsx`, `Alert.tsx` — Core atomic UI design system
- `charts/SignalPreviewChart.tsx` — Waveform preview visualization component
- `charts/FeatureTrendChart.tsx` — Time-series feature trend chart component
- `charts/LongitudinalTrendChart.tsx` — Multi-session progress tracking chart
- `charts/QualityTimeline.tsx` — Signal quality timeline visualization
- `forms/SessionForm.tsx`, `PatientForm.tsx`, `SignalUploadForm.tsx`, `ReviewSignoffForm.tsx` — Form components
- `clinical/FatigueStatusBadge.tsx`, `ConfidenceIndicator.tsx`, `DisclaimerPanel.tsx`, `ReviewChecklist.tsx` — Clinical domain UI components

---

## 2. DANH MỤC THỬ NGHIỆM TỰ ĐỘNG (AUTOMATED TEST INVENTORY)

| Loại Test | Số lượng | Trạng thái | Ghi chú |
|---|---|---|---|
| Unit Tests (`*.test.ts`) | 0 | **MISSING** | Chưa tạo file unit test nào cho các service/schema |
| Component Tests (`*.test.tsx`) | 0 | **MISSING** | Chưa tạo component test cho UI components |
| Playwright E2E (`*.spec.ts`) | 0 | **MISSING** | Chưa tạo kịch bản E2E kiểm thử luồng người dùng |

---

## 3. THỐNG KÊ STATIC CODE CHECKS

- **TypeScript compilation (`npx tsc --noEmit`):** 0 errors.
- **ESLint execution (`npx next lint`):** 0 warnings, 0 errors.
- **Next.js Production Build (`npx next build`):** 22 static pages generated successfully, 1 import warning detected (`getStore` in `uc2/longitudinal/[subjectRef]/page.tsx`).
