from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Sequence
from app.domain.repositories.base_repository import BaseRepository
from app.infrastructure.models.curso import Curso

class CursoRepository(BaseRepository[Curso]):
    """Concrete repository for Curso with eager loading strategies."""
    
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
