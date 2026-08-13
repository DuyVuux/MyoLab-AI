import json
import subprocess
import sys
from pathlib import Path


def test_task_c_integration_gate_blocks_if_fatigue_allowed(tmp_path):
    input_gate = tmp_path / "task-c-input-gate.json"
    input_gate.write_text(json.dumps({
        "task_c_prerequisite_status_accepted": True,
        "hard_fatigue_diagnosis_allowed": True # This should trigger a block
    }))
    
    synthetic = tmp_path / "synthetic.json"
    synthetic.write_text("{}")
    
    integration = tmp_path / "integration.json"
    integration.write_text("{}")
    
    out = tmp_path / "out.json"
    
    script = Path("ai-core/pipelines/finalize_task_c_validation.py")
    
    res = subprocess.run(
        [sys.executable, str(script), "--input-gate", str(input_gate), "--synthetic-evidence", str(synthetic), "--integration-report", str(integration), "--output", str(out)],
        capture_output=True, text=True
    )
    
    assert res.returncode == 0
    data = json.loads(out.read_text())
    assert data["status"] == "BLOCKED_WITH_EVIDENCE"

def test_task_c_integration_gate_passes_if_valid(tmp_path):
    input_gate = tmp_path / "task-c-input-gate.json"
    input_gate.write_text(json.dumps({
        "task_c_prerequisite_status_accepted": True,
        "hard_fatigue_diagnosis_allowed": False
    }))
    
    synthetic = tmp_path / "synthetic.json"
    synthetic.write_text("{}")
    
    integration = tmp_path / "integration.json"
    integration.write_text("{}")
    
    out = tmp_path / "out.json"
    
    script = Path("ai-core/pipelines/finalize_task_c_validation.py")
    
    res = subprocess.run(
        [sys.executable, str(script), "--input-gate", str(input_gate), "--synthetic-evidence", str(synthetic), "--integration-report", str(integration), "--output", str(out)],
        capture_output=True, text=True
    )
    
    assert res.returncode == 0
    data = json.loads(out.read_text())
    assert data["status"] == "GO_FOR_TASK_C_VALIDATION"
