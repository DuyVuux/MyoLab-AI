from technical_summary import SummaryRequest,can_finalize,render
def ev(q='PASS'): return {'bundle_id':'seb','qc':{'signal_quality':q},'metrics':[{'metric_name':'MFCV','value':None,'reason_codes':['SITE_GEOMETRY_NOT_VERIFIED']}],'limitations':['RESEARCH_ONLY']}
def test_fail_block(): assert not can_finalize(SummaryRequest(ev('FAIL'),'FINALIZED_DEMO',True))
def test_approval(): assert not can_finalize(SummaryRequest(ev(),'FINALIZED_DEMO',False))
def test_state(): assert not can_finalize(SummaryRequest(ev(),'ACCEPTED_TECHNICAL',True))
def test_safe(): assert can_finalize(SummaryRequest(ev(),'FINALIZED_DEMO',True))
def test_missing(): assert 'unavailable (SITE_GEOMETRY_NOT_VERIFIED)' in render(SummaryRequest(ev(),'REVIEWING'))
def test_watermark(): assert render(SummaryRequest(ev(),'REVIEWING')).startswith('RESEARCH PROTOTYPE — NOT FOR CLINICAL USE')
def test_no_diag(): assert 'diagnosis' not in render(SummaryRequest(ev(),'REVIEWING')).lower()
