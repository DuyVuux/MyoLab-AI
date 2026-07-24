"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type {
  FeedbackActorRole,
  GestureFeedbackDecision,
  GestureFeedbackReceipt,
} from "../schemas/gesture-feedback-context.schema";
import type {
  UC1ReplayScenarioId,
  UC1ReplaySession,
} from "../schemas/gesture-inference.schema";
import type { UC1ReplayClient } from "../lib/uc1-replay-client";
import {
  canApplyReplayMutation,
  getOrCreateOpaqueIdempotencyKey,
  isFeedbackActorRole,
} from "../utils/uc1ReplayValidation";

export interface UseUC1ReplayOptions {
  readonly client: UC1ReplayClient;
  readonly sessionId: string;
  readonly analysisId: string;
  readonly scenarioId: UC1ReplayScenarioId;
}

export interface UseUC1ReplayResult {
  readonly replay: UC1ReplaySession | null;
  readonly loading: boolean;
  readonly mutationPending: boolean;
  readonly errorCode: string | null;
  readonly feedbackReceipt: GestureFeedbackReceipt | null;
  readonly feedbackErrorCode: string | null;
  readonly advance: () => Promise<void>;
  readonly submitFeedback: (
    decision: GestureFeedbackDecision,
    actorRole: FeedbackActorRole,
  ) => Promise<void>;
}

function isAbortError(reason: unknown): boolean {
  return (
    reason instanceof DOMException
      ? reason.name === "AbortError"
      : reason instanceof Error && reason.name === "AbortError"
  );
}

function requestErrorCode(reason: unknown, fallback: string): string {
  if (
    typeof reason === "object" &&
    reason !== null &&
    "code" in reason &&
    typeof reason.code === "string"
  ) {
    return reason.code;
  }
  return fallback;
}

function requestFingerprint(parts: readonly unknown[]): string {
  return JSON.stringify(parts);
}

export function useUC1Replay({
  client,
  sessionId,
  analysisId,
  scenarioId,
}: UseUC1ReplayOptions): UseUC1ReplayResult {
  const [replay, setReplay] = useState<UC1ReplaySession | null>(null);
  const [loading, setLoading] = useState(true);
  const [mutationPending, setMutationPending] = useState(false);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [feedbackReceipt, setFeedbackReceipt] =
    useState<GestureFeedbackReceipt | null>(null);
  const [feedbackErrorCode, setFeedbackErrorCode] = useState<string | null>(null);
  const mountedRef = useRef(false);
  const requestGenerationRef = useRef(0);
  const mutationLockedRef = useRef(false);
  const mutationAbortRef = useRef<AbortController | null>(null);
  const idempotencyKeysRef = useRef(new Map<string, string>());

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      requestGenerationRef.current += 1;
      mutationAbortRef.current?.abort();
      mutationAbortRef.current = null;
      mutationLockedRef.current = false;
    };
  }, []);

  useEffect(() => {
    const generation = requestGenerationRef.current + 1;
    requestGenerationRef.current = generation;
    mutationAbortRef.current?.abort();
    mutationAbortRef.current = null;
    mutationLockedRef.current = false;

    const controller = new AbortController();
    setReplay(null);
    setLoading(true);
    setMutationPending(false);
    setErrorCode(null);
    setFeedbackReceipt(null);
    setFeedbackErrorCode(null);

    let idempotencyKey: string;
    try {
      idempotencyKey = getOrCreateOpaqueIdempotencyKey(
        idempotencyKeysRef.current,
        requestFingerprint(["create", sessionId, analysisId, scenarioId]),
      );
    } catch (reason) {
      if (
        mountedRef.current &&
        canApplyReplayMutation(
          generation,
          requestGenerationRef.current,
          controller.signal.aborted,
        )
      ) {
        setLoading(false);
        setErrorCode(requestErrorCode(reason, "REPLAY_LAUNCH_FAILED"));
      }
      return () => controller.abort();
    }

    void client
      .createReplay(
        sessionId,
        { analysisId, scenarioId },
        { idempotencyKey, signal: controller.signal },
      )
      .then((createdReplay) => {
        if (
          mountedRef.current &&
          canApplyReplayMutation(
            generation,
            requestGenerationRef.current,
            controller.signal.aborted,
          )
        ) {
          setReplay(createdReplay);
          setLoading(false);
        }
      })
      .catch((reason: unknown) => {
        if (
          mountedRef.current &&
          canApplyReplayMutation(
            generation,
            requestGenerationRef.current,
            controller.signal.aborted,
          ) &&
          !isAbortError(reason)
        ) {
          setLoading(false);
          setErrorCode(requestErrorCode(reason, "REPLAY_LAUNCH_FAILED"));
        }
      });

    return () => controller.abort();
  }, [analysisId, client, scenarioId, sessionId]);

  const advance = useCallback(async (): Promise<void> => {
    if (replay === null || mutationLockedRef.current) {
      return;
    }
    if (!["idle", "running"].includes(replay.state)) {
      return;
    }

    const generation = requestGenerationRef.current;
    mutationLockedRef.current = true;
    setMutationPending(true);
    setErrorCode(null);
    setFeedbackReceipt(null);
    setFeedbackErrorCode(null);
    const controller = new AbortController();
    mutationAbortRef.current = controller;

    try {
      const advancedReplay = await client.advanceReplay(
        replay.replayId,
        {
          expectedCurrentIndex: replay.currentIndex,
          expectedRevision: replay.revision,
        },
        { expectedReplay: replay, signal: controller.signal },
      );
      if (
        mountedRef.current &&
        canApplyReplayMutation(
          generation,
          requestGenerationRef.current,
          controller.signal.aborted,
        )
      ) {
        setReplay(advancedReplay);
      }
    } catch (reason) {
      if (
        mountedRef.current &&
        canApplyReplayMutation(
          generation,
          requestGenerationRef.current,
          controller.signal.aborted,
        ) &&
        !isAbortError(reason)
      ) {
        setErrorCode(requestErrorCode(reason, "REPLAY_ADVANCE_FAILED"));
      }
    } finally {
      if (mutationAbortRef.current === controller) {
        mutationAbortRef.current = null;
        mutationLockedRef.current = false;
        if (
          mountedRef.current &&
          canApplyReplayMutation(
            generation,
            requestGenerationRef.current,
            controller.signal.aborted,
          )
        ) {
          setMutationPending(false);
        }
      }
    }
  }, [client, replay]);

  const submitFeedback = useCallback(
    async (
      decision: GestureFeedbackDecision,
      actorRole: FeedbackActorRole,
    ): Promise<void> => {
      if (
        replay === null ||
        replay.currentWindow === null ||
        mutationLockedRef.current
      ) {
        return;
      }
      if (!isFeedbackActorRole(actorRole)) {
        setFeedbackReceipt(null);
        setFeedbackErrorCode("FEEDBACK_ROLE_FORBIDDEN");
        return;
      }

      const generation = requestGenerationRef.current;
      const expectedWindow = replay.currentWindow;
      mutationLockedRef.current = true;
      setMutationPending(true);
      setFeedbackReceipt(null);
      setFeedbackErrorCode(null);
      const controller = new AbortController();
      mutationAbortRef.current = controller;

      try {
        const logicalFingerprint = requestFingerprint([
          "feedback",
          replay.replayId,
          expectedWindow.windowId,
          replay.revision,
          actorRole,
          decision.action,
          decision.action === "correct" ? decision.correctedGesture : null,
          decision.reviewerCertainty,
        ]);
        const idempotencyKey = getOrCreateOpaqueIdempotencyKey(
          idempotencyKeysRef.current,
          logicalFingerprint,
        );
        const receipt = await client.submitFeedback(
          replay.replayId,
          {
            ...decision,
            expectedWindowId: expectedWindow.windowId,
            expectedRevision: replay.revision,
          },
          {
            actorRole,
            expectedReplay: replay,
            idempotencyKey,
            signal: controller.signal,
          },
        );
        if (
          mountedRef.current &&
          canApplyReplayMutation(
            generation,
            requestGenerationRef.current,
            controller.signal.aborted,
          )
        ) {
          setFeedbackReceipt(receipt);
        }
      } catch (reason) {
        if (
          mountedRef.current &&
          canApplyReplayMutation(
            generation,
            requestGenerationRef.current,
            controller.signal.aborted,
          ) &&
          !isAbortError(reason)
        ) {
          setFeedbackErrorCode(
            requestErrorCode(reason, "FEEDBACK_SUBMISSION_FAILED"),
          );
        }
      } finally {
        if (mutationAbortRef.current === controller) {
          mutationAbortRef.current = null;
          mutationLockedRef.current = false;
          if (
            mountedRef.current &&
            canApplyReplayMutation(
              generation,
              requestGenerationRef.current,
              controller.signal.aborted,
            )
          ) {
            setMutationPending(false);
          }
        }
      }
    },
    [client, replay],
  );

  return {
    replay,
    loading,
    mutationPending,
    errorCode,
    feedbackReceipt,
    feedbackErrorCode,
    advance,
    submitFeedback,
  };
}
