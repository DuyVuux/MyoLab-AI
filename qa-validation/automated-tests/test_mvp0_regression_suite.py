from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'scripts/data'
if str(SCRIPTS) not in sys.path: sys.path.insert(0,str(SCRIPTS))
PIPELINES=ROOT/'ai-core/pipelines'
if str(PIPELINES) not in sys.path: sys.path.insert(0,str(PIPELINES))

from run_mvp0_regression import load_regression_profile, scan_forbidden_keys, within_range, scenario_signature, check_expected
from offline_analysis import run_offline_analysis


def test_profile_loads():
    p=load_regression_profile(ROOT/'qa-validation/configs/mvp0_regression_v0.1.yaml')
    assert p['profile_id']=='mvp0_regression_v0.1'
    assert len(p['scenarios'])==7


def test_range_helper():
    assert within_range(0.95,[0.9,1.0])
    assert not within_range(1.1,[0.9,1.0])


def test_forbidden_key_scanner():
    hits=scan_forbidden_keys({'a':{'samples_uV':[1,2]},'patient_name':'x'},{'samples_uV','patient_name'})
    assert 'root.a.samples_uV' in hits
    assert 'root.patient_name' in hits


def test_golden_and_flatline_contract(tmp_path:Path):
    profile=load_regression_profile(ROOT/'qa-validation/configs/mvp0_regression_v0.1.yaml')
    for scenario_id in ('golden','fail_flatline'):
        cfg=profile['scenarios'][scenario_id]
        out=tmp_path/scenario_id
        manifest=run_offline_analysis(manifest_path=ROOT/cfg['manifest'],output_dir=out,config_path=ROOT/profile['pipeline_config'])
        qc=json.loads((out/'01-qc-result.json').read_text(encoding='utf-8'))
        inference=json.loads((out/'10-explainable-inference.json').read_text(encoding='utf-8'))
        sig=scenario_signature(manifest,qc,inference)
        assert all(x['passed'] for x in check_expected(sig,cfg['expected']))
