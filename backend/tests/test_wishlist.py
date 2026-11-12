def test_agregar_libro_a_wishlist(cliente):
    respuesta = cliente.post(
        "/api/v1/wishlist/",
        json={
            "titulo": "El nombre del viento",
            "autor_referencia": "Patrick Rothfuss",
            "isbn": None,
            "libro_id": None,
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "PENDIENTE"
    assert respuesta.json()["titulo"] == "El nombre del viento"


def test_listar_wishlist(cliente):
    cliente.post(
        "/api/v1/wishlist/",
        json={"titulo": "Libro deseado"},
    )

    respuesta = cliente.get("/api/v1/wishlist/")

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_evitar_duplicados(cliente):
    datos = {"titulo": "Libro repetido"}

    cliente.post("/api/v1/wishlist/", json=datos)
    respuesta = cliente.post("/api/v1/wishlist/", json=datos)

    assert respuesta.status_code == 409


def test_eliminar_de_wishlist(cliente):
    creacion = cliente.post(
        "/api/v1/wishlist/",
        json={"titulo": "Libro para eliminar"},
    )

    wishlist_id = creacion.json()["id"]

    respuesta = cliente.delete(
        f"/api/v1/wishlist/{wishlist_id}"
    )

    assert respuesta.status_code == 204
    assert cliente.get("/api/v1/wishlist/").json() == []


def test_marcar_como_adquirido(cliente):
    creacion = cliente.post(
        "/api/v1/wishlist/",
        json={
            "titulo": "Libro de prueba",
            "libro_id": 1,
        },
    )

    wishlist_id = creacion.json()["id"]

    respuesta = cliente.post(
        f"/api/v1/wishlist/{wishlist_id}/adquirir",
        json={
            "libro_id": 1,
            "estante_id": None,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ADQUIRIDO"

def test_adquirir_crea_ejemplar_y_lectura(cliente):
    # Agregar un libro existente del catálogo a Wishlist
    creacion = cliente.post(
        "/api/v1/wishlist/",
        json={
            "titulo": "Libro de prueba",
            "libro_id": 1,
        },
    )

    assert creacion.status_code == 201
    wishlist_id = creacion.json()["id"]

    # Marcarlo como adquirido
    respuesta = cliente.post(
        f"/api/v1/wishlist/{wishlist_id}/adquirir",
        json={
            "libro_id": 1,
            "estante_id": None,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ADQUIRIDO"

    # Comprobar que se creó un nuevo ejemplar físico
    ejemplares = cliente.get("/api/v1/ejemplares/")

    assert ejemplares.status_code == 200

    nuevos = [
        ejemplar
        for ejemplar in ejemplares.json()
        if ejemplar["libro_id"] == 1 and ejemplar["id"] != 1
    ]

    assert len(nuevos) == 1

    # Comprobar que se generó su lectura inicial
    ejemplar_id = nuevos[0]["id"]

    lecturas = cliente.get(
    f"/api/v1/lecturas/ejemplar/{ejemplar_id}"
)

    assert lecturas.status_code == 200
    assert any(
        lectura["ejemplar_id"] == ejemplar_id
        and lectura["estado"] == "PENDIENTE"
        for lectura in lecturas.json()
    )