import type { AnalysisJob, AnalysisStage } from "../schemas/analysis-job.schema";

export type PrototypeAnalysisScenario =
  | "golden_completed" | "warning_completed" | "qc_abstained" | "runtime_failed";

export interface AnalysisClient {
  createJob(sessionId: string, scenarioId: PrototypeAnalysisScenario, idempotencyKey: string): Promise<AnalysisJob>;
  getJob(analysisId: string): Promise<AnalysisJob>;
  advanceJob(analysisId: string, expectedCurrentStage: AnalysisStage | null): Promise<AnalysisJob>;
  cancelJob(analysisId: string): Promise<AnalysisJob>;
  getSummary<TSummary = unknown>(analysisId: string): Promise<TSummary>;
}

export class HttpAnalysisClient implements AnalysisClient {
  public constructor(private readonly baseUrl = "") {}

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
    if (!response.ok) throw new Error(`HTTP_${response.status}:${await response.text()}`);
    return response.json() as Promise<T>;
  }

  public createJob(sessionId: string, scenarioId: PrototypeAnalysisScenario, idempotencyKey: string): Promise<AnalysisJob> {
    return this.request(`/v1/sessions/${encodeURIComponent(sessionId)}/analysis-jobs`, {
      method: "POST", headers: { "Idempotency-Key": idempotencyKey }, body: JSON.stringify({ scenarioId }),
    });
  }
  public getJob(analysisId: string): Promise<AnalysisJob> {
    return this.request(`/v1/analyses/${encodeURIComponent(analysisId)}`);
  }
  public advanceJob(analysisId: string, expectedCurrentStage: AnalysisStage | null): Promise<AnalysisJob> {
    return this.request(`/v1/analyses/${encodeURIComponent(analysisId)}/advance`, {
      method: "POST", body: JSON.stringify({ expectedCurrentStage }),
    });
  }
  public cancelJob(analysisId: string): Promise<AnalysisJob> {
    return this.request(`/v1/analyses/${encodeURIComponent(analysisId)}/cancel`, { method: "POST" });
  }
  public getSummary<TSummary = unknown>(analysisId: string): Promise<TSummary> {
    return this.request(`/v1/analyses/${encodeURIComponent(analysisId)}/summary`);
  }
}
