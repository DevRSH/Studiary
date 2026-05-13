from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.infrastructure.repositories.curso_repository import CursoRepository
from app.application.services.curso_service import CursoService
from app.application.schemas.requests.curso_requests import CursoCreateRequest, CursoUpdateRequest
from app.application.schemas.responses.curso_responses import CursoResponse, CursoDetailResponse
from app.infrastructure.models.curso import Curso
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/cursos", tags=["cursos"])

def get_curso_service(db: AsyncSession = Depends(get_db)) -> CursoService:
    repository = CursoRepository(model=Curso, session=db)
    return CursoService(repository)

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def create_curso(
    data: CursoCreateRequest,
    service: CursoService = Depends(get_curso_service),
    db: AsyncSession = Depends(get_db)
) -> CursoResponse:
    # Create returns entity, but we need ORM model for response
    entity = await service.create_curso(data)
    # Fetch the ORM model for proper serialization
    result = await db.execute(select(Curso).where(Curso.id == entity.id))
    curso = result.scalar_one()
    return CursoResponse.model_validate(curso)

@router.get("/{curso_id}", response_model=CursoDetailResponse)
async def get_curso(
    curso_id: int,
    service: CursoService = Depends(get_curso_service)
) -> CursoDetailResponse:
    curso = await service.get_curso(curso_id)
    return CursoDetailResponse.model_validate(curso)

@router.put("/{curso_id}", response_model=CursoResponse)
async def update_curso(
    curso_id: int,
    data: CursoUpdateRequest,
    service: CursoService = Depends(get_curso_service),
    db: AsyncSession = Depends(get_db)
) -> CursoResponse:
    entity = await service.update_curso(curso_id, data)
    result = await db.execute(select(Curso).where(Curso.id == entity.id))
    curso = result.scalar_one()
    return CursoResponse.model_validate(curso)

@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(
    curso_id: int,
    service: CursoService = Depends(get_curso_service)
) -> None:
    deleted = await service.delete_curso(curso_id)
    if not deleted:
        raise NotFoundException(f"Curso {curso_id} no encontrado")
