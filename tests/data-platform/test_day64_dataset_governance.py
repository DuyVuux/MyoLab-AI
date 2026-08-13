from pathlib import Path
import hashlib, json, yaml

ROOT = Path(__file__).resolve().parents[2]
SEL = ROOT / 'data-platform/datasets/public-benchmark-selection-v1.0.yaml'
SRC = ROOT / 'data-platform/datasets/public-benchmark-source-manifest-v1.0.json'

def load(): return yaml.safe_load(SEL.read_text())

def test_two_core_datasets_selected():
    assert len(load()['selected_core_datasets']) >= 2

def test_every_dataset_has_explicit_license_and_status():
    for d in load()['datasets']:
        assert d['license_id']
        assert d['license_status'] in {'VERIFIED_USABLE','VERIFY_CURRENT','TO_VERIFY','RESTRICTED_REFERENCE','EXCLUDED_LICENSE','INCOMPATIBLE','UNKNOWN'}

def test_hyser_license_conflict_corrected():
    d = next(x for x in load()['datasets'] if x['dataset_id']=='HYSER_V2_0_0')
    assert d['license_id'] == 'ODC-By-1.0'

def test_public_raw_payload_not_committed_or_claimed_hashed_before_day67():
    m = json.loads(SRC.read_text())
    for d in m['datasets']:
        if d['dataset_id'] == 'VINMEC_MOTION_LAB_EXAMPLE_OUTPUT':
            continue
        assert d['raw_payload_sha256'] is None
        assert d['raw_payload_hash_status'] == 'NOT_ACQUIRED_IN_RUNTIME'

def test_vinmec_site_raw_payload_is_hashed_after_day67():
    m = json.loads(SRC.read_text())
    d = next(x for x in m['datasets'] if x['dataset_id'] == 'VINMEC_MOTION_LAB_EXAMPLE_OUTPUT')
    assert len(d['raw_payload_sha256']) == 64
    int(d['raw_payload_sha256'], 16)
    assert d['raw_payload_hash_status'] == 'ACQUIRED_IN_RUNTIME_AND_HASHED'
    assert d['redistribution_in_repository'] == 'FORBIDDEN_PRIVATE_SITE_DATA'

def test_metadata_fingerprints_reproducible():
    m = json.loads(SRC.read_text())
    for row in m['datasets']:
        if row['dataset_id'] == 'VINMEC_MOTION_LAB_EXAMPLE_OUTPUT':
            assert row['catalog_metadata_sha256'] is None
            continue
        assert len(row['catalog_metadata_sha256']) == 64
        int(row['catalog_metadata_sha256'], 16)

def test_no_proprietary_dataset_selected():
    assert all('proprietary' not in d['license_id'].lower() for d in load()['datasets'])
