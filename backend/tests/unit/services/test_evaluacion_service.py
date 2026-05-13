"""Unit tests for EvaluacionService."""

from datetime import date

import pytest
from unittest.mock import AsyncMock

from app.application.schemas.requests.evaluacion_requests import (
    EvaluacionCreateRequest,
    EvaluacionNotaUpdateRequest,
)
from app.application.services.evaluacion_service import EvaluacionService
from app.core.exceptions import ValidationException
from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import Evaluacion, EstadoEvaluacion


@pytest.mark.asyncio
async def test_create_evaluacion_valida_suma_ponderaciones():
    """Test: Validar que suma de ponderaciones no exceda 100%."""
    # Setup
    mock_repo = AsyncMock()
    mock_db = AsyncMock()

    # Mock curso existe
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = Curso(
        id=1, nombre="Test", periodo_id=1
    )
    mock_db.execute.return_value = mock_result

    # Mock evaluaciones existentes suman 70%
    existing_eval = Evaluacion(
        id=1,
        curso_id=1,
        nombre="Solemne 1",
        fecha=date(2026, 3, 15),
        ponderacion_porcentaje=70.0,
    )
    mock_repo.get_by_curso.return_value = [existing_eval]

    service = EvaluacionService(repository=mock_repo, db_session=mock_db)

    # Act & Assert - Intentar agregar 40% (total 110%)
    request = EvaluacionCreateRequest(
        curso_id=1,
        nombre="Solemne 2",
        fecha=date(2026, 5, 20),
        ponderacion_porcentaje=40.0,
    )

    with pytest.raises(ValidationException) as exc:
        await service.create_evaluacion(request)

    assert "excede 100%" in str(exc.value)


@pytest.mark.asyncio
async def test_update_nota_valida_rango():
    """Test: Validar que nota esté dentro del rango permitido."""
    # Setup
    mock_repo = AsyncMock()
    mock_db = AsyncMock()

    evaluacion = Evaluacion(
        id=1,
        curso_id=1,
        nombre="Solemne 1",
        fecha=date(2026, 3, 15),
        ponderacion_porcentaje=30.0,
        nota_minima=1.0,
        nota_maxima=7.0,
        estado=EstadoEvaluacion.RENDIDA,
    )
    mock_repo.get_by_id.return_value = evaluacion

    service = EvaluacionService(repository=mock_repo, db_session=mock_db)

    # Act & Assert - Nota fuera de rango
    request = EvaluacionNotaUpdateRequest(nota_obtenida=8.5)

    with pytest.raises(ValidationException) as exc:
        await service.update_nota(1, request)

    assert "fuera de rango" in str(exc.value)


@pytest.mark.asyncio
async def test_update_nota_cambia_estado_a_corregida():
    """Test: Actualizar nota debe cambiar estado a CORREGIDA."""
    # Setup
    mock_repo = AsyncMock()
    mock_db = AsyncMock()

    evaluacion = Evaluacion(
        id=1,
        curso_id=1,
        nombre="Solemne 1",
        fecha=date(2026, 3, 15),
        ponderacion_porcentaje=30.0,
        nota_minima=1.0,
        nota_maxima=7.0,
        estado=EstadoEvaluacion.RENDIDA,
    )
    mock_repo.get_by_id.return_value = evaluacion
    mock_repo.update.return_value = evaluacion

    service = EvaluacionService(repository=mock_repo, db_session=mock_db)

    # Act
    request = EvaluacionNotaUpdateRequest(nota_obtenida=5.5)
    await service.update_nota(1, request)

    # Assert
    assert evaluacion.nota_obtenida == 5.5
    assert evaluacion.estado == EstadoEvaluacion.CORREGIDA
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_ponderacion_valida_suma():
    """Test: Al actualizar ponderacion, validar que suma <= 100%."""
    # Setup
    mock_repo = AsyncMock()
    mock_db = AsyncMock()

    # Evaluacion a actualizar
    evaluacion_target = Evaluacion(
        id=1,
        curso_id=1,
        nombre="Solemne 1",
        fecha=date(2026, 3, 15),
        ponderacion_porcentaje=30.0,
    )

    # Otras evaluaciones del curso suman 80%
    otras_evals = [
        Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=80.0,
        ),
    ]

    mock_repo.get_by_id.return_value = evaluacion_target
    mock_repo.get_by_curso.return_value = [evaluacion_target] + otras_evals

    service = EvaluacionService(repository=mock_repo, db_session=mock_db)

    # Act & Assert - Intentar cambiar de 30% a 50% (suma = 50% + 80% = 130%)
    from app.application.schemas.requests.evaluacion_requests import (
        EvaluacionUpdateRequest,
    )

    request = EvaluacionUpdateRequest(ponderacion_porcentaje=50.0)

    with pytest.raises(ValidationException) as exc:
        await service.update_evaluacion(1, request)

    assert "excede 100%" in str(exc.value)
