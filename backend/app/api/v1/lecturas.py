
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.ejemplar import Ejemplar, Lectura
from app.schemas.lectura import LecturaCreate, LecturaResponse, LecturaUpdate


router = APIRouter(
    prefix="/api/v1/lecturas",
    tags=["Lecturas y Relecturas"],
)


def obtener_ejemplar_propio(
    ejemplar_id: int,
    usuario_actual: Usuario,
    db: Session,
) -> Ejemplar:
    ejemplar = (
        db.query(Ejemplar)
        .filter(
            Ejemplar.id == ejemplar_id,
            Ejemplar.usuario_id == usuario_actual.id,
            Ejemplar.activo.is_(True),
        )
        .first()
    )

    if ejemplar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejemplar no encontrado o no pertenece al usuario autenticado",
        )

    return ejemplar


@router.get(
    "/ejemplar/{ejemplar_id}",
    response_model=list[LecturaResponse],
)
def listar_lecturas_de_ejemplar(
    ejemplar_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    obtener_ejemplar_propio(ejemplar_id, usuario_actual, db)

    lecturas = (
        db.query(Lectura)
        .filter(Lectura.ejemplar_id == ejemplar_id)
        .order_by(Lectura.id.asc())
        .all()
    )

    return lecturas


@router.put(
    "/{lectura_id}",
    response_model=LecturaResponse,
)
def actualizar_lectura(
    lectura_id: int,
    datos: LecturaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    lectura = (
        db.query(Lectura)
        .join(Ejemplar, Lectura.ejemplar_id == Ejemplar.id)
        .filter(
            Lectura.id == lectura_id,
            Ejemplar.usuario_id == usuario_actual.id,
            Ejemplar.activo.is_(True),
        )
        .first()
    )

    if lectura is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lectura no encontrada o no pertenece al usuario autenticado",
        )


    cambios = datos.model_dump(exclude_unset=True)

    estado_final = cambios.get("estado", lectura.estado)

    # Proteger las lecturas históricas sin impedir corregir la última.
    if estado_final in ("PENDIENTE", "EN_CURSO"):
        existe_lectura_posterior = (
            db.query(Lectura.id)
            .filter(
                Lectura.ejemplar_id == lectura.ejemplar_id,
                Lectura.id > lectura.id,
            )
            .first()
        )

        if existe_lectura_posterior is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No se puede reiniciar una lectura histórica. "
                    "Solo es posible corregir el estado de la última lectura."
                ),
            )

    # Limpiar la fecha de finalización si la lectura
    # vuelve a estar pendiente o en curso.
    if estado_final in ("PENDIENTE", "EN_CURSO"):
        cambios["fecha_fin"] = None

    fecha_inicio_final = cambios.get("fecha_inicio", lectura.fecha_inicio)
    fecha_fin_final = cambios.get("fecha_fin", lectura.fecha_fin)


    if (
        fecha_inicio_final is not None
        and fecha_fin_final is not None
        and fecha_fin_final < fecha_inicio_final
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha de finalización no puede ser anterior a la de inicio",
        )

    if estado_final == "EN_CURSO":
        otra_lectura_activa = (
            db.query(Lectura)
            .filter(
                Lectura.ejemplar_id == lectura.ejemplar_id,
                Lectura.id != lectura.id,
                Lectura.estado == "EN_CURSO",
            )
            .first()
        )

        if otra_lectura_activa is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este ejemplar ya tiene otra lectura en curso",
            )

    for campo, valor in cambios.items():
        setattr(lectura, campo, valor)

    db.commit()
    db.refresh(lectura)

    return lectura


@router.post(
    "/",
    response_model=LecturaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_lectura(
    datos: LecturaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    # Verificar que el ejemplar exista y pertenezca al usuario.
    obtener_ejemplar_propio(datos.ejemplar_id, usuario_actual, db)

    
    # Una relectura nueva debe comenzar pendiente o en curso.
    if datos.estado.value not in ("PENDIENTE", "EN_CURSO"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Una nueva lectura debe comenzar en estado "
                "PENDIENTE o EN_CURSO."
            ),
        )

    # No permitir datos de finalización en una lectura nueva.
    if (
        datos.fecha_fin is not None
        or datos.calificacion is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Una nueva lectura no puede tener fecha de finalización "
                "ni calificación."
            ),
        )


    # Recuperar el historial de lecturas del ejemplar.
    lecturas_anteriores = (
        db.query(Lectura)
        .filter(Lectura.ejemplar_id == datos.ejemplar_id)
        .order_by(Lectura.id.desc())
        .all()
    )

    # El primer registro se crea automáticamente con el ejemplar.
    if not lecturas_anteriores:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El ejemplar no tiene una lectura inicial. Revisar su creación.",
        )

    # Solo se permite iniciar otra lectura cuando la anterior terminó
    # o fue abandonada.
    ultima_lectura = lecturas_anteriores[0]

    if ultima_lectura.estado not in ("LEIDO", "ABANDONADO"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La última lectura debe estar finalizada o abandonada para iniciar otra.",
        )

    # Impedir dos lecturas simultáneas del mismo ejemplar.
    if any(lectura.estado == "EN_CURSO" for lectura in lecturas_anteriores):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este ejemplar ya tiene una lectura en curso.",
        )

    # Crear un registro independiente para conservar el historial.
    nueva_lectura = Lectura(
        ejemplar_id=datos.ejemplar_id,
        estado=datos.estado.value,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        calificacion=datos.calificacion,
        resena=datos.resena,
    )

    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)

    return nueva_lectura
