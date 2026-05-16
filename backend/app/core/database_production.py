"""Production database configuration with optimizations."""
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.database import engine


def configure_sqlite_production():
    """Configure SQLite for production use."""
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Set SQLite PRAGMAs for performance and reliability."""
        cursor = dbapi_conn.cursor()
        
        # WAL mode (Write-Ahead Logging) para mejor concurrencia
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Synchronous mode NORMAL (balance entre performance y seguridad)
        cursor.execute("PRAGMA synchronous=NORMAL")
        
        # Cache size (10MB)
        cursor.execute("PRAGMA cache_size=-10000")
        
        # Foreign keys enforcement
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # Temp store en memoria
        cursor.execute("PRAGMA temp_store=MEMORY")
        
        # Busy timeout (5 segundos)
        cursor.execute("PRAGMA busy_timeout=5000")
        
        cursor.close()


# Aplicar configuración al importar
configure_sqlite_production()
