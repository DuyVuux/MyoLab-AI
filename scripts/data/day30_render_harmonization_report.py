#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        run = json.loads(Path(args.run_json).read_text(encoding="utf-8"))
        readiness = run["readiness"]
        ontology = run["ontology"]
        policy = run["policy_validation"]
        report = f"""# Báo cáo harmonization Day 30

## Trạng thái

`{readiness['status']}`

## Common class intersection

{', '.join(ontology['intersection'])}

## Quality gates

- input preflight: {str(run['preflight']['pass']).lower()}
- policy bundle: {str(policy['pass']).lower()}
- training: false
- pooled training: false
- sealed test opened: false
- fatigue inference: false
- MFCV: false

## Giới hạn

Đây là contract/representative-evidence run. Số dòng tín hiệu thật đã đọc: {run['real_data_signal_rows_read']}.
Full baseline tiếp tục bị chặn cho đến khi có full subject index hoặc sampling protocol đã khóa, split hashes, dependency lock và authorization Day 31.
"""
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(report)
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"day30 report rendering failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
