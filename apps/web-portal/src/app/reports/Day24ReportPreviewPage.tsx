import type { ClinicalReportPackageContract } from "../../schemas/review-report.schema";
import { ReportPreviewPanel } from "../../components/review/ReportPreviewPanel";

export interface Day24ReportPreviewPageProps {
  report: ClinicalReportPackageContract;
}

export function Day24ReportPreviewPage({
  report,
}: Day24ReportPreviewPageProps): JSX.Element {
  return (
    <main>
      <h1>Báo cáo bằng chứng sEMG</h1>
      <ReportPreviewPanel report={report} />
    </main>
  );
}
