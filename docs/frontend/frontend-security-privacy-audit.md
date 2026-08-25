# Frontend Security Privacy Audit

ASVS-inspired mapping only; no certification claim.

| Control area | Current implementation | Evidence | Gap | Risk | Remediation |
| --- | --- | --- | --- | --- | --- |
| Authentication | mock role selection | `AuthProvider`, `sessionStorage` role | no real auth | expected for prototype; unsafe if deployed as real auth | keep noindex; document UX-only guard |
| Authorization UX | route/action guards | `canAccessRoute`, `RoleGuard`, permission matrices | route maps diverge (`doctor` vs `physician` in one config) | inconsistent UI access | consolidate before real API integration |
| Token storage | none found | no JWT/localStorage tokens | no issue | low | keep |
| Browser storage | mock workflow metadata in `sessionStorage` | `MockWorkflowRepository` | names/subject refs can persist in browser session | privacy confusion | keep de-identified subject refs and no raw signals |
| XSS | React escaping | no `dangerouslySetInnerHTML` found | no sanitizer for future rich text | low current risk | avoid raw HTML; add sanitizer only when needed |
| URL injection | dynamic links use route params and encodeURIComponent in clients | clients encode API path params | some anchor hashes from ids | low | keep encoded API params |
| Error disclosure | some clients display raw HTTP text | `ReviewReportClient` errors | may expose backend detail | P2 | map problem details to safe messages |
| CSRF | frontend assumes JSON API | no cookie auth visible | unknown for real deployment | P2/P1 when real auth exists | backend-owned CSRF strategy |
| Clickjacking/CSP | Next config has no explicit headers | `next.config.js` | no CSP/frame headers | P2 for hosted demo | add deployment headers if public |
| Dependency risk | small dependency set | Next/React/lucide/Jest/Playwright | no npm audit captured | unknown | run dependency scanning in CI |
| Source maps | default Next build | no explicit production sourcemaps | likely not exposed | low | keep default unless needed |

## Privacy Boundary

Visible demo data uses subject refs and mock names. No raw signal arrays are persisted by `MockWorkflowRepository`. Login/admin pages include realistic Vietnamese names; for public portfolio deployment, prefer role/persona labels or de-identified users.
