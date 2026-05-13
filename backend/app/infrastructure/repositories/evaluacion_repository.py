"""Repository for Evaluacion with business queries."""

from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.repositories.base_repository import BaseRepository
from app.infrastructure.models.evaluacion import Evaluacion, EstadoEvaluacion


class EvaluacionRepository(BaseRepository[Evaluacion]):
    """Repository for Evaluacion with business queries."""

    async def get_by_curso(self, curso_id: int) -> Sequence[Evaluacion]:
        """Get all evaluaciones for a curso, ordered by fecha."""
        result = await self.session.execute(
            select(Evaluacion)
            .where(Evaluacion.curso_id == curso_id)
            .order_by(Evaluacion.fecha)
        )
        return result.scalars().all()

    async def get_pendientes_by_curso(self, curso_id: int) -> Sequence[Evaluacion]:
        """Get only pending evaluaciones for a curso."""
        result = await self.session.execute(
            select(Evaluacion)
            .where(
                Evaluacion.curso_id == curso_id,
                Evaluacion.estado == EstadoEvaluacion.PENDIENTE,
            )
            .order_by(Evaluacion.fecha)
        )
        return result.scalars().all()

    async def get_proximas(
        self, fecha_desde: date, fecha_hasta: date
    ) -> Sequence[Evaluacion]:
        """Get evaluaciones in date range."""
        result = await self.session.execute(
            select(Evaluacion)
            .where(
                Evaluacion.fecha >= fecha_desde, Evaluacion.fecha <= fecha_hasta
            )
            .order_by(Evaluacion.fecha)
            .options(selectinload(Evaluacion.curso))
        )
        return result.scalars().all()
