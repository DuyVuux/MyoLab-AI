import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "ai-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "ai-core"))

from governance.phase6r_verifier import evaluate_phase6r_entry, audit_claim_boundaries

class Phase6REntryGateTests(unittest.TestCase):
    def test_empty_repository_blocks_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = evaluate_phase6r_entry(Path(temp_dir))
            self.assertFalse(result['execution_allowed'])
            self.assertEqual(result['phase_entry_status'], 'BLOCKED_WITH_EVIDENCE')

    def test_valid_evidence_fixture_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'ai-core/contracts').mkdir(parents=True, exist_ok=True)
            (root / 'qa-validation/evidence').mkdir(parents=True, exist_ok=True)
            (root / 'docs/00-executive/milestones').mkdir(parents=True, exist_ok=True)
            (root / 'docs/00-executive/gates').mkdir(parents=True, exist_ok=True)

            (root / 'docs/00-executive/milestones/m5-r-public-benchmark.md').write_text('PUBLIC_BENCHMARK_READY')
            (root / 'docs/00-executive/gates/gate-e-r.md').write_text('PASS')
            (root / 'qa-validation/evidence/public-benchmark-evidence-index.md').write_text('public benchmark evidence PASS')
            (root / 'ai-core/contracts/public-feature-window-record.md').write_text('PublicFeatureWindowRecord v1.2')
            (root / 'qa-validation/evidence/research-ml-splits-v0.1.csv').write_text('subject,split\na,train\n')
            (root / 'qa-validation/evidence/leakage-audit.md').write_text('leakage PASS')
            (root / 'qa-validation/evidence/reproducibility-report.md').write_text('PASS')
            (root / 'qa-validation/evidence/ml-feasibility-decision.md').write_text('ML_GO')

            result = evaluate_phase6r_entry(root)
            self.assertTrue(result['execution_allowed'])
            self.assertEqual(result['phase_entry_status'], 'PASS')

    def test_claim_boundary_violations_detected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_dir = root / 'docs'
            docs_dir.mkdir(parents=True, exist_ok=True)
            (docs_dir / 'invalid_claim.md').write_text('This feature is validated at Vinmec in production.')

            violations = audit_claim_boundaries(root)
            self.assertGreaterEqual(len(violations), 1)

if __name__ == '__main__':
    unittest.main()
