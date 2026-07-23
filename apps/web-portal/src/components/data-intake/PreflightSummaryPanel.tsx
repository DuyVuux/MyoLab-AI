import type { PreflightSummary } from "../../schemas/preflight.schema";
import { Alert } from "../ui/Alert";

export interface PreflightSummaryPanelProps {
  readonly summary: PreflightSummary;
}

export const PreflightSummaryPanel = ({ summary }: PreflightSummaryPanelProps): JSX.Element => {
  const tone = summary.state === "ready" ? "success" : summary.state === "mapping_required" ? "warning" : "error";
  return (
    <section>
      <Alert title={`Preflight: ${summary.state}`} variant={tone}>
        <p>Reason codes: {summary.reasonCodes.join(", ") || "Không có"}</p>
      </Alert>
      <table>
        <caption>Tóm tắt thay thế cho biểu đồ preview</caption>
        <tbody>
          <tr><th>Sampling rate</th><td>{summary.samplingRateHz ?? "Không xác định"}</td></tr>
          <tr><th>Duration</th><td>{summary.durationS ?? "Không xác định"}</td></tr>
          <tr><th>Channel count</th><td>{summary.channelCount ?? "Không xác định"}</td></tr>
          <tr><th>Mapping</th><td>{Math.round(summary.mappingCompleteness * 100)}%</td></tr>
        </tbody>
      </table>
    </section>
  );
};
