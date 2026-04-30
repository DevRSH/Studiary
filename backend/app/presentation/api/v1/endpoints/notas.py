"""FastAPI router: Notas endpoint (stub — se completa en Sprint 2)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Listar notas", tags=["Notas"])
async def list_notas() -> dict[str, str]:
    """Stub endpoint — full implementation in Sprint 2."""
    return {"message": "Notas endpoint — Sprint 2"}
