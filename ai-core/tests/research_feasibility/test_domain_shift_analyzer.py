import csv, hashlib, json, os, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class DomainShiftAnalyzerTests(unittest.TestCase):
    def test_day68_hash_exact(self):
        p=ROOT/'data/upstream-evidence/public-feature-summary-v1.1.parquet'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'4575223ace0b8ea6a24499666769b5dae3231e8b85c0505f7dc986062b5efee8')
    def test_replay_shape_and_semantics(self):
        rows=list(csv.DictReader((ROOT/'data/research_feasibility_results/feature_summary.csv').read_text().splitlines()))
        self.assertEqual(len(rows),12)
        self.assertEqual({r['status'] for r in rows},{'AVAILABLE'})
        self.assertEqual({r['fs_hz'] for r in rows},{'2000.0'})
        self.assertEqual({r['unit'] for r in rows},{'V'})
        self.assertEqual({r['sample_count'] for r in rows},{'33000'})
    def test_public_comparisons_fail_closed(self):
        rows=list(csv.DictReader((ROOT/'data/research_feasibility_results/domain_shift/cross-dataset-domain-shift-v1.0.csv').read_text().splitlines()))
        public=[r for r in rows if 'GRABMYO' in r['domain_b'] or 'HYSER' in r['domain_b']]
        self.assertEqual(len(public),2)
        for r in public:
            self.assertEqual(r['comparison_class'],'INCOMPARABLE')
            self.assertEqual(r['support_state'],'UNKNOWN')
            self.assertEqual(r['ood_score'],'')
            self.assertEqual(r['pathology_inference'],'False')
    def test_origin_correction_blocks_public_claim(self):
        d=json.loads((ROOT/'data/legacy_evidence/domain_shift/site-source-origin-correction.json').read_text())
        self.assertEqual(d['actual_evidence_origin'],'VINMEC_SITE_RAW_TECHNICAL')
        self.assertFalse(d['public_benchmark_claim_eligible'])
        self.assertEqual(d['public_dataset_rows_present'],0)
if __name__=='__main__': unittest.main()
