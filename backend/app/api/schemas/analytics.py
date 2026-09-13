from pydantic import BaseModel


class ExportSummaryResponse(BaseModel):
    first_year: int
    latest_year: int
    latest_year_total_usd: int
    tariff_items: int
    observations: int
    latest_year_is_provisional: bool


class YearlyExportResponse(BaseModel):
    year: int
    total_usd: int
    is_provisional: bool


class GrowthPointResponse(BaseModel):
    year: int
    total_usd: int
    previous_year_total_usd: int | None
    growth_pct: float | None
    is_provisional: bool


class TopTariffItemResponse(BaseModel):
    rank: int
    code: str
    description: str | None
    chapter: str
    digits: int
    value_usd: int
    share_pct: float
    is_provisional: bool


class ChapterExportResponse(BaseModel):
    rank: int
    chapter: str
    description: str | None
    total_usd: int
    item_count: int
    share_pct: float
    is_provisional: bool


class TariffItemHistoryPointResponse(BaseModel):
    year: int
    value_usd: int
    is_provisional: bool


class TariffItemDetailResponse(BaseModel):
    code: str
    description: str | None
    chapter: str
    chapter_description: str | None
    digits: int
    total_usd: int
    first_active_year: int | None
    last_active_year: int | None
    history: list[TariffItemHistoryPointResponse]


class YearsResponse(BaseModel):
    years: list[int]
