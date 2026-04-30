"""API v1 router aggregator."""

from fastapi import APIRouter

from app.presentation.api.v1.endpoints import periodos, cursos, evaluaciones, tareas, notas, calculadora

router = APIRouter()

router.include_router(periodos.router, prefix="/periodos", tags=["Periodos"])
router.include_router(cursos.router, prefix="/cursos", tags=["Cursos"])
router.include_router(evaluaciones.router, prefix="/evaluaciones", tags=["Evaluaciones"])
router.include_router(tareas.router, prefix="/tareas", tags=["Tareas"])
router.include_router(notas.router, prefix="/notas", tags=["Notas"])
router.include_router(calculadora.router, prefix="/calculadora", tags=["Calculadora"])
