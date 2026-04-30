from app.infrastructure.repositories.curso_repository import CursoRepository
from app.infrastructure.models.curso import Curso
from app.application.schemas.requests.curso_schemas import CursoCreateRequest, CursoUpdateRequest
from app.core.exceptions import NotFoundException

class CursoService:
    def __init__(self, repository: CursoRepository):
        self.repository = repository
        
    async def create_curso(self, data: CursoCreateRequest) -> Curso:
        curso = Curso(**data.model_dump())
        return await self.repository.create(curso)
        
    async def get_curso(self, curso_id: int) -> Curso:
        curso = await self.repository.get_with_evaluaciones(curso_id)
        if not curso:
            raise NotFoundException(f"Curso con ID {curso_id} no encontrado")
        return curso
        
    async def update_curso(self, curso_id: int, data: CursoUpdateRequest) -> Curso:
        curso = await self.get_curso(curso_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(curso, field, value)
        return await self.repository.update(curso)
        
    async def delete_curso(self, curso_id: int) -> bool:
        return await self.repository.delete(curso_id)
