import type { AnalysisJob, AnalysisStage } from "../../schemas/analysis-job.schema";

const LABELS: Record<AnalysisStage, string> = {
  validating_input: "Đang xác thực đầu vào",
  running_quality_gate: "Đang kiểm tra chất lượng tín hiệu",
  preprocessing: "Đang tiền xử lý tín hiệu",
  windowing: "Đang phân đoạn cửa sổ",
  extracting_time_features: "Đang trích đặc trưng miền thời gian",
  estimating_spectrum: "Đang ước lượng phổ công suất",
  extracting_frequency_features: "Đang trích MDF và MNF",
  computing_trends: "Đang tính xu hướng theo thời gian",
  building_evidence: "Đang tổng hợp bằng chứng",
  running_rule_engine: "Đang chạy rule engine giải thích được",
  building_explanation: "Đang xây dựng phần giải thích",
};

const ORDER = Object.keys(LABELS) as AnalysisStage[];

export interface AnalysisJobTimelineProps { readonly job: AnalysisJob; }

export function AnalysisJobTimeline({ job }: AnalysisJobTimelineProps): JSX.Element {
  const activeIndex = job.currentStage ? ORDER.indexOf(job.currentStage) : -1;
  return (
    <section aria-labelledby="analysis-timeline-heading">
      <h2 id="analysis-timeline-heading">Tiến trình phân tích</h2>
      <p aria-live="polite" role="status">
        {job.currentStage ? `Bước ${activeIndex + 1}/${ORDER.length} — ${LABELS[job.currentStage]}` : `Trạng thái: ${job.status}`}
      </p>
      <ol>
        {ORDER.map((stage, index) => {
          const completed = job.completedStages.includes(stage);
          const active = stage === job.currentStage;
          return (
            <li key={stage} aria-current={active ? "step" : undefined}>
              <span aria-hidden="true">{completed ? "✓" : active ? "●" : "○"}</span>{" "}
              {LABELS[stage]}
            </li>
          );
        })}
      </ol>
      {job.status === "abstained" ? <div role="status">Dữ liệu không đủ điều kiện phân tích. Kiểm tra reason code và thực hiện đo lại nếu cần.</div> : null}
      {job.status === "failed" && job.error ? <div role="alert">{job.error.messageVi} Mã theo dõi: {job.error.traceId}</div> : null}
    </section>
  );
}
