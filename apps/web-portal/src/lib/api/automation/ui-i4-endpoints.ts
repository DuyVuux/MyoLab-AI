export type UiI4Verification = "VERIFIED" | "CANDIDATE" | "UNAVAILABLE";

export interface UiI4Endpoint {
  template: string | null;
  method: "GET";
  verification: UiI4Verification;
  evidence?: string;
}

export interface UiI4EndpointCatalog {
  operations_summary: UiI4Endpoint;
}

export const SOURCE_CANDIDATE_UI_I4_ENDPOINTS: UiI4EndpointCatalog = {
  operations_summary: {
    template: "/v1/operations/summary",
    method: "GET",
    verification: "CANDIDATE",
    evidence: "UI-I4 adapter candidate; live canonical binding required",
  },
};
