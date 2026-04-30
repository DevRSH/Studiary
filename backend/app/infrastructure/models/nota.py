"""SQLAlchemy model: Nota (apunte digital).

Soporta contenido Markdown y referencia a canvas de handwriting (Fabric.js).
"""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel


class Nota(BaseModel):
    """Apunte digital asociado a un curso.

    Attributes:
        titulo: Título del apunte.
        contenido_md: Contenido en formato Markdown.
        canvas_json: Serialización JSON del canvas de Fabric.js (handwriting).
                     Puede ser None si la nota es solo texto.
        tags: Tags separados por coma para búsqueda/filtrado.
        nextcloud_path: Ruta en Nextcloud si el recurso fue sincronizado.
    """

    __tablename__ = "notas"

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    contenido_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    canvas_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    nextcloud_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    curso: Mapped["Curso"] = relationship("Curso", back_populates="notas")  # noqa: F821

    def __repr__(self) -> str:
        """Return a string representation of the Nota model."""
        return f"<Nota id={self.id} titulo={self.titulo!r} curso_id={self.curso_id}>"
