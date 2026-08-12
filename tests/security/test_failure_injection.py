from append_only_store import AppendOnlyJsonlStore
def e(): return {'event_id':'evt1','event_type':'SYSTEM_WORKFLOW','case_id':'C','activity':'A','actor_role':'SYSTEM','event_time_utc':'2026-01-01T00:00:00Z','correlation_id':'corr','reason_codes':[],'source_refs':[],'versions':{'v':'1'}}
def test_tamper(tmp_path):
 p=tmp_path/'x.jsonl'; s=AppendOnlyJsonlStore(p,'R'); s.append(e()); p.write_text(p.read_text().replace('SYSTEM_WORKFLOW','REVIEW_ACTION'))
 try: s.verify_integrity(); assert False
 except ValueError: pass
def test_retry(tmp_path):
 s=AppendOnlyJsonlStore(tmp_path/'x.jsonl','R'); a=s.append(e()); b=s.append(e()); assert b.idempotent_replay and a.sequence==b.sequence
