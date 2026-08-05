#!/usr/bin/env python3
import argparse
import json
import logging
import sys
from pathlib import Path
import yaml

# Add pipelines to path so we can import offline_pipeline_v0_1
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "pipelines"))

from offline_pipeline_v0_1 import OfflinePipeline, GovernanceError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("offline_pipeline_cli")

def main():
    p = argparse.ArgumentParser(description="Offline Integrated Pipeline v0.1 CLI")
    p.add_argument("--input-manifest", required=True, help="Path to input manifest JSON")
    p.add_argument("--pipeline-config", required=True, help="Path to pipeline config YAML")
    p.add_argument("--model-bundle", required=True, help="Path to model bundle JSON")
    p.add_argument("--output-dir", required=True, help="Directory to save the reports")
    p.add_argument("--mode", choices=["synthetic", "normalized", "raw-index"], default="synthetic", help="Execution mode")
    a = p.parse_args()

    try:
        session = json.loads(Path(a.input_manifest).read_text())
        config = yaml.safe_load(Path(a.pipeline_config).read_text())
        bundle = json.loads(Path(a.model_bundle).read_text())
    except Exception as e:
        logger.error(f"Failed to read input files: {e}")
        sys.exit(1)

    try:
        pipeline = OfflinePipeline(config, bundle)
    except GovernanceError as ge:
        logger.error(f"Governance Check Failed: {ge}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        sys.exit(1)

    if a.mode != "synthetic":
        logger.error(f"Mode '{a.mode}' is not yet supported by v0.1 runner.")
        sys.exit(1)

    try:
        report = pipeline.run_synthetic(session)
    except Exception as e:
        logger.error(f"Pipeline execution crashed: {e}", exc_info=True)
        sys.exit(1)

    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    report_json_path = out / "report.json"
    report_md_path = out / "report.md"
    
    report_json_path.write_text(json.dumps(report, indent=2))
    
    # Generate a markdown report
    md_content = [
        "# Offline Pipeline Report",
        f"**Session ID:** `{report.get('session_id')}`",
        f"**Final Status:** `{report.get('status')}`",
        f"**Quality:** `{report.get('quality', {}).get('status')}`",
        f"**Inference Decision:** `{report.get('inference', {}).get('decision')}`",
        "---",
        "> **SAFETY WARNING:**",
        "> Not approved for patient use.",
        "> AI output is decision-support only.",
        "> No automated treatment recommendation.",
        "> Quality fail is not equivalent to no fatigue."
    ]
    report_md_path.write_text("\n".join(md_content))
    
    logger.info(f"Report generated at {out}")
    print(json.dumps(report, indent=2))
    
    if report.get("status") == "FAILED":
        sys.exit(1)

if __name__ == "__main__":
    main()
