from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class TariffItemModel(Base):
    __tablename__ = "tariff_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    digits: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    chapter: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    exports: Mapped[list["ExportValueModel"]] = relationship(
        back_populates="tariff_item",
        cascade="all, delete-orphan",
    )


class ExportValueModel(Base):
    __tablename__ = "export_values"
    __table_args__ = (
        UniqueConstraint("tariff_item_id", "year", name="uq_export_item_year"),
        Index("ix_export_values_year_item", "year", "tariff_item_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tariff_item_id: Mapped[int] = mapped_column(
        ForeignKey("tariff_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    value_usd: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_provisional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    tariff_item: Mapped[TariffItemModel] = relationship(back_populates="exports")


class TariffCatalogModel(Base):
    __tablename__ = "tariff_catalog"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
