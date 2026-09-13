from pydantic import BaseModel


class ForecastModelMetricResponse(BaseModel):
    model: str
    mae: float
    rmse: float


class ForecastPointResponse(BaseModel):
    year: int
    predicted_usd: int
    lower_usd: int
    upper_usd: int


class ForecastResponse(BaseModel):
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
    candidate_models: list[ForecastModelMetricResponse]
    forecast: list[ForecastPointResponse]
