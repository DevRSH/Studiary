"""Response schemas for Nota endpoints."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.infrastructure.models.nota import TipoNota


class TagResponse(BaseModel):
    """Response schema for tag."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    color: str
    created_at: datetime


class DibujoResponse(BaseModel):
    """Response schema for drawing."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nota_id: int
    canvas_json: str
    thumbnail_base64: str | None
    orden: int
    created_at: datetime
    updated_at: datetime


class NotaResponse(BaseModel):
    """Response schema for note."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tema_id: int | None
    titulo: str
    contenido_markdown: str | None
    tipo: TipoNota
    created_at: datetime
    updated_at: datetime


class NotaDetailResponse(NotaResponse):
    """Detailed note response with relations."""

    dibujos: list[DibujoResponse] = []
    tags: list[TagResponse] = []
