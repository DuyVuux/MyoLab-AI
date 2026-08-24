import type { UC2QuantitativeAssessment } from '@/schemas/uc2-assessment.schema';

export type UC2Scenario =
  | 'golden_uc2_longitudinal'
  | 'uc2_protocol_incompatible'
  | 'uc2_missing_baseline'
  | 'uc2_qc_fail_session'
  | 'uc2_bilateral_unavailable';

export function getMockUC2Assessment(
  scenarioId: UC2Scenario
): UC2QuantitativeAssessment {
  const SUBJECT_REF = 'SUBJ-D23-E2E';

  if (scenarioId === 'uc2_protocol_incompatible') {
    return {
      schemaVersion: 'uc2-quantitative-assessment.v0.1',
      assessmentId: `UC2-E2E-${scenarioId}`,
      subjectRef: SUBJECT_REF,
      sessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
      status: 'blocked',
      metrics: [
        {
          metricId: 'longitudinal_summary',
          labelVi: 'Tóm tắt so sánh dọc',
          status: 'blocked',
          value: null,
          unit: null,
          formulaVersion: 'compatibility-gate-v0.1',
          validationStatus: 'not_validated',
          sourceSessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
          limitations: ['PROTOCOLVERSION_MISMATCH'],
        },
      ],
      compatibility: {
        schemaVersion: 'longitudinal-compatibility.v0.1',
        subjectRef: SUBJECT_REF,
        baselineSessionId: 'S-BASE-D23',
        comparisonSessionIds: ['S-WEEK4-D23'],
        status: 'blocked',
        conclusionAllowed: false,
        checks: [
          {
            field: 'S-WEEK4-D23:protocolVersion',
            status: 'mismatch',
            baselineValue: 'v0.1',
            comparisonValue: 'v0.2',
            reasonCode: 'PROTOCOLVERSION_MISMATCH',
          },
        ],
        reasonCodes: ['PROTOCOLVERSION_MISMATCH'],
        safety: {
          rawSamplesIncluded: false,
          clinicalUseAllowed: false,
          humanReviewRequired: true,
        },
      },
      limitations: ['Human review bắt buộc.'],
      reviewStatus: 'pending_human_review',
      safety: {
        scoreIsProbability: false,
        rawSamplesIncluded: false,
        clinicalUseAllowed: false,
        humanReviewRequired: true,
        isClinicalConclusion: false,
      },
    };
  }

  if (scenarioId === 'uc2_missing_baseline') {
    return {
      schemaVersion: 'uc2-quantitative-assessment.v0.1',
      assessmentId: `UC2-E2E-${scenarioId}`,
      subjectRef: SUBJECT_REF,
      sessionIds: ['S-WEEK4-D23'],
      status: 'blocked',
      metrics: [
        {
          metricId: 'longitudinal_summary',
          labelVi: 'Tóm tắt so sánh dọc',
          status: 'blocked',
          value: null,
          unit: null,
          formulaVersion: 'compatibility-gate-v0.1',
          validationStatus: 'not_validated',
          sourceSessionIds: ['S-WEEK4-D23'],
          limitations: ['MISSING_BASELINE'],
        },
      ],
      compatibility: {
        schemaVersion: 'longitudinal-compatibility.v0.1',
        subjectRef: SUBJECT_REF,
        baselineSessionId: '',
        comparisonSessionIds: ['S-WEEK4-D23'],
        status: 'blocked',
        conclusionAllowed: false,
        checks: [
          {
            field: 'baselineSessionId',
            status: 'not_available',
            baselineValue: null,
            comparisonValue: 'S-WEEK4-D23',
            reasonCode: 'MISSING_BASELINE',
          },
        ],
        reasonCodes: ['MISSING_BASELINE'],
        safety: {
          rawSamplesIncluded: false,
          clinicalUseAllowed: false,
          humanReviewRequired: true,
        },
      },
      limitations: ['Human review bắt buộc.'],
      reviewStatus: 'pending_human_review',
      safety: {
        scoreIsProbability: false,
        rawSamplesIncluded: false,
        clinicalUseAllowed: false,
        humanReviewRequired: true,
        isClinicalConclusion: false,
      },
    };
  }

  if (scenarioId === 'uc2_qc_fail_session') {
    return {
      schemaVersion: 'uc2-quantitative-assessment.v0.1',
      assessmentId: `UC2-E2E-${scenarioId}`,
      subjectRef: SUBJECT_REF,
      sessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
      status: 'blocked',
      metrics: [
        {
          metricId: 'longitudinal_summary',
          labelVi: 'Tóm tắt so sánh dọc',
          status: 'blocked',
          value: null,
          unit: null,
          formulaVersion: 'compatibility-gate-v0.1',
          validationStatus: 'not_validated',
          sourceSessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
          limitations: ['QC_FAIL_SESSION'],
        },
      ],
      compatibility: {
        schemaVersion: 'longitudinal-compatibility.v0.1',
        subjectRef: SUBJECT_REF,
        baselineSessionId: 'S-BASE-D23',
        comparisonSessionIds: ['S-WEEK4-D23'],
        status: 'blocked',
        conclusionAllowed: false,
        checks: [
          {
            field: 'S-WEEK4-D23:qcStatus',
            status: 'mismatch',
            baselineValue: 'PASS',
            comparisonValue: 'FAIL',
            reasonCode: 'QC_FAIL_SESSION',
          },
        ],
        reasonCodes: ['QC_FAIL_SESSION'],
        safety: {
          rawSamplesIncluded: false,
          clinicalUseAllowed: false,
          humanReviewRequired: true,
        },
      },
      limitations: ['Human review bắt buộc.'],
      reviewStatus: 'pending_human_review',
      safety: {
        scoreIsProbability: false,
        rawSamplesIncluded: false,
        clinicalUseAllowed: false,
        humanReviewRequired: true,
        isClinicalConclusion: false,
      },
    };
  }

  if (scenarioId === 'uc2_bilateral_unavailable') {
    return {
      schemaVersion: 'uc2-quantitative-assessment.v0.1',
      assessmentId: `UC2-E2E-${scenarioId}`,
      subjectRef: SUBJECT_REF,
      sessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
      status: 'completed_with_warnings',
      metrics: [
        {
          metricId: 'repeatability_cov',
          labelVi: 'Độ biến thiên giữa lần lặp',
          status: 'experimental',
          value: 8.12,
          unit: '% CoV',
          formulaVersion: 'cov-population-v0.1',
          validationStatus: 'not_validated',
          sourceSessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
          limitations: ['Thiếu kênh đối chứng bilateral'],
        },
      ],
      compatibility: {
        schemaVersion: 'longitudinal-compatibility.v0.1',
        subjectRef: SUBJECT_REF,
        baselineSessionId: 'S-BASE-D23',
        comparisonSessionIds: ['S-WEEK4-D23'],
        status: 'compatible',
        conclusionAllowed: true,
        checks: [
          {
            field: 'referenceSide',
            status: 'not_available',
            baselineValue: 'right',
            comparisonValue: null,
            reasonCode: 'BILATERAL_UNAVAILABLE',
          },
        ],
        reasonCodes: ['BILATERAL_UNAVAILABLE'],
        safety: {
          rawSamplesIncluded: false,
          clinicalUseAllowed: false,
          humanReviewRequired: true,
        },
      },
      limitations: ['Human review bắt buộc.'],
      reviewStatus: 'pending_human_review',
      safety: {
        scoreIsProbability: false,
        rawSamplesIncluded: false,
        clinicalUseAllowed: false,
        humanReviewRequired: true,
        isClinicalConclusion: false,
      },
    };
  }

  // Default: golden_uc2_longitudinal
  return {
    schemaVersion: 'uc2-quantitative-assessment.v0.1',
    assessmentId: `UC2-E2E-${scenarioId}`,
    subjectRef: SUBJECT_REF,
    sessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
    status: 'completed_with_warnings',
    metrics: [
      {
        metricId: 'repeatability_cov',
        labelVi: 'Độ biến thiên giữa lần lặp',
        status: 'experimental',
        value: 7.07,
        unit: '% CoV',
        formulaVersion: 'cov-population-v0.1',
        validationStatus: 'not_validated',
        sourceSessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
        limitations: ['Chỉ số kỹ thuật.'],
      },
      {
        metricId: 'symmetry_ratio',
        labelVi: 'Tỷ lệ đối xứng affected/reference',
        status: 'experimental',
        value: 80,
        unit: '%',
        formulaVersion: 'symmetry-ratio-v0.1',
        validationStatus: 'not_validated',
        sourceSessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
        limitations: ['Chỉ diễn giải khi protocol tương thích.'],
      },
      {
        metricId: 'time_to_fatigue_change',
        labelVi: 'Thay đổi thời gian tới mệt',
        status: 'experimental',
        value: 20,
        unit: '%',
        formulaVersion: 'percent-change-v0.1',
        validationStatus: 'not_validated',
        sourceSessionIds: ['S-BASE-D23', 'S-WEEK4-D23'],
        limitations: ['Không phải kết luận lâm sàng.'],
      },
    ],
    compatibility: {
      schemaVersion: 'longitudinal-compatibility.v0.1',
      subjectRef: SUBJECT_REF,
      baselineSessionId: 'S-BASE-D23',
      comparisonSessionIds: ['S-WEEK4-D23'],
      status: 'compatible',
      conclusionAllowed: true,
      checks: [
        {
          field: 'S-WEEK4-D23:protocolVersion',
          status: 'match',
          baselineValue: 'v0.1',
          comparisonValue: 'v0.1',
          reasonCode: null,
        },
      ],
      reasonCodes: [],
      safety: {
        rawSamplesIncluded: false,
        clinicalUseAllowed: false,
        humanReviewRequired: true,
      },
    },
    limitations: ['Human review bắt buộc.'],
    reviewStatus: 'pending_human_review',
    safety: {
      scoreIsProbability: false,
      rawSamplesIncluded: false,
      clinicalUseAllowed: false,
      humanReviewRequired: true,
      isClinicalConclusion: false,
    },
  };
}

export class UC2AssessmentClient {
  constructor(private readonly baseUrl = '') {}

  async create(scenarioId: UC2Scenario): Promise<UC2QuantitativeAssessment> {
    if (this.baseUrl) {
      try {
        const response = await fetch(`${this.baseUrl}/v1/uc2/assessments`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scenarioId }),
        });
        if (response.ok) {
          return (await response.json()) as UC2QuantitativeAssessment;
        }
      } catch {
        // Fallback to local mock if API request fails
      }
    }
    return getMockUC2Assessment(scenarioId);
  }
}
