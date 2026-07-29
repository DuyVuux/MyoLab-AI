#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

import yaml
from day30.view_registry import build_view_registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        path = Path(args.ontology)
        if path.suffix.lower() in {".yaml", ".yml"}:
            ontology = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            ontology = json.loads(path.read_text(encoding="utf-8"))
        result = build_view_registry(ontology)
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
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"day30 view registry build failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
