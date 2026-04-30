"""FastAPI router: Tareas endpoint (stub — se completa en Sprint 1)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Listar tareas", tags=["Tareas"])
async def list_tareas() -> dict[str, str]:
    """Stub endpoint — full implementation in Sprint 1."""
    return {"message": "Tareas endpoint — Sprint 1"}
