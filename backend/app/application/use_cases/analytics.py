from app.domain.entities.analytics import (
    ChapterExport,
    GrowthPoint,
    TariffItemDetail,
    TopTariffItem,
    YearlyExport,
)
from app.domain.entities.export_summary import ExportSummary
from app.domain.repositories.export_repository import ExportRepository


class AnalyticsUseCases:
    def __init__(self, repository: ExportRepository):
        self.repository = repository

    def summary(self) -> ExportSummary:
        return self.repository.get_summary()

    def yearly(
        self,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> list[YearlyExport]:
        return self.repository.get_yearly_exports(start_year, end_year)

    def growth(
        self,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> list[GrowthPoint]:
        query_start = start_year - 1 if start_year is not None else None
        yearly = self.repository.get_yearly_exports(query_start, end_year)

        result: list[GrowthPoint] = []
        previous: YearlyExport | None = None

        for point in yearly:
            growth_pct: float | None = None
            previous_total: int | None = None

            if previous is not None:
                previous_total = previous.total_usd
                if previous.total_usd != 0:
                    growth_pct = round(
                        ((point.total_usd - previous.total_usd) / previous.total_usd) * 100,
                        2,
                    )

            if start_year is None or point.year >= start_year:
                result.append(
                    GrowthPoint(
                        year=point.year,
                        total_usd=point.total_usd,
                        previous_year_total_usd=previous_total,
                        growth_pct=growth_pct,
                        is_provisional=point.is_provisional,
                    )
                )

            previous = point

        return result

    def top_items(
        self,
        year: int | None = None,
        limit: int = 10,
        chapter: str | None = None,
    ) -> list[TopTariffItem]:
        resolved_year = year or self.summary().latest_year
        return self.repository.get_top_items(resolved_year, limit, chapter)

    def chapters(
        self,
        year: int | None = None,
        limit: int | None = None,
    ) -> list[ChapterExport]:
        resolved_year = year or self.summary().latest_year
        return self.repository.get_chapters(resolved_year, limit)

    def item_detail(
        self,
        code: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> TariffItemDetail:
        return self.repository.get_item_detail(code, start_year, end_year)

    def years(self) -> list[int]:
        return self.repository.get_available_years()
