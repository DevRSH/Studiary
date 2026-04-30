"""Response schemas for Periodo endpoints."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PeriodoResponse(BaseModel):
    """Response DTO for a single Periodo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    activo: bool
    created_at: datetime| None = None
    updated_at: datetime| None = None


class PeriodoListResponse(BaseModel):
    """Response DTO for a paginated list of Periodos."""

    model_config = ConfigDict(from_attributes=True)

    items: list[PeriodoResponse]
    total: int
