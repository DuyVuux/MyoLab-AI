import type { DataMode } from "../../contracts/automation";
import type { AutomationRepository } from "./automation-repository";
import type { LegacyMockAutomationBridge } from "./mock-automation-repository";
import { MockAutomationRepository } from "./mock-automation-repository";
import { RealAutomationRepository } from "./real-automation-repository";
import { AutomationHttpClient } from "../../lib/api/automation/http";
import type { AutomationEndpointCatalog } from "../../lib/api/automation/endpoints";

export interface RepositoryFactoryOptions {
  mode: DataMode;
  apiBaseUrl?: string;
  endpoints?: AutomationEndpointCatalog;
  mockBridge?: LegacyMockAutomationBridge;
  fetchImpl?: typeof fetch;
}

export function createAutomationRepository(options: RepositoryFactoryOptions): AutomationRepository {
  if (options.mode === "mock") {
    if (!options.mockBridge) throw new Error("MOCK_AUTOMATION_BRIDGE_REQUIRED");
    return new MockAutomationRepository(options.mockBridge);
  }
  if (!options.apiBaseUrl) throw new Error("AUTOMATION_API_BASE_URL_REQUIRED");
  if (!options.endpoints) throw new Error("VERIFIED_ENDPOINT_CATALOG_REQUIRED");
  return new RealAutomationRepository(
    new AutomationHttpClient({ baseUrl: options.apiBaseUrl, fetchImpl: options.fetchImpl }),
    options.endpoints,
  );
}
