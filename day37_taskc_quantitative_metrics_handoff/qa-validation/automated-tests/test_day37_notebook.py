import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_notebook_valid_and_illustrative():
    path = ROOT / "notebooks" / "Day37_TaskC_Quantitative_Metrics_Scenarios.ipynb"
    nb = json.loads(path.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4
    text = "\n".join(
        "".join(cell.get("source", []))
        for cell in nb["cells"]
    )
    assert "synthetic scenarios" in text.lower()
    assert "implementation chính" in text.lower()
