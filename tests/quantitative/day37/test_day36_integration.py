import json
import subprocess
from pathlib import Path


def test_day36_integration_gate_blocks_if_fatigue_allowed(tmp_path):
    input_gate = tmp_path / "day37-input-gate.json"
    input_gate.write_text(json.dumps({
        "day36_status_accepted": True,
        "hard_fatigue_diagnosis_allowed": True # This should trigger a block
    }))
    
    synthetic = tmp_path / "synthetic.json"
    synthetic.write_text("{}")
    
    integration = tmp_path / "integration.json"
    integration.write_text("{}")
    
    out = tmp_path / "out.json"
    
    script = Path("ai-core/pipelines/day37_finalize.py")
    
    res = subprocess.run(
        ["python", str(script), "--input-gate", str(input_gate), "--synthetic-evidence", str(synthetic), "--integration-report", str(integration), "--output", str(out)],
        capture_output=True, text=True
    )
    
    assert res.returncode == 0
    data = json.loads(out.read_text())
    assert data["status"] == "BLOCKED_WITH_EVIDENCE"

def test_day36_integration_gate_passes_if_valid(tmp_path):
    input_gate = tmp_path / "day37-input-gate.json"
    input_gate.write_text(json.dumps({
        "day36_status_accepted": True,
        "hard_fatigue_diagnosis_allowed": False
    }))
    
    synthetic = tmp_path / "synthetic.json"
    synthetic.write_text("{}")
    
    integration = tmp_path / "integration.json"
    integration.write_text("{}")
    
    out = tmp_path / "out.json"
    
    script = Path("ai-core/pipelines/day37_finalize.py")
    
    res = subprocess.run(
        ["python", str(script), "--input-gate", str(input_gate), "--synthetic-evidence", str(synthetic), "--integration-report", str(integration), "--output", str(out)],
        capture_output=True, text=True
    )
    
    assert res.returncode == 0
    data = json.loads(out.read_text())
    assert data["status"] == "GO_FOR_DAY38_TASK_C_VALIDATION"
