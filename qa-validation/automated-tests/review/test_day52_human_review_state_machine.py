from __future__ import annotations
import importlib.util,pathlib,pytest,yaml,json,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'services/review-service/src/domain/state_machine.py'; s=importlib.util.spec_from_file_location('sm',P); m=importlib.util.module_from_spec(s); sys.modules['sm']=m; s.loader.exec_module(m)
def ctx(**kw):
 d=dict(evidence_bundle_id='seb_sha256_'+'1'*64,qc_signal_quality='PASS',metric_states=('AVAILABLE',),reviewer_id='reviewer_research_01'); d.update(kw); return m.ReviewContext(**d)
def test_happy_path_to_finalized_demo_requires_explicit_approval():
 c=ctx(reviewer_approval=True); state='NEW'; actions=['QUEUE_FOR_REVIEW','START_REVIEW','ACCEPT_TECHNICAL','FINALIZE_DEMO']; events=[]
 for a in actions: r=m.transition(state,a,c); events.append(r.event); state=r.state_after
 assert state=='FINALIZED_DEMO' and len(events)==4 and all(e['event_id'].startswith('revtevt_sha256_') for e in events)
def test_finalize_without_approval_rejected():
 with pytest.raises(ValueError,match='EXPLICIT_REVIEWER_APPROVAL'): m.transition('ACCEPTED_TECHNICAL','FINALIZE_DEMO',ctx(reviewer_approval=False))
def test_direct_finalize_illegal():
 with pytest.raises(ValueError,match='ILLEGAL_TRANSITION'): m.transition('NEW','FINALIZE_DEMO',ctx(reviewer_approval=True))
def test_reprocess_requested_cannot_finalize():
 with pytest.raises(ValueError,match='ILLEGAL_TRANSITION'): m.transition('REPROCESS_REQUESTED','FINALIZE_DEMO',ctx(reviewer_approval=True))
def test_qc_fail_with_valid_metric_is_invalid_context():
 with pytest.raises(ValueError,match='QC_FAIL_CANNOT_HAVE_VALID_METRIC'): m.transition('NEW','QUEUE_FOR_REVIEW',ctx(qc_signal_quality='FAIL'))
def test_qc_fail_can_be_reviewed_if_metric_not_valid_but_not_accepted():
 c=ctx(qc_signal_quality='FAIL',metric_states=('BLOCKED',)); r=m.transition('NEW','QUEUE_FOR_REVIEW',c); assert r.state_after=='NEEDS_REVIEW'
 with pytest.raises(ValueError): m.transition('REVIEWING','ACCEPT_TECHNICAL',c)
def test_reason_required_for_reprocess():
 with pytest.raises(ValueError,match='REASON_CODE_REQUIRED'): m.transition('REVIEWING','REQUEST_REPROCESS',ctx(reason_code=None))
def test_reprocess_completed_requires_new_evidence_ref():
 with pytest.raises(ValueError,match='NEW_EVIDENCE'): m.transition('REPROCESS_REQUESTED','REPROCESS_COMPLETED',ctx())
def test_insufficient_data_and_no_evidence_are_distinct():
 a=ctx(evidence_gap_kind='INSUFFICIENT_DATA'); b=ctx(evidence_gap_kind='NO_EVIDENCE'); assert a.evidence_gap_kind!=b.evidence_gap_kind; m.validate_context(a); m.validate_context(b)
def test_event_is_deterministic_and_signal_free():
 c=ctx(); a=m.transition('NEW','QUEUE_FOR_REVIEW',c).event; b=m.transition('NEW','QUEUE_FOR_REVIEW',c).event; assert a==b; assert a['waveform'] is None and a['diagnosis'] is None
def test_yaml_has_exact_roadmap_states_and_no_diagnostic_state():
 x=yaml.safe_load((ROOT/'packages/common-schemas/state-machines/human-review-state-machine.v0.2-research.yaml').read_text()); expected={'NEW','NEEDS_REVIEW','REVIEWING','REPROCESS_REQUESTED','REMEASURE_SUGGESTED','INCONCLUSIVE','ACCEPTED_TECHNICAL','FINALIZED_DEMO'}; assert set(x['states'])==expected; assert all(tok not in ' '.join(x['states']) for tok in ['DIAGNOSIS','DISEASE','PATHOLOGY'])
def test_m3_freeze_hashes_intact():
 f=json.loads((ROOT/'qa-validation/evidence/day51-phase3-freeze-manifest.v0.1.json').read_text());
 for e in f['artifacts']: assert hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256']
