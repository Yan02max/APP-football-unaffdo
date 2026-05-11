"""Configuración de conexión SQLAlchemy con SQLite."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///unaffdo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_session():
    """Retorna una sesión de BD. Usar con 'with' o cerrar manualmente."""
    return SessionLocal()