/**
 * Quality gate domain types.
 * Per spec Section 6.11.
 * QC fail blocks analysis. QC warning requires structured acknowledgement.
 * Distinct states: import_rejected vs warning vs abstained vs failed.
 */

export type QCVerdict = 'pass' | 'warning' | 'fail';

export type QCCheckId = 'snr' | 'baseline_noise' | 'saturation' | 'artifact' | 'cross_talk' | 'impedance';

export interface QCChannelResult {
  channelId: string;
  channelLabel: string;
  muscle: string;
  side: string;
  checks: QCCheck[];
  verdict: QCVerdict;
}

export interface QCCheck {
  id: QCCheckId;
  label: string;
  value: number;
  unit: string;
  threshold: number;
  thresholdDirection: 'gte' | 'lte'; // value must be >= or <= threshold
  status: QCVerdict;
  detail?: string;
}

export type QCAcknowledgementReason =
  | 'ambient_noise_acceptable'
  | 'electrode_repositioned'
  | 'protocol_allows_degraded'
  | 'research_context_only'
  | 'senior_override';

export const QC_ACKNOWLEDGEMENT_LABELS: Record<QCAcknowledgementReason, string> = {
  ambient_noise_acceptable: 'Nhiễu môi trường ở mức chấp nhận được',
  electrode_repositioned: 'Đã điều chỉnh lại vị trí điện cực',
  protocol_allows_degraded: 'Protocol cho phép chất lượng giảm',
  research_context_only: 'Chỉ dùng cho mục đích nghiên cứu',
  senior_override: 'Phê duyệt bởi senior/BS',
};

export interface QCAcknowledgement {
  reasonCode: QCAcknowledgementReason;
  additionalNote: string;
  acknowledgedBy: string;
  timestamp: string;
}

export interface QCResult {
  sessionId: string;
  importId: string;
  overallVerdict: QCVerdict;
  channelResults: QCChannelResult[];
  acknowledgement?: QCAcknowledgement;
  timestamp: string;
}

export function computeOverallVerdict(channels: QCChannelResult[]): QCVerdict {
  if (channels.some((ch) => ch.verdict === 'fail')) return 'fail';
  if (channels.some((ch) => ch.verdict === 'warning')) return 'warning';
  return 'pass';
}
