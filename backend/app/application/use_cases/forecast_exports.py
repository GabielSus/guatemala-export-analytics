from typing import Protocol

from app.domain.entities.forecast import ForecastResult
from app.domain.repositories.export_repository import ExportRepository


class ExportForecaster(Protocol):
    def forecast(self, yearly_exports, horizon: int) -> ForecastResult:
        ...


class ForecastExports:
    def __init__(
        self,
        repository: ExportRepository,
        forecaster: ExportForecaster,
    ):
        self.repository = repository
        self.forecaster = forecaster

    def execute(self, horizon: int = 3) -> ForecastResult:
        if horizon < 1 or horizon > 5:
            raise ValueError("Forecast horizon must be between 1 and 5 years.")

        yearly = self.repository.get_yearly_exports()

        if len(yearly) < 10:
            raise ValueError(
                "At least 10 annual observations are required for forecasting."
            )

        return self.forecaster.forecast(yearly, horizon)
