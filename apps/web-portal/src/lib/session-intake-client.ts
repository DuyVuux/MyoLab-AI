import type { AnalysisHandoff } from "../schemas/analysis-handoff.schema";
import type { CalibrationRecord } from "../schemas/calibration.schema";
import type { ChannelMapping } from "../schemas/channel-mapping.schema";
import type { SignalImportRecord } from "../schemas/import-workflow.schema";
import type { PreflightSummary } from "../schemas/preflight.schema";
import type { DetailedQualityResult } from "../schemas/quality-gate.schema";
import type { SessionDraft, SessionRecord } from "../schemas/session-intake.schema";

export interface SessionIntakeClient {
  createSession(input: SessionDraft, idempotencyKey: string): Promise<SessionRecord>;
  getSession(sessionId: string): Promise<SessionRecord>;
  startImport(sessionId: string, scenarioId: string): Promise<SignalImportRecord>;
  getImport(importId: string): Promise<SignalImportRecord>;
  saveMapping(importId: string, mappings: readonly ChannelMapping[]): Promise<SignalImportRecord>;
  getPreflight(sessionId: string): Promise<PreflightSummary>;
  runCalibration(sessionId: string, scenarioId: string): Promise<CalibrationRecord>;
  getQuality(sessionId: string, scenarioId: string): Promise<DetailedQualityResult>;
  acknowledgeQualityWarning(sessionId: string, reviewerRef: string, reason: string): Promise<DetailedQualityResult>;
  createAnalysisHandoff(sessionId: string): Promise<AnalysisHandoff>;
}

export class HttpSessionIntakeClient implements SessionIntakeClient {
  public constructor(private readonly baseUrl = "") {}

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`HTTP_${response.status}:${body}`);
    }
    return response.json() as Promise<T>;
  }

  public createSession(input: SessionDraft, idempotencyKey: string): Promise<SessionRecord> {
    return this.request("/v1/sessions", { method: "POST", headers: { "Idempotency-Key": idempotencyKey }, body: JSON.stringify(input) });
  }
  public getSession(sessionId: string): Promise<SessionRecord> { return this.request(`/v1/sessions/${sessionId}`); }
  public startImport(sessionId: string, scenarioId: string): Promise<SignalImportRecord> { return this.request(`/v1/sessions/${sessionId}/imports`, { method: "POST", body: JSON.stringify({ scenario_id: scenarioId }) }); }
  public getImport(importId: string): Promise<SignalImportRecord> { return this.request(`/v1/imports/${importId}`); }
  public saveMapping(importId: string, mappings: readonly ChannelMapping[]): Promise<SignalImportRecord> { return this.request(`/v1/imports/${importId}/mapping`, { method: "PUT", body: JSON.stringify({ mappings }) }); }
  public getPreflight(sessionId: string): Promise<PreflightSummary> { return this.request(`/v1/sessions/${sessionId}/preflight`); }
  public runCalibration(sessionId: string, scenarioId: string): Promise<CalibrationRecord> { return this.request(`/v1/sessions/${sessionId}/calibrations`, { method: "POST", body: JSON.stringify({ scenario_id: scenarioId }) }); }
  public getQuality(sessionId: string, scenarioId: string): Promise<DetailedQualityResult> { return this.request(`/v1/sessions/${sessionId}/quality?scenario_id=${encodeURIComponent(scenarioId)}`); }
  public acknowledgeQualityWarning(sessionId: string, reviewerRef: string, reason: string): Promise<DetailedQualityResult> { return this.request(`/v1/sessions/${sessionId}/quality/acknowledgements`, { method: "POST", body: JSON.stringify({ reviewer_ref: reviewerRef, reason }) }); }
  public createAnalysisHandoff(sessionId: string): Promise<AnalysisHandoff> { return this.request(`/v1/sessions/${sessionId}/analyses`, { method: "POST" }); }
}
