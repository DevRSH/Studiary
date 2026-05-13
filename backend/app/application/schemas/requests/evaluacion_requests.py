"""Request schemas for Evaluacion operations."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class EvaluacionCreateRequest(BaseModel):
    """Request schema for creating an evaluacion."""

    curso_id: int = Field(
        ..., gt=0, description="ID del curso"
    )
    nombre: str = Field(
        ..., min_length=1, max_length=200, description="Nombre de la evaluación"
    )
    tipo: str = Field(
        "solemne",
        max_length=50,
        description="Tipo: solemne, taller, proyecto, examen",
    )
    fecha: date = Field(..., description="Fecha de la evaluación")
    ponderacion_porcentaje: float = Field(
        ..., gt=0, le=100, description="Ponderación en porcentaje (0-100)"
    )
    nota_minima: float = Field(1.0, ge=1.0, le=7.0)
    nota_maxima: float = Field(7.0, ge=1.0, le=7.0)

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator("nota_maxima")
    @classmethod
    def validate_nota_maxima(cls, v: float, info) -> float:
        nota_minima = info.data.get("nota_minima", 1.0)
        if v <= nota_minima:
            raise ValueError("nota_maxima debe ser mayor que nota_minima")
        return v


class EvaluacionUpdateRequest(BaseModel):
    """Request schema for updating an evaluacion."""

    nombre: str | None = Field(None, min_length=1, max_length=200)
    tipo: str | None = Field(None, max_length=50)
    fecha: date | None = None
    ponderacion_porcentaje: float | None = Field(None, gt=0, le=100)
    nota_minima: float | None = Field(None, ge=1.0, le=7.0)
    nota_maxima: float | None = Field(None, ge=1.0, le=7.0)


class EvaluacionNotaUpdateRequest(BaseModel):
    """Request schema for updating only the nota_obtenida.
    
    Note: Only lower bound validated here; upper bound validated
    at service layer based on evaluacion.nota_maxima.
    """

    nota_obtenida: float = Field(
        ..., ge=1.0, description="Nota obtenida (validada contra nota_maxima en servicio)"
    )
