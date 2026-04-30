# SPRINT 1: DOMAIN MODELS & BASIC CRUD

## 1. Objetivo de Ejecución
Implementar el dominio core de Studiary (Periodos, Cursos, Evaluaciones) estableciendo las operaciones CRUD completas. Esto requiere la materialización de los modelos ORM, esquemas de validación, lógica de repositorios/servicios, y la exposición de los endpoints RESTful. Se debe incluir testing unitario y el cliente asíncrono para el frontend.

## 2. Entregables Esperados
1.  Modelos SQLAlchemy 2.0 (Periodo, Curso, Evaluacion) mapeados a SQLite (WAL).
2.  Esquemas Pydantic v2 (Requests/Responses) con validación estricta de *inputs*.
3.  Implementación del patrón *Repository* (Base e implementaciones concretas).
4.  Capa de Servicios (*Business Logic*) con manejo de excepciones custom (`StudiaryError`).
5.  Endpoints API RESTful asíncronos (`/api/v1/cursos`, etc.) con inyección de dependencias.
6.  Migración autogenerada mediante Alembic.
7.  Tests unitarios y de integración (Target: >80% de cobertura en la capa de servicios).
8.  Frontend: Tipos estáticos, cliente Axios y hooks de TanStack Query para el consumo de la API.

## 3. Tareas de Implementación Backend

### Tarea 3.1: SQLAlchemy Models
Crear los modelos ORM en `backend/app/infrastructure/models/`.

**`periodo.py`**:
```python
from sqlalchemy import String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Periodo(BaseModel):
    """Academic period model (e.g., "Semestre 3 2026")."""
    __tablename__ = "periodos"
    
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    fecha_inicio: Mapped[Date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Date] = mapped_column(Date, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    cursos: Mapped[list["Curso"]] = relationship(
        "Curso",
        back_populates="periodo",
        cascade="all, delete-orphan"
    )
curso.py:

Python
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Curso(BaseModel):
    """Course model mapped to an academic period."""
    __tablename__ = "cursos"
    
    periodo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("periodos.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6", nullable=False)
    creditos: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    
    # Relationships
    periodo: Mapped["Periodo"] = relationship("Periodo", back_populates="cursos")
    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        "Evaluacion",
        back_populates="curso",
        cascade="all, delete-orphan"
    )
evaluacion.py:

Python
from datetime import date
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class EstadoEvaluacion(str, PyEnum):
    PENDIENTE = "pendiente"
    RENDIDA = "rendida"
    CORREGIDA = "corregida"

class Evaluacion(BaseModel):
    """Assessment model with strict type constraints."""
    __tablename__ = "evaluaciones"
    
    curso_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cursos.id", ondelete="CASCADE"),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="solemne", nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    ponderacion_porcentaje: Mapped[float] = mapped_column(Float, nullable=False)
    nota_obtenida: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_minima: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    nota_maxima: Mapped[float] = mapped_column(Float, default=7.0, nullable=False)
    estado: Mapped[EstadoEvaluacion] = mapped_column(
        Enum(EstadoEvaluacion),
        default=EstadoEvaluacion.PENDIENTE,
        nullable=False
    )
    
    # Relationships
    curso: Mapped["Curso"] = relationship("Curso", back_populates="evaluaciones")
(Nota para el Agente: Actualizar backend/app/infrastructure/models/__init__.py para exportar explícitamente estas clases y asegurar que Alembic las detecte en el autogenerate).

Tarea 3.2: Capa de Acceso a Datos (Repository Pattern)
Crear las abstracciones en backend/app/domain/repositories/ y las implementaciones en backend/app/infrastructure/repositories/.

domain/repositories/base_repository.py:

Python
from abc import ABC
from typing import Generic, TypeVar, Type, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository executing async ORM operations."""
    
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session
        
    async def get_by_id(self, id: int) -> Optional[T]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()
        
    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
        
    async def update(self, entity: T) -> T:
        merged_entity = await self.session.merge(entity)
        await self.session.flush()
        await self.session.refresh(merged_entity)
        return merged_entity
        
    async def delete(self, id: int) -> bool:
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False
infrastructure/repositories/curso_repository.py:

Python
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
Tarea 3.3: Data Transfer Objects (Pydantic Schemas)
Crear los esquemas de validación en backend/app/application/schemas/requests/ y responses/.

requests/curso_schemas.py:

Python
from pydantic import BaseModel, Field, field_validator

class CursoCreateRequest(BaseModel):
    periodo_id: int = Field(..., gt=0, description="ID del periodo académico")
    nombre: str = Field(..., min_length=1, max_length=200)
    codigo: str | None = Field(None, max_length=20)
    color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    creditos: int = Field(4, ge=1, le=10)
    
    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

class CursoUpdateRequest(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=200)
    codigo: str | None = Field(None, max_length=20)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    creditos: int | None = Field(None, ge=1, le=10)
responses/curso_schemas.py:

Python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    periodo_id: int
    nombre: str
    codigo: str | None
    color: str
    creditos: int
    created_at: datetime
    updated_at: datetime

class CursoDetailResponse(CursoResponse):
    evaluaciones: list = [] # To be strongly typed once EvaluacionResponse is built
    promedio_actual: float | None = None
Tarea 3.4: Business Logic (Services)
Crear el servicio de orquestación en backend/app/application/services/curso_service.py.

Python
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
Tarea 3.5: API Endpoints (Presentation)
Exponer la lógica a través del router en backend/app/presentation/api/v1/endpoints/cursos.py.

Python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.infrastructure.repositories.curso_repository import CursoRepository
from app.application.services.curso_service import CursoService
from app.application.schemas.requests.curso_schemas import CursoCreateRequest, CursoUpdateRequest
from app.application.schemas.responses.curso_schemas import CursoResponse, CursoDetailResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/cursos", tags=["cursos"])

def get_curso_service(db: AsyncSession = Depends(get_db)) -> CursoService:
    repository = CursoRepository(model=Curso, session=db)
    return CursoService(repository)

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def create_curso(
    data: CursoCreateRequest,
    service: CursoService = Depends(get_curso_service)
) -> CursoResponse:
    curso = await service.create_curso(data)
    return CursoResponse.model_validate(curso)

@router.get("/{curso_id}", response_model=CursoDetailResponse)
async def get_curso(
    curso_id: int,
    service: CursoService = Depends(get_curso_service)
) -> CursoDetailResponse:
    curso = await service.get_curso(curso_id)
    return CursoDetailResponse.model_validate(curso)

@router.put("/{curso_id}", response_model=CursoResponse)
async def update_curso(
    curso_id: int,
    data: CursoUpdateRequest,
    service: CursoService = Depends(get_curso_service)
) -> CursoResponse:
    curso = await service.update_curso(curso_id, data)
    return CursoResponse.model_validate(curso)

@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(
    curso_id: int,
    service: CursoService = Depends(get_curso_service)
) -> None:
    deleted = await service.delete_curso(curso_id)
    if not deleted:
        raise NotFoundException(f"Curso {curso_id} no encontrado")
4. Tareas de Implementación Frontend
Implementar en el directorio /frontend/src/features/cursos/:

types/index.ts:

TypeScript
export interface Curso {
  id: number;
  periodo_id: number;
  nombre: string;
  codigo: string | null;
  color: string;
  creditos: number;
  created_at: string;
  updated_at: string;
}

export interface CursoCreateRequest {
  periodo_id: number;
  nombre: string;
  codigo?: string;
  color?: string;
  creditos?: number;
}

export type CursoUpdateRequest = Partial<CursoCreateRequest>;
api/cursoApi.ts:

TypeScript
import { apiClient } from '@/shared/api/client';
import type { Curso, CursoCreateRequest, CursoUpdateRequest } from '../types';

export const cursoApi = {
  getAll: async (): Promise<Curso[]> => {
    const { data } = await apiClient.get<Curso[]>('/cursos');
    return data;
  },
  getById: async (id: number): Promise<Curso> => {
    const { data } = await apiClient.get<Curso>(`/cursos/${id}`);
    return data;
  },
  create: async (curso: CursoCreateRequest): Promise<Curso> => {
    const { data } = await apiClient.post<Curso>('/cursos', curso);
    return data;
  },
  update: async (id: number, updates: CursoUpdateRequest): Promise<Curso> => {
    const { data } = await apiClient.put<Curso>(`/cursos/${id}`, updates);
    return data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/cursos/${id}`);
  },
};
hooks/useCursos.ts:

TypeScript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cursoApi } from '../api/cursoApi';
import type { CursoCreateRequest, CursoUpdateRequest } from '../types';

export const useCursos = () => {
  return useQuery({
    queryKey: ['cursos'],
    queryFn: cursoApi.getAll,
  });
};

export const useCurso = (id: number) => {
  return useQuery({
    queryKey: ['cursos', id],
    queryFn: () => cursoApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateCurso = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CursoCreateRequest) => cursoApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cursos'] });
    },
  });
};
5. Tareas de Testing & Migración
backend/tests/unit/services/test_curso_service.py:

Python
import pytest
from unittest.mock import AsyncMock
from app.application.services.curso_service import CursoService
from app.infrastructure.models.curso import Curso
from app.application.schemas.requests.curso_schemas import CursoCreateRequest

@pytest.mark.asyncio
async def test_create_curso_success():
    mock_repo = AsyncMock()
    service = CursoService(repository=mock_repo)
    
    request_data = CursoCreateRequest(
        periodo_id=1,
        nombre="Ciberseguridad",
        codigo="CSEC301",
        creditos=4
    )
    
    expected_curso = Curso(id=1, **request_data.model_dump())
    mock_repo.create.return_value = expected_curso
    
    result = await service.create_curso(request_data)
    
    assert result.id == 1
    assert result.nombre == "Ciberseguridad"
    mock_repo.create.assert_called_once()
(Nota para el Agente: Autogenerar la migración ejecutando alembic revision --autogenerate -m "Add core domain models" en la consola después de estructurar los archivos).

6. Criterios de Validación (Checklist del Agente)
[ ] Relaciones ORM y lógicas delete-orphan configuradas correctamente.

[ ] Mapeos Pydantic v2 configurados con from_attributes=True.

[ ] Resolución de referencias circulares mediante importaciones tipadas estáticas.

[ ] Integración en el router principal api/v1/__init__.py.

[ ] Los tests de los servicios (pytest) pasan con éxito la validación asíncrona.

[ ] Estructura Frontend compilando sin violaciones a reglas estrictas de TypeScript (tsc --noEmit).

Instrucción Final: Genera la implementación de código y los archivos solicitados en sus rutas exactas. Limita las respuestas explicativas; enfócate en la ejecución técnica y en los comandos de consola requeridos para levantar las migraciones de Alembic.