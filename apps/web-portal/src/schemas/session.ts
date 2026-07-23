/**
 * Session domain types.
 * Per spec Sections 6.3–6.5.
 */
import type { Side, ConsentScope, DataSourceType, SessionType, ElectrodeLayout } from './common';

export interface SessionDraft {
  subjectRef: string;
  useCaseId: string;
  protocolId: string;
  protocolVersion: string;
  affectedSide: Side;
  referenceSide: Side;
  targetMuscles: string[];
  sessionType: SessionType;
  operator: string;
  consentScope: ConsentScope[];
  dataSourceIntent: DataSourceType | '';
}

export interface SessionContext extends SessionDraft {
  sessionId: string;
  createdAt: string;
  electrodeLayout: ElectrodeLayout[];
  requiresCalibration: boolean;
  state: SessionState;
}

/**
 * Derived session state — represents overall progress through the flow.
 * Each sub-step has its own specific state machine.
 */
export type SessionState =
  | 'draft'
  | 'context_confirmed'
  | 'source_selected'
  | 'importing'
  | 'import_complete'
  | 'mapping_complete'
  | 'preflight_pass'
  | 'calibration_complete'
  | 'calibration_skipped'
  | 'qc_pass'
  | 'qc_warning_acknowledged'
  | 'qc_fail'
  | 'analysis_running'
  | 'analysis_complete'
  | 'analysis_failed'
  | 'analysis_abstained';

export interface SessionValidation {
  valid: boolean;
  errors: Partial<Record<keyof SessionDraft, string>>;
}

export function validateSessionContext(ctx: Partial<SessionDraft>): SessionValidation {
  const errors: Partial<Record<keyof SessionDraft, string>> = {};

  if (!ctx.subjectRef?.trim()) errors.subjectRef = 'Vui lòng nhập mã đối tượng.';
  if (!ctx.useCaseId) errors.useCaseId = 'Vui lòng chọn use case.';
  if (!ctx.protocolId) errors.protocolId = 'Vui lòng chọn protocol.';
  if (!ctx.affectedSide) errors.affectedSide = 'Vui lòng chọn bên ảnh hưởng.';
  if (!ctx.targetMuscles?.length) errors.targetMuscles = 'Vui lòng chọn ít nhất 1 cơ.';
  if (!ctx.consentScope?.length) errors.consentScope = 'Vui lòng xác nhận phạm vi đồng thuận.';

  return { valid: Object.keys(errors).length === 0, errors };
}

/** Protocols that require calibration */
export const PROTOCOLS_REQUIRING_CALIBRATION = [
  'PROT-UC1-001',
  'PROT-UC1-002',
  'PROT-UC2-001',
  'PROT-UC2-002',
];
