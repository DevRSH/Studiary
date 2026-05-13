"""Unit tests for NotaService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.nota_service import NotaService
from app.infrastructure.models.nota import Nota, TipoNota, Tag, Dibujo
from app.application.schemas.requests.nota_requests import NotaCreateRequest, DibujoCreateRequest


@pytest.fixture
def mock_db():
    """Create a mock AsyncSession."""
    return AsyncMock()


@pytest.fixture
def nota_service(mock_db):
    """Create NotaService with mock db."""
    return NotaService(db_session=mock_db)


@pytest.mark.asyncio
async def test_create_nota_con_tags(nota_service, mock_db):
    """Test: Crear nota con tags asociados."""
    # Mock tags existentes
    tag1 = Tag(id=1, nombre="importante", color="#FF0000")
    tag2 = Tag(id=2, nombre="estudio", color="#00FF00")
    
    # Setup mock for tag query
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [tag1, tag2]
    mock_db.execute.return_value = mock_result
    
    request = NotaCreateRequest(
        titulo="Teorema CAP",
        contenido_markdown="# CAP Theorem\n\nConsistency, Availability, Partition tolerance",
        tipo=TipoNota.TEXTO,
        tag_ids=[1, 2]
    )
    
    nota = await nota_service.create_nota(request)
    
    # Verificar que se asociaron los tags
    assert nota.titulo == "Teorema CAP"
    assert nota.tipo == TipoNota.TEXTO
    mock_db.add.assert_called()
    mock_db.flush.assert_called()


@pytest.mark.asyncio
async def test_create_nota_con_dibujos(nota_service, mock_db):
    """Test: Crear nota con dibujos."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    dibujo_data = DibujoCreateRequest(
        canvas_json='{"objects": [{"type": "path"}]}',
        thumbnail_base64="data:image/png;base64,abc123",
        orden=0
    )
    
    request = NotaCreateRequest(
        titulo="Diagrama de Clases",
        tipo=TipoNota.HANDWRITTEN,
        dibujos=[dibujo_data]
    )
    
    nota = await nota_service.create_nota(request)
    
    assert nota.titulo == "Diagrama de Clases"
    assert nota.tipo == TipoNota.HANDWRITTEN
    mock_db.add.assert_called()


@pytest.mark.asyncio
async def test_add_dibujo_incrementa_orden(nota_service, mock_db):
    """Test: Agregar dibujo debe incrementar orden automáticamente."""
    # Mock nota con 1 dibujo existente (orden=0)
    existing_dibujo = Dibujo(id=1, nota_id=1, canvas_json='{}', orden=0)
    nota = Nota(id=1, titulo="Test", tipo=TipoNota.HANDWRITTEN)
    nota.dibujos = [existing_dibujo]
    
    # Mock get_nota response
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = nota
    mock_db.execute.return_value = mock_result
    
    dibujo = await nota_service.add_dibujo(
        nota_id=1,
        canvas_json='{"objects": []}',
        thumbnail_base64=None
    )
    
    # El nuevo dibujo debe tener orden=1
    assert dibujo.orden == 1
    assert dibujo.nota_id == 1
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called()


@pytest.mark.asyncio
async def test_get_nota_not_found(nota_service, mock_db):
    """Test: Get nota que no existe debe lanzar NotFoundException."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    from app.core.exceptions import NotFoundException
    
    with pytest.raises(NotFoundException) as exc_info:
        await nota_service.get_nota(999)
    
    assert "Nota 999 no encontrada" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_nota(nota_service, mock_db):
    """Test: Eliminar nota existente."""
    nota = Nota(id=1, titulo="Test", tipo=TipoNota.TEXTO)
    mock_db.get.return_value = nota
    
    result = await nota_service.delete_nota(1)
    
    assert result is True
    mock_db.delete.assert_called_once_with(nota)
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_delete_nota_not_found(nota_service, mock_db):
    """Test: Eliminar nota que no existe."""
    mock_db.get.return_value = None
    
    result = await nota_service.delete_nota(999)
    
    assert result is False
