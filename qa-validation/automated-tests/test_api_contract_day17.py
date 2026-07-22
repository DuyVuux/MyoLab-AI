from pathlib import Path
import json,sys,yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
PIPELINES=ROOT/'ai-core/pipelines'; SCHEMAS=ROOT/'services/api-server/src/schemas'
for p in (PIPELINES,SCHEMAS):
    if str(p) not in sys.path: sys.path.insert(0,str(p))
from offline_analysis import run_offline_analysis
from analysis_contract import build_session_analysis_summary, canonical_hash


def test_golden_and_abstained_summaries(tmp_path:Path):
    cases=[
      ('golden',ROOT/'data-platform/synthetic-data/golden_signal_01.manifest.json','completed','supported_pattern'),
      ('flatline',ROOT/'qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json','abstained','abstained'),
    ]
    schema=json.loads((ROOT/'packages/common-schemas/json/session-analysis-summary.schema.json').read_text(encoding='utf-8'))
    for name,manifest_path,status,conclusion in cases:
        out=tmp_path/name
        run_offline_analysis(manifest_path=manifest_path,output_dir=out,config_path=ROOT/'ai-core/configs/offline_analysis_mvp0.yaml')
        summary=build_session_analysis_summary(out)
        payload=summary.model_dump(mode='json')
        assert summary.status==status
        assert summary.technical_conclusion==conclusion
        assert not list(Draft202012Validator(schema).iter_errors(payload))
        text=json.dumps(payload).lower()
        assert 'raw_samples' not in text and 'patient_name' not in text


def test_summary_deterministic(tmp_path:Path):
    out=tmp_path/'golden'
    run_offline_analysis(manifest_path=ROOT/'data-platform/synthetic-data/golden_signal_01.manifest.json',output_dir=out,config_path=ROOT/'ai-core/configs/offline_analysis_mvp0.yaml')
    a=build_session_analysis_summary(out).model_dump(mode='json')
    b=build_session_analysis_summary(out).model_dump(mode='json')
    assert a==b
    h=a.pop('summary_hash_sha256')
    assert h==canonical_hash(a)


def test_openapi_operation_ids_unique_and_refs_local():
    doc=yaml.safe_load((ROOT/'openapi.yaml').read_text(encoding='utf-8'))
    ids=[]
    for path,ops in doc['paths'].items():
        for method,op in ops.items():
            if method in {'get','post','put','patch','delete'}:
                ids.append(op['operationId'])
    assert len(ids)==len(set(ids))
    assert doc['openapi'].startswith('3.1.')
