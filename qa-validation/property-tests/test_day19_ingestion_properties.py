from __future__ import annotations
import dataclasses
import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / 'services/signal-ingestion-service'
sys.path.insert(0, str(SERVICE))
from src.application import ingest_session as ing
FIX = ROOT / 'qa-validation/test-data/synthetic/day19/single/source.csv'

class TypedFailure(ValueError):

    def __init__(self, code):
        super().__init__(code)
        self.code = code

def clock():
    return datetime(2026, 8, 10, tzinfo=timezone.utc)

def req(path=FIX):
    return ing.IngestionRequest(
        'session_nonphi',
        'case_nonphi',
        'corr',
        ing.InputKind.MR4_SINGLE,
        str(path),
    )

def build(parser):
    sink = ing.CollectingEventSink()
    store = ing.InMemoryIdempotencyStore()
    bindings = ing.ParserBindings(parser, lambda p: None, lambda p: None)
    return (
        ing.IngestionFacade(
            bindings=bindings,
            event_sink=sink,
            idempotency_store=store,
            clock=clock,
        ),
        sink,
    )

def test_property_raw_not_mutated_by_well_behaved_parser():
    before = FIX.read_bytes()
    f, _ = build(lambda p: {'ok': True})
    f.ingest(req())
    assert FIX.read_bytes() == before

def test_property_mutation_can_never_return_success(tmp_path):
    p = tmp_path / 'x'
    p.write_bytes(b'a')

    def bad(path):
        path.write_bytes(b'b')
        return {'ok': True}
    f, _ = build(bad)
    result = f.ingest(req(p))
    assert result.status == 'FAILED' and result.payload is None

def test_property_unknown_unit_reason_is_never_rewritten():

    def bad(_):
        raise TypedFailure('UNIT_MISMATCH')
    f, _ = build(bad)
    result = f.ingest(req())
    assert result.reason_code == 'UNIT_MISMATCH'

def test_property_parser_crash_never_escapes_as_success():

    def bad(_):
        raise RuntimeError('boom')
    f, _ = build(bad)
    result = f.ingest(req())
    assert result.status == 'FAILED' and (not result.final_looking)

def test_property_validation_failure_is_fail_closed():
    for code in ('COUNT_MISMATCH', 'TIMESTAMP_INVALID', 'SAMPLING_INTERVAL_MISMATCH'):

        def bad(_, c=code):
            raise TypedFailure(c)
        f, sink = build(bad)
        result = f.ingest(req())
        assert result.status == 'FAILED' and result.payload is None
        assert sink.events[-1].event_type == 'VALIDATION_FAILED'

def test_property_exact_retry_is_single_effect():
    calls = {'n': 0}

    def ok(_):
        calls['n'] += 1
        return {'rates': (100, 2000)}
    f, sink = build(ok)
    first = f.ingest(req())
    second = f.ingest(req())
    assert first.operation_id == second.operation_id and second.replayed
    assert calls['n'] == 1 and len(sink.events) == 2

def test_property_event_never_has_raw_payload_field():
    assert 'raw_payload' not in {f.name for f in dataclasses.fields(ing.IngestionEvent)}

def test_property_no_processed_looking_success():
    f, _ = build(lambda p: {'ok': True})
    r = f.ingest(req())
    assert r.stage == 'INGESTED' and r.processed is False and (r.final_looking is False)
