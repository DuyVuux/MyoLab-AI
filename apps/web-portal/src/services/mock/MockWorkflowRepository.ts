/**
 * MockWorkflowRepository — Single source of truth for all session workflow state.
 * Persists non-sensitive metadata to sessionStorage. Never stores raw file/signal data.
 * Emits mock audit events for every state transition.
 */
import type { SessionContext, SessionState } from '@/schemas/session';
import type { ImportRecord } from '@/schemas/import';
import type { ChannelMapping } from '@/schemas/mapping';
import type { PreflightResult } from '@/schemas/preflight';
import type { CalibrationWizard } from '@/schemas/calibration';
import type { QCResult } from '@/schemas/quality';
import type { AnalysisJob } from '@/schemas/analysis';
import type { AuditEntry } from '@/schemas/common';
import type { SignalSegment } from '@/schemas/segment';
import type { TechnicalReview, ClinicalReview } from '@/schemas/review';
import type { ReportDocument } from '@/schemas/report';
import type { FeedbackEvent, MLAdjudication } from '@/schemas/feedback';
import type { DataQualityIssue } from '@/schemas/issue';

const STORAGE_KEY = 'myolab_workflow_state';

interface WorkflowStore {
  sessions: Record<string, SessionContext>;
  imports: Record<string, ImportRecord>;
  mappings: Record<string, ChannelMapping[]>; // keyed by sessionId
  preflights: Record<string, PreflightResult>; // keyed by sessionId
  calibrations: Record<string, CalibrationWizard>; // keyed by sessionId
  qcResults: Record<string, QCResult>; // keyed by sessionId
  analysisJobs: Record<string, AnalysisJob>; // keyed by sessionId
  
  // Phase 2 additions
  segments: Record<string, SignalSegment[]>; // keyed by sessionId
  technicalReviews: Record<string, TechnicalReview>; // keyed by sessionId
  clinicalReviews: Record<string, ClinicalReview>; // keyed by sessionId
  reports: Record<string, ReportDocument>; // keyed by sessionId
  feedbackEvents: Record<string, FeedbackEvent>; // keyed by feedbackId
  adjudications: Record<string, MLAdjudication>; // keyed by feedbackId
  issues: Record<string, DataQualityIssue>; // keyed by issueId
  
  auditLog: AuditEntry[];
}

function createEmptyStore(): WorkflowStore {
  return {
    sessions: {},
    imports: {},
    mappings: {},
    preflights: {},
    calibrations: {},
    qcResults: {},
    analysisJobs: {},
    
    segments: {},
    technicalReviews: {},
    clinicalReviews: {},
    reports: {},
    feedbackEvents: {},
    adjudications: {},
    issues: {},
    
    auditLog: [],
  };
}

let _store: WorkflowStore | null = null;

function getStore(): WorkflowStore {
  if (_store) return _store;

  if (typeof window !== 'undefined') {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        _store = JSON.parse(saved) as WorkflowStore;
        return _store;
      }
    } catch {
      // ignore parse errors
    }
  }
  _store = createEmptyStore();
  return _store;
}

function persist(): void {
  if (typeof window === 'undefined') return;
  try {
    const store = getStore();
    // Only persist non-sensitive metadata — strip any large data
    const safe: WorkflowStore = {
      ...store,
      // Keep everything except raw signal data (which we never store)
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(safe));
  } catch {
    // sessionStorage full or unavailable
  }
}

function addAuditEntry(action: string, resource: string, detail: string): void {
  const store = getStore();
  const entry: AuditEntry = {
    id: `AUD-${Date.now().toString(36).toUpperCase()}`,
    timestamp: new Date().toISOString(),
    actor: 'current_user', // injected at call site
    actorRole: 'ktv',
    action,
    resource,
    detail,
  };
  store.auditLog.push(entry);
  persist();
}

// ── Session CRUD ──

export function createSession(ctx: SessionContext): SessionContext {
  const store = getStore();
  store.sessions[ctx.sessionId] = ctx;
  addAuditEntry('session.create', ctx.sessionId, `Created session for ${ctx.subjectRef}`);
  persist();
  return ctx;
}

export function getSession(id: string): SessionContext | null {
  return getStore().sessions[id] ?? null;
}

export function getAllSessions(): SessionContext[] {
  return Object.values(getStore().sessions);
}

export function getSessionsBySubject(subjectRef: string): SessionContext[] {
  return Object.values(getStore().sessions).filter((s) => s.subjectRef === subjectRef);
}

export function updateSessionState(id: string, state: SessionState): void {
  const store = getStore();
  const session = store.sessions[id];
  if (session) {
    const prev = session.state;
    session.state = state;
    addAuditEntry('session.transition', id, `${prev} → ${state}`);
    persist();
  }
}

export function updateSessionContext(id: string, partial: Partial<SessionContext>): SessionContext | null {
  const store = getStore();
  const session = store.sessions[id];
  if (!session) return null;
  Object.assign(session, partial);
  addAuditEntry('session.update', id, `Updated context fields: ${Object.keys(partial).join(', ')}`);
  persist();
  return session;
}

// ── Import CRUD ──

export function saveImport(rec: ImportRecord): void {
  const store = getStore();
  store.imports[rec.importId] = rec;
  persist();
}

export function getImport(id: string): ImportRecord | null {
  return getStore().imports[id] ?? null;
}

export function getImportsBySession(sessionId: string): ImportRecord[] {
  const store = getStore();
  return Object.values(store.imports).filter((i) => i.sessionId === sessionId);
}

export function findImportByHash(sha256: string): ImportRecord | null {
  const store = getStore();
  return Object.values(store.imports).find((i) => i.sha256 === sha256 && i.state !== 'cancelled') ?? null;
}

// ── Mapping CRUD ──

export function saveMappings(sessionId: string, mappings: ChannelMapping[]): void {
  const store = getStore();
  store.mappings[sessionId] = mappings;
  addAuditEntry('mapping.save', sessionId, `Saved ${mappings.length} channel mappings`);
  persist();
}

export function getMappings(sessionId: string): ChannelMapping[] | null {
  return getStore().mappings[sessionId] ?? null;
}

// ── Preflight CRUD ──

export function savePreflight(result: PreflightResult): void {
  const store = getStore();
  store.preflights[result.sessionId] = result;
  addAuditEntry('preflight.complete', result.sessionId, `Outcome: ${result.outcome}`);
  persist();
}

export function getPreflight(sessionId: string): PreflightResult | null {
  return getStore().preflights[sessionId] ?? null;
}

// ── Calibration CRUD ──

export function saveCalibration(wizard: CalibrationWizard): void {
  const store = getStore();
  store.calibrations[wizard.sessionId] = wizard;
  persist();
}

export function getCalibration(sessionId: string): CalibrationWizard | null {
  return getStore().calibrations[sessionId] ?? null;
}

// ── QC CRUD ──

export function saveQCResult(result: QCResult): void {
  const store = getStore();
  store.qcResults[result.sessionId] = result;
  addAuditEntry('qc.complete', result.sessionId, `Verdict: ${result.overallVerdict}`);
  persist();
}

export function getQCResult(sessionId: string): QCResult | null {
  return getStore().qcResults[sessionId] ?? null;
}

// ── Analysis CRUD ──

export function saveAnalysisJob(job: AnalysisJob): void {
  const store = getStore();
  store.analysisJobs[job.sessionId] = job;
  persist();
}

export function getAnalysisJob(sessionId: string): AnalysisJob | null {
  return getStore().analysisJobs[sessionId] ?? null;
}

// ── Audit ──

export function getAuditLog(): AuditEntry[] {
  return getStore().auditLog;
}

export function logAudit(action: string, resource: string, detail: string): void {
  addAuditEntry(action, resource, detail);
}

// ── Segments CRUD ──

export function saveSegments(sessionId: string, segments: SignalSegment[]): void {
  const store = getStore();
  store.segments[sessionId] = segments;
  persist();
}

export function getSegments(sessionId: string): SignalSegment[] {
  return getStore().segments[sessionId] ?? [];
}

// ── Review CRUD ──

export function saveTechnicalReview(review: TechnicalReview): void {
  const store = getStore();
  store.technicalReviews[review.sessionId] = review;
  addAuditEntry('review.technical.save', review.sessionId, `State: ${review.state}`);
  persist();
}

export function getTechnicalReview(sessionId: string): TechnicalReview | null {
  return getStore().technicalReviews[sessionId] ?? null;
}

export function saveClinicalReview(review: ClinicalReview): void {
  const store = getStore();
  store.clinicalReviews[review.sessionId] = review;
  addAuditEntry('review.clinical.save', review.sessionId, `State: ${review.state}`);
  persist();
}

export function getClinicalReview(sessionId: string): ClinicalReview | null {
  return getStore().clinicalReviews[sessionId] ?? null;
}

// ── Report CRUD ──

export function saveReport(report: ReportDocument): void {
  const store = getStore();
  store.reports[report.sessionId] = report;
  addAuditEntry('report.save', report.sessionId, `State: ${report.state}`);
  persist();
}

export function getReport(sessionId: string): ReportDocument | null {
  return getStore().reports[sessionId] ?? null;
}

// ── Feedback & Adjudication CRUD ──

export function saveFeedbackEvent(feedback: FeedbackEvent): void {
  const store = getStore();
  store.feedbackEvents[feedback.id] = feedback;
  addAuditEntry('feedback.create', feedback.segmentId, `Certainty: ${feedback.reviewerCertainty}`);
  persist();
}

export function getFeedbackEvents(): FeedbackEvent[] {
  return Object.values(getStore().feedbackEvents);
}

export function getFeedbackEvent(id: string): FeedbackEvent | null {
  return getStore().feedbackEvents[id] ?? null;
}

export function saveAdjudication(adj: MLAdjudication): void {
  const store = getStore();
  store.adjudications[adj.feedbackId] = adj;
  addAuditEntry('adjudication.save', adj.feedbackId, `Status: ${adj.status}`);
  persist();
}

export function getAdjudication(feedbackId: string): MLAdjudication | null {
  return getStore().adjudications[feedbackId] ?? null;
}

// ── Issues CRUD ──

export function saveIssue(issue: DataQualityIssue): void {
  const store = getStore();
  store.issues[issue.id] = issue;
  persist();
}

export function getIssues(): DataQualityIssue[] {
  return Object.values(getStore().issues);
}

// ── Reset (for testing) ──

export function resetStore(): void {
  _store = createEmptyStore();
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(STORAGE_KEY);
  }
}
