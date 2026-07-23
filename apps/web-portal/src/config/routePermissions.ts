import type { ClinicalAction, UserRole } from '../schemas/role.schema';

const actionPermissions: Readonly<Record<ClinicalAction, readonly UserRole[]>> = {
  view_dashboard: ['ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  create_session: ['ktv', 'physician'],
  map_channels: ['ktv'],
  view_analysis: ['ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  submit_feedback: ['ktv', 'physician', 'researcher', 'ml_qa'],
  technical_adjudication: ['ktv', 'researcher', 'ml_qa'],
  clinical_signoff: ["physician"],
  review_training_candidate: ['researcher', 'ml_qa'],
  manage_workflow: ['admin'],
};

export const canPerformAction = (role: UserRole, action: ClinicalAction): boolean =>
  actionPermissions[action].includes(role);

export const routeRoleMap: Readonly<Record<string, readonly UserRole[]>> = {
  '/dashboard': ['ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  '/use-cases': ['patient', 'ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  '/sessions': ['ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  '/sessions/new': ['ktv', 'physician'],
  '/analyses': ['ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  '/feedback/inbox': ['ktv', 'physician', 'researcher', 'ml_qa'],
  '/uc3/feasibility': ['ktv', 'physician', 'researcher', 'ml_qa', 'admin'],
  '/uc4/feasibility': ['physician', 'researcher', 'ml_qa', 'admin'],
};

export const canAccessDay19Route = (role: UserRole, route: string): boolean =>
  routeRoleMap[route]?.includes(role) ?? false;
