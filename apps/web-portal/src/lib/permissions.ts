/**
 * MyoLab-AI Permission Matrix
 * RBAC per Section 14 of the UI/UX spec
 *
 * Role guard applies at BOTH route and action level — not just menu hiding.
 */
import type { UserRole } from './auth';

export type PermissionAction =
  | 'session.create'
  | 'session.upload_raw'
  | 'session.map_channel'
  | 'session.run_qc'
  | 'session.run_analysis'
  | 'session.acknowledge_qc_warning'
  | 'session.override_qc_fail'
  | 'review.technical'
  | 'review.clinical_signoff'
  | 'feedback.adjudicate_training'
  | 'data.export_training'
  | 'data.delete_raw'
  | 'audit.view';

type PermissionValue = 'yes' | 'no' | 'conditional' | 'limited' | 'view_only' | 'config';

const PERMISSION_MATRIX: Record<PermissionAction, Record<UserRole, PermissionValue>> = {
  'session.create':               { ktv: 'yes', doctor: 'conditional', researcher: 'no',          patient: 'no', admin: 'config' },
  'session.upload_raw':           { ktv: 'yes', doctor: 'conditional', researcher: 'no',          patient: 'no', admin: 'no' },
  'session.map_channel':          { ktv: 'yes', doctor: 'view_only',   researcher: 'no',          patient: 'no', admin: 'config' },
  'session.run_qc':               { ktv: 'yes', doctor: 'conditional', researcher: 'conditional', patient: 'no', admin: 'no' },
  'session.run_analysis':         { ktv: 'yes', doctor: 'conditional', researcher: 'conditional', patient: 'no', admin: 'no' },
  'session.acknowledge_qc_warning': { ktv: 'yes', doctor: 'yes',      researcher: 'no',          patient: 'no', admin: 'no' },
  'session.override_qc_fail':     { ktv: 'no',  doctor: 'conditional', researcher: 'no',          patient: 'no', admin: 'no' },
  'review.technical':             { ktv: 'yes', doctor: 'yes',         researcher: 'no',          patient: 'no', admin: 'no' },
  'review.clinical_signoff':      { ktv: 'no',  doctor: 'yes',         researcher: 'no',          patient: 'no', admin: 'no' },
  'feedback.adjudicate_training': { ktv: 'limited', doctor: 'conditional', researcher: 'conditional', patient: 'no', admin: 'config' },
  'data.export_training':         { ktv: 'no',  doctor: 'no',          researcher: 'conditional', patient: 'no', admin: 'config' },
  'data.delete_raw':              { ktv: 'no',  doctor: 'no',          researcher: 'no',          patient: 'no', admin: 'conditional' },
  'audit.view':                   { ktv: 'limited', doctor: 'limited', researcher: 'limited',     patient: 'no', admin: 'yes' },
};

/**
 * Check if a role can perform a given action.
 * Returns true for 'yes'; returns false for 'no'.
 * 'conditional', 'limited', 'config', 'view_only' return true
 * (specific constraints are enforced in component logic).
 */
export function hasPermission(role: UserRole, action: PermissionAction): boolean {
  const value = PERMISSION_MATRIX[action]?.[role];
  if (!value) return false;
  return value !== 'no';
}

/**
 * Get the raw permission value for detailed UI rendering.
 */
export function getPermissionLevel(role: UserRole, action: PermissionAction): PermissionValue {
  return PERMISSION_MATRIX[action]?.[role] ?? 'no';
}

/**
 * Routes accessible by each role
 */
const ROLE_ROUTE_ACCESS: Record<UserRole, RegExp[]> = {
  patient: [
    /^\/dashboard$/,
    /^\/uc1\/session\//,
    /^\/login$/,
  ],
  ktv: [
    /^\//, // Access to most routes
  ],
  doctor: [
    /^\//, // Access to most routes
  ],
  researcher: [
    /^\/dashboard$/,
    /^\/feedback\//,
    /^\/analyses$/,
    /^\/data-quality\//,
    /^\/uc[1-4]\//,
    /^\/login$/,
  ],
  admin: [
    /^\/dashboard$/,
    /^\/admin\//,
    /^\/audit$/,
    /^\/devices/,
    /^\/protocols/,
    /^\/login$/,
  ],
};

/**
 * Check if a role can access a given route path.
 */
export function canAccessRoute(role: UserRole, pathname: string): boolean {
  const patterns = ROLE_ROUTE_ACCESS[role];
  if (!patterns) return false;
  return patterns.some((pattern) => pattern.test(pathname));
}
