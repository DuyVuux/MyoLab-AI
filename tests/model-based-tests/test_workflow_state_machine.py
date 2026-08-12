import random
from state_machine import ReviewContext,transition
def ctx(q='PASS'): return ReviewContext('seb',q,('AVAILABLE',),reviewer_id='R',reviewer_approval=True,reason_code='R',new_evidence_bundle_ref='seb2')
def test_random_5000():
 rng=random.Random(6201); states=['NEW','NEEDS_REVIEW','REVIEWING','REPROCESS_REQUESTED','REMEASURE_SUGGESTED','INCONCLUSIVE','ACCEPTED_TECHNICAL','FINALIZED_DEMO']; actions=['QUEUE_FOR_REVIEW','START_REVIEW','REQUEST_REPROCESS','SUGGEST_REMEASURE','MARK_INCONCLUSIVE','ACCEPT_TECHNICAL','REPROCESS_COMPLETED','CLOSE_PENDING_REMEASUREMENT','FINALIZE_DEMO']
 for _ in range(5000):
  s=rng.choice(states); a=rng.choice(actions)
  try: r=transition(s,a,ctx()); assert not(s=='NEW' and r.state_after=='FINALIZED_DEMO')
  except ValueError: pass
def test_qc_fail():
 try: transition('REVIEWING','ACCEPT_TECHNICAL',ctx('FAIL')); assert False
 except ValueError: pass
