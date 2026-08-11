from __future__ import annotations
import importlib.util,json,sys
from pathlib import Path
import numpy as np
import pytest,yaml
ROOT=Path(__file__).resolve().parents[3]
LIB=ROOT/'qa-validation/lib/day35_threshold_study.py'
spec=importlib.util.spec_from_file_location('d35',LIB)
m=importlib.util.module_from_spec(spec)
sys.modules['d35']=m
spec.loader.exec_module(m)
PROFILE=yaml.safe_load((ROOT/'configs/qc/day35-threshold-study-profile.v0.1.yaml').read_text())
FXM=yaml.safe_load((ROOT/'qa-validation/evidence/day35-threshold-study-fixtures.v0.1.manifest.yaml').read_text())


def fixtures(): return m.load_fixtures(FXM,ROOT/'qa-validation/test-data/research/day35')

def test_01_claim_scope(): assert FXM['claim_scope']=='RESEARCH_ONLY'
def test_02_no_locked_fixture(): assert all(x['partition']=='benchmark-development' for x in FXM['items'])
def test_03_day33_history_not_mutated(): assert FXM['day33_history_mutated'] is False
def test_04_positive_local_events_overlap_core():
 for x in FXM['items']:
  if x['truth_label']==1 and x['event_bounds']:
   a,b=x['event_bounds']
   s=x['window_context']['start_sample']
   e=x['window_context']['end_sample_exclusive']
   assert max(a,s)<min(b,e)
def test_05_primary_has_pos_neg_each_family():
 primary=[x for x in FXM['items'] if x['stratum']=='PRIMARY']
 for fam in [x for x in PROFILE['readiness'] if x!='LF_POOR_CONTACT']:
  ys={x['truth_label'] for x in primary if x['family_id']==fam}
  assert ys=={0,1}
def test_06_poor_contact_hold(): assert PROFILE['readiness']['LF_POOR_CONTACT']['status']=='HOLD_NOT_SCORABLE'
def test_07_no_training(): assert PROFILE['training_allowed'] is False and PROFILE['label_model_training_allowed'] is False
def test_08_locked_access_forbidden(): assert PROFILE['locked_partition_access_allowed'] is False
def test_09_candidate_grid_dropout_nonempty(): assert len(m.candidate_grid(PROFILE,'LF_MISSING_DROPOUT'))>10
def test_10_candidate_grid_motion_nonempty(): assert len(m.candidate_grid(PROFILE,'LF_LOW_FREQUENCY_CONTAMINATION'))==36

def test_11_load_fixture_hashes(): assert len(fixtures())==len(FXM['items'])
def test_12_deterministic_fixture_payload_hashes():
 f=fixtures()[0]
 assert f['signal_artifact']['sha256']==m.sha256_file(ROOT/'qa-validation/test-data/research/day35'/f['signal_artifact']['relative_path'])
def test_13_window_identity_core():
 w=m.build_window(fixtures()[0])
 assert w.end_sample_exclusive>w.start_sample
def test_14_reject_locked_fixture_in_loader(tmp_path):
 mm=dict(FXM)
 mm['items']=[dict(FXM['items'][0],partition='benchmark-locked')]
 with pytest.raises(m.Day35StudyError,match='LOCKED'): m.load_fixtures(mm,ROOT/'qa-validation/test-data/research/day35')
def test_15_sealed_day33_guard():
 d=yaml.safe_load((ROOT/'qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml').read_text())
 assert m.verify_day33_locked_isolation(d)==6

def test_16_sweep_reproducible():
 p=[x for x in fixtures() if x['stratum']=='PRIMARY']
 a,sa=m.run_sweep(PROFILE,p,ROOT)
 b,sb=m.run_sweep(PROFILE,p,ROOT)
 assert a==b and sa==sb
def test_17_sweep_selects_five():
 p=[x for x in fixtures() if x['stratum']=='PRIMARY']
 _,s=m.run_sweep(PROFILE,p,ROOT)
 assert len(s)==5
def test_18_selected_no_site_claim():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 m.validate_threshold_config(cfg)
def test_19_site_thresholds_all_null():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 assert all(v is None for v in cfg['profiles']['site-template']['thresholds'].values())
def test_20_site_status_not_verified():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 assert cfg['site_threshold_status']=='NOT_VERIFIED'
def test_21_poor_contact_not_selected():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 assert cfg['profiles']['research-synthetic-v0.1']['detectors']['LF_POOR_CONTACT']['status']=='HOLD_NOT_SCORABLE'
def test_22_research_threshold_claim_false():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 assert cfg['profiles']['research-synthetic-v0.1']['clinical_threshold_claim'] is False

def test_23_decision_locked_zero():
 d=json.loads((ROOT/'qa-validation/evidence/day35-threshold-selection-decision.v0.1.json').read_text())
 assert d['locked_partition_consumed']==0
def test_24_decision_five_selected_one_hold():
 d=json.loads((ROOT/'qa-validation/evidence/day35-threshold-selection-decision.v0.1.json').read_text())
 assert sum(v['status']=='SELECTED_RESEARCH_HEURISTIC' for v in d['decisions'].values())==5
def test_25_robustness_has_multiple_fs():
 import csv
 with (ROOT/'qa-validation/evidence/day35-robustness-by-fs-window-v0.1.csv').open() as f: rows=list(csv.DictReader(f))
 assert {int(r['sampling_rate_hz']) for r in rows}=={1000,2000,4000}
def test_26_robustness_has_two_windows():
 import csv
 with (ROOT/'qa-validation/evidence/day35-robustness-by-fs-window-v0.1.csv').open() as f: rows=list(csv.DictReader(f))
 assert {float(r['window_duration_seconds']) for r in rows}=={0.25,0.5}
def test_27_no_locked_word_in_selection_source_as_access():
 text=(ROOT/'qa-validation/lib/day35_threshold_study.py').read_text()
 assert 'np.load' in text and 'DAY35_LOCKED_PARTITION_ACCESS_FORBIDDEN' in text
def test_28_threshold_schema_exists(): assert (ROOT/'packages/common-schemas/json/qc-threshold-research-profile.v0.1.schema.json').exists()
def test_29_readiness_six_rows():
 import csv
 with (ROOT/'qa-validation/evidence/day35-scorable-truth-readiness-matrix.csv').open() as f: assert len(list(csv.DictReader(f)))==6
def test_30_claim_boundary_doc(): assert 'NOT CLINICALLY VALIDATED' in (ROOT/'docs/00-executive/day35/DAY35_CLAIM_BOUNDARY.md').read_text()

@pytest.mark.parametrize('family',["LF_MISSING_DROPOUT","LF_CLIPPING_SATURATION","LF_BASELINE_NOISE","LF_POWERLINE","LF_LOW_FREQUENCY_CONTAMINATION"])
def test_family_selected_params_exist(family):
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 assert cfg['profiles']['research-synthetic-v0.1']['detectors'][family]['parameters']

@pytest.mark.parametrize('bad_status',["APPROVED","SITE_VALIDATED","CLINICALLY_VALIDATED"])
def test_reject_site_promotion(bad_status):
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 cfg['site_threshold_status']=bad_status
 with pytest.raises(m.Day35StudyError): m.validate_threshold_config(cfg)

def test_reject_site_numeric_threshold():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 cfg['profiles']['site-template']['thresholds']['powerline_warning_ratio']=0.08
 with pytest.raises(m.Day35StudyError): m.validate_threshold_config(cfg)

def test_reject_poor_contact_promotion():
 cfg=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 cfg['profiles']['research-synthetic-v0.1']['detectors']['LF_POOR_CONTACT']['status']='SELECTED_RESEARCH_HEURISTIC'
 with pytest.raises(m.Day35StudyError): m.validate_threshold_config(cfg)
