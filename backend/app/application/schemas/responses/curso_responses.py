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
    docente: str | None
    activo: bool
    periodo_id: int
    created_at: datetime
    updated_at: datetime


class CursoListResponse(BaseModel):
    """Response DTO for a list of Cursos."""

    model_config = ConfigDict(from_attributes=True)

    items: list[CursoResponse]
    total: int


class CursoDetailResponse(CursoResponse):
    """Response DTO for Curso with evaluations."""

    evaluaciones: list = []
    promedio_actual: float | None = None
