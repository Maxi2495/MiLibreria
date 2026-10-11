from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())
    estado = Column(String(20), nullable=False, default="ACTIVA")

    # Relaciones
    bibliotecas = relationship("Biblioteca", back_populates="usuario", cascade="all, delete-orphan")
    ejemplares = relationship("Ejemplar", back_populates="usuario", cascade="all, delete-orphan")
    anotaciones = relationship("Anotacion", back_populates="usuario", cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="usuario", cascade="all, delete-orphan")