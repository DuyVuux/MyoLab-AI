from pathlib import Path
import importlib.util, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'ai-core/evaluation/public_qc_benchmark.py'
SUMMARY=ROOT/'ai-core/metrics/public-qc-summary-v1.0.json'

def test_missing_root_blocks_not_passes(tmp_path):
    out=tmp_path/'status.json'
    p=subprocess.run([
        sys.executable,
        str(RUN),
        '--vinmec-root', str(tmp_path/'missing-vinmec'),
        '--data-root', str(tmp_path/'missing-public'),
        '--status-json', str(out),
    ])
    assert p.returncode != 0
    data=json.loads(out.read_text())
    assert data['status']=='BLOCKED_WITH_EVIDENCE' and data['datasets_evaluated']==0

def test_vinmec_raw_payload_completes_without_supervised_metrics(tmp_path):
    root=tmp_path/'vinmec'
    root.mkdir()
    (root/'trial_emg.csv').write_text('type,name,time_units,begin_time,frequency,count,units\nanalog,EMG,s,0,1000,2,V\n0.1,0.2\n', encoding='utf-8')
    (root/'info.csv').write_text('type,last_name,first_name,born,sex,measurement_date,record_name\nmeta,,,,,,rec\n', encoding='utf-8')
    out=tmp_path/'status.json'
    p=subprocess.run([sys.executable,str(RUN),'--vinmec-root',str(root),'--status-json',str(out)])
    assert p.returncode == 0
    data=json.loads(out.read_text())
    assert data['status']=='DAY67_COMPLETED_WITH_SITE_RAW_EVIDENCE'
    assert data['datasets_evaluated'] == 1
    assert data['raw_payload_sha256'] and len(data['raw_payload_sha256']) == 64
    assert data['reason_code_distribution'] == {
        'QC_PARSEABLE_RAW_CSV': 1,
        'PHI_METADATA_EXCLUDED_FROM_QC': 1,
    }
    for k in ['accuracy','sensitivity','specificity','f1']:
        assert data[k] is None

def test_blocked_summary_has_no_fake_supervised_metrics():
    d=json.loads(SUMMARY.read_text())
    for k in ['accuracy','sensitivity','specificity','f1']:
        assert d[k] is None

def test_format_fixtures_never_count_as_public_benchmark():
    d=json.loads(SUMMARY.read_text())
    assert d['public_format_fixtures_count_as_public_benchmark'] is False

def test_day68_allowed_only_after_real_raw_payload():
    d=json.loads(SUMMARY.read_text())
    assert d['downstream_day68_allowed'] is True
    assert d['datasets_evaluated'] == 1

def test_protocol_hash_and_split_hash_are_carried():
    d=json.loads(SUMMARY.read_text())
    assert len(d['locked_protocol_hash'])==64 and len(d['split_manifest_sha256'])==64
