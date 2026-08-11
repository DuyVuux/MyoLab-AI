from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import jsonschema
import yaml


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("day33_semantics", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load DAY33 semantics")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.repo_root
    catalog_path = root / "data-platform/datasets/public-sEMG-catalog.v0.1.yaml"
    manifest_path = root / "qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml"
    schema_path = root / "packages/common-schemas/json/research-benchmark-corpus.v0.1.schema.json"
    corpus_root = root / "qa-validation/test-data/research/day33/corpus"
    semantics = load_module(root / "qa-validation/lib/day33_corpus_semantics.py")
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    semantics.validate_catalog(catalog)
    jsonschema.Draft202012Validator(schema).validate(manifest)
    semantics.validate_manifest(manifest, corpus_root)
    print(
        json.dumps(
            {
                "status": "PASS",
                "datasets": len(catalog["datasets"]),
                "public_sources": len(manifest["public_sources"]),
                "items": len(manifest["items"]),
                "locked_commitments": len(manifest["locked_truth_commitments"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
