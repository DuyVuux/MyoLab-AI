from run_cognitive_walkthrough import run
def test_all(): assert all(x['result']=='PASS' for x in run()['scenarios']) and len(run()['scenarios'])==7
def test_critical(): assert run()['critical_misleading_issues']==0
def test_no_fake_humans(): assert run()['external_human_reviewers']==0
def test_class(): assert run()['evidence_type']=='NON_CLINICAL_ENGINEERING_WALKTHROUGH'
