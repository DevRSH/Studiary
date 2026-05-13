"""Response schemas for Evaluacion operations."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.infrastructure.models.evaluacion import EstadoEvaluacion


class EvaluacionResponse(BaseModel):
    """Response schema for evaluacion data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    curso_id: int
    nombre: str
    tipo: str
    fecha: date
    ponderacion_porcentaje: float
    nota_obtenida: float | None
    nota_minima: float
    nota_maxima: float
    estado: EstadoEvaluacion
    created_at: datetime
    updated_at: datetime
