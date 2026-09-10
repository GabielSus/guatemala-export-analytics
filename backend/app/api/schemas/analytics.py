from pydantic import BaseModel


class ExportSummaryResponse(BaseModel):
    first_year: int
    latest_year: int
    latest_year_total_usd: int
    tariff_items: int
    observations: int
    latest_year_is_provisional: bool
