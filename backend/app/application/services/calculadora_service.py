"""Use case: Calculadora de notas predictiva.

Implementa el motor de cálculo de notas ponderadas y proyección
de nota necesaria para aprobar el curso.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ComponenteNota:
    """Componente de evaluación con su porcentaje y nota obtenida."""

    nombre: str
    porcentaje: float  # 0–100
    nota_obtenida: float | None  # None si aún no se ha evaluado
    nota_maxima: float = 5.0


@dataclass(frozen=True)
class ResultadoCalculadora:
    """Resultado del cálculo predictivo de notas.

    Attributes:
        nota_actual: Nota acumulada con los componentes ya evaluados.
        nota_proyectada: Proyección si el estudiante saca nota_maxima en los restantes.
        nota_minima_necesaria: Nota que debe sacar en lo que queda para aprobar.
        porcentaje_completado: Porcentaje del curso ya evaluado.
        puede_aprobar: Indica si matemáticamente aún es posible aprobar.
        nota_aprobacion: Nota mínima de aprobación configurada.
    """

    nota_actual: float
    nota_proyectada: float
    nota_minima_necesaria: float | None
    porcentaje_completado: float
    puede_aprobar: bool
    nota_aprobacion: float


class CalculadoraService:
    """Predictive grade calculator service.

    Calcula notas ponderadas y proyecta la nota necesaria para aprobar,
    siendo el núcleo del motor predictivo de Studiary.
    """

    def __init__(self, nota_aprobacion: float = 3.0) -> None:
        """Initialize with the minimum passing grade.

        Args:
            nota_aprobacion: Minimum grade to pass the course (default 3.0/5.0).
        """
        self._nota_aprobacion = nota_aprobacion

    def calcular(self, componentes: list[ComponenteNota]) -> ResultadoCalculadora:
        """Calculate the current weighted grade and projections.

        Args:
            componentes: List of grade components with their weights and scores.

        Returns:
            A ResultadoCalculadora with all computed metrics.
        """
        if not componentes:
            return ResultadoCalculadora(
                nota_actual=0.0,
                nota_proyectada=0.0,
                nota_minima_necesaria=None,
                porcentaje_completado=0.0,
                puede_aprobar=True,
                nota_aprobacion=self._nota_aprobacion,
            )

        porcentaje_completado = sum(
            c.porcentaje for c in componentes if c.nota_obtenida is not None
        )
        porcentaje_pendiente = 100.0 - porcentaje_completado

        # Nota actual: suma ponderada de componentes evaluados
        nota_actual = sum(
            (c.nota_obtenida / c.nota_maxima * 5.0) * (c.porcentaje / 100.0)
            for c in componentes
            if c.nota_obtenida is not None
        )

        # Proyección optimista: el estudiante saca nota máxima en los pendientes
        nota_proyectada = nota_actual + (porcentaje_pendiente / 100.0) * 5.0

        # Nota mínima necesaria en los componentes restantes para aprobar
        nota_minima_necesaria: float | None = None
        if porcentaje_pendiente > 0:
            puntos_necesarios = self._nota_aprobacion - nota_actual
            nota_minima_necesaria = min(
                5.0,
                max(0.0, (puntos_necesarios / (porcentaje_pendiente / 100.0))),
            )
        puede_aprobar = nota_proyectada >= self._nota_aprobacion

        return ResultadoCalculadora(
            nota_actual=round(nota_actual, 2),
            nota_proyectada=round(nota_proyectada, 2),
            nota_minima_necesaria=(
                round(nota_minima_necesaria, 2) if nota_minima_necesaria is not None else None
            ),
            porcentaje_completado=round(porcentaje_completado, 2),
            puede_aprobar=puede_aprobar,
            nota_aprobacion=self._nota_aprobacion,
        )

    def calcular_prioridad_tarea(
        self, peso: int, dias_restantes: int, tiempo_estimado_horas: float
    ) -> float:
        """Calculate task priority using formula P = W * D / (T + 1).

        Args:
            peso: Perceived difficulty/importance (W, 1-10).
            dias_restantes: Days remaining until deadline (D).
            tiempo_estimado_horas: Estimated completion time in hours (T).

        Returns:
            Priority score (higher = more urgent).
        """
        if dias_restantes < 0:
            dias_restantes = 0  # Tarea vencida tiene prioridad máxima
        return (peso * max(1, dias_restantes)) / (tiempo_estimado_horas + 1)
