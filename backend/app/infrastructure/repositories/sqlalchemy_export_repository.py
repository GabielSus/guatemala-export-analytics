from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.export_summary import ExportSummary
from app.domain.repositories.export_repository import ExportRepository
from app.infrastructure.database.models import ExportValueModel, TariffItemModel


class SQLAlchemyExportRepository(ExportRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> ExportSummary:
        year_stats = self.db.execute(
            select(
                func.min(ExportValueModel.year),
                func.max(ExportValueModel.year),
                func.count(ExportValueModel.id),
            )
        ).one()

        first_year, latest_year, observations = year_stats

        if latest_year is None:
            raise ValueError(
                "No export data loaded. Run the ETL before requesting analytics."
            )

        latest_total = self.db.scalar(
            select(func.sum(ExportValueModel.value_usd)).where(
                ExportValueModel.year == latest_year
            )
        ) or 0

        latest_is_provisional = bool(
            self.db.scalar(
                select(func.bool_or(ExportValueModel.is_provisional)).where(
                    ExportValueModel.year == latest_year
                )
            )
        )

        tariff_items = self.db.scalar(
            select(func.count(TariffItemModel.id))
        ) or 0

        return ExportSummary(
            first_year=int(first_year),
            latest_year=int(latest_year),
            latest_year_total_usd=int(latest_total),
            tariff_items=int(tariff_items),
            observations=int(observations),
            latest_year_is_provisional=latest_is_provisional,
        )
