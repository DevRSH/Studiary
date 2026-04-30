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
