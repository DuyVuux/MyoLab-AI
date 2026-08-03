import json

from day33.aggregation import aggregate_predictions
from day33.bootstrap import subject_cluster_bootstrap
from day33.cross_day import evaluate_by_day
from day33.failure_cases import extract_failure_cases
from day33.metrics import evaluate_repetitions
from day33.prediction_gate import validate_prediction_rows
from day33.readiness import REQUIRED_REAL, decide_readiness


def row(**kw):
    b={"dataset_id":"d","dataset_view_id":"v","run_id":"r","model_id":"m","feature_arm":"F","outer_fold":0,
       "subject_id":"s","day_id":"D1","session_id":"SE1","repetition_id":"rep","record_id":"rec","window_id":"w",
       "y_true":"a","y_pred":"a","split_name":"validation","score_type":"probability",
       "class_order_json":json.dumps(["a","b"]),"class_scores_json":json.dumps({"a":0.8,"b":0.2}),
       "qc_flags_json":"[]","source_matrix_sha256":"a","fold_manifest_sha256":"b","model_config_sha256":"c"}
    b.update(kw);return b

def test_gate_valid(): assert validate_prediction_rows([row()])["pass"]
def test_gate_test_blocked(): assert not validate_prediction_rows([row(split_name="test")])["pass"]
def test_gate_duplicate(): assert not validate_prediction_rows([row(),row()])["pass"]
def test_gate_pooled(): assert not validate_prediction_rows([row(window_id="w1"),row(dataset_id="x",window_id="w2")])["pass"]
def test_gate_probability_sum(): assert not validate_prediction_rows([row(class_scores_json=json.dumps({"a":.9,"b":.9}))])["pass"]

def test_aggregation_probability():
    rs=[row(window_id="w1"),row(window_id="w2",y_pred="b",class_scores_json=json.dumps({"a":.6,"b":.4}))]
    a=aggregate_predictions(rs)[0];assert a["y_pred"]=="a" and a["window_count"]==2 and a["window_disagreement"]==.5

def test_metrics_subject():
    reps=[]
    for s in ["s1","s2"]:
      reps += [{"subject_id":s,"y_true":"a","y_pred":"a","window_disagreement":0,"score_type":"label_only","probability_confidence":None,"class_order":["a","b"]},
               {"subject_id":s,"y_true":"b","y_pred":"b" if s=="s1" else "a","window_disagreement":0,"score_type":"label_only","probability_confidence":None,"class_order":["a","b"]}]
    m=evaluate_repetitions(reps);assert m["subject_summary"]["subject_count"]==2 and m["subject_summary"]["worst_subject_id"]=="s2"

def test_bootstrap_subject():
    reps=[]
    for s in ["s1","s2","s3"]:
      reps += [{"subject_id":s,"y_true":"a","y_pred":"a","class_order":["a","b"]},
               {"subject_id":s,"y_true":"b","y_pred":"b" if s!="s3" else "a","class_order":["a","b"]}]
    b=subject_cluster_bootstrap(reps,100,1);assert b["cluster_unit"]=="subject_id" and b["window_bootstrap_used"] is False

def test_high_confidence_probability_only():
    r={"dataset_id":"d","dataset_view_id":"v","run_id":"r","model_id":"m","feature_arm":"F","outer_fold":0,"subject_id":"s","day_id":"","session_id":"","repetition_id":"rep","y_true":"a","y_pred":"b","score_type":"probability","probability_confidence":.9,"top2_margin":.7,"window_disagreement":0,"window_count":4,"qc_flags":[],"source_matrix_sha256":"a","fold_manifest_sha256":"b"}
    assert "HIGH_CONFIDENCE_ERROR" in extract_failure_cases([r])[0]["reason_codes"]

def test_decision_not_probability():
    r={"dataset_id":"d","dataset_view_id":"v","run_id":"r","model_id":"m","feature_arm":"F","outer_fold":0,"subject_id":"s","day_id":"","session_id":"","repetition_id":"rep","y_true":"a","y_pred":"b","score_type":"decision_function","probability_confidence":None,"top2_margin":.9,"window_disagreement":0,"window_count":4,"qc_flags":[],"source_matrix_sha256":"a","fold_manifest_sha256":"b"}
    assert "HIGH_CONFIDENCE_ERROR" not in extract_failure_cases([r])[0]["reason_codes"]

def test_cross_day_no_fatigue():
    rs=[{"day_id":"D1","subject_id":"s","y_true":"a","y_pred":"a","class_order":["a","b"]},{"day_id":"D1","subject_id":"s","y_true":"b","y_pred":"b","class_order":["a","b"]}]
    assert evaluate_by_day(rs)[0]["fatigue_inference_allowed"] is False

def test_readiness_blocked_without_predictions(): assert decide_readiness({"prediction_inventory_present":False})["status"]=="TOOLING_READY_REAL_EVALUATION_BLOCKED"
def test_readiness_go(): assert decide_readiness({k:True for k in REQUIRED_REAL})["status"]=="GO_FOR_DAY34_ROBUSTNESS_CALIBRATION"
