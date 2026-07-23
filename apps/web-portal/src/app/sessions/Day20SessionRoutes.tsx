/** Next.js App Router dùng filesystem routing; manifest này phục vụ contract/audit. */
export const DAY20_SESSION_ROUTES = [
  "/sessions/new",
  "/sessions/:sessionId/context",
  "/sessions/:sessionId/data-source",
  "/sessions/:sessionId/import",
  "/sessions/:sessionId/mapping",
  "/sessions/:sessionId/preflight",
  "/sessions/:sessionId/calibration",
  "/sessions/:sessionId/quality",
  "/sessions/:sessionId/analysis",
] as const;
