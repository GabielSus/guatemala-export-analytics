from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.api.schemas.analytics import (
    ChapterExportResponse,
    ExportSummaryResponse,
    GrowthPointResponse,
    TariffItemDetailResponse,
    TariffItemHistoryPointResponse,
    TopTariffItemResponse,
    YearlyExportResponse,
    YearsResponse,
)
from app.application.use_cases.analytics import AnalyticsUseCases
from app.core.database import get_db
from app.infrastructure.repositories.sqlalchemy_export_repository import (
    SQLAlchemyExportRepository,
)


router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _use_cases(db: Session) -> AnalyticsUseCases:
    return AnalyticsUseCases(SQLAlchemyExportRepository(db))


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


@router.get("/summary", response_model=ExportSummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    try:
        result = _use_cases(db).summary()
        return ExportSummaryResponse(**result.__dict__)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/yearly", response_model=list[YearlyExportResponse])
def get_yearly_exports(
    start_year: int | None = Query(default=None, ge=1900, le=2100),
    end_year: int | None = Query(default=None, ge=1900, le=2100),
    db: Session = Depends(get_db),
):
    if start_year is not None and end_year is not None and start_year > end_year:
        raise HTTPException(status_code=422, detail="start_year cannot exceed end_year.")
    try:
        return [
            YearlyExportResponse(**row.__dict__)
            for row in _use_cases(db).yearly(start_year, end_year)
        ]
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/growth", response_model=list[GrowthPointResponse])
def get_growth(
    start_year: int | None = Query(default=None, ge=1900, le=2100),
    end_year: int | None = Query(default=None, ge=1900, le=2100),
    db: Session = Depends(get_db),
):
    if start_year is not None and end_year is not None and start_year > end_year:
        raise HTTPException(status_code=422, detail="start_year cannot exceed end_year.")
    try:
        return [
            GrowthPointResponse(**row.__dict__)
            for row in _use_cases(db).growth(start_year, end_year)
        ]
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/top-items", response_model=list[TopTariffItemResponse])
def get_top_items(
    year: int | None = Query(default=None, ge=1900, le=2100),
    limit: int = Query(default=10, ge=1, le=100),
    chapter: str | None = Query(default=None, pattern=r"^\d{1,2}$"),
    db: Session = Depends(get_db),
):
    try:
        return [
            TopTariffItemResponse(**row.__dict__)
            for row in _use_cases(db).top_items(year, limit, chapter)
        ]
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/chapters", response_model=list[ChapterExportResponse])
def get_chapters(
    year: int | None = Query(default=None, ge=1900, le=2100),
    limit: int | None = Query(default=15, ge=1, le=99),
    db: Session = Depends(get_db),
):
    try:
        return [
            ChapterExportResponse(**row.__dict__)
            for row in _use_cases(db).chapters(year, limit)
        ]
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/items/{code}", response_model=TariffItemDetailResponse)
def get_item_detail(
    code: str = Path(pattern=r"^(\d{8}|\d{10})$"),
    start_year: int | None = Query(default=None, ge=1900, le=2100),
    end_year: int | None = Query(default=None, ge=1900, le=2100),
    db: Session = Depends(get_db),
):
    if start_year is not None and end_year is not None and start_year > end_year:
        raise HTTPException(status_code=422, detail="start_year cannot exceed end_year.")
    try:
        result = _use_cases(db).item_detail(code, start_year, end_year)
        return TariffItemDetailResponse(
            code=result.code,
            chapter=result.chapter,
            digits=result.digits,
            total_usd=result.total_usd,
            first_active_year=result.first_active_year,
            last_active_year=result.last_active_year,
            history=[
                TariffItemHistoryPointResponse(**point.__dict__)
                for point in result.history
            ],
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.get("/years", response_model=YearsResponse)
def get_years(db: Session = Depends(get_db)):
    return YearsResponse(years=_use_cases(db).years())
