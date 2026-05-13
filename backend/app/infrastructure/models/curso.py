from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from .base import BaseModel

# Esto evita referencias circulares en tiempo de ejecución pero satisface a Mypy/SQLAlchemy
if TYPE_CHECKING:
    from .periodo import Periodo
    from .evaluacion import Evaluacion
    from .tarea import Tarea
    from .tema import Tema

class Curso(BaseModel):
    """Course model mapped to an academic period."""
    __tablename__ = "cursos"
    
    periodo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("periodos.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)
    creditos: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    
    # Relationships
    periodo: Mapped["Periodo"] = relationship("Periodo", back_populates="cursos")
    
    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        "Evaluacion",
        back_populates="curso",
        cascade="all, delete-orphan"
    )
    
    tareas: Mapped[list["Tarea"]] = relationship(
        "Tarea",
        back_populates="curso",
        cascade="all, delete-orphan"
    )
    
    temas: Mapped[list["Tema"]] = relationship(
        "Tema",
        back_populates="curso",
        cascade="all, delete-orphan"
    )