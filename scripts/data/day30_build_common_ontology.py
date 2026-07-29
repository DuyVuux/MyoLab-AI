#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

import yaml
from day30.contracts import PROJECT_CLASS_ORDER
from day30.ontology import build_ontology_report, load_supported_canonical_labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mendeley-labels", required=True)
    parser.add_argument("--grabmyo-labels", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = build_ontology_report(
            load_supported_canonical_labels(args.mendeley_labels),
            load_supported_canonical_labels(args.grabmyo_labels),
            PROJECT_CLASS_ORDER,
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix.lower() in {".yaml", ".yml"}:
            output.write_text(
                yaml.safe_dump(result, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
        else:
            output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["intersection"] else 2
    except (OSError, ValueError, TypeError) as error:
        print(f"day30 ontology build failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
