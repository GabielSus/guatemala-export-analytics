from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from pathlib import Path
import re
from statistics import median

import pymupdf
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import settings
from app.core.database import SessionLocal
from app.infrastructure.database.models import TariffCatalogModel


ALLOWED_CODE_LENGTHS = {2, 4, 6, 8, 9, 10}
CODE_ONLY = re.compile(r"^\d{2,10}$")
CODE_WITH_DESCRIPTION = re.compile(
    r"^(?P<code>\d{2,10})\s+(?P<description>.+)$"
)

IGNORED_PHRASES = {
    "BANCO DE GUATEMALA",
    "DEPARTAMENTO DE ESTADÍSTICAS MACROECONÓMICAS",
    "DEPARTAMENTO DE ESTADISTICAS MACROECONOMICAS",
    "SECCIÓN DE ESTADÍSTICAS DE BALANZA DE PAGOS",
    "SECCION DE ESTADISTICAS DE BALANZA DE PAGOS",
    "INCISOS ARANCELARIOS DESCRIPCIÓN",
    "INCISOS ARANCELARIOS DESCRIPCION",
    "LISTADO DE INCISOS ARANCELARIOS",
    "PROVISIONAL",
    "DESCRIPCIÓN",
    "DESCRIPCION",
    "INCISOS ARANCELARIOS",
}

GENERIC_DESCRIPTIONS = {
    "LOS DEMÁS",
    "LOS DEMAS",
    "LAS DEMÁS",
    "LAS DEMAS",
    "OTROS",
    "OTRAS",
    "FRESCAS",
    "FRESCOS",
    "SECAS",
    "SECOS",
    "LOS OTROS",
    "LAS OTRAS",
}

BATCH_SIZE = 2000


@dataclass(frozen=True)
class CatalogRow:
    code: str
    description: str
    display_name: str
    level: str


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\u00a0", " ").split()).strip()


def _valid_code(code: str) -> bool:
    return code.isdigit() and len(code) in ALLOWED_CODE_LENGTHS


def _level(code: str) -> str:
    mapping = {
        2: "chapter",
        4: "heading",
        6: "subheading",
        8: "item_8",
        9: "legacy_9",
        10: "item_10",
    }
    return mapping.get(len(code), "other")


def _is_noise(text: str) -> bool:
    clean = _clean_text(text)
    upper = clean.upper()

    if not clean:
        return True
    if upper in IGNORED_PHRASES:
        return True
    if re.fullmatch(r"\d{1,3}BANCO DE GUATEMALA", upper):
        return True
    if clean.isdigit() and len(clean) in {1, 3}:
        return True

    return False


def parse_catalog_lines(lines: list[str]) -> dict[str, str]:
    records: dict[str, str] = {}
    pending_code: str | None = None
    current_code: str | None = None

    for raw in lines:
        line = _clean_text(raw)
        if _is_noise(line):
            continue

        match = CODE_WITH_DESCRIPTION.match(line)
        if match and _valid_code(match.group("code")):
            code = match.group("code")
            description = _clean_text(match.group("description"))
            if description:
                records[code] = description
                current_code = code
                pending_code = None
            continue

        if CODE_ONLY.fullmatch(line) and _valid_code(line):
            pending_code = line
            current_code = None
            continue

        if pending_code:
            records[pending_code] = line
            current_code = pending_code
            pending_code = None
            continue

        if current_code and not CODE_ONLY.fullmatch(line):
            records[current_code] = _clean_text(
                f"{records[current_code]} {line}"
            )

    return records


def _cluster_words_into_rows(page) -> list[list[tuple]]:
    words = page.get_text("words", sort=True)
    if not words:
        return []

    words = sorted(words, key=lambda word: (round(word[1], 1), word[0]))
    rows: list[list[tuple]] = []
    tolerance = 2.5

    for word in words:
        if not rows:
            rows.append([word])
            continue

        current_y = median([item[1] for item in rows[-1]])
        if abs(word[1] - current_y) <= tolerance:
            rows[-1].append(word)
        else:
            rows.append([word])

    for row in rows:
        row.sort(key=lambda word: word[0])

    return rows


def _records_from_positioned_words(document) -> dict[str, str]:
    records: dict[str, str] = {}

    for page in document:
        page_width = float(page.rect.width)
        rows = _cluster_words_into_rows(page)
        current_code: str | None = None

        code_column_limit = page_width * 0.32
        description_column_start = page_width * 0.18

        for row in rows:
            if not row:
                continue

            row_text = _clean_text(" ".join(word[4] for word in row))
            if _is_noise(row_text):
                continue

            code_word = None
            for word in row:
                token = _clean_text(word[4])
                if (
                    word[0] <= code_column_limit
                    and CODE_ONLY.fullmatch(token)
                    and _valid_code(token)
                ):
                    code_word = word
                    break

            if code_word is not None:
                code = _clean_text(code_word[4])

                description_words = [
                    word[4]
                    for word in row
                    if word is not code_word and word[0] >= description_column_start
                ]
                description = _clean_text(" ".join(description_words))

                if description and not _is_noise(description):
                    records[code] = description
                    current_code = code
                else:
                    current_code = None
                continue

            first_x = min(word[0] for word in row)
            if (
                current_code
                and first_x >= description_column_start
                and not _is_noise(row_text)
            ):
                records[current_code] = _clean_text(
                    f"{records[current_code]} {row_text}"
                )

    return records


def _best_parent_description(code: str, records: dict[str, str]) -> str | None:
    for prefix_length in (6, 4, 2):
        if prefix_length >= len(code):
            continue
        parent = records.get(code[:prefix_length])
        if parent:
            return parent
    return None


def build_catalog(records: dict[str, str]) -> list[CatalogRow]:
    rows: list[CatalogRow] = []

    for code, description in records.items():
        if not _valid_code(code):
            continue

        clean_description = _clean_text(description)
        if not clean_description:
            continue

        display_name = clean_description
        upper = clean_description.upper()

        if len(code) in (8, 9, 10) and upper in GENERIC_DESCRIPTIONS:
            parent = _best_parent_description(code, records)
            if parent and parent.upper() != upper:
                display_name = f"{parent} — {clean_description}"

        rows.append(
            CatalogRow(
                code=code,
                description=clean_description,
                display_name=display_name,
                level=_level(code),
            )
        )

    return rows


def extract_catalog_from_pdf(pdf_path: str | Path) -> list[CatalogRow]:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(
            f"SAC PDF not found: {path}. "
            "Save the official Banguat catalog as data/raw/sac.pdf."
        )

    with path.open("rb") as file:
        signature = file.read(5)

    if not signature.startswith(b"%PDF"):
        raise ValueError(
            f"{path} is not a real PDF (signature={signature!r})."
        )

    with pymupdf.open(path) as document:
        page_count = len(document)
        records = _records_from_positioned_words(document)

        if len(records) < 1000:
            lines: list[str] = []
            for page in document:
                lines.extend(page.get_text("text", sort=True).splitlines())
            fallback_records = parse_catalog_lines(lines)
            if len(fallback_records) > len(records):
                records = fallback_records

    rows = build_catalog(records)

    if len(rows) < 1000:
        raise ValueError(
            f"Too few catalog entries parsed: {len(rows):,} "
            f"across {page_count} pages."
        )

    return rows


def _chunks(items: list[dict], size: int):
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


def _load_catalog_batches(rows: list[CatalogRow]) -> None:
    payload = [row.__dict__ for row in rows]

    with SessionLocal() as db:
        total_batches = (len(payload) + BATCH_SIZE - 1) // BATCH_SIZE

        for batch_number, batch in enumerate(
            _chunks(payload, BATCH_SIZE),
            start=1,
        ):
            statement = pg_insert(TariffCatalogModel).values(batch)
            statement = statement.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "description": statement.excluded.description,
                    "display_name": statement.excluded.display_name,
                    "level": statement.excluded.level,
                },
            )
            db.execute(statement)
            db.commit()

            print(
                f"Loaded catalog batch {batch_number}/{total_batches} "
                f"({len(batch):,} rows)"
            )


def main():
    print("Parsing official SAC PDF...")
    rows = extract_catalog_from_pdf(settings.sac_pdf_path)

    item_entries = sum(
        row.level in {"item_8", "legacy_9", "item_10"}
        for row in rows
    )
    chapters = sum(row.level == "chapter" for row in rows)

    print(f"Parsed catalog entries: {len(rows):,}")
    print(f"Chapter descriptions: {chapters:,}")
    print(f"8/9/10-digit item descriptions: {item_entries:,}")
    print()
    print(f"Loading catalog into PostgreSQL in batches of {BATCH_SIZE:,}...")

    _load_catalog_batches(rows)

    print()
    print("=" * 64)
    print("OFFICIAL SAC CATALOG LOADED")
    print("=" * 64)
    print(f"Total catalog entries: {len(rows):,}")
    print(f"Chapter descriptions: {chapters:,}")
    print(f"8/9/10-digit item descriptions: {item_entries:,}")
    print("=" * 64)


if __name__ == "__main__":
    main()
