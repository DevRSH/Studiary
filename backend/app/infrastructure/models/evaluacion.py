"""SQLAlchemy model: Evaluacion."""

from datetime import date
from enum import Enum as PyEnum

from sqlalchemy import Date, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel


class EstadoEvaluacion(str, PyEnum):
    PENDIENTE = "pendiente"
    RENDIDA = "rendida"
    CORREGIDA = "corregida"

class Evaluacion(BaseModel):
    """Assessment model with strict type constraints."""
    __tablename__ = "evaluaciones"
    
    curso_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cursos.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="solemne", nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    ponderacion_porcentaje: Mapped[float] = mapped_column(Float, nullable=False)
    nota_obtenida: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_minima: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    nota_maxima: Mapped[float] = mapped_column(Float, default=7.0, nullable=False)
    estado: Mapped[EstadoEvaluacion] = mapped_column(
        Enum(EstadoEvaluacion),
        default=EstadoEvaluacion.PENDIENTE,
        nullable=False
    )
    
    # Relationships
    curso: Mapped["Curso"] = relationship("Curso", back_populates="evaluaciones")

    def __repr__(self) -> str:
        """Return a string representation of the Evaluacion model."""
        return f"<Evaluacion id={self.id} nombre={self.nombre!r} porcentaje={self.porcentaje}>"
