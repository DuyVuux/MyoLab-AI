import { requireVerifiedEndpoint, resolveTemplate, SOURCE_CANDIDATE_AUTOMATION_ENDPOINTS } from "../../../lib/api/automation/endpoints";

describe("UI-I1 endpoint verification", () => {
  test("candidate endpoint cannot be used as verified real contract", () => {
    expect(() => requireVerifiedEndpoint(SOURCE_CANDIDATE_AUTOMATION_ENDPOINTS.session_import, "session_import"))
      .toThrow("BACKEND_CONTRACT_NOT_VERIFIED");
  });

  test("templates encode params", () => {
    expect(resolveTemplate("/v1/sessions/{sessionId}", { sessionId: "A/B" }))
      .toBe("/v1/sessions/A%2FB");
  });
});
