"""Unit tests for CalculadoraService — mocking DB where necessary."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.calculadora_service import CalculadoraService
from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import Evaluacion, EstadoEvaluacion


class TestCalculadoraService:
    """Unit tests for the predictive grade calculator."""

    def setup_method(self) -> None:
        """Set up calculator."""
        self.calc = CalculadoraService()

    # ============================================
    # TESTS PRIORIDAD TAREA
    # ============================================

    def test_prioridad_formula(self) -> None:
        """P = W * D / (T + 1) — basic correctness check."""
        priority = self.calc.calcular_prioridad_tarea(
            peso=8, dias_restantes=5, tiempo_estimado_horas=3
        )
        expected = 8 * 5 / (3 + 1)  # = 10.0
        assert priority == pytest.approx(expected, abs=0.001)

    def test_prioridad_vencida_uses_minimum_dias(self) -> None:
        """Overdue task (negative days) should use 1 day minimum."""
        priority = self.calc.calcular_prioridad_tarea(
            peso=5, dias_restantes=-2, tiempo_estimado_horas=1
        )
        # dias_restantes clipped to 0, then max(1, 0) = 1
        assert priority == pytest.approx(5 * 1 / (1 + 1), abs=0.001)

    # ============================================
    # TESTS DE VALIDACIÓN DE ENTRADA
    # ============================================

    @pytest.mark.asyncio
    async def test_proyeccion_nota_objetivo_menor_que_uno(self) -> None:
        """Test: Nota objetivo < 1.0 debe lanzar ValidationException."""
        mock_db = AsyncMock()
        service = CalculadoraService(db_session=mock_db)

        with pytest.raises(ValidationException) as exc:
            await service.calcular_proyeccion(curso_id=1, nota_objetivo=0.5)

        assert "fuera de rango [1.0, 7.0]" in str(exc.value)

    @pytest.mark.asyncio
    async def test_proyeccion_nota_objetivo_mayor_que_siete(self) -> None:
        """Test: Nota objetivo > 7.0 debe lanzar ValidationException."""
        mock_db = AsyncMock()
        service = CalculadoraService(db_session=mock_db)

        with pytest.raises(ValidationException) as exc:
            await service.calcular_proyeccion(curso_id=1, nota_objetivo=7.5)

        assert "fuera de rango [1.0, 7.0]" in str(exc.value)

    @pytest.mark.asyncio
    async def test_proyeccion_sin_db_session(self) -> None:
        """Test: Sin db_session debe lanzar ValidationException."""
        service = CalculadoraService(db_session=None)

        with pytest.raises(ValidationException) as exc:
            await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.0)

        assert "Database session required" in str(exc.value)

    @pytest.mark.asyncio
    async def test_proyeccion_curso_no_encontrado(self) -> None:
        """Test: Curso inexistente debe lanzar NotFoundException."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)

        with pytest.raises(NotFoundException) as exc:
            await service.calcular_proyeccion(curso_id=999, nota_objetivo=5.5)

        assert "Curso 999 no encontrado" in str(exc.value)

    @pytest.mark.asyncio
    async def test_proyeccion_curso_sin_evaluaciones(self) -> None:
        """Test: Curso sin evaluaciones debe lanzar ValidationException."""
        mock_db = AsyncMock()

        # Mock curso existe pero sin evaluaciones
        curso_sin_evals = Curso(id=1, nombre="Test", periodo_id=1, evaluaciones=[])
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso_sin_evals
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)

        with pytest.raises(ValidationException) as exc:
            await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.5)

        assert "sin evaluaciones" in str(exc.value)

    # ============================================
    # TESTS PROYECCION BÁSICA
    # ============================================

    @pytest.mark.asyncio
    async def test_calcular_proyeccion_basic(self) -> None:
        """Test a simple projection scenario with mocked DB."""
        mock_db = AsyncMock()
        self.calc.db = mock_db

        # Setup mock course and evaluations
        curso = Curso(id=1, nombre="Test Course")
        e1 = Evaluacion(
            nombre="Parcial 1",
            ponderacion_porcentaje=30.0,
            nota_obtenida=4.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        e2 = Evaluacion(
            nombre="Final", ponderacion_porcentaje=70.0, estado=EstadoEvaluacion.PENDIENTE
        )
        curso.evaluaciones = [e1, e2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        # Objetivo: 5.0
        # (5.0 * 100 - 4.0 * 30) / 70 = (500 - 120) / 70 = 380 / 70 = 5.43
        res = await self.calc.calcular_proyeccion(curso_id=1, nota_objetivo=5.0)

        assert res.nota_actual == 4.0
        assert res.ponderacion_restante == 70.0
        assert res.es_factible is True
        assert res.estrategias[0].distribuciones[0]["nota_necesaria"] == pytest.approx(
            5.43, abs=0.01
        )

    # ============================================
    # TESTS DE CASOS LÍMITE
    # ============================================

    @pytest.mark.asyncio
    async def test_proyeccion_objetivo_imposible_nota_mayor_siete(self) -> None:
        """Test: Objetivo imposible (requiere nota > 7.0) debe marcar es_factible=False."""
        mock_db = AsyncMock()

        # Curso con 50% rendida con nota 3.0, objetivo 6.5
        # Requiere: (6.5*100 - 3.0*50) / 50 = 10.0 > 7.0 → IMPOSIBLE
        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=50.0,
            nota_obtenida=3.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=50.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=6.5)

        assert proyeccion.es_factible is False
        assert proyeccion.nota_actual == 3.0
        assert proyeccion.ponderacion_restante == 50.0

    @pytest.mark.asyncio
    async def test_proyeccion_sin_evaluaciones_pendientes(self) -> None:
        """Test: Curso con todas las evaluaciones corregidas (sin pendientes)."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=60.0,
            nota_obtenida=5.5,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=40.0,
            nota_obtenida=6.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=6.0)

        # Nota final: (5.5*60 + 6.0*40) / 100 = 5.7
        assert proyeccion.nota_actual == 5.7
        assert proyeccion.ponderacion_restante == 0.0
        assert proyeccion.es_factible is False  # Ya no puede alcanzar 6.0
        assert len(proyeccion.estrategias) == 0  # Sin pendientes, sin estrategias

    @pytest.mark.asyncio
    async def test_proyeccion_objetivo_exacto_nota_actual(self) -> None:
        """Test: Objetivo igual a nota actual (ya alcanzado)."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=30.0,
            nota_obtenida=5.5,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=70.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.5)

        # Requiere: (5.5*100 - 5.5*30) / 70 = 5.5 → FACTIBLE
        assert proyeccion.es_factible is True
        assert proyeccion.nota_actual == 5.5

    @pytest.mark.asyncio
    async def test_proyeccion_sin_evaluaciones_corregidas(self) -> None:
        """Test: Curso sin evaluaciones corregidas (todas pendientes)."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=40.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=60.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.5)

        # Sin notas rendidas, nota_actual es 0.0
        assert proyeccion.nota_actual == 0.0
        assert proyeccion.ponderacion_restante == 100.0
        assert proyeccion.es_factible is True  # Necesita 5.5 en ambas

    # ============================================
    # TESTS DE ESTRATEGIAS
    # ============================================

    @pytest.mark.asyncio
    async def test_estrategia_uniforme_calculada_correctamente(self) -> None:
        """Test: Estrategia uniforme asigna misma nota a todas las pendientes."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=30.0,
            nota_obtenida=5.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=35.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        eval3 = Evaluacion(
            id=3,
            curso_id=1,
            nombre="Proyecto",
            fecha=date(2026, 6, 15),
            ponderacion_porcentaje=35.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2, eval3]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.5)

        # Nota necesaria: (5.5*100 - 5.0*30) / 70 = 5.71
        estrategia_uniforme = proyeccion.estrategias[0]
        assert estrategia_uniforme.nombre == "Uniforme"
        assert len(estrategia_uniforme.distribuciones) == 2  # 2 pendientes

        # Todas las pendientes deben tener la misma nota necesaria
        for dist in estrategia_uniforme.distribuciones:
            assert abs(dist["nota_necesaria"] - 5.71) < 0.1

    @pytest.mark.asyncio
    async def test_estrategia_realista_agrega_margen(self) -> None:
        """Test: Estrategia realista agrega 0.5 puntos de cushion."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=40.0,
            nota_obtenida=5.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=60.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.0)

        # Nota necesaria uniforme: (5.0*100 - 5.0*40) / 60 = 5.0
        # Estrategia realista debe ser: 5.0 + 0.5 = 5.5
        estrategia_realista = [
            e for e in proyeccion.estrategias if "margen" in e.nombre.lower()
        ][0]

        for dist in estrategia_realista.distribuciones:
            assert abs(dist["nota_necesaria"] - 5.5) < 0.1

    @pytest.mark.asyncio
    async def test_genera_dos_estrategias(self) -> None:
        """Test: Siempre genera exactamente 2 estrategias (Uniforme + Realista)."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=20.0,
            nota_obtenida=5.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=40.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        eval3 = Evaluacion(
            id=3,
            curso_id=1,
            nombre="Proyecto",
            fecha=date(2026, 6, 15),
            ponderacion_porcentaje=40.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2, eval3]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.5)

        # Debe generar exactamente 2 estrategias
        assert len(proyeccion.estrategias) == 2

        nombres_estrategias = [e.nombre for e in proyeccion.estrategias]
        assert "Uniforme" in nombres_estrategias
        assert "Realista con margen" in nombres_estrategias

    # ============================================
    # TESTS DE CLASIFICACIÓN DE DIFICULTAD
    # ============================================

    @pytest.mark.asyncio
    async def test_clasificacion_dificultad_facil(self) -> None:
        """Test: Nota necesaria < 4.0 se clasifica como Fácil."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=50.0,
            nota_obtenida=6.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=50.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.0)

        # Nota necesaria: (5.0*100 - 6.0*50) / 50 = 4.0 → Moderado
        estrategia_uniforme = proyeccion.estrategias[0]
        assert estrategia_uniforme.dificultad == "Moderado"

    @pytest.mark.asyncio
    async def test_clasificacion_dificultad_dificil(self) -> None:
        """Test: Nota necesaria >= 6.0 se clasifica como Muy Difícil."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=40.0,
            nota_obtenida=4.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=60.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=5.5)

        # Nota necesaria: (5.5*100 - 4.0*40) / 60 = 6.5 → Muy Difícil
        estrategia_uniforme = proyeccion.estrategias[0]
        assert estrategia_uniforme.dificultad == "Muy Difícil"

    @pytest.mark.asyncio
    async def test_clasificacion_dificultad_imposible(self) -> None:
        """Test: Nota necesaria > 7.0 se clasifica como Imposible."""
        mock_db = AsyncMock()

        curso = Curso(id=1, nombre="Test", periodo_id=1)
        eval1 = Evaluacion(
            id=1,
            curso_id=1,
            nombre="Solemne 1",
            fecha=date(2026, 3, 15),
            ponderacion_porcentaje=30.0,
            nota_obtenida=2.0,
            estado=EstadoEvaluacion.CORREGIDA,
        )
        eval2 = Evaluacion(
            id=2,
            curso_id=1,
            nombre="Solemne 2",
            fecha=date(2026, 5, 20),
            ponderacion_porcentaje=70.0,
            estado=EstadoEvaluacion.PENDIENTE,
        )
        curso.evaluaciones = [eval1, eval2]

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = curso
        mock_db.execute.return_value = mock_result

        service = CalculadoraService(db_session=mock_db)
        proyeccion = await service.calcular_proyeccion(curso_id=1, nota_objetivo=7.0)

        # Nota necesaria: (7.0*100 - 2.0*30) / 70 = 9.14 → Imposible
        estrategia_uniforme = proyeccion.estrategias[0]
        assert estrategia_uniforme.dificultad == "Imposible"

