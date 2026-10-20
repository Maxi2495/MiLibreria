from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
# Importamos ambos modelos desde app.models.ejemplar
from app.models.ejemplar import Ejemplar, Prestamo
from app.models.espacio import Estante, Biblioteca
from app.schemas.prestamo import (
    EstadoPrestamo,
    PrestamoCreate,
    PrestamoDevolucion,
    PrestamoResponse,
)
from app.api.v1.ejemplares import calcular_ocupacion_estante

router = APIRouter(prefix="/api/v1/prestamos", tags=["Préstamos"])


def _obtener_ejemplar_propio(ejemplar_id: int, usuario_id: int, db: Session) -> Ejemplar:
    """Valida la existencia del ejemplar y comprueba que pertenezca al usuario activo."""
    stmt = select(Ejemplar).where(
        Ejemplar.id == ejemplar_id,
        Ejemplar.usuario_id == usuario_id,
        Ejemplar.activo.is_(True)
    )
    ejemplar = db.execute(stmt).scalar_one_or_none()
    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejemplar no encontrado, inactivo o no pertenece al usuario autenticado."
        )
    return ejemplar


def _actualizar_estado_vencido_si_aplica(prestamo: Prestamo) -> None:
    """Si la fecha prevista fue superada y el ejemplar sigue prestado, cambia a VENCIDO."""
    if (
        prestamo.estado == EstadoPrestamo.ACTIVO.value
        and prestamo.fecha_prevista_devolucion
        and prestamo.fecha_prevista_devolucion < date.today()
    ):
        prestamo.estado = EstadoPrestamo.VENCIDO.value


@router.post("/", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED)
def registrar_prestamo(
    payload: PrestamoCreate,
    usuario_id: int = Query(..., description="ID del usuario propietario del ejemplar"),
    db: Session = Depends(get_db),
):
    """
    Registra la salida en préstamo de un ejemplar físico.
    Aplica la regla de negocio: no puede prestarse un ejemplar con préstamo ACTIVO o VENCIDO.
    """
    _obtener_ejemplar_propio(payload.ejemplar_id, usuario_id, db)

    stmt_conflicto = select(Prestamo).where(
        Prestamo.ejemplar_id == payload.ejemplar_id,
        Prestamo.estado.in_([EstadoPrestamo.ACTIVO.value, EstadoPrestamo.VENCIDO.value]),
    )
    prestamo_en_curso = db.execute(stmt_conflicto).scalar_one_or_none()
    if prestamo_en_curso:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El ejemplar ya cuenta con un préstamo en curso (ID: {prestamo_en_curso.id}, estado: '{prestamo_en_curso.estado}')."
        )

    nuevo_prestamo = Prestamo(
        ejemplar_id=payload.ejemplar_id,
        nombre_destinatario=payload.nombre_destinatario,
        apellido_destinatario=payload.apellido_destinatario,
        telefono_destinatario=payload.telefono_destinatario,
        email_destinatario=payload.email_destinatario,
        fecha_prestamo=date.today(),
        fecha_prevista_devolucion=payload.fecha_prevista_devolucion,
        estado=EstadoPrestamo.ACTIVO.value,
    )

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)
    return nuevo_prestamo


@router.get("/", response_model=List[PrestamoResponse])
def listar_prestamos(
    usuario_id: int = Query(..., description="ID del usuario para listar sus préstamos"),
    estado: Optional[EstadoPrestamo] = Query(None, description="Filtrar por estado del préstamo"),
    ejemplar_id: Optional[int] = Query(None, description="Filtrar por ID de ejemplar específico"),
    db: Session = Depends(get_db),
):
    """Consulta préstamos activos e históricos asociados a los ejemplares del usuario."""
    stmt = (
        select(Prestamo)
        .join(Ejemplar, Prestamo.ejemplar_id == Ejemplar.id)
        .where(Ejemplar.usuario_id == usuario_id)
    )

    if estado:
        stmt = stmt.where(Prestamo.estado == estado.value)
    if ejemplar_id:
        stmt = stmt.where(Prestamo.ejemplar_id == ejemplar_id)

    stmt = stmt.order_by(Prestamo.fecha_prestamo.desc(), Prestamo.id.desc())
    prestamos = db.execute(stmt).scalars().all()

    for p in prestamos:
        _actualizar_estado_vencido_si_aplica(p)
    db.commit()

    return prestamos


@router.get("/{prestamo_id}", response_model=PrestamoResponse)
def obtener_prestamo(
    prestamo_id: int,
    usuario_id: int = Query(..., description="ID del usuario propietario"),
    db: Session = Depends(get_db),
):
    """Consulta el detalle de un préstamo asegurando la pertenencia al usuario."""
    prestamo = db.execute(select(Prestamo).where(Prestamo.id == prestamo_id)).scalar_one_or_none()
    if not prestamo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado.")

    _obtener_ejemplar_propio(prestamo.ejemplar_id, usuario_id, db)
    _actualizar_estado_vencido_si_aplica(prestamo)
    db.commit()
    return prestamo


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoResponse)
def registrar_devolucion(
    prestamo_id: int,
    payload: PrestamoDevolucion,
    usuario_id: int = Query(..., description="ID del usuario propietario"),
    db: Session = Depends(get_db),
):
    """
    Registra la restitución del libro:
    - Actualiza fecha_devolucion y estado a 'DEVUELTO'.
    - Permite reubicar el ejemplar en un estante verificando capacidad física o dejarlo en None.
    """
    prestamo = db.execute(select(Prestamo).where(Prestamo.id == prestamo_id)).scalar_one_or_none()
    if not prestamo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado.")

    ejemplar = _obtener_ejemplar_propio(prestamo.ejemplar_id, usuario_id, db)

    if prestamo.estado not in [EstadoPrestamo.ACTIVO.value, EstadoPrestamo.VENCIDO.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede registrar devolución en un préstamo con estado '{prestamo.estado}'."
        )

    if payload.estante_id is not None:
        stmt_estante = (
            select(Estante)
            .join(Biblioteca, Estante.biblioteca_id == Biblioteca.id)
            .where(Estante.id == payload.estante_id, Biblioteca.usuario_id == usuario_id)
        )
        estante = db.execute(stmt_estante).scalar_one_or_none()
        if not estante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El estante seleccionado no existe o no pertenece al usuario."
            )

        ocupacion_actual = calcular_ocupacion_estante(estante.id, db)
        if ocupacion_actual >= estante.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estante '{estante.nombre}' no tiene capacidad disponible ({ocupacion_actual}/{estante.capacidad})."
            )

        ejemplar.estante_id = payload.estante_id
    else:
        ejemplar.estante_id = None

    prestamo.fecha_devolucion = payload.fecha_devolucion or date.today()
    prestamo.estado = EstadoPrestamo.DEVUELTO.value

    db.commit()
    db.refresh(prestamo)
    return prestamo


@router.post("/{prestamo_id}/cancelar", response_model=PrestamoResponse)
def cancelar_prestamo(
    prestamo_id: int,
    usuario_id: int = Query(..., description="ID del usuario propietario"),
    db: Session = Depends(get_db),
):
    """
    Anula un préstamo registrado por error sin eliminar el registro del historial.
    """
    prestamo = db.execute(select(Prestamo).where(Prestamo.id == prestamo_id)).scalar_one_or_none()
    if not prestamo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado.")

    _obtener_ejemplar_propio(prestamo.ejemplar_id, usuario_id, db)

    if prestamo.estado != EstadoPrestamo.ACTIVO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden cancelar préstamos en estado 'ACTIVO'. Estado actual: '{prestamo.estado}'."
        )

    prestamo.estado = EstadoPrestamo.CANCELADO.value
    db.commit()
    db.refresh(prestamo)
    return prestamo