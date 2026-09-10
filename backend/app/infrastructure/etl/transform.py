from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd


SOURCE_HEADER_ROWS = 5
CODE_COLUMN = "Numero de Inciso"


@dataclass(frozen=True)
class TransformResult:
    data: pd.DataFrame
    source_totals: dict[int, int]
    calculated_totals: dict[int, int]


def _parse_usd(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    return pd.to_numeric(cleaned, errors="raise").astype("int64")


def _year_from_label(label: str) -> int:
    match = re.search(r"\d{4}", str(label))
    if not match:
        raise ValueError(f"Could not detect a year in column: {label}")
    return int(match.group())


def read_source(csv_path: str | Path) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(
        path,
        sep=";",
        skiprows=SOURCE_HEADER_ROWS,
        encoding="utf-8-sig",
        dtype="string",
    )

    for column in df.columns:
        df[column] = df[column].str.strip()

    return df


def transform_source(df: pd.DataFrame) -> TransformResult:
    if CODE_COLUMN not in df.columns:
        raise ValueError(f"Required column not found: {CODE_COLUMN}")

    year_columns = [column for column in df.columns if column != CODE_COLUMN]
    if not year_columns:
        raise ValueError("No year columns found.")

    total_rows = df[df[CODE_COLUMN].str.upper() == "TOTAL"]
    if len(total_rows) != 1:
        raise ValueError("Expected exactly one TOTAL row in source file.")

    detail = df[df[CODE_COLUMN].str.upper() != "TOTAL"].copy()

    if detail[CODE_COLUMN].isna().any():
        raise ValueError("Tariff codes contain null values.")

    if detail[CODE_COLUMN].duplicated().any():
        raise ValueError("Tariff codes contain duplicates.")

    valid_codes = detail[CODE_COLUMN].str.fullmatch(r"\d{8}|\d{10}", na=False)
    if not valid_codes.all():
        bad_codes = detail.loc[~valid_codes, CODE_COLUMN].head(10).tolist()
        raise ValueError(f"Invalid tariff codes detected: {bad_codes}")

    source_totals: dict[int, int] = {}
    total_row = total_rows.iloc[0]
    for column in year_columns:
        year = _year_from_label(column)
        source_totals[year] = int(_parse_usd(pd.Series([total_row[column]])).iloc[0])

    long_df = detail.melt(
        id_vars=[CODE_COLUMN],
        value_vars=year_columns,
        var_name="year_label",
        value_name="value_usd",
    )

    long_df["tariff_code"] = long_df[CODE_COLUMN].astype("string")
    long_df["year"] = long_df["year_label"].map(_year_from_label).astype("int16")
    long_df["value_usd"] = _parse_usd(long_df["value_usd"])
    long_df["is_provisional"] = (
        long_df["year_label"].astype("string").str.contains("p/", regex=False)
    )
    long_df["digits"] = long_df["tariff_code"].str.len().astype("int8")
    long_df["chapter"] = long_df["tariff_code"].str[:2]

    result = long_df[
        [
            "tariff_code",
            "digits",
            "chapter",
            "year",
            "value_usd",
            "is_provisional",
        ]
    ].sort_values(["year", "tariff_code"], ignore_index=True)

    calculated_totals = {
        int(year): int(value)
        for year, value in result.groupby("year")["value_usd"].sum().items()
    }

    if source_totals != calculated_totals:
        differences = {
            year: {
                "source": source_totals.get(year),
                "calculated": calculated_totals.get(year),
            }
            for year in sorted(set(source_totals) | set(calculated_totals))
            if source_totals.get(year) != calculated_totals.get(year)
        }
        raise ValueError(f"Source totals validation failed: {differences}")

    return TransformResult(
        data=result,
        source_totals=source_totals,
        calculated_totals=calculated_totals,
    )
