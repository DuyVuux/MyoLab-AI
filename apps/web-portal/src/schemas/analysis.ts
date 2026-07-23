/**
 * Analysis domain types.
 * Per spec Section 6.12.
 * Engineering confidence is NOT clinical probability.
 */

export type AnalysisState =
  | 'pending'
  | 'prerequisites_checking'
  | 'queued'
  | 'running'
  | 'completed'
  | 'partial'
  | 'abstained'
  | 'failed';

export interface AnalysisPrerequisite {
  id: string;
  label: string;
  met: boolean;
  detail: string;
}

export interface MFCVEligibility {
  eligible: boolean;
  reason: string;
  requiredByProtocol: boolean;
  blocksBasicSEMG: boolean; // false unless protocol explicitly requires MFCV
}

export interface AnalysisProvenance {
  modelVersion: string;
  pipelineVersion: string;
  dataHash: string;
  calibrationId?: string;
  qcResultId?: string;
}

export interface AnalysisOutput {
  status: 'completed' | 'partial' | 'abstained' | 'failed';
  technicalConclusion: string;
  reasonCodes: string[];
  limitations: string[];
  provenance: AnalysisProvenance;
  engineeringConfidence: number; // 0.0–1.0, NOT clinical probability
  mfcvEligibility: MFCVEligibility;
}

export interface AnalysisJob {
  jobId: string;
  sessionId: string;
  useCaseId: string;
  pipeline: string;
  state: AnalysisState;
  progress: number; // 0–100
  prerequisites: AnalysisPrerequisite[];
  output?: AnalysisOutput;
  startedAt?: string;
  completedAt?: string;
  errorMessage?: string;
}

export function checkAnalysisPrerequisites(
  contextConfirmed: boolean,
  mappingValid: boolean,
  calibrationDone: boolean,
  calibrationRequired: boolean,
  qcVerdict: 'pass' | 'warning' | 'fail' | null,
  qcAcknowledged: boolean,
): AnalysisPrerequisite[] {
  return [
    {
      id: 'context',
      label: 'Session context xác nhận',
      met: contextConfirmed,
      detail: contextConfirmed ? 'Context đã xác nhận' : 'Chưa xác nhận context',
    },
    {
      id: 'mapping',
      label: 'Channel mapping hoàn tất',
      met: mappingValid,
      detail: mappingValid ? 'Mapping đã xác nhận' : 'Mapping chưa hoàn tất hoặc có lỗi',
    },
    {
      id: 'calibration',
      label: 'Calibration',
      met: calibrationRequired ? calibrationDone : true,
      detail: calibrationRequired
        ? (calibrationDone ? 'Calibration hoàn tất' : 'Calibration chưa hoàn tất')
        : 'Không yêu cầu calibration cho protocol này',
    },
    {
      id: 'qc',
      label: 'Quality gate',
      met: qcVerdict === 'pass' || (qcVerdict === 'warning' && qcAcknowledged),
      detail:
        qcVerdict === 'pass' ? 'QC pass' :
        qcVerdict === 'warning' && qcAcknowledged ? 'QC warning — đã acknowledge' :
        qcVerdict === 'warning' ? 'QC warning — cần acknowledge' :
        qcVerdict === 'fail' ? 'QC fail — không thể chạy analysis' :
        'Chưa chạy QC',
    },
  ];
}
