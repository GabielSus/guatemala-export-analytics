from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

import numpy as np
from statsmodels.tsa.holtwinters import Holt

from app.domain.entities.analytics import YearlyExport
from app.domain.entities.forecast import (
    ForecastModelMetric,
    ForecastPoint,
    ForecastResult,
)


@dataclass(frozen=True)
class _ModelSpec:
    name: str
    forecast_fn: Callable[[np.ndarray, np.ndarray, int], np.ndarray]


def _naive_forecast(
    years: np.ndarray,
    values: np.ndarray,
    horizon: int,
) -> np.ndarray:
    return np.repeat(float(values[-1]), horizon)


def _linear_trend_forecast(
    years: np.ndarray,
    values: np.ndarray,
    horizon: int,
) -> np.ndarray:
    if len(values) < 2:
        return _naive_forecast(years, values, horizon)

    x = years.astype(float) - float(years[0])
    coefficients = np.polyfit(x, values.astype(float), deg=1)

    future_years = np.arange(
        years[-1] + 1,
        years[-1] + horizon + 1,
        dtype=float,
    )
    future_x = future_years - float(years[0])

    predictions = np.polyval(coefficients, future_x)
    return np.maximum(predictions, 0.0)


def _holt_damped_forecast(
    years: np.ndarray,
    values: np.ndarray,
    horizon: int,
) -> np.ndarray:
    # With a short annual series, a damped trend is intentionally preferred
    # over an unrestricted trend to reduce explosive long-horizon forecasts.
    fitted = Holt(
        values.astype(float),
        damped_trend=True,
        initialization_method="estimated",
    ).fit(optimized=True)

    predictions = np.asarray(fitted.forecast(horizon), dtype=float)
    return np.maximum(predictions, 0.0)


class TimeSeriesForecaster:
    """
    Small-data annual forecasting for the Banguat 2002–2025 series.

    Candidate models are evaluated using rolling one-step-ahead backtesting.
    The best MAE wins, then it is refit on the complete series.

    Intervals are an explicit approximation derived from backtest residuals.
    They are not presented as exact model confidence intervals.
    """

    def __init__(self, backtest_points: int = 5):
        self.backtest_points = backtest_points
        self.models = [
            _ModelSpec("naive_last_value", _naive_forecast),
            _ModelSpec("linear_trend", _linear_trend_forecast),
            _ModelSpec("holt_damped_trend", _holt_damped_forecast),
        ]

    def _safe_forecast(
        self,
        model: _ModelSpec,
        years: np.ndarray,
        values: np.ndarray,
        horizon: int,
    ) -> np.ndarray:
        try:
            result = model.forecast_fn(years, values, horizon)
            if len(result) != horizon:
                raise ValueError("Model returned an invalid horizon.")
            if not np.all(np.isfinite(result)):
                raise ValueError("Model returned non-finite values.")
            return np.maximum(np.asarray(result, dtype=float), 0.0)
        except Exception:
            # A candidate model should never take the whole API down.
            # Fallback is deterministic and remains part of the evaluation.
            return _naive_forecast(years, values, horizon)

    def _backtest(
        self,
        model: _ModelSpec,
        years: np.ndarray,
        values: np.ndarray,
        points: int,
    ) -> tuple[float, float, np.ndarray]:
        errors: list[float] = []

        start = len(values) - points
        for test_index in range(start, len(values)):
            train_years = years[:test_index]
            train_values = values[:test_index]

            prediction = float(
                self._safe_forecast(
                    model,
                    train_years,
                    train_values,
                    1,
                )[0]
            )
            actual = float(values[test_index])
            errors.append(actual - prediction)

        residuals = np.asarray(errors, dtype=float)
        mae = float(np.mean(np.abs(residuals)))
        rmse = float(np.sqrt(np.mean(np.square(residuals))))
        return mae, rmse, residuals

    def forecast(
        self,
        yearly_exports: list[YearlyExport],
        horizon: int,
    ) -> ForecastResult:
        ordered = sorted(yearly_exports, key=lambda row: row.year)

        years = np.asarray([row.year for row in ordered], dtype=int)
        values = np.asarray([row.total_usd for row in ordered], dtype=float)

        points = min(self.backtest_points, max(3, len(values) // 4))
        points = min(points, len(values) - 6)

        if points < 3:
            raise ValueError(
                "Not enough observations remain for reliable backtesting."
            )

        scored: list[
            tuple[_ModelSpec, float, float, np.ndarray]
        ] = []

        for model in self.models:
            mae, rmse, residuals = self._backtest(
                model,
                years,
                values,
                points,
            )
            scored.append((model, mae, rmse, residuals))

        # MAE is the primary selection criterion; RMSE breaks ties.
        scored.sort(key=lambda row: (row[1], row[2]))
        selected, selected_mae, selected_rmse, residuals = scored[0]

        predictions = self._safe_forecast(
            selected,
            years,
            values,
            horizon,
        )

        # Approximate uncertainty from rolling backtest errors.
        if len(residuals) > 1:
            residual_std = float(np.std(residuals, ddof=1))
        else:
            residual_std = float(selected_rmse)

        future: list[ForecastPoint] = []

        for offset, prediction in enumerate(predictions, start=1):
            uncertainty = 1.96 * residual_std * math.sqrt(offset)
            lower = max(0.0, float(prediction) - uncertainty)
            upper = max(lower, float(prediction) + uncertainty)

            future.append(
                ForecastPoint(
                    year=int(years[-1] + offset),
                    predicted_usd=int(round(float(prediction))),
                    lower_usd=int(round(lower)),
                    upper_usd=int(round(upper)),
                )
            )

        metrics = [
            ForecastModelMetric(
                model=model.name,
                mae=round(mae, 2),
                rmse=round(rmse, 2),
            )
            for model, mae, rmse, _ in sorted(
                scored,
                key=lambda row: next(
                    index
                    for index, spec in enumerate(self.models)
                    if spec.name == row[0].name
                ),
            )
        ]

        return ForecastResult(
            selected_model=selected.name,
            horizon=horizon,
            training_start_year=int(years[0]),
            training_end_year=int(years[-1]),
            training_observations=len(values),
            uses_provisional_data=bool(ordered[-1].is_provisional),
            backtest_points=points,
            mae=round(selected_mae, 2),
            rmse=round(selected_rmse, 2),
            interval_method="rolling_backtest_residual_approximation_95pct",
            candidate_models=metrics,
            forecast=future,
        )
