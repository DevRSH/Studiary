"""FastAPI router: Notas endpoint."""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.infrastructure.models.nota import Nota
from app.application.services.nota_service import NotaService
from app.application.schemas.requests.nota_requests import (
    DibujoCreateRequest,
    NotaCreateRequest,
    NotaUpdateRequest,
)
from app.application.schemas.responses.nota_responses import (
    DibujoResponse,
    NotaDetailResponse,
    NotaResponse,
)

router = APIRouter(tags=["notas"])


def get_nota_service(db: AsyncSession = Depends(get_db)) -> NotaService:
    """Dependency injection for NotaService."""
    return NotaService(db_session=db)


@router.post("/", response_model=NotaDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_nota(
    data: NotaCreateRequest,
    service: NotaService = Depends(get_nota_service),
) -> NotaDetailResponse:
    """Create new nota with optional drawings and tags."""
    nota = await service.create_nota(data)
    return NotaDetailResponse.model_validate(nota)


@router.get("/", response_model=List[NotaResponse])
async def list_notas(
    tema_id: int | None = Query(None),
    search: str | None = Query(None, min_length=2),
    service: NotaService = Depends(get_nota_service),
) -> List[NotaResponse]:
    """List notas filtered by tema or search query."""
    if search:
        notas = await service.search_notas(search)
    elif tema_id:
        notas = await service.get_by_tema(tema_id)
    else:
        # Get all notas (add pagination later)
        result = await service.db.execute(
            select(Nota).order_by(Nota.updated_at.desc()).limit(100)
        )
        notas = result.scalars().all()

    return [NotaResponse.model_validate(n) for n in notas]


@router.get("/{nota_id}", response_model=NotaDetailResponse)
async def get_nota(
    nota_id: int,
    service: NotaService = Depends(get_nota_service),
) -> NotaDetailResponse:
    """Get nota by ID with drawings and tags."""
    nota = await service.get_nota(nota_id)
    return NotaDetailResponse.model_validate(nota)


@router.put("/{nota_id}", response_model=NotaDetailResponse)
async def update_nota(
    nota_id: int,
    data: NotaUpdateRequest,
    service: NotaService = Depends(get_nota_service),
) -> NotaDetailResponse:
    """Update nota."""
    nota = await service.update_nota(nota_id, data)
    return NotaDetailResponse.model_validate(nota)


@router.post("/{nota_id}/dibujos", response_model=DibujoResponse)
async def add_dibujo(
    nota_id: int,
    data: DibujoCreateRequest,
    service: NotaService = Depends(get_nota_service),
) -> DibujoResponse:
    """Add drawing to existing nota."""
    dibujo = await service.add_dibujo(
        nota_id=nota_id,
        canvas_json=data.canvas_json,
        thumbnail_base64=data.thumbnail_base64,
    )
    return DibujoResponse.model_validate(dibujo)


@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nota(
    nota_id: int,
    service: NotaService = Depends(get_nota_service),
) -> None:
    """Delete nota (cascade deletes drawings)."""
    deleted = await service.delete_nota(nota_id)
    if not deleted:
        raise NotFoundException(f"Nota {nota_id} no encontrada")
