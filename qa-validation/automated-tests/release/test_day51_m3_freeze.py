from __future__ import annotations
import hashlib,json,pathlib,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[3]
FREEZE=json.loads((ROOT/'qa-validation/evidence/day51-phase3-freeze-manifest.v0.1.json').read_text())
def test_all_frozen_hashes_match():
 for e in FREEZE['artifacts']:
  assert hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256']
def test_freeze_claim_and_unsupported_are_explicit():
 assert FREEZE['status']=='PROCESSING_METRIC_RESEARCH_READY'; assert 'MFCV_SITE' in FREEZE['unsupported_capabilities']; assert 'OOD_SCORE' in FREEZE['unsupported_capabilities']
def test_no_site_promotion_in_processing_profiles():
 text=(ROOT/'configs/processing/preprocessing-profiles.v0.1.yaml').read_text(); assert 'RESEARCH_ONLY' in text; assert 'site_binding: null' in text
def test_bundle_deterministic_clean_replay():
 p=ROOT/'services/evidence-service/src/build_bundle.py'; s=importlib.util.spec_from_file_location('bb',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
 ref=json.loads((ROOT/'qa-validation/evidence/day50-session-evidence-bundle.reference.json').read_text()); body={k:v for k,v in ref.items() if k!='bundle_id'}
 a=m.build_session_evidence_bundle(session_id=body['session_id'],source_refs=body['source_refs'],qc=body['qc'],processing=body['processing'],metrics=body['metrics'],distribution_support=body['distribution_support'],uncertainty=body['uncertainty'],unsupported_capabilities=body['unsupported_capabilities'],limitations=body['limitations'],event_correlation_id=body['event_correlation_id'],evidence_refs=body['evidence_refs']); assert a==ref
def test_unsupported_metrics_are_null_with_reason():
 ref=json.loads((ROOT/'qa-validation/evidence/day50-session-evidence-bundle.reference.json').read_text()); u=[m for m in ref['metrics'] if m['status'] in {'NOT_AVAILABLE','UNSUPPORTED'}]; assert u and all(m['value'] is None and m['reason_codes'] for m in u)
def test_no_fake_uncertainty_or_ood_score():
 ref=json.loads((ROOT/'qa-validation/evidence/day50-session-evidence-bundle.reference.json').read_text()); assert ref['distribution_support']['score'] is None; assert ref['uncertainty']['calibrated_probability'] is None; assert ref['uncertainty']['conformal_set'] is None
