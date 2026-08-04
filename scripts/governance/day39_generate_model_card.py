#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add governance path to sys.path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "ai-core" / "governance"))

from day39.registry import load_and_validate_manifest

def generate_model_card(manifest_path: str, output_path: str):
    """
    Generates a Markdown Model Card based on the validated RunManifest.
    """
    try:
        manifest = load_and_validate_manifest(manifest_path)
    except Exception as e:
        print(f"Error validating manifest: {e}", file=sys.stderr)
        sys.exit(1)
        
    text = f"""# Model Card — {manifest.run_id}

## 1. Model Overview
- **Run ID**: `{manifest.run_id}`
- **Git Commit**: `{manifest.git_commit}`
- **Created At (UTC)**: `{manifest.created_at_utc}`
- **Pooled Training**: `{"Yes" if manifest.pooled_training else "No"}`

## 2. Version and Registry State
- **Registry State**: `{manifest.registry_state.value}`
- **Sealed Test Data Opened**: `{"Yes" if manifest.sealed_test_opened else "No"}`

## 3. Intended Use
Research decision-support engineering baseline.

## 4. Out-of-scope Use
Diagnosis, autonomous treatment, patient-facing clinical use.

## 5. Security & Safety (MANDATORY)
> [!WARNING]
> - **Not approved for patient use.**
> - **No automated treatment recommendation.**
> - **Quality fail is not equivalent to no fatigue.**
> - **Single operator cannot approve pilot candidate.**

## 6. Reproducibility Hashes
- **Environment Lock**: `{manifest.environment_lock_sha256}`
- **Data Manifest**: `{manifest.data_manifest_sha256}`
- **Split Manifest**: `{manifest.split_manifest_sha256}`
- **Feature Contract**: `{manifest.feature_contract_sha256}`
- **Model Config**: `{manifest.model_config_sha256}`

## 7. Human Review & Approval
> [!IMPORTANT]
> External review is **REQUIRED** before pilot consideration.
"""
    Path(output_path).write_text(text, encoding="utf-8")
    print(f"Model Card generated successfully at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a Model Card from a Day 39 RunManifest")
    parser.add_argument("--manifest", required=True, help="Path to the JSON Run Manifest")
    parser.add_argument("--output", required=True, help="Path to save the generated Markdown Model Card")
    args = parser.parse_args()
    
    generate_model_card(args.manifest, args.output)

if __name__ == "__main__":
    main()
