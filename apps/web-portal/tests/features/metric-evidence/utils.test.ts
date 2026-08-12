import { validateUncertainty, buildMetricEvidenceView, explainMetric } from '../../../src/features/metric-evidence/utils';
import { MetricEvidenceParams } from '../../../src/features/metric-evidence/types';
import { describe, it, expect } from 'vitest';

describe('Metric Evidence Utils', () => {
  describe('validateUncertainty', () => {
    it('should throw if RULE_CONFIDENCE has calibrated_probability', () => {
      expect(() =>
        validateUncertainty({
          uncertainty_type: 'RULE_CONFIDENCE',
          calibrated_probability: 0.8,
        })
      ).toThrow('RULE_CONFIDENCE_MUST_NOT_BE_PROBABILITY');
    });

    it('should throw if RULE_CONFIDENCE has conformal_set', () => {
      expect(() =>
        validateUncertainty({
          uncertainty_type: 'RULE_CONFIDENCE',
          conformal_set: {},
        })
      ).toThrow('RULE_CONFIDENCE_MUST_NOT_BE_CONFORMAL');
    });

    it('should throw if probability is not CALIBRATED', () => {
      expect(() =>
        validateUncertainty({
          calibrated_probability: 0.9,
          calibration_status: 'UNCALIBRATED',
        })
      ).toThrow('UNCALIBRATED_PROBABILITY_FORBIDDEN');
    });

    it('should pass valid uncertainty', () => {
      expect(validateUncertainty({ uncertainty_type: 'RULE_CONFIDENCE' })).toBe(true);
      expect(
        validateUncertainty({
          calibrated_probability: 0.9,
          calibration_status: 'CALIBRATED',
        })
      ).toBe(true);
    });
  });

  describe('buildMetricEvidenceView', () => {
    it('should throw if claim_scope is not RESEARCH_ONLY', () => {
      expect(() =>
        buildMetricEvidenceView({ claim_scope: 'CLINICAL' } as any)
      ).toThrow('RESEARCH_ONLY_REQUIRED');
    });

    it('should throw if metric identity is missing', () => {
      expect(() =>
        buildMetricEvidenceView({
          metric: { status: 'AVAILABLE' } as any,
        })
      ).toThrow('METRIC_IDENTITY_REQUIRED');
    });

    it('should throw if unsupported or blocked metric has a value', () => {
      expect(() =>
        buildMetricEvidenceView({
          metric: {
            metric_name: 'RMS',
            status: 'UNSUPPORTED',
            value: 123,
          },
        })
      ).toThrow('UNSUPPORTED_OR_BLOCKED_METRIC_MUST_BE_NULL');
    });

    it('should build a frozen view object with correct defaults', () => {
      const view = buildMetricEvidenceView({
        metric: {
          metric_name: 'RMS',
          status: 'AVAILABLE',
          value: 12.5,
          units: 'mV',
        },
      });

      expect(view.metric_name).toBe('RMS');
      expect(view.metric_status).toBe('AVAILABLE');
      expect(view.status_label).toBe('Available for research interpretation');
      expect(view.value).toBe(12.5);
      expect(view.units).toBe('mV');
      expect(view.reason_codes).toEqual([]);
      expect(view.distribution_support.status).toBe('NOT_EVALUATED');
      expect(Object.isFrozen(view)).toBe(true);
    });

    it('should merge reason codes uniquely', () => {
      const view = buildMetricEvidenceView({
        metric: {
          metric_name: 'RMS',
          status: 'BLOCKED',
          reason_codes: ['R1', 'R2'],
        },
        quality_eligibility: {
          reason_codes: ['R2', 'R3'],
        },
      });

      expect(view.reason_codes).toEqual(['R1', 'R2', 'R3']);
    });
  });

  describe('explainMetric', () => {
    it('should generate explanation string correctly', () => {
      const view = buildMetricEvidenceView({
        metric: {
          metric_name: 'RMS',
          status: 'BLOCKED',
          reason_codes: ['LOW_SNR'],
        },
        uncertainty: {
          uncertainty_type: 'RULE_CONFIDENCE',
        },
      });

      const explanation = explainMetric(view);
      expect(explanation).toContain('RMS: Blocked by eligibility gate.');
      expect(explanation).toContain('No numeric value is presented.');
      expect(explanation).toContain('Reason: LOW_SNR.');
      expect(explanation).toContain('Distribution support: NOT_EVALUATED.');
      expect(explanation).toContain('Rule confidence is ordinal evidence, not a calibrated probability.');
      expect(explanation).toContain('No validated OOD score is available.');
    });
  });
});
