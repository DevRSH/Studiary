"""SQLAlchemy models: Nota, Dibujo, Tag.

Sistema de notas con soporte para markdown y handwriting digital (Fabric.js).
"""

from enum import Enum as PyEnum
from sqlalchemy import ForeignKey, String, Integer, Text, Enum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import BaseModel, Base

if TYPE_CHECKING:
    from .tema import Tema


class TipoNota(str, PyEnum):
    """Tipo de contenido de la nota."""

    TEXTO = "texto"
    HANDWRITTEN = "handwritten"
    MIXTO = "mixto"


# Tabla intermedia para many-to-many
nota_tags = Table(
    "nota_tags",
    Base.metadata,
    Column("nota_id", Integer, ForeignKey("notas.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Nota(BaseModel):
    """Note model with markdown and handwriting support."""

    __tablename__ = "notas"

    tema_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("temas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    contenido_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[TipoNota] = mapped_column(
        Enum(TipoNota),
        default=TipoNota.TEXTO,
        nullable=False,
    )

    # Relationships
    tema: Mapped["Tema"] = relationship("Tema", back_populates="notas")
    dibujos: Mapped[list["Dibujo"]] = relationship(
        "Dibujo",
        back_populates="nota",
        cascade="all, delete-orphan",
        order_by="Dibujo.orden",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=nota_tags,
        back_populates="notas",
    )

    def __repr__(self) -> str:
        return f"<Nota id={self.id} titulo={self.titulo!r} tipo={self.tipo}>"


class Dibujo(BaseModel):
    """Canvas drawing stored as Fabric.js JSON."""

    __tablename__ = "dibujos"

    nota_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("notas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    canvas_json: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_base64: Mapped[str | None] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    nota: Mapped["Nota"] = relationship("Nota", back_populates="dibujos")

    def __repr__(self) -> str:
        return f"<Dibujo id={self.id} nota_id={self.nota_id} orden={self.orden}>"


class Tag(BaseModel):
    """Tag for categorizing notes."""

    __tablename__ = "tags"

    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)

    # Relationships
    notas: Mapped[list["Nota"]] = relationship(
        "Nota",
        secondary=nota_tags,
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"<Tag id={self.id} nombre={self.nombre!r}>"
