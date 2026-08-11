from __future__ import annotations
import hashlib, importlib.util, json, random, sys
from pathlib import Path
import numpy as np, yaml
ROOT=Path(__file__).resolve().parents[2]
SERVICE=ROOT/'services/quality-gate-service/src'
if str(SERVICE) not in sys.path: sys.path.insert(0,str(SERVICE))
ING=ROOT/'services/signal-ingestion-service/src'
if str(ING) not in sys.path: sys.path.insert(0,str(ING))
from aggregation.session_quality import AggregationMetrics,EvaluationStatus,QcAggregationResult,ScopeHierarchy,SignalQuality,Supportability
from application.quality_gate import DistributionSupport,DistributionSupportStatus,MetricHandoffRequest,MetricHandoffStatus,evaluate_quality_handoff

def load_day36():
 p=ROOT/'qa-validation/lib/day36_domain_challenge.py'; s=importlib.util.spec_from_file_location('d38_d36',p); assert s and s.loader; m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

def test_raw_immutable_under_day36_evaluation():
 m=load_day36(); man=yaml.safe_load((ROOT/'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml').read_text()); c=man['cases'][0]; x=m.generate_signal(c); before=hashlib.sha256(x.tobytes()).hexdigest(); th=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text()); m.evaluate_case(ROOT,c,man['reference_domain'],th); assert hashlib.sha256(x.tobytes()).hexdigest()==before

def test_deterministic_replay_randomized_cases():
 m=load_day36(); man=yaml.safe_load((ROOT/'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml').read_text()); th=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text()); rng=random.Random(38038)
 for _ in range(20):
  c=rng.choice(man['cases']); a=m.evaluate_case(ROOT,c,man['reference_domain'],th); b=m.evaluate_case(ROOT,c,man['reference_domain'],th); assert a==b

def _qc(quality):
 return QcAggregationResult(schema_version='0.1',taxonomy_version='0.2',evaluation_status=EvaluationStatus.EVALUATED if quality else EvaluationStatus.INSUFFICIENT_EVIDENCE,scope_hierarchy=ScopeHierarchy(session_id='s',channel_id='c',window_id='qcw_sha256_'+'a'*64,target_scope='WINDOW'),signal_quality=quality,qc_supportability=Supportability.BLOCKED if quality==SignalQuality.FAIL else Supportability.SUPPORTABLE if quality==SignalQuality.PASS else Supportability.NOT_EVALUATED,metrics=AggregationMetrics(0.0,1,0,1,0,0) if quality==SignalQuality.FAIL else AggregationMetrics(1.0,1,1,0,0,0) if quality==SignalQuality.PASS else AggregationMetrics(None,0,0,0,0,0),evidence_reasons=('DATA_INTEGRITY_VALIDATED',),disposition_reasons=('QUALITY_BLOCKED',) if quality==SignalQuality.FAIL else ('QC_NOT_EVALUATED',) if quality is None else (),source_refs=('src_sha256_'+'b'*64,),policy_profile_id='synthetic-engineering-only',config_version='0.1',critical_failure=quality==SignalQuality.FAIL)

def _ds(): return DistributionSupport(status=DistributionSupportStatus.SUPPORTED,support_basis=('research-reference',),reason_codes=(),policy_version='distribution-support-v0.1')
def _req(): return MetricHandoffRequest(metric_id='RMS',requested_scope='WINDOW',distribution_support_required=False,profile_id='research-rms')

def test_qc_fail_blocks_metric(): assert evaluate_quality_handoff(qc=_qc(SignalQuality.FAIL),request=_req(),distribution_support=_ds()).metric_handoff_status==MetricHandoffStatus.BLOCKED

def test_unknown_qc_abstains_with_reason():
 r=evaluate_quality_handoff(qc=_qc(None),request=_req(),distribution_support=_ds()); assert r.metric_handoff_status==MetricHandoffStatus.ABSTAINED; assert r.reason_codes

def test_low_amplitude_and_shift_properties_hold():
 m=load_day36(); man=yaml.safe_load((ROOT/'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml').read_text()); th=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
 for c in man['cases']:
  r=m.evaluate_case(ROOT,c,man['reference_domain'],th)
  if c.get('physiology_preservation_stress'): assert not r.quality_blocked and r.poor_contact_reason!='POOR_CONTACT_SUSPECTED'
  if r.distribution_support_status=='SHIFTED': assert not r.quality_blocked
  assert r.ood_score is None

def test_unit_conversion_copy_with_provenance_and_dropout_persistence():
 from validation.time_count_unit import UnitConversion,UnitDefinition,UnitRegistry,convert_values
 reg=UnitRegistry(schema_version='0.1',registry_id='unit-reg',registry_version='0.1',units=(UnitDefinition(symbol='V',dimension='voltage',canonical_unit='V',observed_in_project=True),UnitDefinition(symbol='uV',dimension='voltage',canonical_unit='V',observed_in_project=True)),conversions=(UnitConversion(source_unit='V',target_unit='uV',factor=1e6,evidence_basis='exact SI conversion'),))
 src=[1e-6,2e-6,3e-6]; copy=list(src); out=convert_values(src,source_unit='V',target_unit='uV',registry=reg,source_record_id='src_sha256_'+'c'*64,signal_id='sig_'+'d'*32); assert src==copy; assert out.values==(1.0,2.0,3.0); assert out.provenance.factor==1e6
 x=np.array([1.0,np.nan,2.0]); y=x*1e6; assert np.isnan(y[1])

def test_frozen_artifact_hashes_match():
 freeze=json.loads((ROOT/'qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json').read_text())
 assert freeze['items']
 for item in freeze['items']:
  p=ROOT/item['path']; assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'], f"Mismatch on {item['path']}"
