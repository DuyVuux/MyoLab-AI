import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "ai-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "ai-core"))

from governance.phase6r_branch import resolve_ml_no_go_branch

class BranchTests(unittest.TestCase):
    def test_no_go_without_distinct_question_closes_not_justified(self):
        result = resolve_ml_no_go_branch(
            entry_pass=True,
            leakage_status='PASS',
            claim_status='PASS',
            starting_ml_decision='ML_NO_GO',
            distinct_representation_question=False
        )
        self.assertEqual(result['m6_r'], 'RESEARCH_ML_NOT_JUSTIFIED')

    def test_leakage_failure_blocks(self):
        result = resolve_ml_no_go_branch(
            entry_pass=True,
            leakage_status='FAIL',
            claim_status='PASS',
            starting_ml_decision='ML_NO_GO',
            distinct_representation_question=False
        )
        self.assertEqual(result['execution_status'], 'BLOCKED_WITH_EVIDENCE')

    def test_distinct_question_does_not_force_close(self):
        result = resolve_ml_no_go_branch(
            entry_pass=True,
            leakage_status='PASS',
            claim_status='PASS',
            starting_ml_decision='ML_NO_GO',
            distinct_representation_question=True
        )
        self.assertIsNone(result['m6_r'])

if __name__ == '__main__':
    unittest.main()
