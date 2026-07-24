import type { ClinicalReportPackageContract } from "../../schemas/review-report.schema";

export interface ReportPreviewPanelProps {
  report: ClinicalReportPackageContract;
}

export function ReportPreviewPanel({
  report,
}: ReportPreviewPanelProps): JSX.Element {
  return (
    <article aria-labelledby="report-preview-title">
      <h2 id="report-preview-title">Xem trước báo cáo</h2>
      {report.watermark && <div role="status">{report.watermark}</div>}
      <p>Trạng thái: {report.status}</p>
      <p>Template: {report.templateVersion}</p>
      <p>
        Report hash: <code>{report.reportHashSha256}</code>
      </p>
      <p>Kết quả cần human review và không thay thế quyết định lâm sàng.</p>
    </article>
  );
}
