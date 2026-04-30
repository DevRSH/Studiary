"""SQLAlchemy implementation of Periodo repository."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.periodo import PeriodoEntity
from app.infrastructure.models.periodo import Periodo


class PeriodoRepository:
    """Concrete SQLAlchemy repository for Periodo persistence.

    Implements the PeriodoRepositoryProtocol using async queries.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async DB session.

        Args:
            session: The SQLAlchemy AsyncSession for this request.
        """
        self._session = session

    def _to_entity(self, model: Periodo) -> PeriodoEntity:
        """Map ORM model to domain entity."""
        return PeriodoEntity(
            id=model.id,
            nombre=model.nombre,
            fecha_inicio=model.fecha_inicio,
            fecha_fin=model.fecha_fin,
            activo=model.activo,
        )

    def _to_model(self, entity: PeriodoEntity) -> Periodo:
        """Map domain entity to ORM model (for creation)."""
        return Periodo(
            nombre=entity.nombre,
            fecha_inicio=entity.fecha_inicio,
            fecha_fin=entity.fecha_fin,
            activo=entity.activo,
        )

    async def get_by_id(self, periodo_id: int) -> PeriodoEntity | None:
        """Retrieve a Periodo by primary key."""
        result = await self._session.get(Periodo, periodo_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[PeriodoEntity]:
        """Retrieve all periodos ordered by fecha_inicio descending."""
        stmt = select(Periodo).order_by(Periodo.fecha_inicio.desc())
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars().all()]

    async def get_active(self) -> PeriodoEntity | None:
        """Retrieve the currently active periodo."""
        stmt = select(Periodo).where(Periodo.activo.is_(True)).limit(1)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: PeriodoEntity) -> PeriodoEntity:
        """Persist a new Periodo and return it with the generated ID."""
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: PeriodoEntity) -> PeriodoEntity:
        """Update an existing Periodo."""
        model = await self._session.get(Periodo, entity.id)
        if model is None:
            raise ValueError(f"Periodo with id={entity.id} not found")
        model.nombre = entity.nombre
        model.fecha_inicio = entity.fecha_inicio
        model.fecha_fin = entity.fecha_fin
        model.activo = entity.activo
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, periodo_id: int) -> None:
        """Delete a Periodo by ID."""
        model = await self._session.get(Periodo, periodo_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
