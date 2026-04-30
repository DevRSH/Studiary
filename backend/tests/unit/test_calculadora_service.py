"""Unit tests for CalculadoraService — mocking DB where necessary."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.services.calculadora_service import CalculadoraService
from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import Evaluacion, EstadoEvaluacion

class TestCalculadoraService:
    """Unit tests for the predictive grade calculator."""

    def setup_method(self) -> None:
        """Set up calculator."""
        self.calc = CalculadoraService()

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
            estado=EstadoEvaluacion.CORREGIDA
        )
        e2 = Evaluacion(
            nombre="Final", 
            ponderacion_porcentaje=70.0, 
            estado=EstadoEvaluacion.PENDIENTE
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
        assert res.estrategias[0].distribuciones[0]["nota_necesaria"] == pytest.approx(5.43, abs=0.01)

