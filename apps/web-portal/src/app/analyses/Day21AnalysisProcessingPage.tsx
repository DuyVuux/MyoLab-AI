"use client";

import { useMemo } from "react";

import { AnalysisJobTimeline } from "../../components/analysis/AnalysisJobTimeline";
import { HttpAnalysisClient } from "../../lib/analysis-client";
import { useAnalysisJob } from "../../hooks/useAnalysisJob";

export interface Day21AnalysisProcessingPageProps { readonly analysisId: string; }

export function Day21AnalysisProcessingPage({ analysisId }: Day21AnalysisProcessingPageProps): JSX.Element {
  const client = useMemo(() => new HttpAnalysisClient(), []);
  const { job, loading, error } = useAnalysisJob(client, analysisId);
  if (loading && !job) return <p role="status">Đang tải trạng thái phân tích…</p>;
  if (error) return <div role="alert">Không thể tải analysis job: {error}</div>;
  if (!job) return <p>Không tìm thấy analysis job.</p>;
  return (
    <main>
      <h1>Phiên phân tích {job.analysisId}</h1>
      <p>Độ tin cậy kỹ thuật không phải xác suất lâm sàng. Kết quả yêu cầu human review.</p>
      <AnalysisJobTimeline job={job} />
    </main>
  );
}
