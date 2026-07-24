import type {
  GestureInferenceWindow,
  UC1ReplaySession,
} from "../schemas/gesture-inference.schema";

function belongsToReplay(
  replay: UC1ReplaySession,
  window: GestureInferenceWindow,
): boolean {
  return (
    window.sessionId === replay.sessionId &&
    window.analysisId === replay.analysisId
  );
}

function uniqueHistory(replay: UC1ReplaySession): boolean {
  const windowIds = replay.history.map((window) => window.windowId);
  return new Set(windowIds).size === windowIds.length;
}

export function currentReplayWindow(
  replay: UC1ReplaySession,
): GestureInferenceWindow | null {
  if (
    replay.currentIndex < 0 ||
    replay.currentIndex >= replay.totalWindows ||
    replay.currentWindow === null ||
    replay.history.length !== replay.currentIndex ||
    !belongsToReplay(replay, replay.currentWindow) ||
    replay.history.some(
      (window) => window.windowId === replay.currentWindow?.windowId,
    ) ||
    replay.history.some((window) => !belongsToReplay(replay, window)) ||
    !uniqueHistory(replay)
  ) {
    return null;
  }
  return replay.currentWindow;
}

export function visibleReplayWindows(
  replay: UC1ReplaySession,
): readonly GestureInferenceWindow[] {
  if (replay.currentIndex < 0 || replay.totalWindows <= 0) {
    return [];
  }
  const currentWindow = currentReplayWindow(replay);
  return currentWindow === null ? [] : [...replay.history, currentWindow];
}
