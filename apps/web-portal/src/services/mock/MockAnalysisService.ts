/**
 * MockAnalysisService — Prerequisites check, job lifecycle, structured output.
 * Engineering confidence is NOT presented as clinical probability.
 */
import type { AnalysisJob, AnalysisOutput, AnalysisPrerequisite, MFCVEligibility } from '@/schemas/analysis';
import { checkAnalysisPrerequisites } from '@/schemas/analysis';
import * as repo from './MockWorkflowRepository';

export interface AnalysisEligibility {
  allowed: boolean;
  prerequisites: AnalysisPrerequisite[];
  blockers: string[];
}

export function canStartAnalysis(sessionId: string): AnalysisEligibility {
  const session = repo.getSession(sessionId);
  if (!session) return { allowed: false, prerequisites: [], blockers: ['Session not found'] };

  const mappings = repo.getMappings(sessionId);
  const calibration = repo.getCalibration(sessionId);
  const qcResult = repo.getQCResult(sessionId);

  const contextConfirmed = session.state !== 'draft';
  const mappingValid = !!mappings && mappings.every((m) => m.confirmed && m.muscle && m.side && m.unit !== 'unknown');
  const calibrationDone = session.requiresCalibration
    ? (!!calibration && (calibration.status === 'pass' || calibration.status === 'warning'))
    : true;
  const qcVerdict = qcResult?.overallVerdict ?? null;
  const qcAcknowledged = !!qcResult?.acknowledgement;

  const prerequisites = checkAnalysisPrerequisites(
    contextConfirmed,
    mappingValid,
    calibrationDone,
    session.requiresCalibration,
    qcVerdict,
    qcAcknowledged,
  );

  const blockers = prerequisites.filter((p) => !p.met).map((p) => p.detail);

  return {
    allowed: blockers.length === 0,
    prerequisites,
    blockers,
  };
}

export function startAnalysis(sessionId: string): AnalysisJob | null {
  const eligibility = canStartAnalysis(sessionId);
  if (!eligibility.allowed) return null;

  const session = repo.getSession(sessionId);
  if (!session) return null;

  const job: AnalysisJob = {
    jobId: `AJ-${Date.now().toString(36).toUpperCase()}`,
    sessionId,
    useCaseId: session.useCaseId,
    pipeline: session.useCaseId === 'uc1' ? 'Gesture Recognition' : 'Motor Assessment',
    state: 'running',
    progress: 0,
    prerequisites: eligibility.prerequisites,
    startedAt: new Date().toISOString(),
  };

  repo.saveAnalysisJob(job);
  repo.updateSessionState(sessionId, 'analysis_running');
  repo.logAudit('analysis.start', sessionId, `Job ${job.jobId}`);
  return job;
}

export function completeAnalysis(sessionId: string): AnalysisJob | null {
  const job = repo.getAnalysisJob(sessionId);
  if (!job) return null;

  const session = repo.getSession(sessionId);
  const qcResult = repo.getQCResult(sessionId);
  const calibration = repo.getCalibration(sessionId);
  const imp = repo.getImportsBySession(sessionId)[0];

  const mfcvEligibility: MFCVEligibility = {
    eligible: true,
    reason: 'Sampling rate ≥ 1000 Hz, channel count ≥ 2',
    requiredByProtocol: false,
    blocksBasicSEMG: false,
  };

  const output: AnalysisOutput = {
    status: 'completed',
    technicalConclusion: session?.useCaseId === 'uc1'
      ? 'Gesture recognition pipeline completed. 5 gestures detected with engineering confidence above threshold.'
      : 'Motor assessment pipeline completed. 5 KPIs computed.',
    reasonCodes: ['ANALYSIS_COMPLETE', 'ALL_CHANNELS_PASS'],
    limitations: [
      'Kết quả dựa trên dữ liệu synthetic/mock — chưa validate trên dữ liệu lâm sàng thực.',
      'Engineering confidence KHÔNG phải xác suất lâm sàng.',
    ],
    provenance: {
      modelVersion: 'v1.2.0-mock',
      pipelineVersion: 'v0.1.0-prototype',
      dataHash: imp?.sha256 ?? 'N/A',
      calibrationId: calibration?.calibrationId,
      qcResultId: qcResult ? `QC-${sessionId}` : undefined,
    },
    engineeringConfidence: 0.85,
    mfcvEligibility,
  };

  job.state = 'completed';
  job.progress = 100;
  job.output = output;
  job.completedAt = new Date().toISOString();
  repo.saveAnalysisJob(job);
  repo.updateSessionState(sessionId, 'analysis_complete');
  repo.logAudit('analysis.complete', sessionId, `Job ${job.jobId} completed`);
  return job;
}

export function getAnalysisJob(sessionId: string): AnalysisJob | null {
  return repo.getAnalysisJob(sessionId);
}
