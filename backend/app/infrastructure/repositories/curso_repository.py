from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Sequence

from app.domain.entities.curso import CursoEntity
from app.domain.repositories.base_repository import BaseRepository
from app.infrastructure.models.curso import Curso


class CursoRepository(BaseRepository[Curso]):
    """Concrete repository for Curso with domain entity mapping."""

    def _to_entity(self, model: Curso) -> CursoEntity:
        """Map ORM model to domain entity."""
        return CursoEntity(
            id=model.id,
            periodo_id=model.periodo_id,
            nombre=model.nombre,
            codigo=model.codigo or "",
            color=model.color,
            creditos=model.creditos,
            docente=model.docente,
        )

    async def get_by_periodo(self, periodo_id: int) -> Sequence[Curso]:
        result = await self.session.execute(
            select(Curso)
            .where(Curso.periodo_id == periodo_id)
            .options(selectinload(Curso.evaluaciones))
        )
        return result.scalars().all()

    async def get_with_evaluaciones(self, id: int) -> Curso | None:
        result = await self.session.execute(
            select(Curso)
            .where(Curso.id == id)
            .options(selectinload(Curso.evaluaciones))
        )
        return result.scalar_one_or_none()

    async def get_entity_by_id(self, id: int) -> CursoEntity | None:
        """Get curso by ID as domain entity."""
        model = await self.get_by_id(id)
        return self._to_entity(model) if model else None
