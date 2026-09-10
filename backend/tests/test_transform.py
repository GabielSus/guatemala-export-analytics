import pandas as pd

from app.infrastructure.etl.transform import transform_source


def test_transform_wide_to_long_and_validate_totals():
    source = pd.DataFrame(
        {
            "Numero de Inciso": ["TOTAL", "01011010", "0101210000"],
            "2024": ["3.000", "1.000", "2.000"],
            "2025 p/": ["4.500", "1.500", "3.000"],
        },
        dtype="string",
    )

    result = transform_source(source)

    assert len(result.data) == 4
    assert result.calculated_totals[2024] == 3000
    assert result.calculated_totals[2025] == 4500
    assert result.data["tariff_code"].nunique() == 2
    assert result.data[result.data["year"] == 2025]["is_provisional"].all()
