export const userRoles = [
  'patient',
  'ktv',
  'physician',
  'researcher',
  'ml_qa',
  'admin',
] as const;

export type UserRole = (typeof userRoles)[number];

export type ClinicalAction =
  | 'view_dashboard'
  | 'create_session'
  | 'map_channels'
  | 'view_analysis'
  | 'submit_feedback'
  | 'technical_adjudication'
  | 'clinical_signoff'
  | 'review_training_candidate'
  | 'manage_workflow';
