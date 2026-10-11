from sqlalchemy import Column, BigInteger, String, Date, Text, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.session import Base

# Tabla asociativa N:M Libro <-> Autor
libro_autor = Table(
    "libro_autor",
    Base.metadata,
    Column("libro_id", BigInteger, ForeignKey("libro.id", ondelete="CASCADE"), primary_key=True),
    Column("autor_id", BigInteger, ForeignKey("autor.id", ondelete="RESTRICT"), primary_key=True)
)

# Tabla asociativa N:M Libro <-> Genero
libro_genero = Table(
    "libro_genero",
    Base.metadata,
    Column("libro_id", BigInteger, ForeignKey("libro.id", ondelete="CASCADE"), primary_key=True),
    Column("genero_id", BigInteger, ForeignKey("genero.id", ondelete="RESTRICT"), primary_key=True)
)

class Editorial(Base):
    __tablename__ = "editorial"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, unique=True, index=True)
    libros = relationship("Libro", back_populates="editorial")

class Saga(Base):
    __tablename__ = "saga"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, unique=True, index=True)
    libros = relationship("Libro", back_populates="saga")

class Autor(Base):
    __tablename__ = "autor"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, unique=True, index=True)
    libros = relationship("Libro", secondary=libro_autor, back_populates="autores")

class Genero(Base):
    __tablename__ = "genero"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    libros = relationship("Libro", secondary=libro_genero, back_populates="generos")

class Libro(Base):
    __tablename__ = "libro"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False, index=True)
    isbn = Column(String(20), nullable=True, index=True)
    fecha_publicacion = Column(Date, nullable=True)
    sinopsis = Column(Text, nullable=True)
    portada_url = Column(String(500), nullable=True)
    editorial_id = Column(BigInteger, ForeignKey("editorial.id", ondelete="SET NULL"), nullable=True)
    saga_id = Column(BigInteger, ForeignKey("saga.id", ondelete="SET NULL"), nullable=True)
    posicion_saga = Column(Numeric(5, 2), nullable=True)

    # Relaciones
    editorial = relationship("Editorial", back_populates="libros")
    saga = relationship("Saga", back_populates="libros")
    autores = relationship("Autor", secondary=libro_autor, back_populates="libros")
    generos = relationship("Genero", secondary=libro_genero, back_populates="libros")
    ejemplares = relationship("Ejemplar", back_populates="libro")