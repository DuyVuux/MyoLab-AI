/**
 * MockCalibrationService — Wizard lifecycle, conditional on protocol.
 */
import type { CalibrationWizard, CalibrationStep, CalibrationStatus, RepetitionResult } from '@/schemas/calibration';
import type { ScenarioId } from './fixtures';
import { createSetupCheckFixture, createBaselineFixture, createRepetitionFixtures } from './fixtures';
import * as repo from './MockWorkflowRepository';

export function startCalibration(sessionId: string, scenario: ScenarioId): CalibrationWizard {
  const wizard: CalibrationWizard = {
    calibrationId: `CAL-${Date.now().toString(36).toUpperCase()}`,
    sessionId,
    currentStep: 'setup_check',
    status: 'in_progress',
    repetitions: [],
    startedAt: new Date().toISOString(),
  };
  repo.saveCalibration(wizard);
  repo.logAudit('calibration.start', sessionId, `Calibration ${wizard.calibrationId} started`);
  return wizard;
}

export function runSetupCheck(sessionId: string, scenario: ScenarioId): CalibrationWizard | null {
  const wizard = repo.getCalibration(sessionId);
  if (!wizard) return null;

  wizard.setupResult = createSetupCheckFixture(scenario);
  wizard.currentStep = 'rest_baseline';
  repo.saveCalibration(wizard);
  return wizard;
}

export function recordBaseline(sessionId: string, scenario: ScenarioId): CalibrationWizard | null {
  const wizard = repo.getCalibration(sessionId);
  if (!wizard) return null;

  wizard.baselineResult = createBaselineFixture(scenario);
  wizard.currentStep = 'gesture_repetitions';
  repo.saveCalibration(wizard);
  return wizard;
}

export function loadRepetitions(sessionId: string, scenario: ScenarioId): CalibrationWizard | null {
  const wizard = repo.getCalibration(sessionId);
  if (!wizard) return null;

  wizard.repetitions = createRepetitionFixtures(scenario);
  repo.saveCalibration(wizard);
  return wizard;
}

export function acceptRepetition(sessionId: string, repIndex: number): CalibrationWizard | null {
  const wizard = repo.getCalibration(sessionId);
  if (!wizard) return null;
  if (repIndex >= wizard.repetitions.length) return wizard;

  wizard.repetitions[repIndex].accepted = true;
  wizard.repetitions[repIndex].needsRepeat = false;
  repo.saveCalibration(wizard);
  return wizard;
}

export function repeatRepetition(sessionId: string, repIndex: number): CalibrationWizard | null {
  const wizard = repo.getCalibration(sessionId);
  if (!wizard) return null;
  if (repIndex >= wizard.repetitions.length) return wizard;

  // Replace with a new pass result
  const old = wizard.repetitions[repIndex];
  wizard.repetitions[repIndex] = {
    ...old,
    repetitionId: `REP-${Date.now().toString(36).toUpperCase()}`,
    quality: 'pass',
    peakAmplitude: 700 + ((repIndex + 1) * 45) % 200,
    accepted: true,
    needsRepeat: false,
    reason: undefined,
  };
  repo.saveCalibration(wizard);
  return wizard;
}

export function finishCalibration(sessionId: string): CalibrationWizard | null {
  const wizard = repo.getCalibration(sessionId);
  if (!wizard) return null;

  const passed = wizard.repetitions.filter((r) => r.quality === 'pass' && r.accepted).length;
  const warnings = wizard.repetitions.filter((r) => r.quality === 'warning').length;
  const failed = wizard.repetitions.filter((r) => r.quality === 'fail').length;
  const allAccepted = wizard.repetitions.every((r) => r.accepted);

  let overallStatus: CalibrationStatus;
  if (failed > 0 || !allAccepted) overallStatus = 'fail';
  else if (warnings > 0) overallStatus = 'warning';
  else overallStatus = 'pass';

  wizard.summary = {
    totalRepetitions: wizard.repetitions.length,
    passedRepetitions: passed,
    warningRepetitions: warnings,
    failedRepetitions: failed,
    mvcEstimates: {
      'Flexor carpi radialis': 850,
      'Extensor carpi radialis': 720,
      'Biceps brachii': 680,
      'Upper trapezius': 590,
    },
    overallStatus,
    detail: overallStatus === 'pass' ? 'Calibration hoàn tất thành công.' :
            overallStatus === 'warning' ? 'Calibration hoàn tất với cảnh báo. Một số repetition có chất lượng thấp.' :
            'Calibration thất bại. Cần thực hiện lại.',
  };

  wizard.currentStep = 'result';
  wizard.status = overallStatus;
  wizard.completedAt = new Date().toISOString();
  repo.saveCalibration(wizard);

  if (overallStatus === 'pass' || overallStatus === 'warning') {
    repo.updateSessionState(sessionId, 'calibration_complete');
  }
  repo.logAudit('calibration.complete', sessionId, `Status: ${overallStatus}`);

  return wizard;
}

export function getCalibration(sessionId: string): CalibrationWizard | null {
  return repo.getCalibration(sessionId);
}
