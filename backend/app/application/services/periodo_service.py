"""Use case: Periodo management service."""

import structlog

from app.core.exceptions import NotFoundException
from app.domain.entities.periodo import PeriodoEntity
from app.infrastructure.repositories.periodo_repository import PeriodoRepository

log = structlog.get_logger(__name__)


class PeriodoService:
    """Application service for academic period management.

    Encapsulates business logic for creating, reading, updating, and
    deactivating academic periods. Owns the repository dependency.
    """

    def __init__(self, repository: PeriodoRepository) -> None:
        """Initialize with a Periodo repository instance.

        Args:
            repository: The data access object for periodos.
        """
        self._repo = repository

    async def get_all(self) -> list[PeriodoEntity]:
        """Return all periodos ordered by start date descending."""
        return await self._repo.get_all()

    async def get_by_id(self, periodo_id: int) -> PeriodoEntity:
        """Return a specific periodo or raise NotFoundException.

        Args:
            periodo_id: Primary key of the periodo.

        Returns:
            The PeriodoEntity for the given ID.

        Raises:
            NotFoundException: If no periodo with that ID exists.
        """
        periodo = await self._repo.get_by_id(periodo_id)
        if periodo is None:
            raise NotFoundException(f"Periodo con id={periodo_id} no encontrado")
        return periodo

    async def get_active(self) -> PeriodoEntity | None:
        """Return the currently active periodo, or None."""
        return await self._repo.get_active()

    async def create(
        self,
        nombre: str,
        fecha_inicio: object,
        fecha_fin: object,
        activo: bool = True,
    ) -> PeriodoEntity:
        """Create a new academic period.

        Args:
            nombre: Human-readable period name.
            fecha_inicio: Start date.
            fecha_fin: End date.
            activo: Whether this period is currently active.

        Returns:
            The created PeriodoEntity with generated ID.
        """
        entity = PeriodoEntity(
            nombre=nombre,
            fecha_inicio=fecha_inicio,  # type: ignore[arg-type]
            fecha_fin=fecha_fin,  # type: ignore[arg-type]
            activo=activo,
        )
        created = await self._repo.create(entity)
        log.info("periodo.created", id=created.id, nombre=created.nombre)
        return created

    async def update(self, periodo_id: int, **kwargs: object) -> PeriodoEntity:
        """Partially update a periodo's fields.

        Args:
            periodo_id: ID of the periodo to update.
            **kwargs: Fields to update (nombre, fecha_inicio, fecha_fin, activo).

        Returns:
            The updated PeriodoEntity.

        Raises:
            NotFoundException: If the periodo doesn't exist.
        """
        existing = await self.get_by_id(periodo_id)
        updated_entity = PeriodoEntity(
            id=existing.id,
            nombre=kwargs.get("nombre", existing.nombre),  # type: ignore[arg-type]
            fecha_inicio=kwargs.get("fecha_inicio", existing.fecha_inicio),  # type: ignore[arg-type]
            fecha_fin=kwargs.get("fecha_fin", existing.fecha_fin),  # type: ignore[arg-type]
            activo=kwargs.get("activo", existing.activo),  # type: ignore[arg-type]
        )
        result = await self._repo.update(updated_entity)
        log.info("periodo.updated", id=result.id)
        return result

    async def delete(self, periodo_id: int) -> None:
        """Delete a periodo by ID.

        Args:
            periodo_id: ID of the periodo to delete.

        Raises:
            NotFoundException: If the periodo doesn't exist.
        """
        await self.get_by_id(periodo_id)  # Validates existence
        await self._repo.delete(periodo_id)
        log.info("periodo.deleted", id=periodo_id)
