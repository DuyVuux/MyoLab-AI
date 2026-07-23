/**
 * Next.js App Router integration manifest for Day 19.
 *
 * Routing remains filesystem-driven. This module centralizes compatibility
 * redirects and gives contract tests one framework-neutral integration point.
 */
import { COMPATIBILITY_REDIRECTS, ROUTES } from '@/config/useCaseRoutes';

export const DAY19_FOUNDATION_ROUTES = [
  ROUTES.DASHBOARD,
  ROUTES.USE_CASES,
  ROUTES.SESSIONS,
  ROUTES.ANALYSES,
  ROUTES.FEEDBACK_INBOX,
  ROUTES.UC3_FEASIBILITY,
  ROUTES.UC4_FEASIBILITY,
] as const;

export function resolveCompatibilityRoute(pathname: string): string {
  return COMPATIBILITY_REDIRECTS[pathname] ?? pathname;
}
