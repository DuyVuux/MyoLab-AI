import {
  UC2AssessmentClient,
  getMockUC2Assessment,
  type UC2Scenario,
} from './uc2-assessment-client';

describe('UC2AssessmentClient Unit Tests', () => {
  const scenarios: UC2Scenario[] = [
    'golden_uc2_longitudinal',
    'uc2_protocol_incompatible',
    'uc2_missing_baseline',
    'uc2_qc_fail_session',
    'uc2_bilateral_unavailable',
  ];

  describe('getMockUC2Assessment', () => {
    it('returns valid mock assessment for all scenarios', () => {
      scenarios.forEach((scenario) => {
        const result = getMockUC2Assessment(scenario);
        expect(result.schemaVersion).toBe('uc2-quantitative-assessment.v0.1');
        expect(result.assessmentId).toBe(`UC2-E2E-${scenario}`);
        expect(result.subjectRef).toBe('SUBJ-D23-E2E');
        expect(result.safety.humanReviewRequired).toBe(true);
      });
    });

    it('returns blocked status for uc2_protocol_incompatible', () => {
      const result = getMockUC2Assessment('uc2_protocol_incompatible');
      expect(result.status).toBe('blocked');
      expect(result.compatibility.status).toBe('blocked');
      expect(result.compatibility.conclusionAllowed).toBe(false);
      expect(result.compatibility.reasonCodes).toContain(
        'PROTOCOLVERSION_MISMATCH'
      );
    });

    it('returns blocked status for uc2_missing_baseline', () => {
      const result = getMockUC2Assessment('uc2_missing_baseline');
      expect(result.status).toBe('blocked');
      expect(result.compatibility.status).toBe('blocked');
      expect(result.compatibility.conclusionAllowed).toBe(false);
    });

    it('returns blocked status for uc2_qc_fail_session', () => {
      const result = getMockUC2Assessment('uc2_qc_fail_session');
      expect(result.status).toBe('blocked');
      expect(result.compatibility.status).toBe('blocked');
    });

    it('returns completed_with_warnings status for golden scenario', () => {
      const result = getMockUC2Assessment('golden_uc2_longitudinal');
      expect(result.status).toBe('completed_with_warnings');
      expect(result.metrics.length).toBeGreaterThan(0);
      expect(result.compatibility.conclusionAllowed).toBe(true);
    });
  });

  describe('UC2AssessmentClient class', () => {
    it('returns mock assessment when baseUrl is empty', async () => {
      const client = new UC2AssessmentClient();
      const assessment = await client.create('golden_uc2_longitudinal');
      expect(assessment.assessmentId).toBe('UC2-E2E-golden_uc2_longitudinal');
      expect(assessment.metrics).toHaveLength(3);
    });

    it('falls back to mock assessment when fetch throws', async () => {
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      const client = new UC2AssessmentClient('http://localhost:9999');
      const assessment = await client.create('golden_uc2_longitudinal');
      expect(assessment.assessmentId).toBe('UC2-E2E-golden_uc2_longitudinal');

      global.fetch = originalFetch;
    });

    it('fetches from API when baseUrl is provided and server responds ok', async () => {
      const mockData = getMockUC2Assessment('golden_uc2_longitudinal');
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      } as Response);

      const client = new UC2AssessmentClient('http://localhost:3000');
      const assessment = await client.create('golden_uc2_longitudinal');
      expect(assessment).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/v1/uc2/assessments',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ scenarioId: 'golden_uc2_longitudinal' }),
        })
      );

      global.fetch = originalFetch;
    });
  });
});
