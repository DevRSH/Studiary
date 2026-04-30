"""Request schemas for Periodo endpoints."""

from datetime import date

from pydantic import BaseModel, Field, model_validator


class PeriodoCreateRequest(BaseModel):
    """Payload for creating a new academic periodo.

    Attributes:
        nombre: Human-readable name for the period.
        fecha_inicio: Start date of the period.
        fecha_fin: End date of the period.
        activo: Whether this is the current active period.
    """

    nombre: str = Field(..., min_length=1, max_length=100, examples=["Semestre 2026-I"])
    fecha_inicio: date = Field(..., examples=["2026-01-15"])
    fecha_fin: date = Field(..., examples=["2026-06-15"])
    activo: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_dates(self) -> "PeriodoCreateRequest":
        """Ensure fecha_fin is after fecha_inicio."""
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self


class PeriodoUpdateRequest(BaseModel):
    """Payload for partially updating a periodo (all fields optional)."""

    nombre: str | None = Field(None, min_length=1, max_length=100)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activo: bool | None = None
