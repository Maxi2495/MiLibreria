from datetime import date
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.catalogo import Libro, Autor
from app.models.espacio import Biblioteca, Estante
from app.models.ejemplar import Ejemplar, Lectura, Prestamo
from app.models.usuario import Usuario
from app.schemas.ejemplar import (
    EjemplarCreate,
    EjemplarResponse,
    EjemplarUpdate,
    EstadoFisicoEnum,
)
from app.schemas.prestamo import EstadoPrestamo

router = APIRouter(prefix="/ejemplares", tags=["Ejemplares Físicos"])


# ============================================================
# FUNCIÓN AUXILIAR: Cálculo de ocupación real del estante
# ============================================================

def calcular_ocupacion_estante(estante_id: int, db: Session) -> int:
    """
    Calcula los ejemplares físicamente presentes en un estante.
    Regla 6.7: Un ejemplar prestado libera temporalmente su espacio físico.
    """
    stmt = (
        select(Ejemplar)
        .where(
            Ejemplar.estante_id == estante_id,
            Ejemplar.activo.is_(True)
        )
    )
    ejemplares_en_estante = db.execute(stmt).scalars().all()

    ocupacion_real = 0
    for ej in ejemplares_en_estante:
        stmt_prestamo = (
            select(Prestamo)
            .where(
                Prestamo.ejemplar_id == ej.id,
                Prestamo.estado.in_([EstadoPrestamo.ACTIVO.value, EstadoPrestamo.VENCIDO.value])
            )
        )
        prestamo_activo = db.execute(stmt_prestamo).scalars().first()
        if not prestamo_activo:
            ocupacion_real += 1

    return ocupacion_real


# ============================================================
# 1. ALTA DE EJEMPLAR FÍSICO
# ============================================================

@router.post("/", response_model=EjemplarResponse, status_code=status.HTTP_201_CREATED)
def crear_ejemplar(
    ejemplar_in: EjemplarCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # A. Validar que el libro exista en el catálogo
    stmt_libro = select(Libro).where(Libro.id == ejemplar_in.libro_id)
    libro = db.execute(stmt_libro).scalar_one_or_none()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El libro con ID {ejemplar_in.libro_id} no existe en el catálogo."
        )

    # B. Si se especificó ubicación física, validar estante, propiedad y capacidad
    if ejemplar_in.estante_id is not None:
        stmt_estante = (
            select(Estante)
            .join(Biblioteca, Estante.biblioteca_id == Biblioteca.id)
            .where(
                Estante.id == ejemplar_in.estante_id,
                Biblioteca.usuario_id == usuario_actual.id
            )
        )
        estante = db.execute(stmt_estante).scalar_one_or_none()
        if not estante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El estante especificado no existe o no pertenece a tus bibliotecas."
            )

        ocupacion_actual = calcular_ocupacion_estante(estante.id, db)
        if ocupacion_actual >= estante.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estante '{estante.nombre}' no tiene espacio disponible ({ocupacion_actual}/{estante.capacidad})."
            )

    # C. Instanciar la copia física asignada al usuario autenticado
    nuevo_ejemplar = Ejemplar(
        usuario_id=usuario_actual.id,
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
    db.flush()

    # D. Regla 6.5: Generar lectura inicial en estado PENDIENTE
    lectura_inicial = Lectura(
        ejemplar_id=nuevo_ejemplar.id,
        estado="PENDIENTE"
    )
    db.add(lectura_inicial)

    db.commit()
    db.refresh(nuevo_ejemplar)
    return nuevo_ejemplar


# ============================================================
# 2. LISTADO, BÚSQUEDA Y FILTROS DE EJEMPLARES
# ============================================================

@router.get("/", response_model=List[EjemplarResponse])
def listar_ejemplares(
    buscar: Optional[str] = Query(None, description="Búsqueda libre por título, ISBN o autor del libro"),
    libro_id: Optional[int] = Query(None, description="Filtrar copias físicas de un libro específico"),
    biblioteca_id: Optional[int] = Query(None, description="Filtrar ejemplares por biblioteca"),
    estante_id: Optional[int] = Query(None, description="Filtrar ejemplares por estante"),
    sin_ubicacion: Optional[bool] = Query(None, description="Filtrar ejemplares con o sin ubicación física asignada"),
    estado_lectura: Optional[Literal["PENDIENTE", "EN_CURSO", "LEIDO", "ABANDONADO"]] = Query(
        None, description="Filtrar por estado de lectura actual"
    ),
    prestado: Optional[bool] = Query(None, description="True para ejemplares actualmente prestados, False para disponibles"),
    estado_fisico: Optional[EstadoFisicoEnum] = Query(None, description="Filtrar por condición física de conservación"),
    solo_activos: bool = Query(True, description="Mostrar solo ejemplares activos (no dados de baja)"),
    ordenar_por: Literal["titulo", "autor", "fecha_adquisicion", "id"] = Query(
        "id", description="Criterio de orden (Regla 6.8)"
    ),
    orden_dir: Literal["asc", "desc"] = Query("desc", description="Sentido del ordenamiento"),
    limit: int = Query(50, ge=1, le=100, description="Límite de paginación"),
    offset: int = Query(0, ge=0, description="Desplazamiento de paginación"),
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista y filtra los ejemplares físicos de la colección personal del usuario autenticado,
    incorporando trazabilidad de ubicación, estado de préstamo y lecturas (Reglas 6.2, 6.7 y 6.8).
    """
    stmt = (
        select(Ejemplar)
        .options(
            joinedload(Ejemplar.libro).selectinload(Libro.autores),
            joinedload(Ejemplar.libro).selectinload(Libro.generos),
            joinedload(Ejemplar.libro).joinedload(Libro.editorial),
            joinedload(Ejemplar.libro).joinedload(Libro.saga),
            joinedload(Ejemplar.estante)
        )
        .where(Ejemplar.usuario_id == usuario_actual.id)
    )

    # 1. Filtro de activos / bajas lógicas
    if solo_activos:
        stmt = stmt.where(Ejemplar.activo.is_(True))

    libro_joined = False

    # 2. Búsqueda libre en el catálogo asociado
    if buscar:
        termino = f"%{buscar.strip()}%"
        stmt = stmt.join(Ejemplar.libro)
        libro_joined = True
        stmt = stmt.where(
            or_(
                Libro.titulo.ilike(termino),
                Libro.isbn.ilike(termino),
                Libro.autores.any(Autor.nombre.ilike(termino))
            )
        )

    # 3. Filtros bibliográficos directos
    if libro_id:
        stmt = stmt.where(Ejemplar.libro_id == libro_id)

    # 4. Filtros de espacio físico
    if estante_id:
        stmt = stmt.where(Ejemplar.estante_id == estante_id)

    if biblioteca_id:
        stmt = stmt.where(Ejemplar.estante.has(Estante.biblioteca_id == biblioteca_id))

    if sin_ubicacion is True:
        stmt = stmt.where(Ejemplar.estante_id.is_(None))
    elif sin_ubicacion is False:
        stmt = stmt.where(Ejemplar.estante_id.isnot(None))

    # 5. Filtro por estado de lectura
    if estado_lectura:
        stmt = stmt.where(Ejemplar.lecturas.any(Lectura.estado == estado_lectura))

    # 6. Filtro por estado de préstamo (ACTIVO o VENCIDO)
    condicion_prestado = Ejemplar.prestamos.any(
        Prestamo.estado.in_([EstadoPrestamo.ACTIVO.value, EstadoPrestamo.VENCIDO.value])
    )
    if prestado is True:
        stmt = stmt.where(condicion_prestado)
    elif prestado is False:
        stmt = stmt.where(~condicion_prestado)

    # 7. Filtro por estado físico
    if estado_fisico:
        stmt = stmt.where(Ejemplar.estado_fisico == estado_fisico.value)

    # 8. Ordenamiento dinámico
    if ordenar_por == "titulo":
        if not libro_joined:
            stmt = stmt.join(Ejemplar.libro)
            libro_joined = True
        columna_orden = Libro.titulo
    elif ordenar_por == "autor":
        if not libro_joined:
            stmt = stmt.join(Ejemplar.libro)
            libro_joined = True
        stmt = stmt.outerjoin(Libro.autores)
        columna_orden = Autor.nombre
    else:
        columna_orden = getattr(Ejemplar, ordenar_por)

    if orden_dir == "desc":
        stmt = stmt.order_by(columna_orden.desc())
    else:
        stmt = stmt.order_by(columna_orden.asc())

    # 9. Paginación y ejecución desduplicada
    stmt = stmt.limit(limit).offset(offset)
    ejemplares = db.execute(stmt).scalars().unique().all()
    return ejemplares


# ============================================================
# 3. DETALLE DE UN EJEMPLAR
# ============================================================

@router.get("/{ejemplar_id}", response_model=EjemplarResponse)
def obtener_ejemplar(
    ejemplar_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = (
        select(Ejemplar)
        .options(
            joinedload(Ejemplar.libro).selectinload(Libro.autores),
            joinedload(Ejemplar.libro).selectinload(Libro.generos),
            joinedload(Ejemplar.libro).joinedload(Libro.editorial),
            joinedload(Ejemplar.libro).joinedload(Libro.saga),
            joinedload(Ejemplar.estante)
        )
        .where(
            Ejemplar.id == ejemplar_id,
            Ejemplar.usuario_id == usuario_actual.id
        )
    )
    ejemplar = db.execute(stmt).scalar_one_or_none()

    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con ID {ejemplar_id} no encontrado."
        )
    return ejemplar


# ============================================================
# 4. ACTUALIZACIÓN (Reubicación, condición física)
# ============================================================

@router.put("/{ejemplar_id}", response_model=EjemplarResponse)
def actualizar_ejemplar(
    ejemplar_id: int,
    ejemplar_in: EjemplarUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(Ejemplar).where(
        Ejemplar.id == ejemplar_id,
        Ejemplar.usuario_id == usuario_actual.id
    )
    ejemplar = db.execute(stmt).scalar_one_or_none()

    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con ID {ejemplar_id} no encontrado."
        )

    # Reubicación y control de capacidad verificando propiedad del estante
    if ejemplar_in.estante_id is not None and ejemplar_in.estante_id != ejemplar.estante_id:
        stmt_estante = (
            select(Estante)
            .join(Biblioteca, Estante.biblioteca_id == Biblioteca.id)
            .where(
                Estante.id == ejemplar_in.estante_id,
                Biblioteca.usuario_id == usuario_actual.id
            )
        )
        nuevo_estante = db.execute(stmt_estante).scalar_one_or_none()
        if not nuevo_estante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El estante destino no existe o no pertenece a tus bibliotecas."
            )

        ocupacion_nueva = calcular_ocupacion_estante(nuevo_estante.id, db)
        if ocupacion_nueva >= nuevo_estante.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El estante destino '{nuevo_estante.nombre}' está lleno."
            )
        ejemplar.estante_id = ejemplar_in.estante_id

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
# 5. BAJA LÓGICA (Reglas 6.2 y 6.7)
# ============================================================

@router.delete("/{ejemplar_id}", status_code=status.HTTP_204_NO_CONTENT)
def dar_de_baja_ejemplar(
    ejemplar_id: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(Ejemplar).where(
        Ejemplar.id == ejemplar_id,
        Ejemplar.usuario_id == usuario_actual.id
    )
    ejemplar = db.execute(stmt).scalar_one_or_none()

    if not ejemplar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ejemplar con ID {ejemplar_id} no encontrado."
        )

    # No permitir baja si posee un préstamo activo o vencido
    stmt_prestamo = select(Prestamo).where(
        Prestamo.ejemplar_id == ejemplar.id,
        Prestamo.estado.in_([EstadoPrestamo.ACTIVO.value, EstadoPrestamo.VENCIDO.value])
    )
    prestamo_en_curso = db.execute(stmt_prestamo).scalar_one_or_none()

    if prestamo_en_curso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede dar de baja el ejemplar porque posee un préstamo en curso. Registrá la devolución primero."
        )

    ejemplar.activo = False
    ejemplar.estante_id = None
    db.commit()
    return None