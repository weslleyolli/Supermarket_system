"""
Configuração da conexão com banco de dados
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {},
    echo=settings.DEBUG,  # Log SQL queries em desenvolvimento
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_database_url():
    """
    Retorna a URL do banco de dados
    """
    return settings.DATABASE_URL


def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Cria todas as tabelas no banco de dados
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Remove todas as tabelas do banco de dados
    """
    Base.metadata.drop_all(bind=engine)
