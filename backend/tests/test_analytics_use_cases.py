from app.application.use_cases.analytics import AnalyticsUseCases
from app.domain.entities.analytics import (
    ChapterExport,
    TariffItemDetail,
    TariffItemHistoryPoint,
    TopTariffItem,
    YearlyExport,
)
from app.domain.entities.export_summary import ExportSummary
from app.domain.repositories.export_repository import ExportRepository


class FakeRepository(ExportRepository):
    def get_summary(self):
        return ExportSummary(
            first_year=2002,
            latest_year=2025,
            latest_year_total_usd=120,
            tariff_items=2,
            observations=6,
            latest_year_is_provisional=True,
        )

    def get_yearly_exports(self, start_year=None, end_year=None):
        rows = [
            YearlyExport(2023, 100, False),
            YearlyExport(2024, 110, False),
            YearlyExport(2025, 120, True),
        ]
        if start_year is not None:
            rows = [r for r in rows if r.year >= start_year]
        if end_year is not None:
            rows = [r for r in rows if r.year <= end_year]
        return rows

    def get_top_items(self, year, limit, chapter=None):
        return [TopTariffItem(1, "0901110000", "09", 10, 60, 50.0, year == 2025)]

    def get_chapters(self, year, limit=None):
        return [ChapterExport(1, "09", 60, 1, 50.0, year == 2025)]

    def get_item_detail(self, code, start_year=None, end_year=None):
        return TariffItemDetail(
            code=code,
            chapter=code[:2],
            digits=len(code),
            total_usd=330,
            first_active_year=2023,
            last_active_year=2025,
            history=[
                TariffItemHistoryPoint(2023, 100, False),
                TariffItemHistoryPoint(2024, 110, False),
                TariffItemHistoryPoint(2025, 120, True),
            ],
        )

    def get_available_years(self):
        return [2023, 2024, 2025]


def test_growth_calculation():
    result = AnalyticsUseCases(FakeRepository()).growth()
    assert result[0].growth_pct is None
    assert result[1].growth_pct == 10.0
    assert result[2].growth_pct == 9.09


def test_growth_keeps_previous_year_when_filtering():
    result = AnalyticsUseCases(FakeRepository()).growth(start_year=2024)
    assert result[0].year == 2024
    assert result[0].growth_pct == 10.0


def test_default_top_items_uses_latest_year():
    result = AnalyticsUseCases(FakeRepository()).top_items()
    assert result[0].is_provisional is True


def test_available_years():
    assert AnalyticsUseCases(FakeRepository()).years() == [2023, 2024, 2025]
