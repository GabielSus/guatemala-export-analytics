from app.domain.entities.analytics import YearlyExport
from app.infrastructure.forecasting.time_series_forecaster import (
    TimeSeriesForecaster,
)


def _series():
    values = [
        100, 108, 116, 125, 133, 142, 151, 160, 169, 178,
        188, 198, 208, 219, 230, 241, 253, 265, 278, 291,
        305, 319, 334, 350,
    ]

    return [
        YearlyExport(
            year=2002 + index,
            total_usd=value * 1_000_000,
            is_provisional=index == len(values) - 1,
        )
        for index, value in enumerate(values)
    ]


def test_forecast_returns_requested_horizon():
    result = TimeSeriesForecaster(backtest_points=5).forecast(
        _series(),
        horizon=3,
    )

    assert result.horizon == 3
    assert len(result.forecast) == 3
    assert result.forecast[0].year == 2026
    assert result.forecast[-1].year == 2028
    assert result.training_observations == 24
    assert result.uses_provisional_data is True


def test_forecast_intervals_are_ordered_and_non_negative():
    result = TimeSeriesForecaster(backtest_points=5).forecast(
        _series(),
        horizon=2,
    )

    for point in result.forecast:
        assert point.lower_usd >= 0
        assert point.lower_usd <= point.predicted_usd <= point.upper_usd


def test_all_candidate_models_are_scored():
    result = TimeSeriesForecaster(backtest_points=5).forecast(
        _series(),
        horizon=1,
    )

    names = {metric.model for metric in result.candidate_models}

    assert names == {
        "naive_last_value",
        "linear_trend",
        "holt_damped_trend",
    }
    assert result.selected_model in names
