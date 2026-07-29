"""Build a remote object catalog by issuing HTTP HEAD requests.

Supports concurrent HEAD requests via thread pool, content_type validation,
and redirect chain tracking for audit transparency.
"""
from __future__ import annotations

import argparse
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from _common import write_json


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {'1', 'true', 'yes', 'y'}


def head_remote(url: str, timeout: int) -> dict:
    """Issue an HTTP HEAD (or local stat) and return metadata dict."""
    parsed = urlparse(url)
    if parsed.scheme in {'', 'file'}:
        p = Path(parsed.path if parsed.scheme == 'file' else url)
        return {
            'head_status': 'LOCAL_OK' if p.exists() else 'LOCAL_MISSING',
            'size_bytes_observed': p.stat().st_size if p.exists() else None,
            'etag': None,
            'last_modified': None,
            'accept_ranges': True,
            'content_type': 'application/octet-stream',
        }
    try:
        r = requests.head(
            url, allow_redirects=True, timeout=timeout,
            headers={'User-Agent': 'MyoLab-AI-Research-EDA/0.2'},
        )
        size = r.headers.get('Content-Length')
        content_type = r.headers.get('Content-Type', '')

        # Track redirect chain for audit
        redirect_chain = [
            {'url': resp.url, 'status': resp.status_code}
            for resp in r.history
        ] if r.history else []

        result = {
            'head_status': f'HTTP_{r.status_code}',
            'size_bytes_observed': (
                int(size) if size and size.isdigit() else None
            ),
            'etag': r.headers.get('ETag'),
            'last_modified': r.headers.get('Last-Modified'),
            'accept_ranges': (
                r.headers.get('Accept-Ranges', '').lower() == 'bytes'
            ),
            'content_type': content_type,
            'final_url': r.url,
        }

        # Content-type warnings
        warnings = []
        if redirect_chain:
            result['redirect_chain'] = redirect_chain
        if 'text/html' in content_type.lower():
            warnings.append(
                'CONTENT_TYPE_HTML_UNEXPECTED: server returned HTML, '
                'may be a login page or error page instead of signal data'
            )
        if warnings:
            result['warnings'] = warnings

        return result
    except requests.RequestException as exc:
        return {
            'head_status': 'HEAD_ERROR',
            'head_error': str(exc),
            'accept_ranges': None,
            'size_bytes_observed': None,
        }


def process_row(row: dict, timeout: int) -> dict:
    """Process a single CSV row: parse fields + HEAD request."""
    record = dict(row)
    record['official_source'] = parse_bool(
        row.get('official_source', 'false')
    )
    for key in ('size_bytes', 'sampling_rate_hz'):
        raw = row.get(key, '').strip()
        if key == 'sampling_rate_hz':
            record[key] = float(raw) if raw else None
        else:
            record[key] = int(raw) if raw else None
    record['channel_columns'] = [
        x for x in row.get('channel_columns', '').split('|') if x
    ]
    observed = head_remote(row['url'], timeout)
    record.update(observed)
    if record.get('size_bytes') is None:
        record['size_bytes'] = observed.get('size_bytes_observed')
    return record


def main() -> int:
    ap = argparse.ArgumentParser(
        description='Build remote object catalog with HEAD audit',
    )
    ap.add_argument('--input', required=True, help='CSV with remote objects')
    ap.add_argument('--output', required=True, help='Output catalog JSON')
    ap.add_argument('--timeout', type=int, default=20)
    ap.add_argument(
        '--concurrency', type=int, default=4,
        help='Max concurrent HEAD requests (default: 4)',
    )
    args = ap.parse_args()

    # Read all rows first
    rows = []
    with Path(args.input).open('r', encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            if not row.get('record_id') or not row.get('url'):
                continue
            rows.append(row)

    # Process with thread pool for concurrent HEAD requests
    records = [None] * len(rows)
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(process_row, row, args.timeout): idx
            for idx, row in enumerate(rows)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                records[idx] = future.result()
            except Exception as exc:
                records[idx] = {
                    'record_id': rows[idx].get('record_id', f'ROW_{idx}'),
                    'url': rows[idx].get('url', ''),
                    'head_status': 'PROCESS_ERROR',
                    'head_error': str(exc),
                }

    # Filter out None entries (shouldn't happen but defensive)
    records = [r for r in records if r is not None]

    # Build summary
    html_warnings = sum(
        1 for r in records
        if 'text/html' in str(r.get('content_type', '')).lower()
    )
    result = {
        'schema_version': 'remote-catalog.v1',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'concurrency': args.concurrency,
        'records': records,
        'summary': {
            'record_count': len(records),
            'known_total_bytes': sum(
                r.get('size_bytes') or 0 for r in records
            ),
            'official_record_count': sum(
                bool(r.get('official_source')) for r in records
            ),
            'range_capable_count': sum(
                r.get('accept_ranges') is True for r in records
            ),
            'head_error_count': sum(
                r.get('head_status') == 'HEAD_ERROR' for r in records
            ),
            'html_content_type_warnings': html_warnings,
        },
    }
    write_json(args.output, result)
    print(json.dumps(result['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
