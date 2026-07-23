export type MockScenarioId =
  | "default"
  | "slow_network"
  | "empty_queues"
  | "service_unavailable";

export interface MockScenario {
  readonly id: MockScenarioId;
  readonly latencyMs: number;
  readonly forceError: boolean;
  readonly emptyQueues: boolean;
}

export const mockScenarios: Readonly<Record<MockScenarioId, MockScenario>> = {
  default: { id: "default", latencyMs: 80, forceError: false, emptyQueues: false },
  slow_network: { id: "slow_network", latencyMs: 650, forceError: false, emptyQueues: false },
  empty_queues: { id: "empty_queues", latencyMs: 80, forceError: false, emptyQueues: true },
  service_unavailable: {
    id: "service_unavailable",
    latencyMs: 80,
    forceError: true,
    emptyQueues: false,
  },
};
