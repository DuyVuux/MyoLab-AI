import type {
  FeedbackActorRole,
  GestureFeedbackRequest,
  GestureFeedbackReceipt,
} from "../schemas/gesture-feedback-context.schema";
import type {
  UC1ReplayScenarioId,
  UC1ReplaySession,
} from "../schemas/gesture-inference.schema";
import {
  isFeedbackActorRole,
  isFeedbackReceiptFor,
  isFeedbackRequestForReplay,
  isReplayAdvanceFor,
  isReplayCreatedFor,
  isSafeReplayPayload,
} from "../utils/uc1ReplayValidation";

export interface CreateUC1ReplayInput {
  readonly analysisId: string;
  readonly scenarioId: UC1ReplayScenarioId;
}

export interface AdvanceUC1ReplayInput {
  readonly expectedCurrentIndex: number;
  readonly expectedRevision: number;
}

export interface ReplayRequestOptions {
  readonly signal?: AbortSignal;
}

export interface IdempotentReplayRequestOptions extends ReplayRequestOptions {
  readonly idempotencyKey: string;
}

export interface AdvanceReplayRequestOptions extends ReplayRequestOptions {
  readonly expectedReplay: UC1ReplaySession;
}

export interface FeedbackRequestOptions
  extends IdempotentReplayRequestOptions {
  readonly actorRole: FeedbackActorRole;
  readonly expectedReplay: UC1ReplaySession;
}

export interface UC1ReplayClient {
  createReplay(
    sessionId: string,
    input: CreateUC1ReplayInput,
    options: IdempotentReplayRequestOptions,
  ): Promise<UC1ReplaySession>;
  advanceReplay(
    replayId: string,
    input: AdvanceUC1ReplayInput,
    options: AdvanceReplayRequestOptions,
  ): Promise<UC1ReplaySession>;
  submitFeedback(
    replayId: string,
    request: GestureFeedbackRequest,
    options: FeedbackRequestOptions,
  ): Promise<GestureFeedbackReceipt>;
}

interface ProblemDetails {
  readonly detail?: string;
  readonly error_code?: string;
  readonly title?: string;
}

export class UC1ReplayClientError extends Error {
  public constructor(
    public readonly status: number,
    public readonly code: string,
    public readonly detail?: string,
  ) {
    super(code);
    this.name = "UC1ReplayClientError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

async function readProblem(response: Response): Promise<ProblemDetails> {
  try {
    const payload: unknown = await response.json();
    return isRecord(payload) ? (payload as ProblemDetails) : {};
  } catch {
    return {};
  }
}

export class HttpUC1ReplayClient implements UC1ReplayClient {
  public constructor(private readonly baseUrl = "") {}

  private async request<T>(
    path: string,
    init: RequestInit,
    validate?: (value: unknown) => asserts value is T,
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    });
    if (!response.ok) {
      const problem = await readProblem(response);
      throw new UC1ReplayClientError(
        response.status,
        problem.error_code ?? `HTTP_${response.status}`,
        problem.detail ?? problem.title,
      );
    }

    const payload: unknown = await response.json();
    validate?.(payload);
    return payload as T;
  }

  public createReplay(
    sessionId: string,
    input: CreateUC1ReplayInput,
    options: IdempotentReplayRequestOptions,
  ): Promise<UC1ReplaySession> {
    const validateCreatedReplay: (
      value: unknown,
    ) => asserts value is UC1ReplaySession = (
      value,
    ): asserts value is UC1ReplaySession => {
      if (
        !isReplayCreatedFor(
          value,
          sessionId,
          input.analysisId,
          input.scenarioId,
        )
      ) {
        throw new UC1ReplayClientError(502, "INVALID_REPLAY_RESPONSE");
      }
    };

    return this.request(
      `/v1/uc1/sessions/${encodeURIComponent(sessionId)}/replays`,
      {
        method: "POST",
        signal: options.signal,
        headers: { "Idempotency-Key": options.idempotencyKey },
        body: JSON.stringify(input),
      },
      validateCreatedReplay,
    );
  }

  public advanceReplay(
    replayId: string,
    input: AdvanceUC1ReplayInput,
    options: AdvanceReplayRequestOptions,
  ): Promise<UC1ReplaySession> {
    const previousReplay = options.expectedReplay;
    if (
      !isSafeReplayPayload(previousReplay) ||
      previousReplay.replayId !== replayId ||
      !["idle", "running"].includes(previousReplay.state) ||
      input.expectedCurrentIndex !== previousReplay.currentIndex ||
      input.expectedRevision !== previousReplay.revision
    ) {
      return Promise.reject(
        new UC1ReplayClientError(
          409,
          "INVALID_REPLAY_ADVANCE_CONTEXT",
        ),
      );
    }

    const validateAdvancedReplay: (
      value: unknown,
    ) => asserts value is UC1ReplaySession = (
      value,
    ): asserts value is UC1ReplaySession => {
      if (!isReplayAdvanceFor(value, previousReplay)) {
        throw new UC1ReplayClientError(502, "INVALID_REPLAY_RESPONSE");
      }
    };

    return this.request(
      `/v1/uc1/replays/${encodeURIComponent(replayId)}/advance`,
      {
        method: "POST",
        signal: options.signal,
        body: JSON.stringify(input),
      },
      validateAdvancedReplay,
    );
  }

  public submitFeedback(
    replayId: string,
    request: GestureFeedbackRequest,
    options: FeedbackRequestOptions,
  ): Promise<GestureFeedbackReceipt> {
    if (!isFeedbackActorRole(options.actorRole)) {
      return Promise.reject(
        new UC1ReplayClientError(403, "FEEDBACK_ROLE_FORBIDDEN"),
      );
    }
    if (
      !isFeedbackRequestForReplay(
        request,
        replayId,
        options.actorRole,
        options.expectedReplay,
      )
    ) {
      return Promise.reject(
        new UC1ReplayClientError(
          422,
          "INVALID_FEEDBACK_REQUEST_CONTEXT",
        ),
      );
    }

    const validateReceipt: (
      value: unknown,
    ) => asserts value is GestureFeedbackReceipt = (
      value,
    ): asserts value is GestureFeedbackReceipt => {
      if (
        !isFeedbackReceiptFor(
          value,
          replayId,
          request,
          options.actorRole,
          options.expectedReplay,
        )
      ) {
        throw new UC1ReplayClientError(502, "INVALID_FEEDBACK_RESPONSE");
      }
    };

    return this.request(
      `/v1/uc1/replays/${encodeURIComponent(replayId)}/feedback`,
      {
        method: "POST",
        signal: options.signal,
        headers: {
          "Idempotency-Key": options.idempotencyKey,
          "X-Actor-Role": options.actorRole,
        },
        body: JSON.stringify(request),
      },
      validateReceipt,
    );
  }
}
