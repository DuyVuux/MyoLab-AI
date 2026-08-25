# Frontend Accessibility And Human Factors Audit

## WCAG 2.2 AA Readiness Assessment

This is an evidence-based readiness assessment, not a compliance claim.

| Criterion/reference | Location | Evidence | Severity | Affected users | Remediation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| Bypass blocks | AppShell/global layout | No skip link found | P2 | keyboard/screen-reader users | Add skip-to-content link targeting main content | keyboard smoke |
| Focus visible | global CSS | `:focus-visible` 3px outline exists | PASS | keyboard users | keep | manual keyboard |
| Info not color only | Alert/evidence features | alerts use icon + text + reason code | PASS_WITH_LIMITATIONS | color-blind users | keep; audit all badges | component review |
| Status semantics | `Badge` | all badges use `role=status`, including static labels | P3 | screen-reader users | use status role only for dynamic status updates | component test/manual |
| Accessible names | AppShell/Login/UC1 | nav labels, button names, form labels mostly present | PASS_WITH_LIMITATIONS | screen-reader users | audit stub routes | Playwright queries |
| Reflow/responsive | AppShell | mobile sidebar exists; not yet manually verified at 320/375/768/1024/1280/1440/1920 | P2 | mobile users | screenshot smoke at representative widths | Playwright screenshots |
| Dialogs | current inventory | no major modal/dialog primitives found | NOT_APPLICABLE | keyboard users | if added, implement focus trap/escape/restore | component test |
| Automated a11y | test setup | no axe dependency/config | P2 | all assistive tech users | add lightweight smoke if dependency allowed | axe/Playwright |

## Critical Workflows

| Task | Possible use error | Existing protection | Gap | Severity |
| --- | --- | --- | --- | --- |
| Start UC1 replay | User may treat result as live clinical output | Requires query provenance; warning banner; synthetic/model badges | no final golden E2E spanning evidence pages | P1 |
| Advance replay | Double submit/stale replay | mutation lock, disabled loading, expected index/revision | no visible retry button after error | P2 |
| Submit feedback | Feedback attached to wrong window | expected window/revision, server receipt validation, idempotency | no persistent audit trail visible in UC1 page | P2 |
| Clinical/human sign-off | User may believe report is clinically valid | Some disclaimers exist | visible labels say clinical conclusion/report/sign-off | P0 |
| Override QC fail | User may override into "normal" claim | guard blocks "bình thường" on QC fail | override option copy references diagnosis/clinical history | P0 |
| Finalize report | User may treat finalized document as medical report | report hash/watermark | button and title imply clinical release | P0 |
| Reprocess/remeasure | User may not understand consequence | Day24 request_remeasurement exists | primary session workflow lacks explicit recovery audit UI | P2 |

## Human Factors Summary

The UC1 replay workflow is the safest and clearest implementation: it fails closed, carries reason codes, and prevents patient-role feedback actions. The older session review/report pages carry the highest use-error risk because they present a clinical sign-off flow inside a project that is currently research-only.
