"""FastAPI router: Evaluaciones endpoint (stub — se completa en Sprint 1)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Listar evaluaciones", tags=["Evaluaciones"])
async def list_evaluaciones() -> dict[str, str]:
    """Stub endpoint — full implementation in Sprint 1."""
    return {"message": "Evaluaciones endpoint — Sprint 1"}
