"""SQLAlchemy model: Tema (topic/theme for organizing course content)."""

from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import BaseModel

if TYPE_CHECKING:
    from .curso import Curso
    from .nota import Nota


class Tema(BaseModel):
    """Topic/theme model for organizing course content."""

    __tablename__ = "temas"

    curso_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cursos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("temas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    curso: Mapped["Curso"] = relationship("Curso", back_populates="temas")
    notas: Mapped[list["Nota"]] = relationship(
        "Nota",
        back_populates="tema",
        cascade="all, delete-orphan",
    )
    parent: Mapped["Tema"] = relationship(
        "Tema",
        remote_side="Tema.id",
        back_populates="children",
    )
    children: Mapped[list["Tema"]] = relationship(
        "Tema",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Tema id={self.id} nombre={self.nombre!r} curso_id={self.curso_id}>"
