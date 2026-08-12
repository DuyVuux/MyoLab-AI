from offline_workbench import demo_suite
def test_reproducible(): assert demo_suite()==demo_suite() and len(demo_suite())==6
def test_happy_not_final(): assert demo_suite()[0]['finalized'] is False
def test_qc_fail_stops(): assert 'PROCESSING' not in [e['stage'] for e in demo_suite()[1]['events']]
def test_unknown_unit(): assert demo_suite()[2]['events'][-1]['reason']=='UNIT_UNKNOWN'
def test_missing_sync(): assert demo_suite()[3]['events'][-1]['reason']=='SYNC_MISSING'
def test_mfcv_unavailable(): assert any(e['stage']=='MFCV' and e['status']=='UNSUPPORTED' for e in demo_suite()[4]['events'])
def test_reprocess(): assert [e['stage'] for e in demo_suite()[5]['events']].count('REVIEW_QUEUE')==2
def test_no_continue_on_error():
 for x in demo_suite():
  bad=next((i for i,e in enumerate(x['events']) if e['status'] in {'FAIL','BLOCKED'}),None)
  if bad is not None: assert all(e['stage'] not in {'PROCESSING','METRICS'} for e in x['events'][bad+1:])
