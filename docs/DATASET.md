# Dataset inspection — Banguat export file

Source file analyzed: `EXPO_CG4(X_CG) (2).csv`

Metadata contained in the file:

- Title: Exportaciones por Inciso Arancelario
- Scope: Comercio General
- Period: 2002–2025
- Unit: US dollars
- 2025 is marked `p/` in the source, therefore it is treated as provisional.

## Actual structure found

- Encoding: UTF-8 with BOM (`UTF-8-SIG`)
- Delimiter: semicolon (`;`)
- Metadata rows before the header: 5
- Source rows: 13,047
- Columns: 25
- Year columns: 24 (`2002` through `2025 p/`)
- Detail tariff codes: 13,046
- Duplicate tariff codes: 0
- Null tariff codes: 0
- Null year values: 0
- 8-digit codes: 6,950
- 10-digit codes: 6,096

The file uses periods as thousands separators. Example:

`4.162.053.620` -> `4162053620`

## Important modeling decision

The original source is in **wide format**:

| Numero de Inciso | 2002 | 2003 | ... | 2025 p/ |
|---|---:|---:|---:|---:|

For analytics/database work, the ETL converts it to **long format**:

| tariff_code | year | value_usd | is_provisional |
|---|---:|---:|---|
| 01011010 | 2002 | 0 | false |
| 01011010 | 2003 | 41445 | false |
| ... | ... | ... | ... |

Expected transformed observations:

`13,046 tariff codes × 24 years = 313,104 rows`

## Validation performed

The source includes a `TOTAL` row.

The ETL does **not** store that row as an export item. Instead, it recalculates totals from detail rows and verifies them against the source.

For every year from 2002 to 2025, the calculated totals matched the source exactly.

Example source total for 2025:

`15,592,574,551 USD`

## Tariff-code change visible in the data

- 2002–2016: non-zero observations are on 8-digit codes.
- 2017: both 8- and 10-digit codes appear.
- 2018 onward: data is overwhelmingly represented with 10-digit codes.
- 2025: all non-zero detail observations are on 10-digit codes.

This means code length must be preserved and should not be coerced to integer.

## Current limitation

This CSV contains tariff **codes** but does not contain human-readable product descriptions. The project can analyze codes and chapters immediately. A product/nomenclature catalog will be needed later if the dashboard should display official item descriptions.
