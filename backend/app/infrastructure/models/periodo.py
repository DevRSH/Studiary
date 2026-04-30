"""SQLAlchemy model: Periodo Académico."""

from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel


class Periodo(BaseModel):
    """Academic period model (e.g., "Semestre 3 2026")."""
    __tablename__ = "periodos"
    
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    cursos: Mapped[list["Curso"]] = relationship(
        "Curso",
        back_populates="periodo",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a string representation of the Periodo model."""
        return f"<Periodo id={self.id} nombre={self.nombre!r} activo={self.activo}>"
