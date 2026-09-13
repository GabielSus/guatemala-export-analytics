from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.infrastructure.database.models import (
    ExportValueModel,
    TariffCatalogModel,
    TariffItemModel,
)
from app.infrastructure.etl.load_exports import main as load_exports
from app.infrastructure.etl.load_tariff_catalog import main as load_catalog


EXPECTED_TARIFF_ITEMS = 13_046
EXPECTED_EXPORT_VALUES = 313_104
MINIMUM_CATALOG_ROWS = 17_000


def counts() -> tuple[int, int, int]:
    with SessionLocal() as db:
        tariff_items = int(
            db.scalar(select(func.count(TariffItemModel.id))) or 0
        )
        export_values = int(
            db.scalar(select(func.count(ExportValueModel.id))) or 0
        )
        catalog_rows = int(
            db.scalar(select(func.count(TariffCatalogModel.code))) or 0
        )

    return tariff_items, export_values, catalog_rows


def main():
    tariff_items, export_values, catalog_rows = counts()

    print("=" * 68)
    print("PRODUCTION DATA BOOTSTRAP")
    print("=" * 68)
    print(f"tariff_items:  {tariff_items:,}")
    print(f"export_values: {export_values:,}")
    print(f"catalog_rows:  {catalog_rows:,}")
    print()

    if (
        tariff_items < EXPECTED_TARIFF_ITEMS
        or export_values < EXPECTED_EXPORT_VALUES
    ):
        print("Export dataset is missing/incomplete. Running ETL...")
        load_exports()
    else:
        print("Export dataset already loaded. Skipping main ETL.")

    _, _, catalog_rows = counts()

    if catalog_rows < MINIMUM_CATALOG_ROWS:
        print("SAC catalog is missing/incomplete. Loading catalog...")
        load_catalog()
    else:
        print("SAC catalog already loaded. Skipping catalog load.")

    tariff_items, export_values, catalog_rows = counts()

    print()
    print("Final production counts:")
    print(f"tariff_items:  {tariff_items:,}")
    print(f"export_values: {export_values:,}")
    print(f"catalog_rows:  {catalog_rows:,}")

    if tariff_items < EXPECTED_TARIFF_ITEMS:
        raise RuntimeError("Production tariff_items count is incomplete.")

    if export_values < EXPECTED_EXPORT_VALUES:
        raise RuntimeError("Production export_values count is incomplete.")

    if catalog_rows < MINIMUM_CATALOG_ROWS:
        raise RuntimeError("Production SAC catalog count is incomplete.")

    print("=" * 68)
    print("PRODUCTION DATA BOOTSTRAP OK")
    print("=" * 68)


if __name__ == "__main__":
    main()
