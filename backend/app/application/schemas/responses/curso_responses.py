"""Response schemas for Curso endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CursoResponse(BaseModel):
    """Response DTO for a single Curso."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    codigo: str
    creditos: int
    color: str
    periodo_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # Optional fields not in Curso model
    docente: str | None = None
    activo: bool = True


class CursoListResponse(BaseModel):
    """Response DTO for a list of Cursos."""

    model_config = ConfigDict(from_attributes=True)

    items: list[CursoResponse]
    total: int


class CursoDetailResponse(CursoResponse):
    """Response DTO for Curso with evaluations."""

    evaluaciones: list = []
    promedio_actual: float | None = None
