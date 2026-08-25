from fastapi import APIRouter, HTTPException, Request
from .backend import AutoDataOperationsBackend
from .contracts import OperationsSummaryOut

router = APIRouter(prefix="/v1", tags=["auto-data-operations-ui"])

def _backend(request: Request) -> AutoDataOperationsBackend:
    backend = getattr(request.app.state, "auto_data_operations_backend", None)
    if backend is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "OPERATIONS_BACKEND_BINDING_NOT_CONFIGURED",
                "message": "Operational read model is not bound. No dashboard KPI was fabricated.",
                "retryable": False,
            },
        )
    return backend

@router.get("/operations/summary", response_model=OperationsSummaryOut)
def operations_summary(request: Request) -> OperationsSummaryOut:
    return _backend(request).get_operations_summary()
