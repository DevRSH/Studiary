"""Abstract repository interfaces — Domain layer contracts.

Estos protocolos definen el contrato que la capa de infraestructura
debe implementar. La capa de aplicación solo conoce estas interfaces.
"""

from typing import Protocol

from app.domain.entities.periodo import PeriodoEntity
from app.domain.entities.curso import CursoEntity


class PeriodoRepositoryProtocol(Protocol):
    """Abstract interface for periodo persistence operations."""

    async def get_by_id(self, periodo_id: int) -> PeriodoEntity | None:
        """Retrieve a periodo by its primary key."""
        ...

    async def get_all(self) -> list[PeriodoEntity]:
        """Retrieve all periodos ordered by fecha_inicio descending."""
        ...

    async def get_active(self) -> PeriodoEntity | None:
        """Retrieve the currently active periodo."""
        ...

    async def create(self, entity: PeriodoEntity) -> PeriodoEntity:
        """Persist a new periodo and return it with generated ID."""
        ...

    async def update(self, entity: PeriodoEntity) -> PeriodoEntity:
        """Update an existing periodo."""
        ...

    async def delete(self, periodo_id: int) -> None:
        """Delete a periodo by ID."""
        ...


class CursoRepositoryProtocol(Protocol):
    """Abstract interface for curso persistence operations."""

    async def get_by_id(self, curso_id: int) -> CursoEntity | None:
        """Retrieve a curso by its primary key."""
        ...

    async def get_by_periodo(self, periodo_id: int) -> list[CursoEntity]:
        """Retrieve all cursos for a given periodo."""
        ...

    async def create(self, entity: CursoEntity) -> CursoEntity:
        """Persist a new curso and return it with generated ID."""
        ...

    async def update(self, entity: CursoEntity) -> CursoEntity:
        """Update an existing curso."""
        ...

    async def delete(self, curso_id: int) -> None:
        """Delete a curso by ID."""
        ...
