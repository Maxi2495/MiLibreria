from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.catalogo import Libro
from app.models.espacio import Estante
from app.models.ejemplar import Ejemplar, Lectura, Prestamo
from app.schemas.ejemplar import (
    EjemplarCreate,
    EjemplarResponse,
    EjemplarUpdate
)

router = APIRouter(prefix="/ejemplares", tags=["Ejemplares Físicos"])


# ============================================================
# FUNCIÓN AUXILIAR: Cálculo de ocupación real del estante
# ============================================================

def calcular_ocupacion_estante(estante_id: int, db: Session) -> int:
    """
    Calcula los ejemplares físicamente presentes en un estante.
    Regla 6.7: Un ejemplar prestado libera temporalmente su espacio físico.
    """
    ejemplares_en_estante = db.query(Ejemplar).filter(
        Ejemplar.estante_id == estante_id,
        Ejemplar.activo == True
    ).all()

    ocupacion_real = 0
    for ej in ejemplares_en_estante:
        prestamo_activo = db.query(Prestamo).filter(
            Prestamo.ejemplar_id == ej.id,
            Prestamo.estado == "ACTIVO"
        ).first()
        # Solo ocupa lugar si no está prestado
        if not prestamo_activo:
            ocupacion_real += 1

    return ocupacion_real


# ============================================================
# 1. ALTA DE EJEMPLAR FÍSICO
# ============================================================

@router.post("/", response_model=EjemplarResponse, status_code=status.HTTP_201_CREATED)
def crear_ejemplar(
    ejemplar_in: EjemplarCreate,
    usuario_id: int = 1,  # Fijo temporalmente hasta integrar autenticación JWT
    db: Session = Depends(get_db)
):
    # A. Validar que el libro exista en el catálogo
    libro = db.query(Libro).filter(Libro.id == ejemplar_in.libro_id).first()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El libro con ID {ejemplar_in.libro_id} no existe en el catálogo."
        )

    # B. Si se especificó ubicación física, validar estante y capacidad
    if ejemplar_in.estante_id is not None:
        estante = db.query(Estante).filter(Estante.id == ejemplar_in.estante_id).first()
        if not estante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El estante con ID {ejemplar_in.estante_id} no existe."
            )

        ocupacion_actual = calcular_ocupacion_estante(estante.id, db)
        if ocupacion_actual >= estante.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estante '{estante.nombre}' no tiene espacio disponible ({ocupacion_actual}/{estante.capacidad})."
            )

    # C. Instanciar la copia física
    nuevo_ejemplar = Ejemplar(
        usuario_id=usuario_id,
        libro_id=ejemplar_in.libro_id,
        estante_id=ejemplar_in.estante_id,
        fecha_adquisicion=ejemplar_in.fecha_adquisicion,
        estado_fisico=ejemplar_in.estado_fisico.value if ejemplar_in.estado_fisico else None,
        precio_compra=ejemplar_in.precio_compra,
        moneda=ejemplar_in.moneda,
        observacion=ejemplar_in.observacion,
        activo=True
    )
    db.add(nuevo_ejemplar)
    db.flush()  # Genera el ID de nuevo_ejemplar sin cerrar la transacción

    # D. Regla de Negocio 6.5: Generar lectura inicial en estado PENDIENTE
    lectura_inicial = Lectura(
        ejemplar_id=nuevo_ejemplar.id,
        estado="PENDIENTE"
    )
    db.add(lectura_inicial)

    # Confirmación atómica de ambas entidades
    db.commit()
    db.refresh(nuevo_ejemplar)
    return nuevo_ejemplar


# ============================================================
# 2. LISTADO Y FILTROS DE EJEMPLARES
# ============================================================

@router.get("/", response_model=List[EjemplarResponse])
def listar_ejemplares(
    libro_id: Optional[int] = Query(None, description="Filtrar copias de un libro"),
    estante_id: Optional[int] = Query(None, description="Filtrar por estante"),
    sin_ubicacion: Optional[bool] = Query(None, description="Filtrar ejemplares sin estante asignado"),
    solo_activos: bool = Query(True, description="Mostrar solo ejemplares activos"),
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    query = db.query(Ejemplar).filter(Ejemplar.usuario_id == usuario_id)

    if solo_activos:
        query = query.filter(Ejemplar.activo == True)
    if libro_id:
        query = query.filter(Ejemplar.libro_id == libro_id)
    if estante_id:
        query = query.filter(Ejemplar.estante_id == estante_id)
    if sin_ubicacion is True:
        query = query.filter(Ejemplar.estante_id.is_(None))

    return query.order_by(Ejemplar.id.desc()).all()


# ============================================================
# 3. DETALLE DE UN EJEMPLAR
# ============================================================

@router.get("/{ejemplar_id}", response_model=EjemplarResponse)
def obtener_ejemplar(
    ejemplar_id: int,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == ejemplar_id,
        Ejemplar.usuario_id == usuario_id
    ).first()

    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con ID {ejemplar_id} no encontrado."
        )
    return ejemplar


# ============================================================
# 4. ACTUALIZACIÓN (Reubicación, cambio de condición física)
# ============================================================

@router.put("/{ejemplar_id}", response_model=EjemplarResponse)
def actualizar_ejemplar(
    ejemplar_id: int,
    ejemplar_in: EjemplarUpdate,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == ejemplar_id,
        Ejemplar.usuario_id == usuario_id
    ).first()

    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con ID {ejemplar_id} no encontrado."
        )

    # Si se cambia o asigna un nuevo estante, verificar disponibilidad física
    if ejemplar_in.estante_id is not None and ejemplar_in.estante_id != ejemplar.estante_id:
        nuevo_estante = db.query(Estante).filter(Estante.id == ejemplar_in.estante_id).first()
        if not nuevo_estante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El estante con ID {ejemplar_in.estante_id} no existe."
            )

        ocupacion_nueva = calcular_ocupacion_estante(nuevo_estante.id, db)
        if ocupacion_nueva >= nuevo_estante.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estante destino '{nuevo_estante.nombre}' está lleno."
            )
        ejemplar.estante_id = ejemplar_in.estante_id

    # Actualizar campos opcionales si vienen en el body
    if ejemplar_in.fecha_adquisicion is not None:
        ejemplar.fecha_adquisicion = ejemplar_in.fecha_adquisicion
    if ejemplar_in.estado_fisico is not None:
        ejemplar.estado_fisico = ejemplar_in.estado_fisico.value
    if ejemplar_in.precio_compra is not None:
        ejemplar.precio_compra = ejemplar_in.precio_compra
    if ejemplar_in.moneda is not None:
        ejemplar.moneda = ejemplar_in.moneda
    if ejemplar_in.observacion is not None:
        ejemplar.observacion = ejemplar_in.observacion
    if ejemplar_in.activo is not None:
        ejemplar.activo = ejemplar_in.activo

    db.commit()
    db.refresh(ejemplar)
    return ejemplar


# ============================================================
# 5. BAJA LÓGICA (Regla 6.2 y 6.7)
# ============================================================

@router.delete("/{ejemplar_id}", status_code=status.HTTP_204_NO_CONTENT)
def dar_de_baja_ejemplar(
    ejemplar_id: int,
    usuario_id: int = 1,
    db: Session = Depends(get_db)
):
    ejemplar = db.query(Ejemplar).filter(
        Ejemplar.id == ejemplar_id,
        Ejemplar.usuario_id == usuario_id
    ).first()

    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con ID {ejemplar_id} no encontrado."
        )

    # Regla de negocio 6.2: No dar de baja si posee un préstamo activo
    prestamo_activo = db.query(Prestamo).filter(
        Prestamo.ejemplar_id == ejemplar.id,
        Prestamo.estado == "ACTIVO"
    ).first()

    if prestamo_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede dar de baja el ejemplar porque posee un préstamo activo. Registrá la devolución primero."
        )

    # Baja lógica: se desactiva y se libera de su ubicación física
    ejemplar.activo = False
    ejemplar.estante_id = None
    db.commit()
    return None