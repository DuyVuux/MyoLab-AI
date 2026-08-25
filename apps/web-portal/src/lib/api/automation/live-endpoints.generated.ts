import type { AutomationEndpointCatalog } from "./endpoints";

/** GENERATED FROM LIVE ROUTE DECORATORS — DO NOT HAND-EDIT */
export const LIVE_AUTOMATION_ENDPOINTS: AutomationEndpointCatalog = {
  sessions_collection: {
    template: "/v1/sessions",
    verification: "VERIFIED",
    method: "GET",
    evidence: "services/api-server/src/ui_i2/routes.py:40",
  },
  session_detail: {
    template: "/v1/sessions/{sessionId}",
    verification: "VERIFIED",
    method: "GET",
    evidence: "services/api-server/src/ui_i2/routes.py:44",
  },
  session_import: {
    template: "/v1/sessions/import",
    verification: "VERIFIED",
    method: "POST",
    evidence: "services/api-server/src/ui_i2/routes.py:48",
  },
  session_import_upload: {
    template: "/v1/sessions/import/upload",
    verification: "VERIFIED",
    method: "POST",
    evidence: "services/api-server/src/ui_i2/routes.py:99",
  },
  pipeline_job: {
    template: "/v1/analyses/{jobId}",
    verification: "VERIFIED",
    method: "GET",
    evidence: "services/api-server/src/routes/analysis_jobs.py:35",
  },
  session_preflight: {
    template: "/v1/sessions/{sessionId}/preflight",
    verification: "VERIFIED",
    method: "GET",
    evidence: "services/api-server/src/ui_i2/routes.py:112",
  },
  session_mapping: {
    template: "/v1/sessions/{sessionId}/mapping",
    verification: "VERIFIED",
    method: "GET",
    evidence: "services/api-server/src/ui_i2/routes.py:116",
  },
  session_mapping_resolve: {
    template: "/v1/sessions/{sessionId}/mapping/resolve",
    verification: "VERIFIED",
    method: "POST",
    evidence: "services/api-server/src/ui_i2/routes.py:123",
  },
  session_quality: {
    template: "/v1/sessions/{sessionId}/quality",
    verification: "VERIFIED",
    method: "GET",
    evidence: "services/api-server/src/ui_i2/routes.py:131",
  },
  signal_window: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "Deferred to UI-I3",
  },
  session_metrics: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "Deferred to UI-I3",
  },
  session_evidence: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "Deferred to UI-I3",
  },
  review_cases: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "Deferred to UI-I3",
  },
  session_audit: {
    template: null,
    verification: "UNAVAILABLE",
    evidence: "Deferred to UI-I3",
  },
};
