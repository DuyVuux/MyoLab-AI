import { buildQueueSummary, PRIORITY } from '../../../src/features/qc-dashboard/utils/qc-semantics';
import { CaseRecord } from '../../../src/features/qc-dashboard/types/qc-semantics';
import { describe, it, expect } from 'vitest';

describe('qc-semantics Stress Test (DAY 56)', () => {
  it('should process and sort 10,000+ sessions efficiently', () => {
    const NUM_RECORDS = 15000;
    const records: CaseRecord[] = [];
    
    // Generate massive mock data
    const possibleQC = [
      { signal_quality: 'FAIL' },
      { supportability: 'BLOCKED' },
      { signal_quality: 'WARNING' },
      { supportability: 'UNKNOWN' },
      { signal_quality: 'PASS', supportability: 'SUPPORTABLE' },
      { evaluation_status: 'INSUFFICIENT_EVIDENCE' },
      null,
    ];

    for (let i = 0; i < NUM_RECORDS; i++) {
      const qcState = possibleQC[i % possibleQC.length];
      records.push({
        case_id: `CASE_${i.toString().padStart(6, '0')}`,
        qc: qcState as any,
        review_state: i % 10 === 0 ? 'NEEDS_REVIEW' : 'NEW',
        claim_scope: 'RESEARCH_ONLY',
        source_refs: [],
      });
    }

    const startTime = performance.now();
    const summary = buildQueueSummary(records);
    const endTime = performance.now();

    const duration = endTime - startTime;
    console.log(`Processed ${NUM_RECORDS} records in ${duration.toFixed(2)}ms`);

    expect(summary.items.length).toBe(NUM_RECORDS);
    // Should be reasonably fast (e.g. < 50ms)
    expect(duration).toBeLessThan(100);

    // Verify ordering is preserved: priority 0 (FAIL) first, then 1, 2, 3 (PASS)
    let prevPriority = -1;
    for (const item of summary.items) {
      expect(item.priority).toBeGreaterThanOrEqual(prevPriority);
      prevPriority = item.priority;
    }
  });

  it('should handle state conflicts and unknown properly without crashing', () => {
    const conflictingRecords: CaseRecord[] = [
      {
        case_id: 'CONFLICT_1',
        qc: { signal_quality: 'FAIL', supportability: 'SUPPORTABLE' }, // Conflict
        review_state: 'APPROVED' as any,
      },
      {
        case_id: 'CONFLICT_2',
        qc: null,
      },
      {
        case_id: 'CONFLICT_3',
        qc: { signal_quality: 'PASS', supportability: 'UNKNOWN' },
      }
    ];

    const summary = buildQueueSummary(conflictingRecords);
    expect(summary.items).toHaveLength(3);
    
    const conflict1 = summary.items.find(i => i.case_id === 'CONFLICT_1');
    expect(conflict1?.attention).toBe('FAIL'); // FAIL overrides

    const conflict2 = summary.items.find(i => i.case_id === 'CONFLICT_2');
    expect(conflict2?.attention).toBe('UNKNOWN'); // Null fallback

    const conflict3 = summary.items.find(i => i.case_id === 'CONFLICT_3');
    expect(conflict3?.attention).toBe('UNKNOWN'); // Unknown fallback
  });
});
