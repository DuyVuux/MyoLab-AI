import json, os, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class GeneralizationReporterTests(unittest.TestCase):
    def setUp(self): self.d=json.loads((ROOT/'data/research_feasibility_results/generalization_summary.json').read_text())
    def test_denominators(self):
        x=self.d['denominators']; self.assertEqual(x['public_acquisition_all_csv'],187); self.assertEqual(x['public_acquisition_parseable_csv'],183); self.assertEqual(x['public_acquisition_phi_metadata_excluded'],4); self.assertEqual(x['site_metric_rows'],12); self.assertEqual(x['site_metric_available'],12)
    def test_no_supervised_metric_fabrication(self):
        self.assertEqual(self.d['supervised_qc_performance'],'NOT_EVALUATED_NO_REFERENCE_LABELS')
        self.assertEqual(self.d['false_block_proxy'],'NOT_EVALUATED_NO_REFERENCE_LABELS')
    def test_generalization_not_overclaimed(self):
        self.assertEqual(self.d['cross_dataset_generalization'],'NOT_ESTABLISHED_NO_PUBLIC_FEATURE_ROWS')
        self.assertEqual(self.d['subject_generalization'],'NOT_EVALUATED_SUBJECT_IDENTIFIERS_ABSENT')
    def test_ml_question_is_clear(self):
        self.assertEqual(self.d['ml_question']['decision_recommendation'],'ML_NO_GO')
        self.assertFalse(self.d['ml_question']['deterministic_system_insufficient'])
if __name__=='__main__': unittest.main()
