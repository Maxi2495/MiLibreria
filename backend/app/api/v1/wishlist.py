from app.schemas.wishlist import WishlistAdquirir
from app.schemas.ejemplar import EjemplarCreate
from app.api.v1.ejemplares import crear_ejemplar
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.catalogo import Libro
from app.models.ejemplar import Wishlist
from app.schemas.wishlist import WishlistCreate, WishlistResponse


router = APIRouter(
    prefix="/api/v1/wishlist",
    tags=["Wishlist"],
)


@router.post(
    "/",
    response_model=WishlistResponse,
    status_code=status.HTTP_201_CREATED,
)
def agregar_a_wishlist(
    payload: WishlistCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    titulo = payload.titulo.strip()
    if not titulo:
        raise HTTPException(
            status_code=422,
            detail="El título no puede estar vacío",
        )

    if payload.libro_id is not None:
        libro = db.query(Libro).filter(
            Libro.id == payload.libro_id
        ).first()

        if libro is None:
            raise HTTPException(
                status_code=404,
                detail="Libro no encontrado en el catálogo",
            )

    # Evitar duplicados por libro del catálogo.
    if payload.libro_id is not None:
        duplicado = db.query(Wishlist).filter(
            Wishlist.usuario_id == usuario_actual.id,
            Wishlist.libro_id == payload.libro_id,
        ).first()
    else:
        # Para libros sin vínculo al catálogo, comparar título y autor.
        duplicado = db.query(Wishlist).filter(
            Wishlist.usuario_id == usuario_actual.id,
            Wishlist.libro_id.is_(None),
            Wishlist.titulo == titulo,
            Wishlist.autor_referencia == payload.autor_referencia,
        ).first()

    if duplicado:
        raise HTTPException(
            status_code=409,
            detail="El libro ya está en tu Wishlist",
        )

    nuevo_deseo = Wishlist(
        usuario_id=usuario_actual.id,
        libro_id=payload.libro_id,
        titulo=titulo,
        autor_referencia=payload.autor_referencia,
        isbn=payload.isbn,
        estado="PENDIENTE",
    )

    db.add(nuevo_deseo)
    db.commit()
    db.refresh(nuevo_deseo)

    return nuevo_deseo


@router.get("/", response_model=list[WishlistResponse])
def listar_wishlist(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    deseos = (
        db.query(Wishlist)
        .filter(Wishlist.usuario_id == usuario_actual.id)
        .order_by(Wishlist.fecha_creacion.desc(), Wishlist.id.desc())
        .all()
    )

    return deseos


@router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_de_wishlist(
    wishlist_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    deseo = (
        db.query(Wishlist)
        .filter(
            Wishlist.id == wishlist_id,
            Wishlist.usuario_id == usuario_actual.id,
        )
        .first()
    )

    if deseo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado en tu Wishlist",
        )

    db.delete(deseo)
    db.commit()
    return None

@router.post("/{wishlist_id}/adquirir", response_model=WishlistResponse)
def marcar_como_adquirido(
    wishlist_id: int,
    payload: WishlistAdquirir,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    # Buscar el deseo del usuario autenticado
    deseo = (
        db.query(Wishlist)
        .filter(
            Wishlist.id == wishlist_id,
            Wishlist.usuario_id == usuario_actual.id,
        )
        .first()
    )

    if deseo is None:
        raise HTTPException(
            status_code=404,
            detail="Libro no encontrado en tu Wishlist",
        )

    if deseo.estado == "ADQUIRIDO":
        raise HTTPException(
            status_code=409,
            detail="Este libro ya fue marcado como adquirido",
        )

    # Usar el libro asociado o el indicado en la solicitud
    libro_id = deseo.libro_id or payload.libro_id

    if libro_id is None:
        raise HTTPException(
            status_code=422,
            detail="Primero debés registrar el libro en el catálogo e indicar su libro_id",
        )

    if deseo.libro_id is not None and payload.libro_id is not None:
        if deseo.libro_id != payload.libro_id:
            raise HTTPException(
                status_code=422,
                detail="El libro indicado no coincide con el de la Wishlist",
            )

    # Reutilizar la creación de ejemplares existente
    ejemplar_in = EjemplarCreate(
        libro_id=libro_id,
        estante_id=payload.estante_id,
    )

    # La función crea el ejemplar y su lectura inicial
    crear_ejemplar(
        ejemplar_in=ejemplar_in,
        usuario_actual=usuario_actual,
        db=db,
        confirmar=False,
    )

    # Actualizar el deseo después de crear el ejemplar
    deseo.libro_id = libro_id
    deseo.estado = "ADQUIRIDO"

    db.commit()
    db.refresh(deseo)

    return deseo