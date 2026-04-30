from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import EstadoEvaluacion, Evaluacion


@dataclass
class EstrategiaDistribucion:
    """Representa una estrategia de distribución de notas."""

    nombre: str
    descripcion: str
    distribuciones: list[dict[str, Any]]
    dificultad: str


@dataclass
class ProyeccionNotas:
    """Resultado de la proyección de notas para un curso."""

    curso_id: int
    nota_objetivo: float
    nota_actual: float
    ponderacion_usada: float
    ponderacion_restante: float
    es_factible: bool
    margen_error: float
    estrategias: list[EstrategiaDistribucion]


class CalculadoraService:
    """Predictive grade calculator and task priority service."""

    def __init__(self, db_session: AsyncSession | None = None) -> None:
        """Inicializa el servicio con una sesión de DB opcional."""
        self.db = db_session

    async def calcular_proyeccion(self, curso_id: int, nota_objetivo: float) -> ProyeccionNotas:
        """Calcula la proyección de notas necesaria para alcanzar un objetivo académico."""
        if not (1.0 <= nota_objetivo <= 7.0):
            raise ValidationException(f"Nota objetivo {nota_objetivo} fuera de rango [1.0, 7.0]")

        if not self.db:
            raise ValidationException("Database session required for projections")

        result = await self.db.execute(
            select(Curso).where(Curso.id == curso_id).options(selectinload(Curso.evaluaciones))
        )
        curso = result.scalar_one_or_none()

        if not curso:
            raise NotFoundException(f"Curso {curso_id} no encontrado")
        if not curso.evaluaciones:
            raise ValidationException(f"Curso '{curso.nombre}' sin evaluaciones")

        rendidas = [
            e
            for e in curso.evaluaciones
            if e.estado == EstadoEvaluacion.CORREGIDA and e.nota_obtenida is not None
        ]
        pendientes = [e for e in curso.evaluaciones if e.estado == EstadoEvaluacion.PENDIENTE]

        suma_ponderada = sum(e.nota_obtenida * e.ponderacion_porcentaje for e in rendidas)
        pond_usada = sum(e.ponderacion_porcentaje for e in rendidas)
        pond_restante = sum(e.ponderacion_porcentaje for e in pendientes)

        nota_actual = suma_ponderada / pond_usada if pond_usada > 0 else 0.0

        if not pendientes or pond_restante <= 0:
            return ProyeccionNotas(
                curso_id=curso_id,
                nota_objetivo=nota_objetivo,
                nota_actual=nota_actual,
                ponderacion_usada=pond_usada,
                ponderacion_restante=pond_restante,
                es_factible=nota_actual >= nota_objetivo,
                margen_error=0.0,
                estrategias=[],
            )

        # Cálculo de nota necesaria: (Objetivo * 100 - Actual * pond_usada) / pond_restante
        # Nota: Asumimos que las ponderaciones suman 100%.
        nota_promedio_necesaria = ((nota_objetivo * 100) - suma_ponderada) / pond_restante
        estrategias = self._generar_estrategias(pendientes, nota_promedio_necesaria)

        return ProyeccionNotas(
            curso_id=curso_id,
            nota_objetivo=nota_objetivo,
            nota_actual=nota_actual,
            ponderacion_usada=pond_usada,
            ponderacion_restante=pond_restante,
            es_factible=1.0 <= nota_promedio_necesaria <= 7.0,
            margen_error=nota_promedio_necesaria - 4.0,
            estrategias=estrategias,
        )

    def _generar_estrategias(
        self, pendientes: list[Evaluacion], nota_req: float
    ) -> list[EstrategiaDistribucion]:
        """Genera diferentes estrategias para alcanzar la nota requerida."""
        # Estrategia 1: Uniforme
        uniforme = EstrategiaDistribucion(
            nombre="Uniforme",
            descripcion=f"Mantener promedio de {nota_req:.2f}",
            distribuciones=[
                {
                    "evaluacion": e.nombre,
                    "nota_necesaria": round(nota_req, 2),
                    "ponderacion": e.ponderacion_porcentaje,
                }
                for e in pendientes
            ],
            dificultad=self._clasificar_dificultad(nota_req),
        )
        # Estrategia 2: Realista (con margen)
        nota_m = nota_req + 0.5
        realista = EstrategiaDistribucion(
            nombre="Realista con margen",
            descripcion="Apuntar a +0.5 para seguridad",
            distribuciones=[
                {
                    "evaluacion": e.nombre,
                    "nota_necesaria": round(min(nota_m, 7.0), 2),
                    "ponderacion": e.ponderacion_porcentaje,
                }
                for e in pendientes
            ],
            dificultad=self._clasificar_dificultad(nota_m),
        )
        return [uniforme, realista]

    def _clasificar_dificultad(self, nota: float) -> str:
        """Clasifica la dificultad según la nota requerida."""
        if nota > 7.0:
            return "Imposible"
        if nota >= 6.0:
            return "Muy Difícil"
        if nota >= 5.0:
            return "Difícil"
        return "Moderado" if nota >= 4.0 else "Fácil"

    def calcular_prioridad_tarea(
        self, peso: int, dias_restantes: int, tiempo_estimado_horas: float
    ) -> float:
        """Calcula la prioridad de una tarea usando la fórmula P = W * D / (T + 1)."""
        d_val = max(1, dias_restantes) if dias_restantes >= 0 else 1
        return (peso * d_val) / (tiempo_estimado_horas + 1)


