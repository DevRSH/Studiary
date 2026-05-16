from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Health check endpoint for Railway.
    
    Verifies:
    - API is responding
    - Database connection works
    """
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
