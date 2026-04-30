"""Unit tests for CalculadoraService — no I/O required."""

import pytest

from app.application.services.calculadora_service import (
    CalculadoraService,
    ComponenteNota,
)


class TestCalculadoraService:
    """Unit tests for the predictive grade calculator."""

    def setup_method(self) -> None:
        """Set up calculator with default 3.0 passing grade."""
        self.calc = CalculadoraService(nota_aprobacion=3.0)

    def test_empty_components_returns_zero(self) -> None:
        """Empty component list should return zeroed result."""
        result = self.calc.calcular([])
        assert result.nota_actual == 0.0
        assert result.porcentaje_completado == 0.0
        assert result.puede_aprobar is True

    def test_perfect_score(self) -> None:
        """All components with max scores should yield nota_actual = 5.0."""
        componentes = [
            ComponenteNota("Parcial 1", 30.0, 5.0),
            ComponenteNota("Parcial 2", 30.0, 5.0),
            ComponenteNota("Final", 40.0, 5.0),
        ]
        result = self.calc.calcular(componentes)
        assert result.nota_actual == pytest.approx(5.0, abs=0.01)
        assert result.porcentaje_completado == 100.0
        assert result.puede_aprobar is True

    def test_failing_course(self) -> None:
        """Insufficient scores with no pending components should fail."""
        componentes = [
            ComponenteNota("Parcial 1", 50.0, 1.0),
            ComponenteNota("Final", 50.0, 1.0),
        ]
        result = self.calc.calcular(componentes)
        assert result.nota_actual < 3.0
        assert result.puede_aprobar is False

    def test_pending_components_enable_recovery(self) -> None:
        """A bad first score with pending evaluations should allow recovery."""
        componentes = [
            ComponenteNota("Parcial 1", 30.0, 2.0),  # evaluado
            ComponenteNota("Final", 70.0, None),      # pendiente
        ]
        result = self.calc.calcular(componentes)
        assert result.porcentaje_completado == 30.0
        assert result.puede_aprobar is True  # Proyección optimista >= 3.0

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
        # dias_restantes clipped to 0, luego max(1, 0) = 1
        assert priority == pytest.approx(5 * 1 / (1 + 1), abs=0.001)
