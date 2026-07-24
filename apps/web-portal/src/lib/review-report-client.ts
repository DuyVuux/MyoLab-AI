import type {
  ClinicalReportPackageContract,
  ReviewCaseContract,
  ReviewEventContract,
} from '@/schemas/review-report.schema';

export interface CreateReviewCaseRequest {
  readonly analysisId: string;
  readonly originalResultHash: string;
  readonly analysisStatus: 'completed' | 'completed_with_warnings' | 'abstained';
}

export interface ReportBuildRequest {
  readonly reviewCase: ReviewCaseContract;
  readonly analysisSummary: Record<string, unknown>;
  readonly finalize?: boolean;
  readonly templateVersion?: string;
}

export class ReviewReportClient {
  public constructor(private readonly baseUrl = '') {}

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`HTTP_${response.status}: ${detail}`);
    }

    return response.json() as Promise<T>;
  }

  public createReviewCase(
    body: CreateReviewCaseRequest,
  ): Promise<ReviewCaseContract> {
    return this.request('/v1/review-cases', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  public getReviewCase(caseId: string): Promise<ReviewCaseContract> {
    return this.request(`/v1/review-cases/${encodeURIComponent(caseId)}`);
  }

  public addReviewEvent(
    caseId: string,
    event: ReviewEventContract,
  ): Promise<ReviewCaseContract> {
    return this.request(`/v1/review-cases/${encodeURIComponent(caseId)}/events`, {
      method: 'POST',
      body: JSON.stringify(event),
    });
  }

  public previewReport(
    body: ReportBuildRequest,
  ): Promise<ClinicalReportPackageContract> {
    return this.request('/v1/reports/preview', {
      method: 'POST',
      body: JSON.stringify({ ...body, finalize: false }),
    });
  }

  public finalizeReport(
    body: ReportBuildRequest,
  ): Promise<ClinicalReportPackageContract> {
    return this.request('/v1/reports/finalize', {
      method: 'POST',
      body: JSON.stringify({ ...body, finalize: true }),
    });
  }

  public getReport(reportId: string): Promise<ClinicalReportPackageContract> {
    return this.request(`/v1/reports/${encodeURIComponent(reportId)}`);
  }
}
