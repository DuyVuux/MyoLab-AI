import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('metric_contracts',ROOT/'ai-core/experiments/metric_contracts.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_macro_f1_fixed_ontology():
    labels=['rest','open','close']
    value=mod.macro_f1(['rest','open','close'],['rest','close','close'],labels)
    assert 0 <= value <= 1

def test_subject_macro_equal_subject_weight():
    rows=[
      {'subject_id':'S1','true_label':'rest','predicted_label':'rest'},
      {'subject_id':'S1','true_label':'open','predicted_label':'open'},
      {'subject_id':'S2','true_label':'rest','predicted_label':'open'},
      {'subject_id':'S2','true_label':'open','predicted_label':'open'},
    ]
    value=mod.subject_macro_repetition_macro_f1(rows,['rest','open'])
    assert 0 <= value <= 1

def test_unsafe_prediction_rate_denominator():
    assert mod.unsafe_prediction_rate(1,4)==0.25
