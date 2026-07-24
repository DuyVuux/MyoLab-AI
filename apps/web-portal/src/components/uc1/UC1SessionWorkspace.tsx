"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  CircleSlash2,
  Gauge,
  HelpCircle,
  RotateCcw,
  ShieldCheck,
  WifiOff,
} from "lucide-react";

import { useAuth, type UserRole as AuthUserRole } from "@/lib/auth";
import {
  HttpUC1ReplayClient,
  type UC1ReplayClient,
} from "@/lib/uc1-replay-client";
import { isLatencyBreakdownValid } from "@/lib/latencyMetrics";
import { canPerformAction } from "@/config/routePermissions";
import { Alert } from "@/components/ui/Alert";
import { Badge, type BadgeVariant } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { useUC1Replay } from "@/hooks/useUC1Replay";
import type {
  FeedbackActorRole,
  GestureFeedbackDecision,
} from "@/schemas/gesture-feedback-context.schema";
import type {
  EngineeringConfidence,
  GestureId,
  GestureInferenceWindow,
  UC1ReplayScenarioId,
  UC1ReplaySession,
} from "@/schemas/gesture-inference.schema";
import type { UserRole as Day22UserRole } from "@/schemas/role.schema";
import { isFeedbackActorRole } from "@/utils/uc1ReplayValidation";
import {
  currentReplayWindow,
  visibleReplayWindows,
} from "@/utils/replayView";

import { GestureHistoryTable } from "./GestureHistoryTable";
import styles from "./UC1SessionWorkspace.module.css";

const GESTURE_LABELS: Readonly<Record<GestureId, string>> = {
  rest: "Nghỉ",
  hand_open: "Mở bàn tay",
  hand_close: "Nắm bàn tay",
  wrist_flexion: "Gập cổ tay",
  wrist_extension: "Duỗi cổ tay",
};

const CONFIDENCE_LABELS: Readonly<Record<EngineeringConfidence, string>> = {
  engineering_high: "Cao — chỉ số kỹ thuật",
  engineering_moderate: "Vừa — chỉ số kỹ thuật",
  engineering_low: "Thấp — cần người có chuyên môn xem lại",
  engineering_very_low: "Rất thấp — cần người có chuyên môn xem lại",
  not_available: "Không khả dụng",
};

const GATE_STATUS_LABELS = {
  inactive: "Chưa vượt ngưỡng hoạt động",
  uncertain: "Gần ngưỡng kỹ thuật",
  active: "Đủ bằng chứng hoạt động",
} as const;

function toDay22Role(role: AuthUserRole): Day22UserRole | null {
  if (role === "doctor") {
    return "physician";
  }
  if (
    role === "patient" ||
    role === "ktv" ||
    role === "researcher" ||
    role === "admin"
  ) {
    return role;
  }
  return null;
}

interface ResultNotice {
  readonly title: string;
  readonly body: string;
  readonly variant: "success" | "warning" | "error" | "abstention" | "info";
  readonly icon: typeof Activity;
}

function resultNotice(
  replay: UC1ReplaySession,
  window: GestureInferenceWindow | null,
): ResultNotice {
  if (replay.state === "failed") {
    return {
      title: "Replay lỗi kỹ thuật",
      body:
        "Replay dừng do lỗi kỹ thuật và không tạo kết quả thay thế. Hãy kiểm tra reason code trước khi chủ động chạy lại.",
      variant: "error",
      icon: AlertTriangle,
    };
  }

  if (window === null) {
    if (replay.state === "abstained") {
      return {
        title: "Replay không phát kết quả",
        body:
          "Phân tích đầu vào không đủ điều kiện để replay. Không có dự đoán ẩn và cần người có chuyên môn xem lại dữ liệu nguồn.",
        variant: "abstention",
        icon: CircleSlash2,
      };
    }
    if (replay.state === "disconnected") {
      return {
        title: "Replay bị gián đoạn",
        body:
          "Kết nối replay bị gián đoạn. Phiên đã tạm dừng và không tạo kết quả mới.",
        variant: "error",
        icon: WifiOff,
      };
    }
    return {
      title: "Đang chờ bắt đầu",
      body: "Replay chưa bắt đầu. Chưa có kết quả kỹ thuật.",
      variant: "info",
      icon: Activity,
    };
  }

  if (window.deviceState !== "connected" || replay.state === "disconnected") {
    return {
      title: "Replay bị gián đoạn",
      body:
        "Kết nối replay bị gián đoạn. Phiên đã tạm dừng và không tạo kết quả mới.",
      variant: "error",
      icon: WifiOff,
    };
  }
  if (window.qualityContext.status === "fail") {
    return {
      title: "Không đạt kiểm soát chất lượng",
      body:
        "Cửa sổ không đạt điều kiện chất lượng. Hệ thống không tạo kết quả; hãy kiểm tra điện cực và đo lại.",
      variant: "abstention",
      icon: ShieldCheck,
    };
  }
  if (window.fatigueOverlay.status === "abstain") {
    return {
      title: "Tạm không kết luận",
      body:
        "Mẫu thay đổi kỹ thuật chưa đủ điều kiện diễn giải. Hệ thống tạm không tạo kết quả; cần người có chuyên môn xem lại.",
      variant: "abstention",
      icon: CircleSlash2,
    };
  }
  if (window.activityGate.status === "inactive") {
    return {
      title: "Chưa đủ hoạt động cơ",
      body:
        "Chưa đủ bằng chứng hoạt động cơ trong cửa sổ này. Đây không phải lỗi mô hình và không kết luận người bệnh không cố gắng.",
      variant: "info",
      icon: Activity,
    };
  }
  if (window.activityGate.status === "uncertain") {
    return {
      title: "Hoạt động gần ngưỡng",
      body:
        "Tín hiệu nằm gần ngưỡng kỹ thuật; hệ thống không kết luận cử chỉ. KTV cần kiểm tra hoặc đo lại.",
      variant: "warning",
      icon: HelpCircle,
    };
  }
  if (window.predictedGesture === null) {
    return {
      title: "Không có kết quả kỹ thuật",
      body:
        "Cửa sổ đã được xử lý nhưng không đủ điều kiện tạo kết quả. Cần xem các reason code và đo lại khi phù hợp.",
      variant: "abstention",
      icon: CircleSlash2,
    };
  }
  return {
    title: "Cửa sổ đã được xử lý",
    body: `Cửa sổ tạo kết quả kỹ thuật: ${
      GESTURE_LABELS[window.predictedGesture]
    }. Kết quả này không phản ánh mức độ cố gắng và không phải kết luận lâm sàng.`,
    variant: "success",
    icon: CheckCircle2,
  };
}

function badgeVariantForConfidence(
  confidence: EngineeringConfidence,
): BadgeVariant {
  if (confidence === "engineering_high") return "success";
  if (confidence === "engineering_moderate") return "info";
  if (
    confidence === "engineering_low" ||
    confidence === "engineering_very_low"
  ) {
    return "warning";
  }
  return "abstention";
}

function formatLatency(value: number | null): string {
  return value === null ? "Chưa có" : `${value.toFixed(0)} ms`;
}

interface FeedbackControlsProps {
  readonly window: GestureInferenceWindow;
  readonly pending: boolean;
  readonly onSubmit: (decision: GestureFeedbackDecision) => Promise<void>;
}

function FeedbackControls({
  window,
  pending,
  onSubmit,
}: FeedbackControlsProps) {
  const correctionChoices = useMemo(
    () => GESTURE_LABELS_ENTRIES.filter(([gesture]) => gesture !== window.predictedGesture),
    [window.predictedGesture],
  );
  const [correctedGesture, setCorrectedGesture] = useState<GestureId>(
    correctionChoices[0]?.[0] ?? "rest",
  );

  useEffect(() => {
    setCorrectedGesture(correctionChoices[0]?.[0] ?? "rest");
  }, [correctionChoices, window.windowId]);

  return (
    <Card variant="outlined" className={styles.feedbackCard}>
      <CardHeader>
        <h2>Feedback kỹ thuật cho đúng cửa sổ</h2>
      </CardHeader>
      <CardContent>
        <p className={styles.supportingText}>
          Feedback gắn với <code>{window.windowId}</code>. Server chịu trách
          nhiệm gắn provenance đã ký nhận; trình duyệt chỉ gửi quyết định.
        </p>
        <div className={styles.feedbackActions}>
          {window.predictedGesture !== null && (
            <Button
              type="button"
              variant="secondary"
              disabled={pending}
              onClick={() =>
                void onSubmit({
                  action: "accept",
                  reviewerCertainty: "high",
                })
              }
              icon={<CheckCircle2 size={18} />}
            >
              Chấp nhận kết quả
            </Button>
          )}
          <Button
            type="button"
            variant="secondary"
            disabled={pending}
            onClick={() =>
              void onSubmit({
                action: "uncertain",
                reviewerCertainty: "moderate",
              })
            }
            icon={<HelpCircle size={18} />}
          >
            Chưa chắc
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={pending}
            onClick={() =>
              void onSubmit({
                action: "remeasure",
                reviewerCertainty: "moderate",
              })
            }
            icon={<RotateCcw size={18} />}
          >
            Đề nghị đo lại
          </Button>
        </div>

        {window.predictedGesture !== null && (
          <div className={styles.correctionRow}>
            <label htmlFor={`corrected-gesture-${window.windowId}`}>
              Cử chỉ hiệu chỉnh
            </label>
            <select
              id={`corrected-gesture-${window.windowId}`}
              value={correctedGesture}
              disabled={pending}
              onChange={(event) =>
                setCorrectedGesture(event.target.value as GestureId)
              }
            >
              {correctionChoices.map(([gesture, label]) => (
                <option key={gesture} value={gesture}>
                  {label}
                </option>
              ))}
            </select>
            <Button
              type="button"
              variant="secondary"
              disabled={pending}
              onClick={() =>
                void onSubmit({
                  action: "correct",
                  correctedGesture,
                  reviewerCertainty: "high",
                })
              }
            >
              Cần sửa
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

const GESTURE_LABELS_ENTRIES = Object.entries(GESTURE_LABELS) as Array<
  [GestureId, string]
>;

export interface UC1SessionWorkspaceProps {
  readonly sessionId: string;
  readonly analysisId: string;
  readonly scenarioId: UC1ReplayScenarioId;
  readonly client?: UC1ReplayClient;
}

export function UC1SessionWorkspace({
  sessionId,
  analysisId,
  scenarioId,
  client: suppliedClient,
}: UC1SessionWorkspaceProps) {
  const { user } = useAuth();
  const defaultClient = useMemo(
    () =>
      new HttpUC1ReplayClient(process.env.NEXT_PUBLIC_API_BASE_URL ?? ""),
    [],
  );
  const client = suppliedClient ?? defaultClient;
  const {
    replay,
    loading,
    mutationPending,
    errorCode,
    feedbackReceipt,
    feedbackErrorCode,
    advance,
    submitFeedback,
  } = useUC1Replay({ client, sessionId, analysisId, scenarioId });

  const currentWindow = replay === null ? null : currentReplayWindow(replay);
  const history = replay === null ? [] : visibleReplayWindows(replay);
  const actorRole = user === null ? null : toDay22Role(user.role);
  const feedbackActorRole: FeedbackActorRole | null =
    isFeedbackActorRole(actorRole) ? actorRole : null;
  const maySubmitFeedback =
    feedbackActorRole !== null &&
    canPerformAction(feedbackActorRole, "submit_feedback") &&
    currentWindow !== null;
  const notice =
    replay === null ? null : resultNotice(replay, currentWindow);
  const statusReasonCodes =
    replay === null
      ? []
      : Array.from(
          new Set([
            ...replay.reasonCodes,
            ...(currentWindow?.fatigueOverlay.reasonCodes ?? []),
          ]),
        );
  const canAdvance =
    replay !== null && (replay.state === "idle" || replay.state === "running");
  const advanceLabel =
    replay?.currentIndex === -1 ? "Bắt đầu replay" : "Cửa sổ tiếp theo";

  return (
    <div className={`page-container ${styles.workspace}`}>
      <header className={styles.pageHeader}>
        <div>
          <p className={styles.eyebrow}>Deterministic offline replay</p>
          <h1>UC1 · Biofeedback cử chỉ — Replay kỹ thuật</h1>
          <p className={styles.subtitle}>
            Phiên <code>{sessionId}</code> · Phân tích{" "}
            <code>{analysisId}</code>
          </p>
        </div>
        <div className={styles.headerBadges} aria-label="Giới hạn sử dụng">
          <Badge variant="source-synthetic">Nguồn mô phỏng</Badge>
          <Badge variant="warning">Model chưa được xác thực</Badge>
          <Badge variant="review-pending">Bắt buộc human review</Badge>
        </div>
      </header>

      <Alert variant="warning" title="Phạm vi an toàn">
        Replay dùng để kiểm chứng kỹ thuật. Không dùng cho chẩn đoán, quyết định
        điều trị, tự động dừng bài tập hoặc điều khiển thiết bị vật lý.
      </Alert>

      {errorCode !== null && (
        <Alert
          variant="error"
          title="Không tải được kết quả kỹ thuật"
          reasonCode={errorCode}
          className={styles.topNotice}
        >
          Dịch vụ replay không phản hồi đúng contract. Không có kết quả nào được
          suy diễn thay thế. Hãy kiểm tra kết nối rồi chủ động thử lại từ luồng
          phân tích.
        </Alert>
      )}

      {loading && (
        <div
          className={styles.loadingState}
          role="status"
          aria-live="polite"
        >
          Đang khởi tạo replay an toàn…
        </div>
      )}

      {replay !== null && notice !== null && (
        <>
          <section aria-labelledby="uc1-current-result">
            <Card variant={notice.variant} className={styles.resultCard}>
              <CardHeader>
                <div className={styles.sectionHeading}>
                  <notice.icon size={24} aria-hidden="true" />
                  <div>
                    <h2 id="uc1-current-result">Kết quả cửa sổ hiện tại</h2>
                    <p>
                      {currentWindow === null
                        ? "Chưa có cửa sổ được công bố"
                        : currentWindow.windowId}
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div
                  className={styles.liveResult}
                  role="status"
                  aria-live="polite"
                  aria-atomic="true"
                >
                  <strong>{notice.title}</strong>
                  <p>{notice.body}</p>
                  {statusReasonCodes.length > 0 && (
                    <div className={styles.evidenceBlock}>
                      <strong>Reason code trạng thái</strong>
                      <ul className={styles.reasonList}>
                        {statusReasonCodes.map((reason) => (
                          <li key={reason}>
                            <code>{reason}</code>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </section>

          {currentWindow !== null && (
            <>
              <div className={styles.twoColumnGrid}>
                <Card variant="outlined">
                  <CardHeader>
                    <h2>Mục tiêu và kết quả kỹ thuật</h2>
                  </CardHeader>
                  <CardContent>
                    <dl className={styles.definitionGrid}>
                      <div>
                        <dt>Cử chỉ mục tiêu</dt>
                        <dd>{GESTURE_LABELS[currentWindow.targetGesture]}</dd>
                      </div>
                      <div>
                        <dt>Kết quả replay</dt>
                        <dd>
                          {currentWindow.predictedGesture === null
                            ? "Không có kết quả"
                            : GESTURE_LABELS[
                                currentWindow.predictedGesture
                              ]}
                        </dd>
                      </div>
                      <div>
                        <dt>Độ tin cậy</dt>
                        <dd>
                          <Badge
                            variant={badgeVariantForConfidence(
                              currentWindow.engineeringConfidence,
                            )}
                          >
                            {
                              CONFIDENCE_LABELS[
                                currentWindow.engineeringConfidence
                              ]
                            }
                          </Badge>
                        </dd>
                      </div>
                      <div>
                        <dt>Khoảng mẫu half-open</dt>
                        <dd>
                          [{currentWindow.segmentRef.startSample},{" "}
                          {currentWindow.segmentRef.endSampleExclusive})
                        </dd>
                      </div>
                    </dl>
                  </CardContent>
                </Card>

                <Card variant="outlined">
                  <CardHeader>
                    <div className={styles.sectionHeading}>
                      <Gauge size={22} aria-hidden="true" />
                      <h2>Activity Gate</h2>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <dl className={styles.definitionGrid}>
                      <div>
                        <dt>Trạng thái</dt>
                        <dd>
                          {GATE_STATUS_LABELS[currentWindow.activityGate.status]}
                        </dd>
                      </div>
                      <div>
                        <dt>RMS cửa sổ</dt>
                        <dd>
                          {currentWindow.activityGate.windowRmsUv.toFixed(2)} µV
                        </dd>
                      </div>
                      <div>
                        <dt>Ngưỡng kích hoạt</dt>
                        <dd>
                          {currentWindow.activityGate.activationThresholdUv.toFixed(
                            2,
                          )}{" "}
                          µV
                        </dd>
                      </div>
                      <div>
                        <dt>Ngưỡng nhả</dt>
                        <dd>
                          {currentWindow.activityGate.releaseThresholdUv.toFixed(
                            2,
                          )}{" "}
                          µV
                        </dd>
                      </div>
                    </dl>
                    <code className={styles.reasonCode}>
                      {currentWindow.activityGate.reasonCode}
                    </code>
                  </CardContent>
                </Card>

                <Card
                  variant={
                    currentWindow.qualityContext.status === "fail"
                      ? "abstention"
                      : currentWindow.qualityContext.status === "warning"
                        ? "warning"
                        : "outlined"
                  }
                >
                  <CardHeader>
                    <h2>Ngữ cảnh chất lượng</h2>
                  </CardHeader>
                  <CardContent>
                    <dl className={styles.definitionGrid}>
                      <div>
                        <dt>Trạng thái QC</dt>
                        <dd>{currentWindow.qualityContext.status}</dd>
                      </div>
                      <div>
                        <dt>Nguồn QC</dt>
                        <dd>{currentWindow.qualityContext.source}</dd>
                      </div>
                      <div className={styles.fullWidthDefinition}>
                        <dt>Quality result</dt>
                        <dd>
                          <code>
                            {currentWindow.qualityContext.qualityResultId}
                          </code>
                        </dd>
                      </div>
                    </dl>
                    {currentWindow.qualityContext.reasonCodes.length > 0 && (
                      <ul className={styles.reasonList}>
                        {currentWindow.qualityContext.reasonCodes.map((reason) => (
                          <li key={reason}>
                            <code>{reason}</code>
                          </li>
                        ))}
                      </ul>
                    )}
                  </CardContent>
                </Card>

                <Card
                  variant={
                    currentWindow.fatigueOverlay.status === "abstain"
                      ? "abstention"
                      : currentWindow.fatigueOverlay.status === "warning"
                        ? "warning"
                        : "outlined"
                  }
                >
                  <CardHeader>
                    <h2>Fatigue overlay có giới hạn</h2>
                  </CardHeader>
                  <CardContent>
                    <p className={styles.supportingText}>
                      Đây là lớp bằng chứng kỹ thuật, không phải chẩn đoán mỏi cơ
                      hoặc chỉ định nghỉ tập.
                    </p>
                    <dl className={styles.definitionGrid}>
                      <div>
                        <dt>Trạng thái</dt>
                        <dd>{currentWindow.fatigueOverlay.status}</dd>
                      </div>
                      <div>
                        <dt>Nguồn bằng chứng</dt>
                        <dd>{currentWindow.fatigueOverlay.source}</dd>
                      </div>
                      <div>
                        <dt>Điều chỉnh confidence</dt>
                        <dd>
                          {currentWindow.fatigueOverlay
                            .confidenceAdjustmentApplied
                            ? "Có — chỉ hạ mức"
                            : "Không"}
                        </dd>
                      </div>
                    </dl>
                    {currentWindow.fatigueOverlay.evidenceSummaryVi.length >
                      0 && (
                      <div className={styles.evidenceBlock}>
                        <strong>Bằng chứng</strong>
                        <ul>
                          {currentWindow.fatigueOverlay.evidenceSummaryVi.map(
                            (item) => <li key={item}>{item}</li>,
                          )}
                        </ul>
                      </div>
                    )}
                    {currentWindow.fatigueOverlay.counterevidenceVi.length >
                      0 && (
                      <div className={styles.evidenceBlock}>
                        <strong>Phản chứng</strong>
                        <ul>
                          {currentWindow.fatigueOverlay.counterevidenceVi.map(
                            (item) => <li key={item}>{item}</li>,
                          )}
                        </ul>
                      </div>
                    )}
                    <div className={styles.evidenceBlock}>
                      <strong>Giới hạn</strong>
                      {currentWindow.fatigueOverlay.limitationsVi.length === 0 ? (
                        <p>Chưa có diễn giải giới hạn từ server.</p>
                      ) : (
                        <ul>
                          {currentWindow.fatigueOverlay.limitationsVi.map(
                            (item) => <li key={item}>{item}</li>,
                          )}
                        </ul>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card variant="outlined" className={styles.telemetryCard}>
                <CardHeader>
                  <h2>Độ trễ replay quan sát được</h2>
                </CardHeader>
                <CardContent>
                  <div className={styles.telemetryGrid}>
                    <div>
                      <span>Cửa sổ hiện tại</span>
                      <strong>{currentWindow.latency.totalMs.toFixed(0)} ms</strong>
                    </div>
                    <div>
                      <span>p50 nearest-rank</span>
                      <strong>
                        {formatLatency(replay.latencySummary.p50Ms)}
                      </strong>
                    </div>
                    <div>
                      <span>p95 nearest-rank</span>
                      <strong>
                        {formatLatency(replay.latencySummary.p95Ms)}
                      </strong>
                    </div>
                    <div>
                      <span>Cửa sổ rơi</span>
                      <strong>{replay.latencySummary.droppedWindows}</strong>
                    </div>
                  </div>
                  <p className={styles.supportingText}>
                    Telemetry của deterministic replay là số đo prototype, không
                    phải cam kết hiệu năng khi triển khai.
                  </p>
                  {!isLatencyBreakdownValid(currentWindow.latency) && (
                    <p className={styles.inlineError} role="alert">
                      Tổng độ trễ không khớp các thành phần. Không dùng số đo này.
                    </p>
                  )}
                </CardContent>
              </Card>

              <Card variant="outlined" className={styles.provenanceCard}>
                <CardHeader>
                  <h2>Provenance do server cung cấp</h2>
                </CardHeader>
                <CardContent>
                  <dl className={styles.provenanceGrid}>
                    <div>
                      <dt>Model version</dt>
                      <dd>
                        <code>{currentWindow.modelVersion}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>Result SHA-256</dt>
                      <dd>
                        <code>{currentWindow.resultHashSha256}</code>
                      </dd>
                    </div>
                    <div>
                      <dt>Source SHA-256</dt>
                      <dd>
                        <code>
                          {currentWindow.segmentRef.sourceHashSha256}
                        </code>
                      </dd>
                    </div>
                    <div>
                      <dt>Calibration</dt>
                      <dd>
                        <code>
                          {currentWindow.segmentRef.calibrationId}
                        </code>
                      </dd>
                    </div>
                  </dl>
                </CardContent>
              </Card>
            </>
          )}

          <div className={styles.replayControls}>
            <div>
              <strong>
                Cửa sổ {Math.max(0, replay.currentIndex + 1)}/
                {replay.totalWindows}
              </strong>
              <p>
                Trạng thái: {replay.state} · Revision {replay.revision}
              </p>
            </div>
            {canAdvance && (
              <Button
                type="button"
                size="lg"
                loading={mutationPending}
                loadingText="Đang xử lý cửa sổ…"
                disabled={mutationPending}
                className={styles.primaryAction}
                icon={<ArrowRight size={18} />}
                iconPosition="right"
                onClick={() => void advance()}
              >
                {advanceLabel}
              </Button>
            )}
          </div>

          {maySubmitFeedback &&
            currentWindow !== null &&
            feedbackActorRole !== null && (
            <FeedbackControls
              key={currentWindow.windowId}
              window={currentWindow}
              pending={mutationPending}
              onSubmit={(decision) => submitFeedback(decision, feedbackActorRole)}
            />
          )}

          {feedbackReceipt !== null && (
            <div
              className={styles.feedbackSuccess}
              role="status"
              aria-live="polite"
            >
              <CheckCircle2 size={20} aria-hidden="true" />
              <span>
                Feedback đã được ghi nhận cho cửa sổ{" "}
                <code>{feedbackReceipt.context.windowId}</code>.
              </span>
            </div>
          )}
          {feedbackErrorCode !== null && (
            <div className={styles.inlineError} role="alert">
              <AlertTriangle size={20} aria-hidden="true" />
              <span>
                Không gửi được feedback kỹ thuật. Mã:{" "}
                <code>{feedbackErrorCode}</code>
              </span>
            </div>
          )}

          <section
            className={styles.historySection}
            aria-labelledby="uc1-history-heading"
          >
            <h2 id="uc1-history-heading">Lịch sử đã công bố</h2>
            <p className={styles.supportingText}>
              Bảng ghép <code>history</code> (các cửa sổ trước) với
              <code>currentWindow</code>; các cửa sổ tương lai không được tải
              vào giao diện.
            </p>
            <GestureHistoryTable windows={history} />
          </section>
        </>
      )}
    </div>
  );
}
