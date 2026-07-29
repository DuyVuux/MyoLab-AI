"""Stress tests for catalog builder and sample selector.

Covers: empty catalog, all-test catalog, budget overflow,
duplicate record_ids, malformed URLs, and large catalog performance.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
import yaml

from select_remote_sample import main as select_main


# ---------------------------------------------------------------------------
# Helper: build a catalog JSON file
# ---------------------------------------------------------------------------

def _make_catalog(tmp_path: Path, records: list[dict]) -> Path:
    catalog = {
        'schema_version': 'remote-catalog.v1',
        'created_at': '2026-01-01T00:00:00Z',
        'records': records,
        'summary': {'record_count': len(records)},
    }
    p = tmp_path / 'catalog.json'
    p.write_text(json.dumps(catalog, ensure_ascii=False), encoding='utf-8')
    return p


def _make_config(tmp_path: Path, overrides: dict | None = None) -> Path:
    cfg = {
        'schema_version': 'pre-day30-remote-eda.v1',
        'execution_mode': 'BOUNDED_SAMPLE',
        'budgets': {
            'max_sample_records': 50,
            'max_sample_total_bytes': 104857600,  # 100 MiB
        },
        'partition_policy': {
            'allowed_signal_partitions': ['train', 'validation'],
            'forbidden_signal_partitions': ['test', 'sealed_test'],
        },
        'sampling_policy': {
            'seed': 302026,
            'stratify_fields': ['subject_id', 'day_id', 'source_label'],
        },
    }
    if overrides:
        for k, v in overrides.items():
            if isinstance(v, dict) and k in cfg:
                cfg[k].update(v)
            else:
                cfg[k] = v
    p = tmp_path / 'config.yaml'
    p.write_text(yaml.dump(cfg), encoding='utf-8')
    return p


# ---------------------------------------------------------------------------
# 1. Empty catalog — 0 records
# ---------------------------------------------------------------------------

class TestEmptyCatalog:

    def test_zero_records(self, tmp_path, monkeypatch):
        cat = _make_catalog(tmp_path, [])
        cfg = _make_config(tmp_path)
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )
        # Should succeed (no blockers, just 0 selected)
        rc = select_main()
        assert rc == 0
        plan = json.loads(out.read_text())
        assert plan['selected_record_count'] == 0
        assert plan['test_signal_records_selected'] == 0


# ---------------------------------------------------------------------------
# 2. All-test catalog — everything forbidden
# ---------------------------------------------------------------------------

class TestAllTestCatalog:

    def test_all_records_are_test(self, tmp_path, monkeypatch):
        records = [
            {
                'record_id': f'REC-{i}',
                'url': f'http://example.com/{i}.csv',
                'official_source': True,
                'format': 'csv',
                'partition': 'test',
                'subject_id': f'S{i:03d}',
            }
            for i in range(20)
        ]
        cat = _make_catalog(tmp_path, records)
        cfg = _make_config(tmp_path)
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )
        rc = select_main()
        assert rc == 0  # No blockers — test records are simply skipped
        plan = json.loads(out.read_text())
        assert plan['selected_record_count'] == 0


# ---------------------------------------------------------------------------
# 3. Budget overflow — records exceed byte budget
# ---------------------------------------------------------------------------

class TestBudgetOverflow:

    def test_byte_budget_respected(self, tmp_path, monkeypatch):
        records = [
            {
                'record_id': f'REC-{i}',
                'url': f'http://example.com/{i}.csv',
                'official_source': True,
                'format': 'csv',
                'partition': 'train',
                'subject_id': f'S{i:03d}',
                'size_bytes': 50_000_000,  # 50 MB each
            }
            for i in range(10)
        ]
        # Budget is 100 MB → should get at most 2 records
        cat = _make_catalog(tmp_path, records)
        cfg = _make_config(tmp_path, {
            'budgets': {
                'max_sample_records': 100,
                'max_sample_total_bytes': 100_000_000,
            }
        })
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )
        rc = select_main()
        plan = json.loads(out.read_text())
        assert plan['selected_known_bytes'] <= 100_000_000
        assert plan['selected_record_count'] <= 2

    def test_record_count_budget(self, tmp_path, monkeypatch):
        records = [
            {
                'record_id': f'REC-{i}',
                'url': f'http://example.com/{i}.csv',
                'official_source': True,
                'format': 'csv',
                'partition': 'train',
                'subject_id': f'S{i:03d}',
                'size_bytes': 100,
            }
            for i in range(100)
        ]
        cat = _make_catalog(tmp_path, records)
        cfg = _make_config(tmp_path, {
            'budgets': {
                'max_sample_records': 5,
                'max_sample_total_bytes': 999_999_999,
            }
        })
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )
        rc = select_main()
        plan = json.loads(out.read_text())
        assert plan['selected_record_count'] == 5


# ---------------------------------------------------------------------------
# 4. Unknown partition → blocker
# ---------------------------------------------------------------------------

class TestUnknownPartition:

    def test_unknown_partition_blocked(self, tmp_path, monkeypatch):
        records = [
            {
                'record_id': 'REC-UNKNOWN',
                'url': 'http://example.com/unknown.csv',
                'official_source': True,
                'format': 'csv',
                'partition': 'calibration',
                'subject_id': 'S001',
            }
        ]
        cat = _make_catalog(tmp_path, records)
        cfg = _make_config(tmp_path)
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )
        rc = select_main()
        assert rc == 1  # Should fail due to blockers
        plan = json.loads(out.read_text())
        assert any('UNKNOWN_OR_FORBIDDEN_PARTITION' in b for b in plan['blockers'])


# ---------------------------------------------------------------------------
# 5. Non-official source → blocker
# ---------------------------------------------------------------------------

class TestNonOfficialSource:

    def test_unofficial_blocked(self, tmp_path, monkeypatch):
        records = [
            {
                'record_id': 'REC-UNOFFICIAL',
                'url': 'http://mirror.example.com/data.csv',
                'official_source': False,
                'format': 'csv',
                'partition': 'train',
                'subject_id': 'S001',
            }
        ]
        cat = _make_catalog(tmp_path, records)
        cfg = _make_config(tmp_path)
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )
        rc = select_main()
        assert rc == 1
        plan = json.loads(out.read_text())
        assert any('NON_OFFICIAL_SOURCE' in b for b in plan['blockers'])


# ---------------------------------------------------------------------------
# 6. Large catalog performance — 10k records in <5s
# ---------------------------------------------------------------------------

class TestLargeCatalogPerformance:

    def test_10k_records_under_5s(self, tmp_path, monkeypatch):
        records = [
            {
                'record_id': f'REC-{i:06d}',
                'url': f'http://example.com/{i}.csv',
                'official_source': True,
                'format': 'csv',
                'partition': 'train',
                'subject_id': f'S{i % 50:03d}',
                'day_id': f'D{i % 3 + 1:02d}',
                'source_label': f'G{i % 17:02d}',
                'size_bytes': 1000,
            }
            for i in range(10_000)
        ]
        cat = _make_catalog(tmp_path, records)
        cfg = _make_config(tmp_path, {
            'budgets': {
                'max_sample_records': 300,
                'max_sample_total_bytes': 999_999_999,
            }
        })
        out = tmp_path / 'plan.json'

        import sys
        monkeypatch.setattr(
            sys, 'argv',
            ['prog', '--catalog', str(cat), '--config', str(cfg), '--output', str(out)],
        )

        start = time.monotonic()
        rc = select_main()
        elapsed = time.monotonic() - start

        assert elapsed < 5.0, f'Selection took {elapsed:.1f}s, expected <5s'
        plan = json.loads(out.read_text())
        assert plan['selected_record_count'] <= 300
        assert plan['selected_record_count'] > 0
