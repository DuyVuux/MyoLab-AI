#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/04-api/examples'; out.mkdir(parents=True,exist_ok=True)
golden=json.loads((ROOT/'qa-validation/evidence/day17-golden-api-summary.json').read_text(encoding='utf-8'))
abstained=json.loads((ROOT/'qa-validation/evidence/day17-abstained-api-summary.json').read_text(encoding='utf-8'))
examples={
 'session-import.response.json':{
   'schema_version':'session-import-response.v0.1','session_id':golden['session_id'],'status':'imported','source_file_sha256':golden['provenance']['source_hash_sha256'],'reason_codes':[],'links':{'self':f"/v1/sessions/{golden['session_id']}"}
 },
 'analysis-job.response.json':{
   'schema_version':'analysis-job.v0.1','analysis_id':golden['analysis_id'],'session_id':golden['session_id'],'status':'completed','submitted_at':None,'completed_at':None,'links':{'self':f"/v1/analyses/{golden['analysis_id']}",'summary':f"/v1/analyses/{golden['analysis_id']}/summary"}
 },
 'analysis-completed.response.json':golden,
 'analysis-abstained.response.json':abstained,
 'problem-details.response.json':{
   'type':'https://example.local/problems/semantic-validation','title':'Semantic validation không đạt','status':422,'detail':'Manifest thiếu metadata bắt buộc.','instance':'/v1/sessions/import','error_code':'MANIFEST_REQUIRED_FIELD_MISSING','trace_id':'TRACE-DEMO-0001','invalid_params':[{'name':'sampling_rate_hz','reason':'required'}]
 }
}
for name,payload in examples.items():
    (out/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('DAY 17 EXAMPLES: GENERATED')
