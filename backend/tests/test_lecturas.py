
import pytest
from pydantic import ValidationError

from app.schemas.lectura import LecturaCreate


def test_rechazar_fecha_fin_anterior_a_inicio():
    with pytest.raises(ValidationError):
        LecturaCreate(
            ejemplar_id=1,
            estado="LEIDO",
            fecha_inicio="2026-10-21",
            fecha_fin="2026-10-20",
        )

@pytest.mark.parametrize("calificacion", [0, 6, -1])
def test_rechazar_calificaciones_invalidas(calificacion):
    with pytest.raises(ValidationError):
        LecturaCreate(
            ejemplar_id=1,
            estado="LEIDO",
            calificacion=calificacion,
        )


@pytest.mark.parametrize("calificacion", [1, 2, 3, 4, 5])
def test_aceptar_calificaciones_validas(calificacion):
    lectura = LecturaCreate(
        ejemplar_id=1,
        estado="LEIDO",
        calificacion=calificacion,
    )

    assert lectura.calificacion == calificacion


def test_listar_lecturas_del_ejemplar(cliente):
    respuesta = cliente.get("/api/v1/lecturas/ejemplar/1")

    assert respuesta.status_code == 200

    lecturas = respuesta.json()

    assert len(lecturas) == 1
    assert lecturas[0]["id"] == 1
    assert lecturas[0]["ejemplar_id"] == 1
    assert lecturas[0]["estado"] == "PENDIENTE"


def test_no_crear_relectura_si_ultima_pendiente(cliente):
    respuesta = cliente.post(
        "/api/v1/lecturas/",
        json={
            "ejemplar_id": 1,
            "estado": "EN_CURSO",
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "La última lectura debe estar finalizada o abandonada "
        "para iniciar otra."
    )

    # Verificar que no se haya creado ninguna lectura adicional.
    historial = cliente.get("/api/v1/lecturas/ejemplar/1")

    assert historial.status_code == 200
    assert len(historial.json()) == 1


def test_crear_relectura_si_ultima_finalizada(cliente):
    # Finalizar la lectura inicial.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "LEIDO",
            "calificacion": 5,
        },
    )

    assert respuesta.status_code == 200

    # Crear una nueva lectura.
    respuesta = cliente.post(
        "/api/v1/lecturas/",
        json={
            "ejemplar_id": 1,
            "estado": "EN_CURSO",
        },
    )

    assert respuesta.status_code == 201

    nueva_lectura = respuesta.json()

    assert nueva_lectura["estado"] == "EN_CURSO"
    assert nueva_lectura["ejemplar_id"] == 1

    # Verificar que se conserve el historial.
    historial = cliente.get("/api/v1/lecturas/ejemplar/1")

    assert historial.status_code == 200
    assert len(historial.json()) == 2
    assert historial.json()[0]["estado"] == "LEIDO"
    assert historial.json()[1]["estado"] == "EN_CURSO"


def test_no_reiniciar_lectura_historica(cliente):
    # Finalizar la primera lectura.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "LEIDO",
            "calificacion": 5,
        },
    )
    assert respuesta.status_code == 200

    # Crear una segunda lectura.
    respuesta = cliente.post(
        "/api/v1/lecturas/",
        json={
            "ejemplar_id": 1,
            "estado": "EN_CURSO",
        },
    )
    assert respuesta.status_code == 201

    # Intentar reiniciar la primera lectura.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "EN_CURSO",
        },
    )

    assert respuesta.status_code == 409

    # Verificar que el historial permanezca intacto.
    historial = cliente.get("/api/v1/lecturas/ejemplar/1")
    assert historial.status_code == 200

    lecturas = historial.json()
    assert len(lecturas) == 2
    assert lecturas[0]["estado"] == "LEIDO"
    assert lecturas[1]["estado"] == "EN_CURSO"


def test_modificar_calificacion_lectura_historica(cliente):
    # Finalizar la primera lectura.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "LEIDO",
            "calificacion": 5,
            "resena": "Primera lectura.",
        },
    )
    assert respuesta.status_code == 200

    # Crear una relectura.
    respuesta = cliente.post(
        "/api/v1/lecturas/",
        json={
            "ejemplar_id": 1,
            "estado": "EN_CURSO",
        },
    )
    assert respuesta.status_code == 201

    # Corregir la calificación de la primera lectura.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "calificacion": 4,
            "resena": "Reseña corregida.",
        },
    )

    assert respuesta.status_code == 200

    lectura = respuesta.json()
    assert lectura["estado"] == "LEIDO"
    assert lectura["calificacion"] == 4
    assert lectura["resena"] == "Reseña corregida."

    # Comprobar que la relectura sigue en curso.
    historial = cliente.get("/api/v1/lecturas/ejemplar/1")
    assert historial.status_code == 200
    assert len(historial.json()) == 2
    assert historial.json()[1]["estado"] == "EN_CURSO"


def test_rechazar_fecha_fin_anterior_al_actualizar(cliente):
    # Registrar una fecha de inicio válida.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "EN_CURSO",
            "fecha_inicio": "2026-10-21",
        },
    )

    assert respuesta.status_code == 200

    # Intentar finalizar con una fecha anterior.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "LEIDO",
            "fecha_fin": "2026-10-20",
        },
    )

    assert respuesta.status_code == 422

    # Comprobar que no se guardó el cambio inválido.
    historial = cliente.get("/api/v1/lecturas/ejemplar/1")

    assert historial.status_code == 200

    lectura = historial.json()[0]
    assert lectura["estado"] == "EN_CURSO"
    assert lectura["fecha_inicio"] == "2026-10-21"
    assert lectura["fecha_fin"] is None


def test_reabrir_lectura_limpia_fecha_fin(cliente):
    # Registrar una lectura finalizada.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "LEIDO",
            "fecha_inicio": "2026-10-20",
            "fecha_fin": "2026-10-21",
            "calificacion": 5,
        },
    )

    assert respuesta.status_code == 200

    # Volver a poner la lectura en curso.
    respuesta = cliente.put(
        "/api/v1/lecturas/1",
        json={
            "estado": "EN_CURSO",
        },
    )

    assert respuesta.status_code == 200

    lectura = respuesta.json()

    assert lectura["estado"] == "EN_CURSO"
    assert lectura["fecha_inicio"] == "2026-10-20"
    assert lectura["fecha_fin"] is None
    assert lectura["calificacion"] == 5


def test_no_consultar_lecturas_de_otro_usuario(cliente):
    from app.main import app
    from app.dependencies import get_current_user

    # Simular que la solicitud pertenece a otro usuario.
    class OtroUsuario:
        id = 2

    app.dependency_overrides[get_current_user] = lambda: OtroUsuario()

    respuesta = cliente.get("/api/v1/lecturas/ejemplar/1")

    # El ejemplar 1 pertenece al usuario 1.
    assert respuesta.status_code == 404
