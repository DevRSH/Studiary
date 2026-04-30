import pytest
from unittest.mock import AsyncMock
from app.application.services.curso_service import CursoService
from app.infrastructure.models.curso import Curso
from app.application.schemas.requests.curso_schemas import CursoCreateRequest

@pytest.mark.asyncio
async def test_create_curso_success():
    mock_repo = AsyncMock()
    service = CursoService(repository=mock_repo)
    
    request_data = CursoCreateRequest(
        periodo_id=1,
        nombre="Ciberseguridad",
        codigo="CSEC301",
        creditos=4
    )
    
    expected_curso = Curso(id=1, **request_data.model_dump())
    mock_repo.create.return_value = expected_curso
    
    result = await service.create_curso(request_data)
    
    assert result.id == 1
    assert result.nombre == "Ciberseguridad"
    mock_repo.create.assert_called_once()
