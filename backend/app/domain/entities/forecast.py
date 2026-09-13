from dataclasses import dataclass


@dataclass(frozen=True)
class ForecastModelMetric:
    model: str
    mae: float
    rmse: float


@dataclass(frozen=True)
class ForecastPoint:
    year: int
    predicted_usd: int
    lower_usd: int
    upper_usd: int


@dataclass(frozen=True)
class ForecastResult:
    selected_model: str
    horizon: int
    training_start_year: int
    training_end_year: int
    training_observations: int
    uses_provisional_data: bool
    backtest_points: int
    mae: float
    rmse: float
    interval_method: str
    candidate_models: list[ForecastModelMetric]
    forecast: list[ForecastPoint]
