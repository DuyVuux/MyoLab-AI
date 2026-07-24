import type {
  EngineeringConfidence,
  GestureId,
  GestureInferenceWindow,
} from "@/schemas/gesture-inference.schema";

import styles from "./UC1SessionWorkspace.module.css";

const GESTURE_LABELS: Readonly<Record<GestureId, string>> = {
  rest: "Nghỉ",
  hand_open: "Mở bàn tay",
  hand_close: "Nắm bàn tay",
  wrist_flexion: "Gập cổ tay",
  wrist_extension: "Duỗi cổ tay",
};

const CONFIDENCE_LABELS: Readonly<Record<EngineeringConfidence, string>> = {
  engineering_high: "Cao — kỹ thuật",
  engineering_moderate: "Vừa — kỹ thuật",
  engineering_low: "Thấp — cần xem lại",
  engineering_very_low: "Rất thấp — cần xem lại",
  not_available: "Không có kết quả",
};

function outcomeLabel(window: GestureInferenceWindow): string {
  if (window.deviceState !== "connected") {
    return "Gián đoạn kết nối";
  }
  if (window.qualityContext.status === "fail") {
    return "Không đạt QC";
  }
  if (window.fatigueOverlay.status === "abstain") {
    return "Tạm không kết luận";
  }
  if (window.activityGate.status === "inactive") {
    return "Chưa đủ hoạt động";
  }
  if (window.activityGate.status === "uncertain") {
    return "Gần ngưỡng kỹ thuật";
  }
  return window.predictedGesture === null
    ? "Không có kết quả"
    : GESTURE_LABELS[window.predictedGesture];
}

export interface GestureHistoryTableProps {
  readonly windows: readonly GestureInferenceWindow[];
}

export function GestureHistoryTable({
  windows,
}: GestureHistoryTableProps) {
  return (
    <div className={styles.tableScroller}>
      <table className={styles.historyTable}>
        <caption>
          Lịch sử các cửa sổ replay đã được server công bố
        </caption>
        <thead>
          <tr>
            <th scope="col">Cửa sổ</th>
            <th scope="col">Khoảng thời gian</th>
            <th scope="col">Mục tiêu</th>
            <th scope="col">Kết quả kỹ thuật</th>
            <th scope="col">Độ tin cậy</th>
            <th scope="col">Độ trễ tổng</th>
          </tr>
        </thead>
        <tbody>
          {windows.length === 0 ? (
            <tr>
              <td colSpan={6} className={styles.emptyCell}>
                Chưa có cửa sổ nào được công bố.
              </td>
            </tr>
          ) : (
            windows.map((window) => (
              <tr key={window.windowId}>
                <td>
                  <code>{window.windowId}</code>
                </td>
                <td>
                  {window.segmentRef.startTimeS.toFixed(2)}–
                  {window.segmentRef.endTimeExclusiveS.toFixed(2)} giây
                </td>
                <td>{GESTURE_LABELS[window.targetGesture]}</td>
                <td>{outcomeLabel(window)}</td>
                <td>
                  {CONFIDENCE_LABELS[window.engineeringConfidence]}
                </td>
                <td>{window.latency.totalMs.toFixed(0)} ms</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
