/**
 * Calibration domain types.
 * Per spec Section 6.10 — conditional on protocol.
 */

export type CalibrationStep = 'setup_check' | 'rest_baseline' | 'gesture_repetitions' | 'summary' | 'result';

export type CalibrationStatus = 'not_started' | 'in_progress' | 'pass' | 'warning' | 'fail';

export type RepetitionQuality = 'pass' | 'warning' | 'fail';

export interface RepetitionResult {
  repetitionId: string;
  index: number;
  gesture: string;
  quality: RepetitionQuality;
  peakAmplitude: number;
  duration: number;
  accepted: boolean;
  needsRepeat: boolean;
  reason?: string;
}

export interface SetupCheckResult {
  impedanceOk: boolean;
  channelsDetected: number;
  channelsExpected: number;
  skinContact: 'good' | 'fair' | 'poor';
  detail: string;
}

export interface BaselineResult {
  baselineNoiseRms: number;
  baselineDuration: number;
  acceptable: boolean;
  detail: string;
}

export interface CalibrationSummary {
  totalRepetitions: number;
  passedRepetitions: number;
  warningRepetitions: number;
  failedRepetitions: number;
  mvcEstimates: Record<string, number>; // muscle → MVC in µV
  overallStatus: CalibrationStatus;
  detail: string;
}

export interface CalibrationWizard {
  calibrationId: string;
  sessionId: string;
  currentStep: CalibrationStep;
  status: CalibrationStatus;
  setupResult?: SetupCheckResult;
  baselineResult?: BaselineResult;
  repetitions: RepetitionResult[];
  summary?: CalibrationSummary;
  startedAt: string;
  completedAt?: string;
}

export const CALIBRATION_STEPS: { id: CalibrationStep; label: string }[] = [
  { id: 'setup_check', label: 'Kiểm tra setup' },
  { id: 'rest_baseline', label: 'Baseline nghỉ' },
  { id: 'gesture_repetitions', label: 'Lặp cử chỉ' },
  { id: 'summary', label: 'Tóm tắt' },
  { id: 'result', label: 'Kết quả' },
];
