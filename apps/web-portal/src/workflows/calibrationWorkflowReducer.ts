import type { CalibrationRecord, CalibrationState } from "../schemas/calibration.schema";

export type CalibrationEvent =
  | "START"
  | "SETUP_PASS"
  | "SETUP_FAIL"
  | "REST_COMPLETE"
  | "FINISH_REPETITIONS"
  | "SUMMARY_PASS"
  | "SUMMARY_WARNING"
  | "SUMMARY_FAIL"
  | "ACKNOWLEDGE_WARNING"
  | "RETRY"
  | "CANCEL";

const transitions: Readonly<Record<CalibrationState, Partial<Record<CalibrationEvent, CalibrationState>>>> = {
  not_started: { START: "setup_check", CANCEL: "cancelled" },
  setup_check: { SETUP_PASS: "rest_baseline", SETUP_FAIL: "fail", CANCEL: "cancelled" },
  rest_baseline: { REST_COMPLETE: "gesture_repetitions", CANCEL: "cancelled" },
  gesture_repetitions: { FINISH_REPETITIONS: "summary", CANCEL: "cancelled" },
  summary: { SUMMARY_PASS: "pass", SUMMARY_WARNING: "warning", SUMMARY_FAIL: "fail" },
  pass: {},
  warning: { ACKNOWLEDGE_WARNING: "pass", RETRY: "setup_check", CANCEL: "cancelled" },
  fail: { RETRY: "setup_check", CANCEL: "cancelled" },
  cancelled: { RETRY: "setup_check" },
};

export const nextCalibrationState = (
  current: CalibrationState,
  event: CalibrationEvent,
): CalibrationState => {
  const next = transitions[current][event];
  if (!next) throw new Error(`INVALID_CALIBRATION_TRANSITION:${current}:${event}`);
  return next;
};

export const calibrationWorkflowReducer = (
  state: CalibrationRecord,
  event: CalibrationEvent,
): CalibrationRecord => ({
  ...state,
  state: nextCalibrationState(state.state, event),
  warningAcknowledged:
    event === "ACKNOWLEDGE_WARNING" ? true : state.warningAcknowledged,
});
