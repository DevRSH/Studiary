"""Request schemas for Nota endpoints."""

from pydantic import BaseModel, Field, field_validator

from app.infrastructure.models.nota import TipoNota


class DibujoCreateRequest(BaseModel):
    """Request for creating a drawing."""

    canvas_json: str = Field(..., min_length=1, description="Fabric.js serialized JSON")
    thumbnail_base64: str | None = Field(None, description="Base64 thumbnail")
    orden: int = Field(0, ge=0)


class NotaCreateRequest(BaseModel):
    """Request for creating a note."""

    tema_id: int | None = Field(None, description="Associated tema ID")
    titulo: str = Field(..., min_length=1, max_length=200)
    contenido_markdown: str | None = Field(None, description="Markdown content")
    tipo: TipoNota = Field(TipoNota.TEXTO)
    tag_ids: list[int] = Field(default_factory=list, description="List of tag IDs")
    dibujos: list[DibujoCreateRequest] = Field(default_factory=list)

    @field_validator("titulo")
    @classmethod
    def validate_titulo(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip()


class NotaUpdateRequest(BaseModel):
    """Request for updating a note."""

    tema_id: int | None = None
    titulo: str | None = Field(None, min_length=1, max_length=200)
    contenido_markdown: str | None = None
    tipo: TipoNota | None = None
    tag_ids: list[int] | None = None


class TagCreateRequest(BaseModel):
    """Request for creating a tag."""

    nombre: str = Field(..., min_length=1, max_length=50)
    color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, v: str) -> str:
        return v.strip().lower()
