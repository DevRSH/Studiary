#!/usr/bin/env python3
"""Test script to diagnose curso creation error"""

import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from app.core.database import AsyncSessionLocal
    from app.application.services.curso_service import CursoService
    from app.infrastructure.repositories.curso_repository import CursoRepository
    from app.infrastructure.models.curso import Curso
    from app.application.schemas.requests.curso_requests import CursoCreateRequest
    
    async with AsyncSessionLocal() as session:
        try:
            repo = CursoRepository(model=Curso, session=session)
            service = CursoService(repository=repo)
            
            data = CursoCreateRequest(
                periodo_id=1,
                nombre="Test",
                codigo="TST",
                creditos=4
            )
            
            print(f"Creating curso with data: {data.model_dump()}")
            result = await service.create_curso(data)
            print(f"✓ Success! Created: {result}")
            
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
