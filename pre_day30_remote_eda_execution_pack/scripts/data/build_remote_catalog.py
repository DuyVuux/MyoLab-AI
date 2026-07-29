from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from _common import write_json


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {'1', 'true', 'yes', 'y'}


def head_remote(url: str, timeout: int) -> dict:
    parsed = urlparse(url)
    if parsed.scheme in {'', 'file'}:
        p = Path(parsed.path if parsed.scheme == 'file' else url)
        return {
            'head_status': 'LOCAL_OK' if p.exists() else 'LOCAL_MISSING',
            'size_bytes_observed': p.stat().st_size if p.exists() else None,
            'etag': None,
            'last_modified': None,
            'accept_ranges': True,
            'content_type': None,
        }
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout, headers={'User-Agent': 'MyoLab-AI-Research-EDA/0.1'})
        size = r.headers.get('Content-Length')
        return {
            'head_status': f'HTTP_{r.status_code}',
            'size_bytes_observed': int(size) if size and size.isdigit() else None,
            'etag': r.headers.get('ETag'),
            'last_modified': r.headers.get('Last-Modified'),
            'accept_ranges': r.headers.get('Accept-Ranges', '').lower() == 'bytes',
            'content_type': r.headers.get('Content-Type'),
            'final_url': r.url,
        }
    except requests.RequestException as exc:
        return {'head_status': 'HEAD_ERROR', 'head_error': str(exc), 'accept_ranges': None, 'size_bytes_observed': None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--timeout', type=int, default=20)
    args = ap.parse_args()

    records = []
    with Path(args.input).open('r', encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            if not row.get('record_id') or not row.get('url'):
                continue
            record = dict(row)
            record['official_source'] = parse_bool(row.get('official_source', 'false'))
            for key in ('size_bytes', 'sampling_rate_hz'):
                raw = row.get(key, '').strip()
                record[key] = float(raw) if raw and key == 'sampling_rate_hz' else (int(raw) if raw else None)
            record['channel_columns'] = [x for x in row.get('channel_columns', '').split('|') if x]
            observed = head_remote(row['url'], args.timeout)
            record.update(observed)
            if record.get('size_bytes') is None:
                record['size_bytes'] = observed.get('size_bytes_observed')
            records.append(record)

    result = {
        'schema_version': 'remote-catalog.v1',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'records': records,
        'summary': {
            'record_count': len(records),
            'known_total_bytes': sum(r.get('size_bytes') or 0 for r in records),
            'official_record_count': sum(bool(r.get('official_source')) for r in records),
            'range_capable_count': sum(r.get('accept_ranges') is True for r in records),
            'head_error_count': sum(r.get('head_status') == 'HEAD_ERROR' for r in records),
        },
    }
    write_json(args.output, result)
    print(result['summary'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
