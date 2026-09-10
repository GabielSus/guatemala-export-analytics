from app.domain.entities.export_summary import ExportSummary
from app.domain.repositories.export_repository import ExportRepository


class GetExportSummary:
    def __init__(self, repository: ExportRepository):
        self.repository = repository

    def execute(self) -> ExportSummary:
        return self.repository.get_summary()
