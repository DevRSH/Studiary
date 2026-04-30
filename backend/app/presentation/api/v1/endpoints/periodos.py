"""FastAPI router: Periodos endpoint."""

from fastapi import APIRouter, status

from app.application.schemas.requests.periodo_requests import (
    PeriodoCreateRequest,
    PeriodoUpdateRequest,
)
from app.application.schemas.responses.periodo_responses import (
    PeriodoListResponse,
    PeriodoResponse,
)
from app.application.services.periodo_service import PeriodoService
from app.core.dependencies import DbSession
from app.infrastructure.repositories.periodo_repository import PeriodoRepository

router = APIRouter()


def _get_service(session: DbSession) -> PeriodoService:
    """Build PeriodoService with repository dependency."""
    return PeriodoService(PeriodoRepository(session))


@router.get(
    "/",
    response_model=PeriodoListResponse,
    summary="Listar todos los periodos académicos",
)
async def list_periodos(session: DbSession) -> PeriodoListResponse:
    """Return all academic periods ordered by start date."""
    service = _get_service(session)
    items = await service.get_all()
    return PeriodoListResponse(items=items, total=len(items))  # type: ignore[arg-type]


@router.get(
    "/active",
    response_model=PeriodoResponse | None,
    summary="Obtener el periodo académico activo",
)
async def get_active_periodo(session: DbSession) -> object:
    """Return the currently active academic period."""
    service = _get_service(session)
    return await service.get_active()


@router.get(
    "/{periodo_id}",
    response_model=PeriodoResponse,
    summary="Obtener un periodo por ID",
)
async def get_periodo(periodo_id: int, session: DbSession) -> object:
    """Return a specific academic period by ID."""
    service = _get_service(session)
    return await service.get_by_id(periodo_id)


@router.post(
    "/",
    response_model=PeriodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo periodo académico",
)
async def create_periodo(payload: PeriodoCreateRequest, session: DbSession) -> object:
    """Create a new academic period."""
    service = _get_service(session)
    return await service.create(
        nombre=payload.nombre,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        activo=payload.activo,
    )


@router.patch(
    "/{periodo_id}",
    response_model=PeriodoResponse,
    summary="Actualizar un periodo académico",
)
async def update_periodo(
    periodo_id: int, payload: PeriodoUpdateRequest, session: DbSession
) -> object:
    """Partially update an academic period."""
    service = _get_service(session)
    return await service.update(
        periodo_id,
        **payload.model_dump(exclude_none=True),
    )


@router.delete(
    "/{periodo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un periodo académico",
)
async def delete_periodo(periodo_id: int, session: DbSession) -> None:
    """Delete an academic period and all its related data."""
    service = _get_service(session)
    await service.delete(periodo_id)
