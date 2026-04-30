"""SQLAlchemy model: Recurso (archivo/enlace asociado a un curso)."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class Recurso(BaseModel):
    """Recurso educativo (PDF, enlace, imagen) asociado a un curso.

    Attributes:
        nombre: Nombre descriptivo del recurso.
        tipo: Tipo de recurso (pdf, link, imagen, video, otro).
        url: URL del recurso (externo o en Nextcloud).
        tamanio_bytes: Tamaño en bytes si es archivo local/Nextcloud.
        nextcloud_path: Ruta en Nextcloud para recursos sincronizados.
    """

    __tablename__ = "recursos"

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="otro")
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    tamanio_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nextcloud_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    def __repr__(self) -> str:
        """Return a string representation of the Recurso model."""
        return f"<Recurso id={self.id} nombre={self.nombre!r} tipo={self.tipo!r}>"
