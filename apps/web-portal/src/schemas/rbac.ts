export type Role = 'technician' | 'clinician' | 'ml_qa' | 'admin';

export interface UserContext {
  id: string;
  name: string;
  roles: Role[];
  department?: string;
}

// Quyền hạn định nghĩa theo Prompt 1.3
export const RBAC_POLICIES = {
  canSubmitTechnicalReview: (user: UserContext) => user.roles.includes('technician') || user.roles.includes('clinician'),
  canSubmitClinicalSignOff: (user: UserContext) => user.roles.includes('clinician'),
  canSubmitFeedback: (user: UserContext) => user.roles.includes('technician') || user.roles.includes('clinician'),
  canAdjudicateML: (user: UserContext) => user.roles.includes('ml_qa'),
  canManageWorkflow: (user: UserContext) => user.roles.includes('admin'),
};
