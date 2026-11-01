
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, BigInteger
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.catalogo import Libro
from app.models.ejemplar import Ejemplar, Lectura

# Registrar todos los modelos de BookNest.
from app.models import usuario, catalogo, espacio, ejemplar


@compiles(BigInteger, "sqlite")
def compilar_bigint_sqlite(tipo, compilador, **kwargs):
    return "INTEGER"


@pytest.fixture
def cliente():
    # Base SQLite en memoria, compartida entre conexiones del test.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def activar_claves_foraneas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    SessionPrueba = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    # Datos ficticios con identificadores explícitos.
    with SessionPrueba() as db:
        usuario_prueba = Usuario(
            id=1,
            nombre="Usuario",
            apellido="Prueba",
            email="prueba@booknest.test",
            password_hash="hash_ficticio",
            estado="ACTIVA",
        )

        libro_prueba = Libro(
            id=1,
            titulo="Libro de prueba",
        )

        ejemplar_prueba = Ejemplar(
            id=1,
            usuario_id=1,
            libro_id=1,
            activo=True,
        )

        lectura_inicial = Lectura(
            id=1,
            ejemplar_id=1,
            estado="PENDIENTE",
        )

        db.add_all([
            usuario_prueba,
            libro_prueba,
            ejemplar_prueba,
            lectura_inicial,
        ])
        db.commit()

    def reemplazar_db():
        with SessionPrueba() as db:
            yield db

    def reemplazar_usuario():
        with SessionPrueba() as db:
            return db.get(Usuario, 1)

    app.dependency_overrides[get_db] = reemplazar_db
    app.dependency_overrides[get_current_user] = reemplazar_usuario

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
