from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.domain.entities.analytics import (
    ChapterExport,
    TariffItemDetail,
    TariffItemHistoryPoint,
    TopTariffItem,
    YearlyExport,
)
from app.domain.entities.export_summary import ExportSummary
from app.domain.repositories.export_repository import ExportRepository
from app.infrastructure.database.models import ExportValueModel, TariffItemModel


class SQLAlchemyExportRepository(ExportRepository):
    def __init__(self, db: Session):
        self.db = db

    def _ensure_year_exists(self, year: int) -> None:
        exists = self.db.scalar(
            select(func.count(ExportValueModel.id)).where(ExportValueModel.year == year)
        )
        if not exists:
            raise ValueError(f"No export data found for year {year}.")

    def _year_total(self, year: int) -> int:
        total = self.db.scalar(
            select(func.sum(ExportValueModel.value_usd)).where(
                ExportValueModel.year == year
            )
        )
        return int(total or 0)

    def get_summary(self) -> ExportSummary:
        first_year, latest_year, observations = self.db.execute(
            select(
                func.min(ExportValueModel.year),
                func.max(ExportValueModel.year),
                func.count(ExportValueModel.id),
            )
        ).one()

        if latest_year is None:
            raise ValueError(
                "No export data loaded. Run the ETL before requesting analytics."
            )

        latest_total = self._year_total(int(latest_year))
        latest_is_provisional = bool(
            self.db.scalar(
                select(func.bool_or(ExportValueModel.is_provisional)).where(
                    ExportValueModel.year == latest_year
                )
            )
        )
        tariff_items = int(
            self.db.scalar(select(func.count(TariffItemModel.id))) or 0
        )

        return ExportSummary(
            first_year=int(first_year),
            latest_year=int(latest_year),
            latest_year_total_usd=latest_total,
            tariff_items=tariff_items,
            observations=int(observations),
            latest_year_is_provisional=latest_is_provisional,
        )

    def get_yearly_exports(
        self,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> list[YearlyExport]:
        statement = select(
            ExportValueModel.year,
            func.sum(ExportValueModel.value_usd).label("total_usd"),
            func.bool_or(ExportValueModel.is_provisional).label("is_provisional"),
        )

        if start_year is not None:
            statement = statement.where(ExportValueModel.year >= start_year)
        if end_year is not None:
            statement = statement.where(ExportValueModel.year <= end_year)

        rows = self.db.execute(
            statement.group_by(ExportValueModel.year).order_by(ExportValueModel.year)
        ).all()

        if not rows:
            raise ValueError("No export data found for the requested period.")

        return [
            YearlyExport(
                year=int(row.year),
                total_usd=int(row.total_usd),
                is_provisional=bool(row.is_provisional),
            )
            for row in rows
        ]

    def get_top_items(
        self,
        year: int,
        limit: int,
        chapter: str | None = None,
    ) -> list[TopTariffItem]:
        self._ensure_year_exists(year)
        year_total = self._year_total(year)

        statement = (
            select(
                TariffItemModel.code,
                TariffItemModel.chapter,
                TariffItemModel.digits,
                ExportValueModel.value_usd,
                ExportValueModel.is_provisional,
            )
            .join(
                ExportValueModel,
                ExportValueModel.tariff_item_id == TariffItemModel.id,
            )
            .where(
                ExportValueModel.year == year,
                ExportValueModel.value_usd > 0,
            )
        )

        if chapter is not None:
            statement = statement.where(TariffItemModel.chapter == chapter.zfill(2))

        rows = self.db.execute(
            statement.order_by(ExportValueModel.value_usd.desc()).limit(limit)
        ).all()

        return [
            TopTariffItem(
                rank=index,
                code=row.code,
                chapter=row.chapter,
                digits=int(row.digits),
                value_usd=int(row.value_usd),
                share_pct=round((int(row.value_usd) / year_total) * 100, 4)
                if year_total
                else 0.0,
                is_provisional=bool(row.is_provisional),
            )
            for index, row in enumerate(rows, start=1)
        ]

    def get_chapters(self, year: int, limit: int | None = None) -> list[ChapterExport]:
        self._ensure_year_exists(year)
        year_total = self._year_total(year)

        statement = (
            select(
                TariffItemModel.chapter,
                func.sum(ExportValueModel.value_usd).label("total_usd"),
                func.count(ExportValueModel.tariff_item_id).label("item_count"),
                func.bool_or(ExportValueModel.is_provisional).label("is_provisional"),
            )
            .join(
                ExportValueModel,
                ExportValueModel.tariff_item_id == TariffItemModel.id,
            )
            .where(
                ExportValueModel.year == year,
                ExportValueModel.value_usd > 0,
            )
            .group_by(TariffItemModel.chapter)
            .order_by(func.sum(ExportValueModel.value_usd).desc())
        )

        if limit is not None:
            statement = statement.limit(limit)

        rows = self.db.execute(statement).all()

        return [
            ChapterExport(
                rank=index,
                chapter=row.chapter,
                total_usd=int(row.total_usd),
                item_count=int(row.item_count),
                share_pct=round((int(row.total_usd) / year_total) * 100, 2)
                if year_total
                else 0.0,
                is_provisional=bool(row.is_provisional),
            )
            for index, row in enumerate(rows, start=1)
        ]

    def get_item_detail(
        self,
        code: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> TariffItemDetail:
        item = self.db.scalar(
            select(TariffItemModel).where(TariffItemModel.code == code)
        )
        if item is None:
            raise ValueError(f"Tariff item {code} was not found.")

        statement = select(
            ExportValueModel.year,
            ExportValueModel.value_usd,
            ExportValueModel.is_provisional,
        ).where(ExportValueModel.tariff_item_id == item.id)

        if start_year is not None:
            statement = statement.where(ExportValueModel.year >= start_year)
        if end_year is not None:
            statement = statement.where(ExportValueModel.year <= end_year)

        rows = self.db.execute(statement.order_by(ExportValueModel.year)).all()
        if not rows:
            raise ValueError("No observations found for the requested item period.")

        history = [
            TariffItemHistoryPoint(
                year=int(row.year),
                value_usd=int(row.value_usd),
                is_provisional=bool(row.is_provisional),
            )
            for row in rows
        ]
        active_years = [point.year for point in history if point.value_usd > 0]

        return TariffItemDetail(
            code=item.code,
            chapter=item.chapter,
            digits=int(item.digits),
            total_usd=sum(point.value_usd for point in history),
            first_active_year=min(active_years) if active_years else None,
            last_active_year=max(active_years) if active_years else None,
            history=history,
        )

    def get_available_years(self) -> list[int]:
        rows = self.db.scalars(
            select(distinct(ExportValueModel.year)).order_by(ExportValueModel.year)
        ).all()
        return [int(year) for year in rows]
