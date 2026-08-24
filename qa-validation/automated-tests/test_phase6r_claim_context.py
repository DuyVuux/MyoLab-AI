import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "ai-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "ai-core"))

from governance.phase6r_claims import audit_claim_boundaries

class ClaimContextTests(unittest.TestCase):
    def test_negated_boundary_is_not_blocking(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'README.md'
            file_path.write_text('Status: NOT CLINICALLY VALIDATED\n', encoding='utf-8')
            result = audit_claim_boundaries(Path(temp_dir))
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['blocking_count'], 0)

    def test_policy_literal_is_not_blocking(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'policy.md'
            file_path.write_text('Forbidden claim: validated at Vinmec\n', encoding='utf-8')
            result = audit_claim_boundaries(Path(temp_dir))
            self.assertEqual(result['status'], 'PASS')

    def test_positive_unsupported_assertion_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'claim.md'
            file_path.write_text('This system is clinically validated.\n', encoding='utf-8')
            result = audit_claim_boundaries(Path(temp_dir))
            self.assertEqual(result['status'], 'FAIL')

if __name__ == '__main__':
    unittest.main()
