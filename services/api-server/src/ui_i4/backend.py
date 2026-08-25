from abc import ABC, abstractmethod
from .contracts import OperationsSummaryOut

class AutoDataOperationsBackend(ABC):
    """Bind to canonical session/job/QC/review read models. No fatigue/clinical KPI."""
    @abstractmethod
    def get_operations_summary(self) -> OperationsSummaryOut:
        raise NotImplementedError
