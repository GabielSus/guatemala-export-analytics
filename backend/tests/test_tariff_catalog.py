from app.infrastructure.etl.load_tariff_catalog import (
    build_catalog,
    parse_catalog_lines,
)


def test_parse_catalog_and_build_display_names():
    lines = [
        "08 FRUTAS Y FRUTOS COMESTIBLES",
        "0803 BANANAS O PLATANOS, FRESCOS O SECOS",
        "0803901100 Frescas",
        "09 CAFE, TE, YERBA MATE Y ESPECIAS",
        "0901113000 Café oro",
    ]

    records = parse_catalog_lines(lines)
    rows = {row.code: row for row in build_catalog(records)}

    assert rows["0901113000"].display_name == "Café oro"
    assert "BANANAS O PLATANOS" in rows["0803901100"].display_name
    assert rows["08"].level == "chapter"


def test_parse_catalog_when_pdf_columns_become_separate_lines():
    lines = [
        "09",
        "CAFE, TE, YERBA MATE Y ESPECIAS",
        "0901113000",
        "Café oro",
    ]

    records = parse_catalog_lines(lines)

    assert records["09"] == "CAFE, TE, YERBA MATE Y ESPECIAS"
    assert records["0901113000"] == "Café oro"
