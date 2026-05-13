from app.application.schemas.requests.curso_requests import (
    CursoCreateRequest,
    CursoUpdateRequest,
)
from app.core.exceptions import NotFoundException
from app.domain.entities.curso import CursoEntity
from app.infrastructure.models.curso import Curso
from app.infrastructure.repositories.curso_repository import CursoRepository


class CursoService:
    """Service layer for Curso management returning domain entities."""

    def __init__(self, repository: CursoRepository):
        self.repository = repository

    async def create_curso(self, data: CursoCreateRequest) -> CursoEntity:
        """Create new curso and return domain entity."""
        curso = Curso(**data.model_dump())
        created_model = await self.repository.create(curso)
        return self.repository._to_entity(created_model)

    async def get_curso(self, curso_id: int) -> Curso:
        """
        Get curso by ID with evaluaciones.

        Returns ORM model because endpoint needs to serialize evaluaciones.
        """
        curso = await self.repository.get_with_evaluaciones(curso_id)
        if not curso:
            raise NotFoundException(f"Curso con ID {curso_id} no encontrado")
        return curso

    async def get_curso_entity(self, curso_id: int) -> CursoEntity:
        """Get curso by ID as domain entity (without relations)."""
        entity = await self.repository.get_entity_by_id(curso_id)
        if not entity:
            raise NotFoundException(f"Curso con ID {curso_id} no encontrado")
        return entity

    async def update_curso(
        self, curso_id: int, data: CursoUpdateRequest
    ) -> CursoEntity:
        """Update curso and return domain entity."""
        # Get ORM model to update
        curso = await self.repository.get_by_id(curso_id)
        if not curso:
            raise NotFoundException(f"Curso con ID {curso_id} no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(curso, field, value)

        updated_model = await self.repository.update(curso)
        return self.repository._to_entity(updated_model)

    async def delete_curso(self, curso_id: int) -> bool:
        """Delete curso by ID."""
        return await self.repository.delete(curso_id)
