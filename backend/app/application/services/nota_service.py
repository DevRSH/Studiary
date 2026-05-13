"""Use case: Nota management service."""

from typing import Sequence

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.infrastructure.models.nota import Dibujo, Nota, Tag
from app.application.schemas.requests.nota_requests import NotaCreateRequest, NotaUpdateRequest

log = structlog.get_logger(__name__)


class NotaService:
    """Service for managing notes with drawings and tags."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session

    async def create_nota(self, data: NotaCreateRequest) -> Nota:
        """Create note with optional drawings and tags."""
        # Create base nota
        nota = Nota(
            tema_id=data.tema_id,
            titulo=data.titulo,
            contenido_markdown=data.contenido_markdown,
            tipo=data.tipo,
        )
        self.db.add(nota)
        await self.db.flush()  # Get nota.id

        # Associate tags
        if data.tag_ids:
            result = await self.db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
            tags = result.scalars().all()
            nota.tags = list(tags)

        # Create dibujos
        for dibujo_data in data.dibujos:
            dibujo = Dibujo(
                nota_id=nota.id,
                canvas_json=dibujo_data.canvas_json,
                thumbnail_base64=dibujo_data.thumbnail_base64,
                orden=dibujo_data.orden,
            )
            self.db.add(dibujo)

        await self.db.flush()
        await self.db.refresh(nota, ["dibujos", "tags"])

        log.info("nota_created", nota_id=nota.id, titulo=nota.titulo)
        return nota

    async def get_nota(self, nota_id: int) -> Nota:
        """Get nota by ID with relations."""
        result = await self.db.execute(
            select(Nota)
            .where(Nota.id == nota_id)
            .options(selectinload(Nota.dibujos), selectinload(Nota.tags))
        )
        nota = result.scalar_one_or_none()

        if nota is None:
            raise NotFoundException(f"Nota {nota_id} no encontrada")

        return nota

    async def get_by_tema(self, tema_id: int) -> Sequence[Nota]:
        """Get all notas for a tema."""
        result = await self.db.execute(
            select(Nota)
            .where(Nota.tema_id == tema_id)
            .options(selectinload(Nota.tags))
            .order_by(Nota.updated_at.desc())
        )
        return result.scalars().all()

    async def update_nota(self, nota_id: int, data: NotaUpdateRequest) -> Nota:
        """Update nota fields and tags."""
        nota = await self.get_nota(nota_id)

        # Update basic fields
        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        for field, value in update_data.items():
            setattr(nota, field, value)

        # Update tags if provided
        if data.tag_ids is not None:
            result = await self.db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
            tags = result.scalars().all()
            nota.tags = list(tags)

        await self.db.flush()
        await self.db.refresh(nota, ["dibujos", "tags"])

        log.info("nota_updated", nota_id=nota_id)
        return nota

    async def delete_nota(self, nota_id: int) -> bool:
        """Delete nota (cascade deletes dibujos)."""
        nota = await self.db.get(Nota, nota_id)
        if nota:
            await self.db.delete(nota)
            await self.db.flush()
            log.info("nota_deleted", nota_id=nota_id)
            return True
        return False

    async def add_dibujo(
        self,
        nota_id: int,
        canvas_json: str,
        thumbnail_base64: str | None = None,
    ) -> Dibujo:
        """Add drawing to existing nota."""
        nota = await self.get_nota(nota_id)

        # Get max orden
        max_orden = max((d.orden for d in nota.dibujos), default=-1)

        dibujo = Dibujo(
            nota_id=nota_id,
            canvas_json=canvas_json,
            thumbnail_base64=thumbnail_base64,
            orden=max_orden + 1,
        )
        self.db.add(dibujo)
        await self.db.flush()
        await self.db.refresh(dibujo)

        log.info("dibujo_added", dibujo_id=dibujo.id, nota_id=nota_id)
        return dibujo

    async def search_notas(self, query: str) -> Sequence[Nota]:
        """Search notas by titulo or contenido_markdown."""
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(Nota)
            .where(
                (Nota.titulo.ilike(search_pattern))
                | (Nota.contenido_markdown.ilike(search_pattern))
            )
            .options(selectinload(Nota.tags))
            .order_by(Nota.updated_at.desc())
            .limit(50)
        )
        return result.scalars().all()
