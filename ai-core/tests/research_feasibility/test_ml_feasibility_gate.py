import hashlib, json, os, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class MlFeasibilityGateTests(unittest.TestCase):
    def setUp(self): self.d=json.loads((ROOT/'data/research_feasibility_results/gate_evaluation.json').read_text())
    def test_gate_blocks_public_milestone(self):
        self.assertEqual(self.d['status'],'BLOCKED_WITH_EVIDENCE'); self.assertFalse(self.d['public_benchmark_ready']); self.assertFalse(self.d['next_stage_ready'])
    def test_expected_blockers(self):
        expected={'NO_PUBLIC_CROSS_DATASET_FEATURE_COMPARISON','PUBLIC_GENERALIZATION_NOT_ESTABLISHED','SITE_EVIDENCE_ORIGIN_IS_NOT_PUBLIC'}
        self.assertEqual(set(self.d['blockers']),expected)
    def test_site_feature_hash_frozen(self):
        self.assertEqual(self.d['frozen_input_hashes']['site_feature_parquet_sha256'],'4575223ace0b8ea6a24499666769b5dae3231e8b85c0505f7dc986062b5efee8')
    def test_leakage_contract_preserved(self):
        self.assertTrue(self.d['locked_policy_preserved']); self.assertFalse(self.d['locked_outcome_tuning_detected'])
    def test_mandatory_outputs_exist(self):
        paths=['docs/executive/gates/GATE-E-R-public-benchmark.md','docs/executive/milestones/M5-R-public-benchmark.md','docs/evidence_index/public-benchmark-evidence-index.md']
        for p in paths: self.assertTrue((ROOT/p).is_file(),p)
if __name__=='__main__': unittest.main()
