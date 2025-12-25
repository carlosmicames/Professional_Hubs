"""
Configuración de la base de datos SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Motor de base de datos
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=5,  # Conexiones en el pool
    max_overflow=10,  # Conexiones adicionales permitidas
    echo=settings.debug  # Log de SQL queries en modo debug
)

# Factory de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para modelos ORM
Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos para FastAPI.
    Cierra automáticamente la sesión al terminar.

    Uso:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
