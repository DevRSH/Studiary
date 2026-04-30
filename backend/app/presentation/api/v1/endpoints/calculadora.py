from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.responses.calculadora_schemas import ProyeccionResponse
from app.application.services.calculadora_service import CalculadoraService
from app.core.database import get_db

router = APIRouter(prefix="/calculadora", tags=["calculadora"])


def get_calculadora_service(db: AsyncSession = Depends(get_db)) -> CalculadoraService:
    """Dependency provider for CalculadoraService."""
    return CalculadoraService(db_session=db)


@router.get("/proyeccion/{curso_id}", response_model=ProyeccionResponse)
async def get_proyeccion(
    curso_id: int,
    nota_objetivo: float = Query(4.0, ge=1.0, le=7.0),
    service: CalculadoraService = Depends(get_calculadora_service),
) -> ProyeccionResponse:
    """Calcula la proyección de notas necesaria para alcanzar un objetivo."""
    proyeccion = await service.calcular_proyeccion(curso_id, nota_objetivo)
    return ProyeccionResponse.model_validate(proyeccion, from_attributes=True)


@router.get("/promedio/{curso_id}")
async def get_promedio(
    curso_id: int, service: CalculadoraService = Depends(get_calculadora_service)
) -> dict[str, Any]:
    """Retorna el promedio actual ponderado de un curso."""
    # Reutilizamos la lógica de proyección con un objetivo arbitrario (no afecta al promedio actual)
    proyeccion = await service.calcular_proyeccion(curso_id, 4.0)
    return {
        "curso_id": curso_id,
        "nota_actual": round(proyeccion.nota_actual, 2),
        "ponderacion_usada": proyeccion.ponderacion_usada,
    }

