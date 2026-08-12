from __future__ import annotations
import importlib.util, json, pathlib, pytest
from jsonschema import Draft202012Validator
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'services/evidence-service/src/build_bundle.py'
spec=importlib.util.spec_from_file_location('b',P); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
SCHEMA=json.loads((ROOT/'packages/common-schemas/json/session-evidence-bundle.v0.1.schema.json').read_text())
SRC='src_sha256_'+'1'*64; MAN='pman_sha256_'+'2'*64; RUN='prun_sha256_'+'3'*64; ART='part_sha256_'+'4'*64

def base():
 return dict(session_id='s1',source_refs=[SRC],qc={'signal_quality':'PASS','supportability':'SUPPORTABLE','evaluation_status':'EVALUATED','reason_codes':['QC_PASS'],'evidence_refs':['day30-qc']},processing={'manifest_id':MAN,'processing_run_id':RUN,'processed_artifact_id':ART,'profile_id':'research','profile_fingerprint':'pf','outcome':'COMPLETED'},metrics=[{'metric_id':'m1','metric_name':'RMS','status':'AVAILABLE','value':3.5,'units':'uV','reason_codes':[],'manifest_id':MAN,'evidence_class':'ANALYTICAL_RESEARCH'},{'metric_id':'m2','metric_name':'ACTIVATION_TIMING','status':'NOT_AVAILABLE','value':None,'units':'s','reason_codes':['REAL_ALIGNED_EVENT_COHORT_NOT_AVAILABLE'],'manifest_id':MAN,'evidence_class':'NOT_VERIFIED'},{'metric_id':'m3','metric_name':'MFCV','status':'UNSUPPORTED','value':None,'units':'m/s','reason_codes':['SITE_GEOMETRY_NOT_VERIFIED'],'manifest_id':MAN,'evidence_class':'NOT_VERIFIED'}],distribution_support={'status':'UNKNOWN','method_status':'INFORMATIONAL_RESEARCH_ONLY','score':None,'reason_codes':['NO_VALIDATED_OOD_METHOD']},uncertainty={'uncertainty_type':'RULE_CONFIDENCE','calibration_status':'NOT_APPLICABLE','rule_confidence_level':'UNKNOWN','calibrated_probability':None,'conformal_set':None,'calibration_ref':None,'abstention':False,'abstention_reason':None},unsupported_capabilities=[{'capability':'MFCV_SITE','status':'NOT_VERIFIED','reason_codes':['SITE_GEOMETRY_NOT_VERIFIED']}],limitations=['research only'],event_correlation_id='corr_1',evidence_refs=['day45','day46'])
def test_round_trip_and_determinism():
 x=b.build_session_evidence_bundle(**base()); y=b.build_session_evidence_bundle(**base()); assert x==y; Draft202012Validator(SCHEMA).validate(x)
def test_unavailable_requires_null_reason():
 d=base(); d['metrics'][1]['value']=0.0
 with pytest.raises(ValueError,match='UNAVAILABLE_METRIC'): b.build_session_evidence_bundle(**d)
def test_orphan_metric_rejected():
 d=base(); d['metrics'][0]['manifest_id']='pman_sha256_'+'9'*64
 with pytest.raises(ValueError,match='ORPHAN'): b.build_session_evidence_bundle(**d)
def test_fake_ood_score_rejected():
 d=base(); d['distribution_support']['score']=0.9
 with pytest.raises(ValueError,match='FAKE_OOD'): b.build_session_evidence_bundle(**d)
def test_rule_confidence_not_probability():
 d=base(); d['uncertainty']['calibrated_probability']=0.8
 with pytest.raises(ValueError,match='RULE_CONFIDENCE'): b.build_session_evidence_bundle(**d)
def test_human_summary_contains_null_and_limitations():
 x=b.build_session_evidence_bundle(**base()); s=b.render_human_summary(x); assert 'value=null' in s and 'Limitations:' in s
def test_processing_failed_rejected():
 d=base(); d['processing']['outcome']='FAILED'
 with pytest.raises(ValueError,match='PROCESSING_MUST_BE_COMPLETED'): b.build_session_evidence_bundle(**d)
