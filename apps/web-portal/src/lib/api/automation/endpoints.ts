export type EndpointVerification = "VERIFIED" | "CANDIDATE" | "UNAVAILABLE";

export interface EndpointTemplate {
  template: string | null;
  verification: EndpointVerification;
  evidence?: string;
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
}

export interface AutomationEndpointCatalog {
  sessions_collection: EndpointTemplate;
  session_detail: EndpointTemplate;
  session_import: EndpointTemplate;
  session_import_upload: EndpointTemplate;
  pipeline_job: EndpointTemplate;
  session_preflight: EndpointTemplate;
  session_mapping: EndpointTemplate;
  session_mapping_resolve: EndpointTemplate;
  session_quality: EndpointTemplate;
  signal_window: EndpointTemplate;
  session_metrics: EndpointTemplate;
  session_evidence: EndpointTemplate;
  review_cases: EndpointTemplate;
  session_audit: EndpointTemplate;
}

export const SOURCE_CANDIDATE_AUTOMATION_ENDPOINTS: AutomationEndpointCatalog = {
  sessions_collection: {
    template: "/v1/sessions",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "UI-I1 source candidate; live decorator required",
  },
  session_detail: {
    template: "/v1/sessions/{sessionId}",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "UI-I1 source candidate; live decorator required",
  },
  session_import: {
    template: "/v1/sessions/import",
    method: "POST",
    verification: "CANDIDATE",
    evidence: "source-supported API candidate; live binding required",
  },
  session_import_upload: {
    template: "/v1/sessions/import/upload",
    method: "POST",
    verification: "CANDIDATE",
    evidence: "UI-I2 explicit multipart adapter endpoint; must be registered and bound before verification",
  },
  pipeline_job: {
    template: "/v1/analyses/{jobId}",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "Live api-server exposes GET /v1/analyses/{analysis_id}; contract shape still requires live binding audit",
  },
  session_preflight: {
    template: "/v1/sessions/{sessionId}/preflight",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "UI-I2 adapter contract; live binding required",
  },
  session_mapping: {
    template: "/v1/sessions/{sessionId}/mapping",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "UI-I2 adapter contract; live binding required",
  },
  session_mapping_resolve: {
    template: "/v1/sessions/{sessionId}/mapping/resolve",
    method: "POST",
    verification: "CANDIDATE",
    evidence: "UI-I2 adapter contract; live binding required",
  },
  session_quality: {
    template: "/v1/sessions/{sessionId}/quality",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "source-supported API candidate; live binding required",
  },
  signal_window: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "deferred to UI-I3",
  },
  session_metrics: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "deferred to UI-I3 evidence integration",
  },
  session_evidence: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "deferred to UI-I3 evidence integration",
  },
  review_cases: {
    template: "/v1/review-cases",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "existing ReviewReportClient; deferred consumer migration to UI-I3",
  },
  session_audit: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "deferred to UI-I3",
  },
};

export function resolveTemplate(template: string, params: Record<string, string | number>): string {
  return template.replace(/\{([^}]+)\}/g, (_, key: string) => {
    const value = params[key];
    if (value === undefined) throw new Error(`MISSING_ENDPOINT_PARAM:${key}`);
    return encodeURIComponent(String(value));
  });
}

export function requireVerifiedEndpoint(endpoint: EndpointTemplate, name: string): string {
  if (endpoint.verification !== "VERIFIED" || !endpoint.template) {
    throw new Error(`BACKEND_CONTRACT_NOT_VERIFIED:${name}`);
  }
  return endpoint.template;
}
