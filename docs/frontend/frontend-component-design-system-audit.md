# Frontend Component And Design System Audit

## Component Tree

```text
RootLayout
  AuthProvider
    /login
    (authenticated)/layout
      AppShell
        nav/sidebar/mobile header
        page route
          UI primitives
          feature/workflow components
          mock/API clients
```

## UI Primitives

- `Alert`: icon + title + body + optional reason code/action/dismiss. Strong for non-color-only semantics.
- `Badge`: variant-based status/source/review labels. Strong visible text, but static badges use `role="status"` which may be noisy.
- `Button`: variants, sizes, loading/aria-busy, disabled reason title.
- `Card`: reusable surface variants.
- `Input`: base form primitive.

## Tokens

Central tokens exist for:

- colors: primary, fatigue accent, surface, text, borders, semantic states, tiers, sidebar.
- spacing: 4 px to 64 px on an 8 px rhythm.
- type scale/weights/line height.
- radius, shadows, transitions, z-index, shell widths.

Design system status: `PARTIALLY_CENTRALIZED`.

## Fragmentation

- Most mature pages use CSS Modules and tokens.
- Feature files under `src/features/qc-dashboard` use Tailwind-like classes, but Tailwind is not installed. These classes do not produce intended styling.
- Some pages still use inline styles for image treatment and 403 padding.
- Comments and copy still reference "clinical intelligence" and medical-device usability language more strongly than the current research-only boundary allows.

## Color Semantics

Semantic variants include success, warning, error, info, abstention, and neutral. `Alert` and most evidence features combine icon/text/color. Some dashboard state chips rely on badge text plus color; this is acceptable, though labels such as `Pass` need research-only context when adjacent to user/patient language.

## Typography

System UI font stack. Numeric-heavy screens do not consistently use tabular numerals. The design is readable and conservative, but not highly distinctive. This is acceptable for a data/research portal.

## Accessibility Readiness

Strengths:

- Visible global `:focus-visible`.
- Many controls have accessible names.
- Alerts use live regions.
- AppShell navigation uses `aria-current`.

Gaps:

- No skip link.
- No automated axe test.
- Badge live-region role overuse.
- Some custom/stub pages use minimal semantic structure.
- No formal contrast report; token comments claim AA but measured verification is not present.

## Preservation Classification

- KEEP_AS_IS: `Alert`, `Button`, `Card`, UC1 workspace layout, signal utility model, metric evidence model.
- KEEP_WITH_MINOR_POLISH: `Badge`, AppShell visible research-only copy, login copy, dashboard copy.
- KEEP_WITH_INTEGRATION_FIX: Day24 review/report API pages.
- REFACTOR_LOCAL: visible clinical report/sign-off wording on session review/report pages.
- DEPRECATE/REMOVE: none by default.
