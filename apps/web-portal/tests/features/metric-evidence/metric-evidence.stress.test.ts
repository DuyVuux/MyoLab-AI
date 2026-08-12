import { validateUncertainty, buildMetricEvidenceView } from '../../../src/features/metric-evidence/utils';
import { MetricEvidenceParams, MetricStatus } from '../../../src/features/metric-evidence/types';
import { describe, it, expect } from 'vitest';
// In a real environment, we would use fast-check: 
// import fc from 'fast-check';

describe('Metric Evidence Viewer (DAY 58) - Chaos & Property Stress', () => {
  it('should never allow a blocked/unsupported metric to have a numeric value', () => {
    // Generate 1000 random chaotic inputs
    const badStatuses: MetricStatus[] = ['BLOCKED', 'NOT_AVAILABLE', 'UNSUPPORTED', 'ABSTAINED'];
    
    for (let i = 0; i < 1000; i++) {
      const status = badStatuses[Math.floor(Math.random() * badStatuses.length)];
      const value = Math.random() * 100; // A non-null value
      
      const payload: MetricEvidenceParams = {
        metric: {
          metric_name: `TEST_METRIC_${i}`,
          status: status,
          value: value,
        }
      };

      expect(() => buildMetricEvidenceView(payload))
        .toThrow('UNSUPPORTED_OR_BLOCKED_METRIC_MUST_BE_NULL');
    }
  });

  it('should strictly reject uncalibrated probabilities or confusing confidence', () => {
    // We expect 1000 iterations of chaotic uncertainty objects to throw or pass correctly
    for (let i = 0; i < 1000; i++) {
      const isRuleConf = Math.random() > 0.5;
      const hasProb = Math.random() > 0.5;
      
      const uncertainty = {
        uncertainty_type: isRuleConf ? 'RULE_CONFIDENCE' : 'STATISTICAL',
        calibrated_probability: hasProb ? Math.random() : null,
        calibration_status: Math.random() > 0.5 ? 'CALIBRATED' : 'UNCALIBRATED',
      };

      if (isRuleConf && hasProb) {
        expect(() => validateUncertainty(uncertainty)).toThrow('RULE_CONFIDENCE_MUST_NOT_BE_PROBABILITY');
      } else if (hasProb && uncertainty.calibration_status !== 'CALIBRATED') {
        expect(() => validateUncertainty(uncertainty)).toThrow('UNCALIBRATED_PROBABILITY_FORBIDDEN');
      } else {
        expect(validateUncertainty(uncertainty)).toBe(true);
      }
    }
  });

  it('should handle extreme reason_codes gracefully', () => {
    // Generate 100 random reason codes
    const reasons = Array.from({ length: 100 }, (_, i) => `REASON_CODE_OVERFLOW_${i}`);
    
    const payload: MetricEvidenceParams = {
      metric: {
        metric_name: `RMS_EXTREME`,
        status: 'BLOCKED',
        reason_codes: reasons,
      }
    };

    const view = buildMetricEvidenceView(payload);
    expect(view.reason_codes.length).toBe(100);
    // Real validation of layout overflow will happen in the E2E test.
  });
});
