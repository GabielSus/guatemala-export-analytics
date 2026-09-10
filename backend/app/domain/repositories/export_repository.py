from abc import ABC, abstractmethod

from app.domain.entities.export_summary import ExportSummary


class ExportRepository(ABC):
    @abstractmethod
    def get_summary(self) -> ExportSummary:
        raise NotImplementedError
