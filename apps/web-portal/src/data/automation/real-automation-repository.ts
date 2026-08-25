import type { AutomationRepository } from "./automation-repository";
import type {
  AuditEvent, CreateImportRequest, ImportJob, MetricEvidence, PageResult, PipelineJob,
  QualityAssessment, ReviewCase, SessionDetail, SessionEvidenceBundle, SessionSummary,
  SignalWindow, SignalWindowRequest,
} from "../../contracts/automation";
import {
  parseAuditEvent, parseImportJob, parseMetricEvidence, parsePipelineJob,
  parseQualityAssessment, parseReviewCase, parseSessionDetail, parseSessionEvidenceBundle,
  parseSessionSummary, parseSignalWindow, unwrapItems,
} from "../../contracts/automation/validators";
import { AutomationHttpClient } from "../../lib/api/automation/http";
import {
  type AutomationEndpointCatalog,
  requireVerifiedEndpoint,
  resolveTemplate,
} from "../../lib/api/automation/endpoints";

export class RealAutomationRepository implements AutomationRepository {
  constructor(
    private readonly http: AutomationHttpClient,
    private readonly endpoints: AutomationEndpointCatalog,
  ) {}

  async listSessions(): Promise<PageResult<SessionSummary>> {
    const path = requireVerifiedEndpoint(this.endpoints.sessions_collection, "sessions_collection");
    const body = await this.http.json<unknown>(path);
    return { items: unwrapItems(body).map(parseSessionSummary) };
  }

  async getSession(sessionId: string): Promise<SessionDetail> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_detail, "session_detail");
    return parseSessionDetail(await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })));
  }

  async createImport(request: CreateImportRequest): Promise<ImportJob> {
    const path = requireVerifiedEndpoint(this.endpoints.session_import, "session_import");
    return parseImportJob(await this.http.json<unknown>(path, {
      method: "POST",
      body: JSON.stringify(request),
    }));
  }

  async getPipelineJob(jobId: string): Promise<PipelineJob> {
    const tpl = requireVerifiedEndpoint(this.endpoints.pipeline_job, "pipeline_job");
    return parsePipelineJob(await this.http.json<unknown>(resolveTemplate(tpl, { jobId })));
  }

  async getQuality(sessionId: string): Promise<QualityAssessment> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_quality, "session_quality");
    return parseQualityAssessment(await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })));
  }

  async getSignalWindow(request: SignalWindowRequest): Promise<SignalWindow> {
    const tpl = requireVerifiedEndpoint(this.endpoints.signal_window, "signal_window");
    const base = resolveTemplate(tpl, { sessionId: request.session_id, channelId: request.channel_id });
    const qs = new URLSearchParams({
      start: String(request.start_s), end: String(request.end_s), representation: request.representation,
    });
    return parseSignalWindow(await this.http.json<unknown>(`${base}?${qs}`));
  }

  async getMetrics(sessionId: string): Promise<MetricEvidence[]> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_metrics, "session_metrics");
    const body = await this.http.json<unknown>(resolveTemplate(tpl, { sessionId }));
    return unwrapItems(body).map(parseMetricEvidence);
  }

  async getEvidence(sessionId: string): Promise<SessionEvidenceBundle> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_evidence, "session_evidence");
    return parseSessionEvidenceBundle(await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })));
  }

  async listReviewCases(): Promise<ReviewCase[]> {
    const path = requireVerifiedEndpoint(this.endpoints.review_cases, "review_cases");
    return unwrapItems(await this.http.json<unknown>(path)).map(parseReviewCase);
  }

  async getAuditTrail(sessionId: string): Promise<AuditEvent[]> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_audit, "session_audit");
    return unwrapItems(await this.http.json<unknown>(resolveTemplate(tpl, { sessionId }))).map(parseAuditEvent);
  }
}
