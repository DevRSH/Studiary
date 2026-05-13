"""Use case: Evaluacion management service (Sprint 1)."""

from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.requests.evaluacion_requests import (
    EvaluacionCreateRequest,
    EvaluacionNotaUpdateRequest,
    EvaluacionUpdateRequest,
)
from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.models.curso import Curso
from app.infrastructure.models.evaluacion import EstadoEvaluacion, Evaluacion
from app.infrastructure.repositories.evaluacion_repository import EvaluacionRepository


class EvaluacionService:
    """Service layer for Evaluacion management with business validations."""

    def __init__(
        self, repository: EvaluacionRepository, db_session: AsyncSession
    ) -> None:
        self.repository = repository
        self.db = db_session

    async def create_evaluacion(
        self, data: EvaluacionCreateRequest
    ) -> Evaluacion:
        """Create new evaluacion with validations.

        Validations:
        1. Curso exists
        2. Suma de ponderaciones <= 100%

        Raises:
            NotFoundException: If curso doesn't exist
            ValidationException: If validations fail
        """
        # Validar que curso existe
        result = await self.db.execute(
            select(Curso).where(Curso.id == data.curso_id)
        )
        curso = result.scalar_one_or_none()

        if not curso:
            raise NotFoundException(f"Curso {data.curso_id} no encontrado")

        # Validar suma de ponderaciones
        evaluaciones_existentes = await self.repository.get_by_curso(
            data.curso_id
        )
        suma_actual = sum(
            e.ponderacion_porcentaje for e in evaluaciones_existentes
        )
        suma_nueva = suma_actual + data.ponderacion_porcentaje

        if suma_nueva > 100:
            raise ValidationException(
                f"La suma de ponderaciones excede 100%. "
                f"Actual: {suma_actual}%, Nueva: {data.ponderacion_porcentaje}%, "
                f"Total: {suma_nueva}%"
            )

        # Crear evaluacion
        evaluacion = Evaluacion(**data.model_dump())
        return await self.repository.create(evaluacion)

    async def get_evaluacion(self, evaluacion_id: int) -> Evaluacion:
        """Get evaluacion by ID."""
        evaluacion = await self.repository.get_by_id(evaluacion_id)
        if not evaluacion:
            raise NotFoundException(
                f"Evaluación {evaluacion_id} no encontrada"
            )
        return evaluacion

    async def get_by_curso(self, curso_id: int) -> Sequence[Evaluacion]:
        """Get all evaluaciones for a curso."""
        return await self.repository.get_by_curso(curso_id)

    async def update_evaluacion(
        self, evaluacion_id: int, data: EvaluacionUpdateRequest
    ) -> Evaluacion:
        """Update evaluacion with ponderacion validation."""
        evaluacion = await self.get_evaluacion(evaluacion_id)

        # Si se actualiza ponderacion, validar suma
        if data.ponderacion_porcentaje is not None:
            evaluaciones_curso = await self.repository.get_by_curso(
                evaluacion.curso_id
            )
            suma_otras = sum(
                e.ponderacion_porcentaje
                for e in evaluaciones_curso
                if e.id != evaluacion_id
            )
            suma_nueva = suma_otras + data.ponderacion_porcentaje

            if suma_nueva > 100:
                raise ValidationException(
                    f"La suma de ponderaciones excede 100%. Total: {suma_nueva}%"
                )

        # Actualizar campos
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(evaluacion, field, value)

        return await self.repository.update(evaluacion)

    async def update_nota(
        self, evaluacion_id: int, data: EvaluacionNotaUpdateRequest
    ) -> Evaluacion:
        """Update nota_obtenida and change estado to CORREGIDA.

        Validates that nota is within [nota_minima, nota_maxima].
        """
        evaluacion = await self.get_evaluacion(evaluacion_id)

        # Validar rango de nota
        if not (
            evaluacion.nota_minima
            <= data.nota_obtenida
            <= evaluacion.nota_maxima
        ):
            raise ValidationException(
                f"Nota {data.nota_obtenida} fuera de rango "
                f"[{evaluacion.nota_minima}, {evaluacion.nota_maxima}]"
            )

        # Actualizar nota y estado
        evaluacion.nota_obtenida = data.nota_obtenida
        evaluacion.estado = EstadoEvaluacion.CORREGIDA

        return await self.repository.update(evaluacion)

    async def delete_evaluacion(self, evaluacion_id: int) -> bool:
        """Delete evaluacion by ID."""
        return await self.repository.delete(evaluacion_id)
