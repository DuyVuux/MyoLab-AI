import type { AutomationRepository } from "./automation-repository";
import type {
  AuditEvent,
  CreateImportRequest,
  ImportJob,
  MappingResolutionReceipt,
  MappingResolutionRequest,
  MetricEvidence,
  PageResult,
  PipelineJob,
  ProcessingManifestEvidence,
  QualityAssessment,
  ReviewActionReceipt,
  ReviewActionRequest,
  ReviewCase,
  ReviewCaseDetail,
  SessionDetail,
  SessionEvidenceDetail,
  SessionEvidenceBundle,
  SessionMappingState,
  SessionPreflight,
  SessionSummary,
  SignalIndex,
  SignalWindow,
  SignalWindowRequest,
  UploadImportRequest,
} from "../../contracts/automation";
import {
  parseAuditEvent,
  parseImportJob,
  parseMappingResolutionReceipt,
  parseMetricEvidence,
  parsePipelineJob,
  parseQualityAssessment,
  parseReviewCase,
  parseSessionDetail,
  parseSessionEvidenceBundle,
  parseSessionMappingState,
  parseSessionPreflight,
  parseSessionSummary,
  parseSignalWindow,
  unwrapItems,
} from "../../contracts/automation/validators";
import {
  parseProcessingManifestEvidence,
  parseReviewActionReceipt,
  parseReviewCaseDetail,
  parseScientificSignalWindow,
  parseSessionEvidenceDetail,
  parseSignalIndex,
} from "../../contracts/automation/ui-i3-validators";
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
    return parseSessionDetail(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    );
  }

  async createImport(request: CreateImportRequest): Promise<ImportJob> {
    const path = requireVerifiedEndpoint(this.endpoints.session_import, "session_import");
    return parseImportJob(await this.http.json<unknown>(path, {
      method: "POST",
      body: JSON.stringify(request),
    }));
  }

  async uploadImport(request: UploadImportRequest): Promise<ImportJob> {
    const path = requireVerifiedEndpoint(
      this.endpoints.session_import_upload,
      "session_import_upload",
    );
    const form = new FormData();
    form.set("file", request.file);
    if (request.expected_format) form.set("expected_format", request.expected_format);
    return parseImportJob(await this.http.form<unknown>(path, form));
  }

  async getPipelineJob(jobId: string): Promise<PipelineJob> {
    const tpl = requireVerifiedEndpoint(this.endpoints.pipeline_job, "pipeline_job");
    return parsePipelineJob(
      await this.http.json<unknown>(resolveTemplate(tpl, { jobId })),
    );
  }

  async getPreflight(sessionId: string): Promise<SessionPreflight> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_preflight, "session_preflight");
    return parseSessionPreflight(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    );
  }

  async getMapping(sessionId: string): Promise<SessionMappingState> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_mapping, "session_mapping");
    return parseSessionMappingState(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    );
  }

  async resolveMapping(
    sessionId: string,
    request: MappingResolutionRequest,
  ): Promise<MappingResolutionReceipt> {
    const tpl = requireVerifiedEndpoint(
      this.endpoints.session_mapping_resolve,
      "session_mapping_resolve",
    );
    return parseMappingResolutionReceipt(await this.http.json<unknown>(
      resolveTemplate(tpl, { sessionId }),
      { method: "POST", body: JSON.stringify(request) },
    ));
  }

  async getQuality(sessionId: string): Promise<QualityAssessment> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_quality, "session_quality");
    return parseQualityAssessment(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    );
  }

  async getSignalIndex(sessionId: string): Promise<SignalIndex> {
    const tpl = requireVerifiedEndpoint(this.endpoints.signal_index, "signal_index");
    return parseSignalIndex(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    );
  }

  async getSignalWindow(request: SignalWindowRequest): Promise<SignalWindow> {
    const tpl = requireVerifiedEndpoint(this.endpoints.signal_window, "signal_window");
    const base = resolveTemplate(tpl, {
      sessionId: request.session_id,
      channelId: request.channel_id,
    });
    const qs = new URLSearchParams({
      start: String(request.start_s),
      end: String(request.end_s),
      representation: request.representation,
    });
    return parseScientificSignalWindow(await this.http.json<unknown>(`${base}?${qs}`));
  }

  async getProcessingManifest(manifestId: string): Promise<ProcessingManifestEvidence> {
    const tpl = requireVerifiedEndpoint(this.endpoints.processing_manifest, "processing_manifest");
    return parseProcessingManifestEvidence(
      await this.http.json<unknown>(resolveTemplate(tpl, { manifestId })),
    );
  }

  async getMetrics(sessionId: string): Promise<MetricEvidence[]> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_metrics, "session_metrics");
    const body = await this.http.json<unknown>(resolveTemplate(tpl, { sessionId }));
    return unwrapItems(body).map(parseMetricEvidence);
  }

  async getEvidence(sessionId: string): Promise<SessionEvidenceBundle> {
    const detail = await this.getSessionEvidenceDetail(sessionId);
    return parseSessionEvidenceBundle({
      session_id: detail.session_id,
      provenance: detail.provenance ?? { source_hash: detail.source_hash },
      quality: detail.quality,
      metrics: detail.metrics,
      limitations: detail.limitations,
      review_case_ids: detail.review_case_ids,
      evidence_refs: detail.evidence_refs,
    });
  }

  async getSessionEvidenceDetail(sessionId: string): Promise<SessionEvidenceDetail> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_evidence, "session_evidence");
    return parseSessionEvidenceDetail(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    );
  }

  async listReviewCases(): Promise<ReviewCase[]> {
    return (await this.listReviewCaseDetails()).map(parseReviewCase);
  }

  async listReviewCaseDetails(sessionId?: string): Promise<ReviewCaseDetail[]> {
    const path = requireVerifiedEndpoint(this.endpoints.review_cases, "review_cases");
    const qs = sessionId ? `?${new URLSearchParams({ session_id: sessionId })}` : "";
    return unwrapItems(await this.http.json<unknown>(`${path}${qs}`)).map(parseReviewCaseDetail);
  }

  async getReviewCase(caseId: string): Promise<ReviewCaseDetail> {
    const tpl = requireVerifiedEndpoint(this.endpoints.review_case, "review_case");
    return parseReviewCaseDetail(
      await this.http.json<unknown>(resolveTemplate(tpl, { caseId })),
    );
  }

  async submitReviewAction(
    caseId: string,
    request: ReviewActionRequest,
  ): Promise<ReviewActionReceipt> {
    const tpl = requireVerifiedEndpoint(this.endpoints.review_action, "review_action");
    return parseReviewActionReceipt(await this.http.json<unknown>(
      resolveTemplate(tpl, { caseId }),
      { method: "POST", body: JSON.stringify(request) },
    ));
  }

  async getAuditTrail(sessionId: string): Promise<AuditEvent[]> {
    const tpl = requireVerifiedEndpoint(this.endpoints.session_audit, "session_audit");
    return unwrapItems(
      await this.http.json<unknown>(resolveTemplate(tpl, { sessionId })),
    ).map(parseAuditEvent);
  }
}
