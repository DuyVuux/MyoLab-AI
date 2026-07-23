/**
 * MockSessionService — Session lifecycle management.
 * All state goes through MockWorkflowRepository.
 */
import type { SessionContext, SessionDraft } from '@/schemas/session';
import { validateSessionContext, PROTOCOLS_REQUIRING_CALIBRATION } from '@/schemas/session';
import * as repo from './MockWorkflowRepository';

export function createSession(draft: SessionDraft): SessionContext {
  const sessionId = `S-${Date.now().toString(36).toUpperCase()}`;
  const requiresCalibration = PROTOCOLS_REQUIRING_CALIBRATION.includes(draft.protocolId);

  const ctx: SessionContext = {
    ...draft,
    sessionId,
    createdAt: new Date().toISOString(),
    electrodeLayout: [],
    requiresCalibration,
    state: 'draft',
  };

  return repo.createSession(ctx);
}

export function getSession(id: string): SessionContext | null {
  return repo.getSession(id);
}

export function confirmContext(id: string, updates: Partial<SessionDraft>): SessionContext | null {
  const session = repo.getSession(id);
  if (!session) return null;

  const merged = { ...session, ...updates };
  const validation = validateSessionContext(merged);
  if (!validation.valid) return null;

  const requiresCalibration = PROTOCOLS_REQUIRING_CALIBRATION.includes(merged.protocolId);
  repo.updateSessionContext(id, { ...updates, requiresCalibration });
  repo.updateSessionState(id, 'context_confirmed');
  return repo.getSession(id);
}

export function setDataSource(id: string, sourceType: SessionDraft['dataSourceIntent']): void {
  repo.updateSessionContext(id, { dataSourceIntent: sourceType });
  repo.updateSessionState(id, 'source_selected');
}

export function advanceState(id: string, newState: SessionContext['state']): void {
  repo.updateSessionState(id, newState);
}

export { validateSessionContext };
