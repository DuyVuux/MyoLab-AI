import { createAutomationRepository } from "../repository-factory";

describe("UI-I1 repository factory", () => {
  test("real mode fails closed without verified catalog", () => {
    expect(() => createAutomationRepository({ mode: "real", apiBaseUrl: "http://localhost:8000" }))
      .toThrow("VERIFIED_ENDPOINT_CATALOG_REQUIRED");
  });

  test("mock mode requires explicit legacy bridge", () => {
    expect(() => createAutomationRepository({ mode: "mock" })).toThrow("MOCK_AUTOMATION_BRIDGE_REQUIRED");
  });
});
