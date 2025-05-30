import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Ruta de la base de datos SQLite (archivo en el directorio actual)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')

# Crear engine de SQLAlchemy (en SQLite hay que deshabilitar el "check_same_thread")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Sólo para SQLite
)

# Configurar la sesión: no commit automático, no flush automático
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()