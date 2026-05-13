"""FastAPI router: Evaluaciones endpoint (Sprint 1)."""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.requests.evaluacion_requests import (
    EvaluacionCreateRequest,
    EvaluacionNotaUpdateRequest,
    EvaluacionUpdateRequest,
)
from app.application.schemas.responses.evaluacion_responses import (
    EvaluacionResponse,
)
from app.application.services.evaluacion_service import EvaluacionService
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.infrastructure.models.evaluacion import Evaluacion
from app.infrastructure.repositories.evaluacion_repository import (
    EvaluacionRepository,
)

router = APIRouter(prefix="/evaluaciones", tags=["evaluaciones"])


def get_evaluacion_service(
    db: AsyncSession = Depends(get_db),
) -> EvaluacionService:
    """Dependency injection for EvaluacionService."""
    repository = EvaluacionRepository(model=Evaluacion, session=db)
    return EvaluacionService(repository=repository, db_session=db)


@router.post(
    "/", response_model=EvaluacionResponse, status_code=status.HTTP_201_CREATED
)
async def create_evaluacion(
    data: EvaluacionCreateRequest,
    service: EvaluacionService = Depends(get_evaluacion_service),
) -> EvaluacionResponse:
    """Create new evaluacion with validations.

    Validates:
    - Curso exists
    - Sum of ponderaciones <= 100%
    """
    evaluacion = await service.create_evaluacion(data)
    return EvaluacionResponse.model_validate(evaluacion)


@router.get("/", response_model=List[EvaluacionResponse])
async def list_evaluaciones(
    curso_id: int | None = Query(None, description="Filter by curso_id"),
    service: EvaluacionService = Depends(get_evaluacion_service),
) -> List[EvaluacionResponse]:
    """List all evaluaciones, optionally filtered by curso."""
    if curso_id:
        evaluaciones = await service.get_by_curso(curso_id)
    else:
        evaluaciones = await service.repository.get_all()

    return [EvaluacionResponse.model_validate(e) for e in evaluaciones]


@router.get("/{evaluacion_id}", response_model=EvaluacionResponse)
async def get_evaluacion(
    evaluacion_id: int,
    service: EvaluacionService = Depends(get_evaluacion_service),
) -> EvaluacionResponse:
    """Get evaluacion by ID."""
    evaluacion = await service.get_evaluacion(evaluacion_id)
    return EvaluacionResponse.model_validate(evaluacion)


@router.put("/{evaluacion_id}", response_model=EvaluacionResponse)
async def update_evaluacion(
    evaluacion_id: int,
    data: EvaluacionUpdateRequest,
    service: EvaluacionService = Depends(get_evaluacion_service),
) -> EvaluacionResponse:
    """Update evaluacion."""
    evaluacion = await service.update_evaluacion(evaluacion_id, data)
    return EvaluacionResponse.model_validate(evaluacion)


@router.patch("/{evaluacion_id}/nota", response_model=EvaluacionResponse)
async def update_nota(
    evaluacion_id: int,
    data: EvaluacionNotaUpdateRequest,
    service: EvaluacionService = Depends(get_evaluacion_service),
) -> EvaluacionResponse:
    """Update only nota_obtenida and set estado to CORREGIDA.

    Validates nota is within [nota_minima, nota_maxima].
    """
    evaluacion = await service.update_nota(evaluacion_id, data)
    return EvaluacionResponse.model_validate(evaluacion)


@router.delete("/{evaluacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluacion(
    evaluacion_id: int,
    service: EvaluacionService = Depends(get_evaluacion_service),
) -> None:
    """Delete evaluacion by ID."""
    deleted = await service.delete_evaluacion(evaluacion_id)
    if not deleted:
        raise NotFoundException(f"Evaluación {evaluacion_id} no encontrada")
