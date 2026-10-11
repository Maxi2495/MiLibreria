from sqlalchemy import Column, BigInteger, String, Date, DateTime, Numeric, Boolean, Text, ForeignKey, SmallInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Ejemplar(Base):
    __tablename__ = "ejemplar"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    libro_id = Column(BigInteger, ForeignKey("libro.id", ondelete="RESTRICT"), nullable=False)
    estante_id = Column(BigInteger, ForeignKey("estante.id", ondelete="SET NULL"), nullable=True)
    fecha_adquisicion = Column(Date, nullable=True)
    estado_fisico = Column(String(20), nullable=True)
    precio_compra = Column(Numeric(10, 2), nullable=True)
    moneda = Column(String(10), nullable=True)
    observacion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    usuario = relationship("Usuario", back_populates="ejemplares")
    libro = relationship("Libro", back_populates="ejemplares")
    estante = relationship("Estante", back_populates="ejemplares")
    lecturas = relationship("Lectura", back_populates="ejemplar", cascade="all, delete-orphan")
    prestamos = relationship("Prestamo", back_populates="ejemplar", cascade="all, delete-orphan")
    anotaciones = relationship("Anotacion", back_populates="ejemplar")

class Lectura(Base):
    __tablename__ = "lectura"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ejemplar_id = Column(BigInteger, ForeignKey("ejemplar.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    calificacion = Column(SmallInteger, nullable=True)
    resena = Column(Text, nullable=True)

    ejemplar = relationship("Ejemplar", back_populates="lecturas")

class Prestamo(Base):
    __tablename__ = "prestamo"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ejemplar_id = Column(BigInteger, ForeignKey("ejemplar.id", ondelete="CASCADE"), nullable=False)
    nombre_destinatario = Column(String(100), nullable=False)
    apellido_destinatario = Column(String(100), nullable=False)
    telefono_destinatario = Column(String(50), nullable=True)
    email_destinatario = Column(String(255), nullable=True)
    fecha_prestamo = Column(Date, nullable=False)
    fecha_prevista_devolucion = Column(Date, nullable=True)
    fecha_devolucion = Column(Date, nullable=True)
    estado = Column(String(20), nullable=False, default="ACTIVO")

    ejemplar = relationship("Ejemplar", back_populates="prestamos")

class Anotacion(Base):
    __tablename__ = "anotacion"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    ejemplar_id = Column(BigInteger, ForeignKey("ejemplar.id", ondelete="CASCADE"), nullable=True)
    titulo = Column(String(255), nullable=True)
    contenido = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_modificacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="anotaciones")
    ejemplar = relationship("Ejemplar", back_populates="anotaciones")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    libro_id = Column(BigInteger, ForeignKey("libro.id", ondelete="SET NULL"), nullable=True)
    titulo = Column(String(255), nullable=False)
    autor_referencia = Column(String(500), nullable=True)
    isbn = Column(String(20), nullable=True)
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="wishlist")
    libro = relationship("Libro")