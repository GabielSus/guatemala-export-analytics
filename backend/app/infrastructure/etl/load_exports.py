from itertools import islice

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.core.database import SessionLocal
from app.infrastructure.database.models import ExportValueModel, TariffItemModel
from app.infrastructure.etl.transform import read_source, transform_source


BATCH_SIZE = 5000


def chunks(items, size):
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


def load_tariff_items(db, transformed):
    item_rows = (
        transformed[["tariff_code", "digits", "chapter"]]
        .drop_duplicates()
        .rename(columns={"tariff_code": "code"})
        .to_dict(orient="records")
    )

    for batch in chunks(item_rows, BATCH_SIZE):
        statement = (
            pg_insert(TariffItemModel)
            .values(batch)
            .on_conflict_do_nothing(index_elements=["code"])
        )
        db.execute(statement)

    db.commit()


def load_export_values(db, transformed):
    code_to_id = dict(
        db.execute(
            select(TariffItemModel.code, TariffItemModel.id)
        ).all()
    )

    records = []
    for row in transformed.itertuples(index=False):
        records.append(
            {
                "tariff_item_id": code_to_id[row.tariff_code],
                "year": int(row.year),
                "value_usd": int(row.value_usd),
                "is_provisional": bool(row.is_provisional),
            }
        )

    for number, batch in enumerate(chunks(records, BATCH_SIZE), start=1):
        statement = pg_insert(ExportValueModel).values(batch)
        statement = statement.on_conflict_do_update(
            constraint="uq_export_item_year",
            set_={
                "value_usd": statement.excluded.value_usd,
                "is_provisional": statement.excluded.is_provisional,
            },
        )
        db.execute(statement)
        db.commit()
        print(f"Loaded batch {number}")


def main():
    print("Reading source CSV...")
    source = read_source(settings.raw_csv_path)

    print("Transforming and validating...")
    result = transform_source(source)
    transformed = result.data

    print(f"Validated {len(transformed):,} observations.")

    with SessionLocal() as db:
        print("Loading tariff items...")
        load_tariff_items(db, transformed)

        print("Loading export values...")
        load_export_values(db, transformed)

    print("ETL completed successfully.")


if __name__ == "__main__":
    main()
