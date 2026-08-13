import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class TrainResearchBaselineTests(unittest.TestCase):
    def setUp(self): self.d=json.loads((ROOT/'data/research_feasibility_results/ml_feasibility_decision.json').read_text())
    def test_ml_no_go(self):
        self.assertEqual(self.d['decision'],'ML_NO_GO'); self.assertFalse(self.d['training_executed']); self.assertIsNone(self.d['model_artifact'])
    def test_no_fake_uncertainty(self):
        self.assertEqual(self.d['calibration'],'NOT_APPLICABLE'); self.assertEqual(self.d['conformal'],'NOT_APPLICABLE')
    def test_locked_untouched(self): self.assertFalse(self.d['locked_evaluation_consumed'])
    def test_gate_script_replays_deterministically(self):
        cmd=[sys.executable,str(ROOT/'pipelines/train_research_baseline.py'),'--generalization',str(ROOT/'data/research_feasibility_results/generalization_summary.json')]
        a=subprocess.check_output(cmd,text=True); b=subprocess.check_output(cmd,text=True); self.assertEqual(a,b); self.assertIn('ML_NO_GO',a)
if __name__=='__main__': unittest.main()
