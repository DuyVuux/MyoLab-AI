import type { AnalysisHandoff } from "../../schemas/analysis-handoff.schema";
import { Alert } from "../ui/Alert";

export interface AnalysisHandoffPanelProps {
  readonly handoff: AnalysisHandoff;
}

export const AnalysisHandoffPanel = ({ handoff }: AnalysisHandoffPanelProps): JSX.Element => {
  const tone = handoff.status === "abstained" ? "abstention" : handoff.status === "queued_with_warnings" ? "warning" : "info";
  return (
    <Alert title={`Analysis handoff: ${handoff.status}`} variant={tone}>
      <p>Analysis ID: <code>{handoff.analysisId}</code></p>
      <p>Human review bắt buộc: Có</p>
      <p>Điểm số là xác suất lâm sàng: Không</p>
      <p>Next route: {handoff.nextRoute ?? "Đo lại hoặc sửa setup"}</p>
      <p>Reason codes: {handoff.reasonCodes.join(", ") || "Không có"}</p>
    </Alert>
  );
};
