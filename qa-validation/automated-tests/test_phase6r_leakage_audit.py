import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "ai-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "ai-core"))

from governance.phase6r_leakage import audit_leakage

def base_repo(root: Path):
    (root / 'qa-validation/evidence').mkdir(parents=True, exist_ok=True)
    (root / 'ai-core/features').mkdir(parents=True, exist_ok=True)
    (root / 'ai-core/features/research-feature-registry-v0.1.yaml').write_text('features:\n  - rms\n  - mav\n  - mdf_hz\n  - mnf_hz\n', encoding='utf-8')
    (root / 'qa-validation/evidence/locked-evaluation-policy.md').write_text('LOCKED_EVALUATION remained UNTOUCHED and excluded from tuning.\n', encoding='utf-8')

class LeakageTests(unittest.TestCase):
    def test_subject_overlap_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_repo(root)
            (root / 'qa-validation/evidence/research-ml-splits-v0.1.csv').write_text(
                'dataset,subject_id,source_window_id,example_id,split\na,s1,w1,e1,train\na,s1,w9,e9,locked_evaluation\n',
                encoding='utf-8'
            )
            result = audit_leakage(root)
            findings = {x['check']: x for x in result['findings']}
            self.assertEqual(findings['subject_overlap']['status'], 'FAIL')

    def test_source_derivative_overlap_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_repo(root)
            (root / 'qa-validation/evidence/research-ml-splits-v0.1.csv').write_text(
                'dataset,subject_id,source_window_id,example_id,split\na,s1,w1,e1,train\na,s2,w1,e2,locked_evaluation\n',
                encoding='utf-8'
            )
            result = audit_leakage(root)
            findings = {x['check']: x for x in result['findings']}
            self.assertEqual(findings['source_derivative_leakage']['status'], 'FAIL')

    def test_clean_grouped_split_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_repo(root)
            (root / 'qa-validation/evidence/research-ml-splits-v0.1.csv').write_text(
                'dataset,subject_id,source_window_id,example_id,split\na,s1,w1,e1,train\na,s2,w2,e2,validation\na,s3,w3,e3,locked_evaluation\n',
                encoding='utf-8'
            )
            result = audit_leakage(root)
            self.assertEqual(result['status'], 'PASS')

if __name__ == '__main__':
    unittest.main()
