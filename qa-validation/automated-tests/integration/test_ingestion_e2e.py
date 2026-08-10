from __future__ import annotations
import dataclasses
import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest
import yaml
ROOT = Path(__file__).resolve().parents[3]
SERVICE = ROOT / 'services/signal-ingestion-service'
sys.path.insert(0, str(SERVICE))
sys.path.insert(0, str(SERVICE / 'src/adapters'))
from src.application import ingest_session as ing
FIX = ROOT / 'qa-validation/test-data/synthetic/day19'
EVENT_CONTRACT = ROOT / 'data-platform/events/ingestion-event-emission-contract.v0.1.yaml'

@dataclasses.dataclass(frozen=True)
class FakePayload:
    name: str
    sampling_rates: tuple[float, ...] = ()

class TypedFailure(ValueError):

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code

def fixed_clock():
    return datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc)

def bindings(single=None, separated=None, vicon=None):
    return ing.ParserBindings(
        single_csv=single or (lambda p: FakePayload('single', (2000.0,))),
        separated_csv=separated
        or (lambda p: FakePayload('separated', (100.0, 2000.0))),
        vicon_stacked=vicon
        or (lambda p: FakePayload('vicon', (100.0, 2000.0))),
    )

def facade(*, parser_bindings=None):
    sink = ing.CollectingEventSink()
    store = ing.InMemoryIdempotencyStore()
    obj = ing.IngestionFacade(
        bindings=parser_bindings or bindings(),
        event_sink=sink,
        idempotency_store=store,
        clock=fixed_clock,
    )
    return (obj, sink, store)

def request(kind, path):
    return ing.IngestionRequest(
        session_id='session_nonphi_001',
        case_id='case_nonphi_001',
        correlation_id='corr_001',
        input_kind=kind,
        source_path=str(path),
    )

def test_01_target_module_exists():
    assert Path(ing.__file__).is_file()

def test_02_event_contract_loads():
    payload = yaml.safe_load(EVENT_CONTRACT.read_text())
    assert payload['contract_id'] == 'INGESTION_EVENT_EMISSION_V0_1'

@pytest.mark.parametrize(
    'kind,path',
    [
        (ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'),
        (ing.InputKind.MR4_SEPARATED, FIX / 'separated'),
        (ing.InputKind.VICON_STACKED, FIX / 'vicon/source.csv'),
    ],
)
def test_03_all_input_kinds_use_same_facade_contract(kind, path):
    f, sink, _ = facade()
    result = f.ingest(request(kind, path))
    assert result.status == 'SUCCEEDED'
    assert result.stage == 'INGESTED'
    assert result.processed is False
    assert result.final_looking is False
    assert [e.event_type for e in sink.events] == ['IMPORT_STARTED', 'IMPORT_SUCCEEDED']

def test_04_mixed_sampling_rates_are_preserved_not_normalized():
    f, _, _ = facade()
    result = f.ingest(request(ing.InputKind.MR4_SEPARATED, FIX / 'separated'))
    assert result.payload.sampling_rates == (100.0, 2000.0)

def test_05_deterministic_operation_id_for_same_request():
    f1, _, _ = facade()
    f2, _, _ = facade()
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    assert f1.ingest(r).operation_id == f2.ingest(r).operation_id

def test_06_exact_retry_is_idempotent_and_emits_no_duplicate_events():
    f, sink, _ = facade()
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    first = f.ingest(r)
    second = f.ingest(r)
    assert first.operation_id == second.operation_id
    assert second.replayed is True
    assert len(sink.events) == 2

def test_07_event_ids_are_deterministic():
    f1, s1, _ = facade()
    f2, s2, _ = facade()
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    f1.ingest(r)
    f2.ingest(r)
    assert [x.event_id for x in s1.events] == [x.event_id for x in s2.events]

def test_08_validation_failure_emits_validation_failed():

    def fail(_):
        raise TypedFailure('UNIT_MISMATCH')
    f, sink, _ = facade(parser_bindings=bindings(single=fail))
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert result.status == 'FAILED'
    assert result.reason_code == 'UNIT_MISMATCH'
    assert result.payload is None
    assert sink.events[-1].event_type == 'VALIDATION_FAILED'

def test_09_structural_failure_emits_import_failed():

    def fail(_):
        raise TypedFailure('INGEST_SCHEMA_ERROR')
    f, sink, _ = facade(parser_bindings=bindings(single=fail))
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert result.status == 'FAILED'
    assert sink.events[-1].event_type == 'IMPORT_FAILED'

def test_10_untyped_parser_crash_is_captured_fail_closed():

    def explode(_):
        raise RuntimeError('boom')
    f, sink, _ = facade(parser_bindings=bindings(single=explode))
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert result.status == 'FAILED'
    assert result.reason_code == 'UNEXPECTED_PARSER_FAILURE'
    assert result.ready_for_downstream is False
    assert sink.events[-1].event_type == 'IMPORT_FAILED'

def test_11_failure_never_looks_processed_or_final():

    def fail(_):
        raise TypedFailure('TIMESTAMP_INVALID')
    f, _, _ = facade(parser_bindings=bindings(single=fail))
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert (
        result.processed,
        result.final_looking,
        result.ready_for_downstream,
    ) == (False, False, False)

def test_12_success_is_ingested_not_processed():
    f, _, _ = facade()
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert result.stage == 'INGESTED'
    assert result.processed is False
    assert result.final_looking is False

def test_13_raw_source_not_mutated_by_facade():
    path = FIX / 'single/source.csv'
    before = path.read_bytes()
    f, _, _ = facade()
    f.ingest(request(ing.InputKind.MR4_SINGLE, path))
    assert path.read_bytes() == before

def test_14_mutating_parser_is_detected_even_if_parser_returns_success(tmp_path):
    path = tmp_path / 'x.csv'
    path.write_text('original\n')

    def mutate(p):
        p.write_text('mutated\n')
        return FakePayload('bad')
    f, sink, _ = facade(parser_bindings=bindings(single=mutate))
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, path))
    assert result.status == 'FAILED'
    assert result.reason_code == 'RAW_MUTATION_DETECTED'
    assert result.payload is None
    assert sink.events[-1].event_type == 'VALIDATION_FAILED'

def test_15_directory_fingerprint_covers_all_separated_files():
    f, _, _ = facade()
    result = f.ingest(request(ing.InputKind.MR4_SEPARATED, FIX / 'separated'))
    assert len(result.source_refs) == 2

def test_16_changing_one_source_file_changes_operation_identity(tmp_path):
    d = tmp_path / 'rec'
    d.mkdir()
    (d / 'a.csv').write_text('a\n')
    f1, _, _ = facade()
    r = request(ing.InputKind.MR4_SEPARATED, d)
    first = f1.ingest(r)
    (d / 'a.csv').write_text('b\n')
    f2, _, _ = facade()
    second = f2.ingest(r)
    assert first.operation_id != second.operation_id

def test_17_failed_exact_retry_is_idempotent():
    calls = {'n': 0}

    def fail(_):
        calls['n'] += 1
        raise TypedFailure('COUNT_MISMATCH')
    f, sink, _ = facade(parser_bindings=bindings(single=fail))
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    one = f.ingest(r)
    two = f.ingest(r)
    assert one.status == two.status == 'FAILED'
    assert two.replayed is True
    assert calls['n'] == 1
    assert len(sink.events) == 2

def test_18_event_contains_source_session_correlation_refs():
    f, sink, _ = facade()
    f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    event = sink.events[0]
    assert event.session_id == 'session_nonphi_001'
    assert event.case_id == 'case_nonphi_001'
    assert event.correlation_id == 'corr_001'
    assert event.source_refs[0].startswith('src_sha256_')

def test_19_event_object_has_no_raw_payload_or_source_path_field():
    fields = {x.name for x in dataclasses.fields(ing.IngestionEvent)}
    assert 'raw_payload' not in fields
    assert 'source_path' not in fields
    assert 'patient_name' not in fields
    assert 'mrn' not in fields

def test_20_event_contract_forbids_raw_payload_and_phi_fields():
    payload = yaml.safe_load(EVENT_CONTRACT.read_text())
    assert payload['privacy']['raw_payload'] == 'forbidden'
    assert payload['privacy']['patient_name'] == 'forbidden'
    assert payload['privacy']['mrn'] == 'forbidden'

def test_21_collecting_sink_rejects_duplicate_event_id():
    sink = ing.CollectingEventSink()
    event = ing.IngestionEvent(
        'evt_x',
        'IMPORT_STARTED',
        'op',
        'c',
        'corr',
        's',
        'MR4_SINGLE',
        (),
        'v',
        '2026-08-10T00:00:00+00:00',
        None,
        None,
    )
    sink.emit(event)
    with pytest.raises(RuntimeError):
        sink.emit(event)

def test_22_idempotency_store_rejects_conflicting_same_operation():
    store = ing.InMemoryIdempotencyStore()
    r1 = ing.IngestionResult(
        'op',
        'SUCCEEDED',
        'INGESTED',
        's',
        'c',
        'corr',
        'MR4_SINGLE',
        (),
        'v',
        None,
        FakePayload('a'),
        True,
        False,
        False,
    )
    r2 = dataclasses.replace(r1, status='FAILED')
    store.put('op', r1)
    with pytest.raises(RuntimeError):
        store.put('op', r2)

def test_23_input_kind_routes_correct_binding():
    seen = []

    def mk(name):

        def inner(_):
            seen.append(name)
            return FakePayload(name)
        return inner
    f, _, _ = facade(parser_bindings=ing.ParserBindings(mk('single'), mk('sep'), mk('vicon')))
    f.ingest(request(ing.InputKind.VICON_STACKED, FIX / 'vicon/source.csv'))
    assert seen == ['vicon']

def test_24_empty_identity_fields_rejected_before_parser():
    f, _, _ = facade()
    bad = dataclasses.replace(
        request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'),
        session_id='',
    )
    with pytest.raises(ValueError):
        f.ingest(bad)

def test_25_missing_source_fails_without_final_looking_success(tmp_path):

    def parser(p):
        raise FileNotFoundError(str(p))
    f, sink, _ = facade(parser_bindings=bindings(single=parser))
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, tmp_path / 'missing.csv'))
    assert result.status == 'FAILED'
    assert result.reason_code == 'SOURCE_NOT_FOUND'
    assert result.final_looking is False
    assert sink.events[-1].event_type == 'IMPORT_FAILED'

def test_26_no_resampling_interpolation_or_ml_in_facade_source():
    text = Path(ing.__file__).read_text().lower()
    forbidden = (
        'resample(',
        'interpolate(',
        'torch',
        'tensorflow',
        'sklearn',
        'predict(',
        'fit(',
    )
    for token in forbidden:
        assert token not in text

def test_27_event_contract_states_store_is_not_day19_implementation():
    payload = yaml.safe_load(EVENT_CONTRACT.read_text())
    assert payload['persistent_event_store_implemented'] is False
    assert payload['persistent_event_store_target_day'] == 53

def test_28_terminal_success_event_has_succeeded_outcome():
    f, sink, _ = facade()
    f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert sink.events[-1].outcome_status == 'SUCCEEDED'

def test_29_terminal_failure_event_has_failed_outcome():

    def fail(_):
        raise TypedFailure('COUNT_MISMATCH')
    f, sink, _ = facade(parser_bindings=bindings(single=fail))
    f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert sink.events[-1].outcome_status == 'FAILED'

def test_30_fixed_clock_makes_event_timestamps_reproducible_in_test():
    f1, s1, _ = facade()
    f2, s2, _ = facade()
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    f1.ingest(r)
    f2.ingest(r)
    assert [e.emitted_at_utc for e in s1.events] == [e.emitted_at_utc for e in s2.events]

def test_31_operation_identity_changes_with_config_version():
    f1, _, _ = facade()
    f2, _, _ = facade()
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    a = f1.ingest(r)
    b = f2.ingest(dataclasses.replace(r, config_version='day19.v0.2'))
    assert a.operation_id != b.operation_id

def test_32_operation_identity_changes_with_session_identity():
    f1, _, _ = facade()
    f2, _, _ = facade()
    r = request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv')
    a = f1.ingest(r)
    b = f2.ingest(dataclasses.replace(r, session_id='session_nonphi_002'))
    assert a.operation_id != b.operation_id

def test_33_facade_result_is_frozen():
    f, _, _ = facade()
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.status = 'FAILED'

def test_34_started_event_is_nonterminal():
    f, sink, _ = facade()
    f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert sink.events[0].event_type == 'IMPORT_STARTED'
    assert sink.events[0].outcome_status is None

def test_35_success_has_no_reason_code():
    f, _, _ = facade()
    result = f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert result.reason_code is None

def test_36_validation_reason_set_includes_day13_day17_failures():
    expected = {
        'COUNT_MISMATCH',
        'TIMESTAMP_INVALID',
        'UNIT_MISMATCH',
        'INFO_LAYOUT_NOT_VERIFIED',
    }
    assert expected <= ing.VALIDATION_REASON_CODES

def test_37_no_event_contains_parser_payload_value():
    secret = 'RAW_SIGNAL_SHOULD_NOT_APPEAR'
    f, sink, _ = facade(parser_bindings=bindings(single=lambda p: FakePayload(secret)))
    f.ingest(request(ing.InputKind.MR4_SINGLE, FIX / 'single/source.csv'))
    assert all((secret not in repr(event) for event in sink.events))

def test_38_facade_does_not_require_persistent_cloud_or_network():
    text = Path(ing.__file__).read_text().lower()
    assert 'requests' not in text and 'http' not in text and ('socket' not in text)

def test_39_vicon_day18_adapter_can_be_bound_when_present():
    from src.adapters.vicon import vicon_stacked_csv as vicon
    source = ROOT / 'qa-validation/test-data/golden/day18/vicon_minimal_stacked.csv'
    b = bindings(vicon=lambda p: vicon.parse_vicon_stacked_csv(source))
    f, _, _ = facade(parser_bindings=b)
    result = f.ingest(request(ing.InputKind.VICON_STACKED, FIX / 'vicon/source.csv'))
    assert result.status == 'SUCCEEDED'
    assert result.payload.section('Trajectories') is not None

def test_40_vicon_alignment_not_verified_remains_not_verified_through_facade():
    from src.adapters.vicon import vicon_stacked_csv as vicon
    source = ROOT / 'qa-validation/test-data/golden/day18/vicon_minimal_stacked.csv'
    b = bindings(vicon=lambda p: vicon.parse_vicon_stacked_csv(source))
    f, _, _ = facade(parser_bindings=b)
    result = f.ingest(request(ing.InputKind.VICON_STACKED, FIX / 'vicon/source.csv'))
    assert result.payload.alignment.sync_status == 'NOT_VERIFIED'
    assert result.payload.alignment.offset_seconds is None
