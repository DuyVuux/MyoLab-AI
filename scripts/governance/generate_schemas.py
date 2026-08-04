import sys
import json
from pathlib import Path

# Add governance path to sys.path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "ai-core" / "governance"))

from day39.models import RunManifest, RerunResult

def main():
    schema_dir = root / "packages" / "common-schemas" / "json" / "day39"
    schema_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate RunManifest Schema
    run_manifest_schema = RunManifest.model_json_schema()
    (schema_dir / "run-manifest.schema.json").write_text(
        json.dumps(run_manifest_schema, indent=2), encoding="utf-8"
    )
    
    # Generate RerunResult Schema
    rerun_result_schema = RerunResult.model_json_schema()
    (schema_dir / "rerun-result.schema.json").write_text(
        json.dumps(rerun_result_schema, indent=2), encoding="utf-8"
    )
    
    print("Schemas generated successfully.")

if __name__ == "__main__":
    main()
