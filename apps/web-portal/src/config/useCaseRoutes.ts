/**
 * MyoLab-AI Route Configuration
 * Canonical routes per Section 4.1 of the UI/UX spec
 */

export const ROUTES = {
  // Global
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  USE_CASES: '/use-cases',
  
  // Sessions
  SESSIONS: '/sessions',
  SESSION_NEW: '/sessions/new',
  SESSION_CONTEXT: (id: string) => `/sessions/${id}/context` as const,
  SESSION_DATA_SOURCE: (id: string) => `/sessions/${id}/data-source` as const,
  SESSION_IMPORT: (id: string) => `/sessions/${id}/import` as const,
  SESSION_MAPPING: (id: string) => `/sessions/${id}/mapping` as const,
  SESSION_PREFLIGHT: (id: string) => `/sessions/${id}/preflight` as const,
  SESSION_CALIBRATION: (id: string) => `/sessions/${id}/calibration` as const,
  SESSION_ACQUISITION: (id: string) => `/sessions/${id}/acquisition` as const,
  SESSION_QUALITY: (id: string) => `/sessions/${id}/quality` as const,
  SESSION_ANALYSIS: (id: string) => `/sessions/${id}/analysis` as const,
  SESSION_REVIEW: (id: string) => `/sessions/${id}/review` as const,
  SESSION_REPORT: (id: string) => `/sessions/${id}/report` as const,

  // Imports
  IMPORTS: '/imports',
  IMPORT_DETAIL: (id: string) => `/imports/${id}` as const,

  // Analyses
  ANALYSES: '/analyses',
  DATA_QUALITY: '/data-quality/issues',

  // Devices / Protocols
  DEVICES: '/devices',
  DEVICE_DETAIL: (id: string) => `/devices/${id}` as const,
  PROTOCOLS: '/protocols',
  PROTOCOL_DETAIL: (id: string) => `/protocols/${id}` as const,

  // Audit
  AUDIT: '/audit',

  // UC1 — Biofeedback (Tier 1 MVP)
  UC1_INTRO: '/uc1/intro',
  UC1_CALIBRATION: (sessionId: string) => `/uc1/calibration/${sessionId}` as const,
  UC1_SESSION: (sessionId: string) => `/uc1/session/${sessionId}` as const,
  UC1_REVIEW: (analysisId: string) => `/uc1/review/${analysisId}` as const,

  // UC2 — Quantitative Assessment (Tier 1 MVP)
  UC2_INTRO: '/uc2/intro',
  UC2_ASSESSMENT: (sessionId: string) => `/uc2/assessment/${sessionId}` as const,
  UC2_LONGITUDINAL: (subjectRef: string) => `/uc2/longitudinal/${subjectRef}` as const,
  UC2_REVIEW: (analysisId: string) => `/uc2/review/${analysisId}` as const,

  // UC3 — Prosthetics Feasibility (Tier 2 Research)
  UC3_INTRO: '/uc3/intro',
  UC3_FEASIBILITY: '/uc3/feasibility',
  UC3_REPLAY: (sessionId: string) => `/uc3/replay/${sessionId}` as const,
  UC3_EXPERT_REVIEW: (analysisId: string) => `/uc3/expert-review/${analysisId}` as const,

  // UC4 — Medical HMI Feasibility (Tier 2 Research)
  UC4_INTRO: '/uc4/intro',
  UC4_FEASIBILITY: '/uc4/feasibility',
  UC4_STERILE_COMMAND: '/uc4/sterile-command',
  UC4_SIGN_SEQUENCE: '/uc4/sign-sequence',
  UC4_EXPERT_REVIEW: (analysisId: string) => `/uc4/expert-review/${analysisId}` as const,

  // Feedback
  FEEDBACK_INBOX: '/feedback/inbox',
  FEEDBACK_DETAIL: (id: string) => `/feedback/${id}` as const,
  FEEDBACK_ADJUDICATE: (id: string) => `/feedback/${id}/adjudicate` as const,
  FEEDBACK_ANALYTICS: '/feedback/analytics',
  FEEDBACK_TRAINING_CANDIDATES: '/feedback/training-candidates',

  // Admin
  ADMIN_USERS: '/admin/users',
  ADMIN_PROTOCOLS: '/admin/protocols',
  ADMIN_MODELS: '/admin/models',
} as const;

/** Compatibility routes per Section 4.2 */
export const COMPATIBILITY_REDIRECTS: Record<string, string> = {
  '/uc1/demo': '/uc1/session/DEMO-UC1-001',
  '/uc2/demo': '/uc2/assessment/DEMO-UC2-001',
};

/** Use case metadata */
export interface UseCaseConfig {
  id: string;
  tier: 1 | 2;
  name: string;
  description: string;
  targetAudience: string;
  hardware: string;
  status: string;
  disclaimer: string;
  cta: string;
  introRoute: string;
}

export const USE_CASE_CONFIGS: UseCaseConfig[] = [
  {
    id: 'uc1',
    tier: 1,
    name: 'Biofeedback cử chỉ trong PHCN đột quỵ',
    description: 'Nhận diện cử chỉ tay theo thời gian thực hỗ trợ tập luyện phục hồi chức năng sau đột quỵ.',
    targetAudience: 'KTV PHCN, Bệnh nhân đột quỵ',
    hardware: 'Noraxon Ultium sEMG (4–8 kênh)',
    status: 'Thiết kế và triển khai chi tiết',
    disclaimer: 'Kết quả hỗ trợ kỹ thuật — cần KTV/bác sĩ xem xét.',
    cta: 'Mở use case',
    introRoute: ROUTES.UC1_INTRO,
  },
  {
    id: 'uc2',
    tier: 1,
    name: 'Đánh giá định lượng chức năng vận động tay',
    description: 'Phân tích định lượng chất lượng vận động, repeatability, symmetry và fatigue qua nhiều phiên.',
    targetAudience: 'KTV PHCN, Bác sĩ PHCN',
    hardware: 'Noraxon Ultium sEMG (4–8 kênh)',
    status: 'Thiết kế và triển khai chi tiết',
    disclaimer: 'Chỉ số kỹ thuật — không thay thế đánh giá lâm sàng tổng thể.',
    cta: 'Mở use case',
    introRoute: ROUTES.UC2_INTRO,
  },
  {
    id: 'uc3',
    tier: 2,
    name: 'Điều khiển chi giả cơ điện',
    description: 'Nghiên cứu khả thi nhận diện ý định cử chỉ để điều khiển chi giả — offline replay only.',
    targetAudience: 'Nghiên cứu viên, Kỹ sư y sinh',
    hardware: 'Hệ thống sEMG + chi giả cơ điện (chưa xác nhận)',
    status: 'Nghiên cứu khả thi — không điều khiển thiết bị thật',
    disclaimer: 'Nghiên cứu khả thi — không điều khiển thiết bị thật.',
    cta: 'Xem nghiên cứu khả thi',
    introRoute: ROUTES.UC3_INTRO,
  },
  {
    id: 'uc4',
    tier: 2,
    name: 'Giao diện người–máy trong môi trường y tế',
    description: 'Nghiên cứu khả thi ra lệnh bằng cử chỉ trong môi trường vô trùng và nhận dạng chuỗi ký hiệu.',
    targetAudience: 'Nghiên cứu viên, Phẫu thuật viên (khảo sát)',
    hardware: 'Wearable sEMG chuyên dụng (cần phát triển)',
    status: 'Nghiên cứu khả thi — cần wearable mới',
    disclaimer: 'Nghiên cứu khả thi — cần wearable mới để đánh giá triển khai.',
    cta: 'Xem nghiên cứu khả thi',
    introRoute: ROUTES.UC4_INTRO,
  },
];
