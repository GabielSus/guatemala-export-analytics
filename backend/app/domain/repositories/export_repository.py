from abc import ABC, abstractmethod

from app.domain.entities.analytics import (
    ChapterExport,
    TariffItemDetail,
    TopTariffItem,
    YearlyExport,
)
from app.domain.entities.export_summary import ExportSummary


class ExportRepository(ABC):
    @abstractmethod
    def get_summary(self) -> ExportSummary:
        raise NotImplementedError

    @abstractmethod
    def get_yearly_exports(
        self,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> list[YearlyExport]:
        raise NotImplementedError

    @abstractmethod
    def get_top_items(
        self,
        year: int,
        limit: int,
        chapter: str | None = None,
    ) -> list[TopTariffItem]:
        raise NotImplementedError

    @abstractmethod
    def get_chapters(self, year: int, limit: int | None = None) -> list[ChapterExport]:
        raise NotImplementedError

    @abstractmethod
    def get_item_detail(
        self,
        code: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> TariffItemDetail:
        raise NotImplementedError

    @abstractmethod
    def get_available_years(self) -> list[int]:
        raise NotImplementedError
