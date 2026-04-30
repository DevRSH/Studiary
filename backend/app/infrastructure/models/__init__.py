"""Infrastructure models package — re-exports all ORM models for Alembic detection."""

from app.infrastructure.models.base import BaseModel, TimestampMixin
from app.infrastructure.models.periodo import Periodo
from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import Evaluacion
from app.infrastructure.models.tarea import Tarea
from app.infrastructure.models.nota import Nota
from app.infrastructure.models.recurso import Recurso

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "Periodo",
    "Curso",
    "Evaluacion",
    "Tarea",
    "Nota",
    "Recurso",
]
