from app.core.config import settings
from app.infrastructure.etl.transform import read_source, transform_source


def main():
    source = read_source(settings.raw_csv_path)
    result = transform_source(source)
    data = result.data

    print("=" * 64)
    print("GUATEMALA EXPORT ANALYTICS - DATASET INSPECTION")
    print("=" * 64)
    print(f"Source rows (including TOTAL): {len(source):,}")
    print(f"Source columns: {len(source.columns):,}")
    print(f"Tariff items: {data['tariff_code'].nunique():,}")
    print(f"Transformed observations: {len(data):,}")
    print(f"Year range: {int(data['year'].min())} - {int(data['year'].max())}")
    print(f"Null values: {int(data.isna().sum().sum()):,}")
    print(f"Duplicate item-year pairs: {int(data.duplicated(['tariff_code', 'year']).sum()):,}")
    print()
    print("Tariff-code lengths:")
    print(
        data[["tariff_code", "digits"]]
        .drop_duplicates()["digits"]
        .value_counts()
        .sort_index()
        .to_string()
    )
    print()
    print("Totals validation: OK")
    print(
        f"Latest year total: ${result.calculated_totals[max(result.calculated_totals)]:,}"
    )
    print("=" * 64)


if __name__ == "__main__":
    main()
