"""SQLAlchemy model: Tarea.

Incluye los campos necesarios para el algoritmo de priorización P = W*D/(T+1).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel


class Tarea(BaseModel):
    """Tarea o actividad asignada en un curso.

    El campo `prioridad` se calcula usando P = W * D / (T + 1) donde:
        W = peso/dificultad estimada de la tarea
        D = días restantes hasta la fecha límite
        T = tiempo estimado de completado en horas

    Attributes:
        peso: Dificultad/importancia percibida (W, 1-10).
        tiempo_estimado_horas: Tiempo estimado en horas (T).
        prioridad: Prioridad calculada (mayor = más urgente).
        completada: Estado de completitud.
    """

    __tablename__ = "tareas"

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_limite: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    peso: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    tiempo_estimado_horas: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    prioridad: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)

    curso_id: Mapped[int] = mapped_column(
        ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    curso: Mapped["Curso"] = relationship("Curso", back_populates="tareas")  # noqa: F821

    def __repr__(self) -> str:
        """Return a string representation of the Tarea model."""
        return f"<Tarea id={self.id} titulo={self.titulo!r} prioridad={self.prioridad:.2f}>"
