from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.espacio import Biblioteca, Estante
from app.models.ejemplar import Ejemplar
from app.models.usuario import Usuario
from app.schemas.espacio import (
    BibliotecaCreate,
    BibliotecaResponse,
    BibliotecaUpdate,
    EstanteCreate,
    EstanteResponse,
    EstanteUpdate
)

router = APIRouter(prefix="/espacios", tags=["Bibliotecas y Estantes"])

# 1. Crear una nueva Biblioteca
@router.post("/bibliotecas", response_model=BibliotecaResponse, status_code=status.HTTP_201_CREATED)
def crear_biblioteca(
    biblioteca_in: BibliotecaCreate,
    usuario_id: int = 1,  # Temporalmente fijo en 1 hasta implementar el token de login
    db: Session = Depends(get_db)
):
    # Verificar si el usuario ya tiene una biblioteca con ese nombre
    existente = db.query(Biblioteca).filter(
        Biblioteca.usuario_id == usuario_id,
        Biblioteca.nombre == biblioteca_in.nombre
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tenés una biblioteca registrada con ese nombre."
        )

    nueva_biblio = Biblioteca(
        usuario_id=usuario_id,
        nombre=biblioteca_in.nombre
    )
    db.add(nueva_biblio)
    db.commit()
    db.refresh(nueva_biblio)
    return nueva_biblio


# 2. Listar todas las Bibliotecas del usuario (con sus estantes)
@router.get("/bibliotecas", response_model=List[BibliotecaResponse])
def listar_bibliotecas(
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    return db.query(Biblioteca).filter(Biblioteca.usuario_id == usuario_id).all()


# 3. Crear un Estante dentro de una Biblioteca
@router.post("/bibliotecas/{biblioteca_id}/estantes", response_model=EstanteResponse, status_code=status.HTTP_201_CREATED)
def crear_estante(
    biblioteca_id: int,
    estante_in: EstanteCreate,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    # Validar que la biblioteca exista y pertenezca al usuario
    biblioteca = db.query(Biblioteca).filter(
        Biblioteca.id == biblioteca_id,
        Biblioteca.usuario_id == usuario_id
    ).first()

    if not biblioteca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La biblioteca especificada no existe."
        )

    # Validar nombre repetido de estante dentro de la misma biblioteca
    existente = db.query(Estante).filter(
        Estante.biblioteca_id == biblioteca_id,
        Estante.nombre == estante_in.nombre
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un estante con ese nombre en esta biblioteca."
        )

    nuevo_estante = Estante(
        biblioteca_id=biblioteca_id,
        nombre=estante_in.nombre,
        capacidad=estante_in.capacidad
    )
    db.add(nuevo_estante)
    db.commit()
    db.refresh(nuevo_estante)
    return nuevo_estante


# 4. Listar Estantes de una Biblioteca específica
@router.get("/bibliotecas/{biblioteca_id}/estantes", response_model=List[EstanteResponse])
def listar_estantes(
    biblioteca_id: int,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    biblioteca = db.query(Biblioteca).filter(
        Biblioteca.id == biblioteca_id,
        Biblioteca.usuario_id == usuario_id
    ).first()

    if not biblioteca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La biblioteca especificada no existe."
        )

    return db.query(Estante).filter(Estante.biblioteca_id == biblioteca_id).all()

# 5. Modificar Biblioteca
@router.put("/bibliotecas/{biblioteca_id}", response_model=BibliotecaResponse)
def actualizar_biblioteca(
    biblioteca_id: int,
    biblioteca_in: BibliotecaUpdate,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    biblio = db.query(Biblioteca).filter(
        Biblioteca.id == biblioteca_id,
        Biblioteca.usuario_id == usuario_id
    ).first()

    if not biblio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Biblioteca no encontrada.")

    # Validar nombre repetido si lo cambia
    if biblio.nombre != biblioteca_in.nombre:
        existe = db.query(Biblioteca).filter(
            Biblioteca.usuario_id == usuario_id,
            Biblioteca.nombre == biblioteca_in.nombre
        ).first()
        if existe:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe una biblioteca con ese nombre.")

    biblio.nombre = biblioteca_in.nombre
    db.commit()
    db.refresh(biblio)
    return biblio


# 6. Eliminar Biblioteca
@router.delete("/bibliotecas/{biblioteca_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_biblioteca(
    biblioteca_id: int,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    biblio = db.query(Biblioteca).filter(
        Biblioteca.id == biblioteca_id,
        Biblioteca.usuario_id == usuario_id
    ).first()

    if not biblio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Biblioteca no encontrada.")

    # Regla de negocio: Verificar si algún estante contiene ejemplares
    estante_ids = [e.id for e in biblio.estantes]
    if estante_ids:
        ejemplares_count = db.query(Ejemplar).filter(Ejemplar.estante_id.in_(estante_ids)).count()
        if ejemplares_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar la biblioteca porque contiene ejemplares ubicados. Reubicalos primero."
            )

    db.delete(biblio)
    db.commit()
    return None


# 7. Modificar Estante
@router.put("/estantes/{estante_id}", response_model=EstanteResponse)
def actualizar_estante(
    estante_id: int,
    estante_in: EstanteUpdate,
    db: Session = Depends(get_db)
):
    estante = db.query(Estante).filter(Estante.id == estante_id).first()
    if not estante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estante no encontrado.")

    # Regla de negocio: La nueva capacidad no puede ser menor a la ocupación física actual
    if estante_in.capacidad is not None:
        ocupacion_actual = db.query(Ejemplar).filter(Ejemplar.estante_id == estante.id).count()
        if estante_in.capacidad < ocupacion_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La capacidad no puede ser menor a la cantidad de ejemplares actuales ({ocupacion_actual})."
            )
        estante.capacidad = estante_in.capacidad

    if estante_in.nombre is not None:
        estante.nombre = estante_in.nombre

    db.commit()
    db.refresh(estante)
    return estante


# 8. Eliminar Estante
@router.delete("/estantes/{estante_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estante(
    estante_id: int,
    db: Session = Depends(get_db)
):
    estante = db.query(Estante).filter(Estante.id == estante_id).first()
    if not estante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estante no encontrado.")

    # Regla de negocio: No eliminar si tiene ejemplares asignados
    ejemplares_count = db.query(Ejemplar).filter(Ejemplar.estante_id == estante.id).count()
    if ejemplares_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el estante porque contiene ejemplares físicos asignados."
        )

    db.delete(estante)
    db.commit()
    return None