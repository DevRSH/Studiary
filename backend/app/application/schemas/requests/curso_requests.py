"""Request schemas for Curso endpoints."""

from pydantic import BaseModel, Field


class CursoCreateRequest(BaseModel):
    """Payload for creating a new course.

    Attributes:
        nombre: Course name.
        codigo: Official course code.
        creditos: Number of academic credits.
        periodo_id: Parent periodo ID.
        color: HEX color for UI identification.
        docente: Optional instructor name.
    """

    nombre: str = Field(..., min_length=1, max_length=150, examples=["Cálculo Diferencial"])
    codigo: str = Field(default="", max_length=20, examples=["MAT-101"])
    creditos: int = Field(..., ge=1, le=20, examples=[3])
    periodo_id: int = Field(..., gt=0)
    color: str = Field(default="#6366f1", pattern=r"^#[0-9a-fA-F]{6}$")
    docente: str | None = Field(None, max_length=150)


class CursoUpdateRequest(BaseModel):
    """Payload for partially updating a course."""

    nombre: str | None = Field(None, min_length=1, max_length=150)
    codigo: str | None = Field(None, max_length=20)
    creditos: int | None = Field(None, ge=1, le=20)
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    docente: str | None = None
    activo: bool | None = None
