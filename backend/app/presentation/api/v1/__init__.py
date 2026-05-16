"""API v1 router aggregator."""

from fastapi import APIRouter

from app.presentation.api.v1.endpoints import periodos, cursos, evaluaciones, tareas, notas, calculadora, health

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(periodos.router, prefix="/periodos", tags=["Periodos"])
router.include_router(cursos.router, tags=["Cursos"])
router.include_router(evaluaciones.router, tags=["evaluaciones"])
router.include_router(tareas.router, prefix="/tareas", tags=["Tareas"])
router.include_router(notas.router, prefix="/notas", tags=["Notas"])
router.include_router(calculadora.router, tags=["Calculadora"])
