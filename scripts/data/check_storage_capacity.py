from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _common import write_json


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-root', required=True)
    ap.add_argument('--catalog')
    ap.add_argument('--output')
    ap.add_argument('--acquisition-multiplier', type=float, default=2.5)
    args = ap.parse_args()

    root = Path(args.data_root)
    root.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(root)
    known_bytes = 0
    if args.catalog:
        data = json.loads(Path(args.catalog).read_text(encoding='utf-8'))
        known_bytes = sum(int(r.get('size_bytes') or 0) for r in data.get('records', []))
    estimate = int(known_bytes * args.acquisition_multiplier)
    result = {
        'schema_version': 'storage-capacity-check.v1',
        'data_root': str(root),
        'total_bytes': usage.total,
        'used_bytes': usage.used,
        'free_bytes': usage.free,
        'catalog_known_bytes': known_bytes,
        'controlled_acquisition_estimate_bytes': estimate,
        'enough_for_estimate': usage.free >= estimate if estimate else None,
        'note': 'Estimate only; remote-only modes need less at-rest space but still transfer signal bytes.',
    }
    if args.output:
        write_json(args.output, result)
    print(result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
