from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Biblioteca(Base):
    __tablename__ = "biblioteca"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)

    usuario = relationship("Usuario", back_populates="bibliotecas")
    estantes = relationship("Estante", back_populates="biblioteca", cascade="all, delete-orphan")

class Estante(Base):
    __tablename__ = "estante"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    biblioteca_id = Column(BigInteger, ForeignKey("biblioteca.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    capacidad = Column(Integer, nullable=False)

    biblioteca = relationship("Biblioteca", back_populates="estantes")
    ejemplares = relationship("Ejemplar", back_populates="estante")