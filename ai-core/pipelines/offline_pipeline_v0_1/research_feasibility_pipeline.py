#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd):
    print(f"Running: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}")
        sys.exit(1)
    return result.stdout


def main():
    current_dir = Path(__file__).resolve().parents[2]

    out_dir = current_dir / "data" / "research_feasibility_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    domain_shift_script = current_dir / "evaluation" / "domain_shift_analyzer.py"
    generalization_script = current_dir / "evaluation" / "generalization_reporter.py"
    ml_feasibility_script = current_dir / "pipelines" / "train_research_baseline.py"
    gate_script = current_dir / "governance" / "ml_feasibility_gate.py"

    upstream = current_dir / "data" / "upstream-evidence"
    feature_summary_csv = upstream / "feature_summary_dummy.csv"
    extract_script = current_dir / "evaluation" / "parquet_extractor_lite.py"
    parquet_path = upstream / "public-feature-summary-v1.1.parquet"

    if extract_script.exists():
        print("Extracting benchmark feature parquet...")
        feature_summary_csv = out_dir / "feature_summary.csv"
        run_cmd([
            "python3", str(extract_script),
            str(parquet_path), str(feature_summary_csv),
            "--expected-sha256", "4575223ace0b8ea6a24499666769b5dae3231e8b85c0505f7dc986062b5efee8",
        ])
    else:
        print("Warning: feature extraction script not found, assuming CSV exists.")

    print("\n--- Running Domain Shift Analysis ---")
    domain_shift_out = out_dir / "domain_shift"
    run_cmd(["python3", str(domain_shift_script), str(feature_summary_csv), "--out-dir", str(domain_shift_out)])
    domain_shift_matrix = domain_shift_out / "cross-dataset-domain-shift-v1.0.csv"

    print("\n--- Running Generalization Analysis ---")
    generalization_json = out_dir / "generalization_summary.json"
    run_cmd([
        "python3", str(generalization_script),
        "--public-acquisition-summary", str(upstream / "public-raw-acquisition-completion-summary.json"),
        "--site-metric-summary", str(upstream / "site-metric-execution-summary-v1.1.json"),
        "--domain-shift-matrix", str(domain_shift_matrix),
        "--out", str(generalization_json),
    ])

    print("\n--- Running ML Feasibility Decision ---")
    ml_feasibility_json = out_dir / "ml_feasibility_decision.json"
    run_cmd([
        "python3", str(ml_feasibility_script),
        "--generalization", str(generalization_json),
        "--out", str(ml_feasibility_json),
    ])

    print("\n--- Running Research Feasibility Gate ---")
    gate_evaluation_json = out_dir / "gate_evaluation.json"
    run_cmd([
        "python3", str(gate_script),
        "--selection", str(upstream / "public-benchmark-selection-v1.0.yaml"),
        "--protocol", str(upstream / "public-benchmark-protocol.v1.0.yaml"),
        "--split", str(upstream / "public-benchmark-splits-v1.0.csv"),
        "--public-acquisition-summary", str(upstream / "public-raw-acquisition-completion-summary.json"),
        "--site-feature-parquet", str(parquet_path),
        "--domain-shift-matrix", str(domain_shift_matrix),
        "--generalization-summary", str(generalization_json),
        "--ml-feasibility-decision", str(ml_feasibility_json),
        "--out", str(gate_evaluation_json),
    ])

    print("\nOrchestration Complete!")
    gate_status = json.loads(gate_evaluation_json.read_text())
    print(f"Final Gate Status: {gate_status.get('status')}")


if __name__ == "__main__":
    main()
