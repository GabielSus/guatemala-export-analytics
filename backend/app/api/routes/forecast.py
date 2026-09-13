from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas.forecast import ForecastResponse
from app.application.use_cases.forecast_exports import ForecastExports
from app.core.database import get_db
from app.infrastructure.forecasting.time_series_forecaster import (
    TimeSeriesForecaster,
)
from app.infrastructure.repositories.sqlalchemy_export_repository import (
    SQLAlchemyExportRepository,
)


router = APIRouter(prefix="/forecast", tags=["Forecasting"])


@router.get("", response_model=ForecastResponse)
def get_export_forecast(
    horizon: int = Query(default=3, ge=1, le=5),
    db: Session = Depends(get_db),
):
    use_case = ForecastExports(
        repository=SQLAlchemyExportRepository(db),
        forecaster=TimeSeriesForecaster(backtest_points=5),
    )

    try:
        result = use_case.execute(horizon=horizon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ForecastResponse.model_validate(result, from_attributes=True)
