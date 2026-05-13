import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.application.schemas.requests.curso_requests import CursoCreateRequest
from app.application.services.curso_service import CursoService
from app.domain.entities.curso import CursoEntity
from app.infrastructure.models.curso import Curso


@pytest.mark.asyncio
async def test_create_curso_retorna_entity():
    """Test: create_curso debe retornar CursoEntity, no modelo ORM."""
    # Arrange
    mock_repo = AsyncMock()
    service = CursoService(repository=mock_repo)

    request_data = CursoCreateRequest(
        periodo_id=1,
        nombre="Ciberseguridad",
        codigo="CSEC301",
        creditos=4,
        color="#6366f1",
    )

    # Mock: repository.create retorna modelo ORM
    now = datetime.now()
    created_model = Curso(
        id=1,
        periodo_id=1,
        nombre="Ciberseguridad",
        codigo="CSEC301",
        creditos=4,
        color="#6366f1",
        created_at=now,
        updated_at=now,
    )
    mock_repo.create.return_value = created_model

    # Mock: mapper _to_entity (sync method, use MagicMock)
    expected_entity = CursoEntity(
        id=1,
        periodo_id=1,
        nombre="Ciberseguridad",
        codigo="CSEC301",
        creditos=4,
        color="#6366f1",
    )
    mock_repo._to_entity = MagicMock(return_value=expected_entity)

    # Act
    result = await service.create_curso(request_data)

    # Assert
    assert isinstance(result, CursoEntity)
    assert result.id == 1
    assert result.nombre == "Ciberseguridad"
    mock_repo.create.assert_called_once()
    mock_repo._to_entity.assert_called_once_with(created_model)
