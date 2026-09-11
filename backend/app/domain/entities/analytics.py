from dataclasses import dataclass


@dataclass(frozen=True)
class YearlyExport:
    year: int
    total_usd: int
    is_provisional: bool


@dataclass(frozen=True)
class GrowthPoint:
    year: int
    total_usd: int
    previous_year_total_usd: int | None
    growth_pct: float | None
    is_provisional: bool


@dataclass(frozen=True)
class TopTariffItem:
    rank: int
    code: str
    chapter: str
    digits: int
    value_usd: int
    share_pct: float
    is_provisional: bool


@dataclass(frozen=True)
class ChapterExport:
    rank: int
    chapter: str
    total_usd: int
    item_count: int
    share_pct: float
    is_provisional: bool


@dataclass(frozen=True)
class TariffItemHistoryPoint:
    year: int
    value_usd: int
    is_provisional: bool


@dataclass(frozen=True)
class TariffItemDetail:
    code: str
    chapter: str
    digits: int
    total_usd: int
    first_active_year: int | None
    last_active_year: int | None
    history: list[TariffItemHistoryPoint]
