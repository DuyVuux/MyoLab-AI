import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "services/api-server/src"
sys.path.insert(0, str(SRC))

from ui_i4.backend import AutoDataOperationsBackend
from ui_i4.contracts import OperationsSummaryOut
from ui_i4.routes import operations_summary

class Fake(AutoDataOperationsBackend):
    def get_operations_summary(self):
        return OperationsSummaryOut(
            generated_at="2026-08-25T00:00:00Z",
            sessions_total=10,
            imports_running=1,
            qc_warning=2,
            blocked=1,
            awaiting_review=2,
            completed=6,
            unknown=0,
        )

def request(bound=True):
    state = SimpleNamespace()
    if bound:
        state.auto_data_operations_backend = Fake()
    return SimpleNamespace(app=SimpleNamespace(state=state))


def test_unbound_dashboard_fails_closed():
    with pytest.raises(HTTPException) as exc:
        operations_summary(request(False))
    assert exc.value.status_code == 503
    assert "OPERATIONS_BACKEND_BINDING_NOT_CONFIGURED" in str(exc.value.detail)


def test_bound_dashboard_returns_canonical_counts():
    d = operations_summary(request()).model_dump()
    assert d["source"] == "CANONICAL_READ_MODEL"
    assert d["sessions_total"] == 10
