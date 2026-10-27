from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import List, Optional, Literal

from app.db.session import get_db
from app.models.catalogo import Autor, Editorial, Genero, Saga, Libro
from app.schemas.catalogo import (
    AutorCreate, AutorResponse,
    EditorialCreate, EditorialResponse,
    GeneroCreate, GeneroResponse,
    SagaCreate, SagaResponse,
    LibroCreate, LibroResponse, LibroISBNResponse
)
from app.services.isbn_service import isbn_service
from app.dependencies import get_current_user
from app.models.usuario import Usuario


router = APIRouter(prefix="/catalogo", tags=["Catálogo de Libros"])


# ============================================================
# 1. GESTIÓN DE AUTORES
# ============================================================

@router.post("/autores", response_model=AutorResponse, status_code=status.HTTP_201_CREATED)
def crear_autor(autor_in: AutorCreate, db: Session = Depends(get_db)):
    existente = db.query(Autor).filter(Autor.nombre.ilike(autor_in.nombre.strip())).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un autor registrado con el nombre '{autor_in.nombre}'."
        )
    
    nuevo_autor = Autor(nombre=autor_in.nombre.strip())
    db.add(nuevo_autor)
    db.commit()
    db.refresh(nuevo_autor)
    return nuevo_autor


@router.get("/autores", response_model=List[AutorResponse])
def listar_autores(
    buscar: Optional[str] = Query(None, description="Filtrar por coincidencia en el nombre"),
    db: Session = Depends(get_db)
):
    query = db.query(Autor)
    if buscar:
        query = query.filter(Autor.nombre.ilike(f"%{buscar}%"))
    return query.order_by(Autor.nombre.asc()).all()


# ============================================================
# 2. GESTIÓN DE EDITORIALES
# ============================================================

@router.post("/editoriales", response_model=EditorialResponse, status_code=status.HTTP_201_CREATED)
def crear_editorial(editorial_in: EditorialCreate, db: Session = Depends(get_db)):
    existente = db.query(Editorial).filter(Editorial.nombre.ilike(editorial_in.nombre.strip())).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una editorial con el nombre '{editorial_in.nombre}'."
        )
    
    nueva_editorial = Editorial(nombre=editorial_in.nombre.strip())
    db.add(nueva_editorial)
    db.commit()
    db.refresh(nueva_editorial)
    return nueva_editorial


@router.get("/editoriales", response_model=List[EditorialResponse])
def listar_editoriales(db: Session = Depends(get_db)):
    return db.query(Editorial).order_by(Editorial.nombre.asc()).all()


# ============================================================
# 3. GESTIÓN DE GÉNEROS
# ============================================================

@router.post("/generos", response_model=GeneroResponse, status_code=status.HTTP_201_CREATED)
def crear_genero(genero_in: GeneroCreate, db: Session = Depends(get_db)):
    existente = db.query(Genero).filter(Genero.nombre.ilike(genero_in.nombre.strip())).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe el género '{genero_in.nombre}'."
        )
    
    nuevo_genero = Genero(nombre=genero_in.nombre.strip())
    db.add(nuevo_genero)
    db.commit()
    db.refresh(nuevo_genero)
    return nuevo_genero


@router.get("/generos", response_model=List[GeneroResponse])
def listar_generos(db: Session = Depends(get_db)):
    return db.query(Genero).order_by(Genero.nombre.asc()).all()


# ============================================================
# 4. GESTIÓN DE SAGAS
# ============================================================

@router.post("/sagas", response_model=SagaResponse, status_code=status.HTTP_201_CREATED)
def crear_saga(saga_in: SagaCreate, db: Session = Depends(get_db)):
    existente = db.query(Saga).filter(Saga.nombre.ilike(saga_in.nombre.strip())).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una saga con el nombre '{saga_in.nombre}'."
        )
    
    nueva_saga = Saga(nombre=saga_in.nombre.strip())
    db.add(nueva_saga)
    db.commit()
    db.refresh(nueva_saga)
    return nueva_saga


@router.get("/sagas", response_model=List[SagaResponse])
def listar_sagas(db: Session = Depends(get_db)):
    return db.query(Saga).order_by(Saga.nombre.asc()).all()


# ============================================================
# 5. GESTIÓN DE LIBROS (CATÁLOGO BIBLIOGRÁFICO)
# ============================================================

@router.post("/libros", response_model=LibroResponse, status_code=status.HTTP_201_CREATED)
def crear_libro(libro_in: LibroCreate, db: Session = Depends(get_db)):
    # Validar Editorial si fue provista
    if libro_in.editorial_id is not None:
        editorial = db.query(Editorial).filter(Editorial.id == libro_in.editorial_id).first()
        if not editorial:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La editorial con ID {libro_in.editorial_id} no existe."
            )

    # Validar Saga si fue provista
    if libro_in.saga_id is not None:
        saga = db.query(Saga).filter(Saga.id == libro_in.saga_id).first()
        if not saga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La saga con ID {libro_in.saga_id} no existe."
            )

    # Validar existencia de Autores (mínimo 1)
    autores_encontrados = db.query(Autor).filter(Autor.id.in_(libro_in.autores_ids)).all()
    if len(autores_encontrados) != len(set(libro_in.autores_ids)):
        ids_encontrados = {a.id for a in autores_encontrados}
        ids_faltantes = set(libro_in.autores_ids) - ids_encontrados
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Los siguientes IDs de autores no existen: {list(ids_faltantes)}"
        )

    # Validar Géneros si se enviaron
    generos_encontrados = []
    if libro_in.generos_ids:
        generos_encontrados = db.query(Genero).filter(Genero.id.in_(libro_in.generos_ids)).all()
        if len(generos_encontrados) != len(set(libro_in.generos_ids)):
            ids_encontrados = {g.id for g in generos_encontrados}
            ids_faltantes = set(libro_in.generos_ids) - ids_encontrados
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Los siguientes IDs de géneros no existen: {list(ids_faltantes)}"
            )

    nuevo_libro = Libro(
        titulo=libro_in.titulo.strip(),
        isbn=libro_in.isbn.strip() if libro_in.isbn else None,
        fecha_publicacion=libro_in.fecha_publicacion,
        sinopsis=libro_in.sinopsis,
        portada_url=libro_in.portada_url,
        editorial_id=libro_in.editorial_id,
        saga_id=libro_in.saga_id,
        posicion_saga=libro_in.posicion_saga
    )
    nuevo_libro.autores = autores_encontrados
    nuevo_libro.generos = generos_encontrados

    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)
    return nuevo_libro


@router.get("/libros", response_model=List[LibroResponse])
def listar_libros(
    buscar: Optional[str] = Query(None, description="Búsqueda libre en título, ISBN o nombre de autor"),
    titulo: Optional[str] = Query(None, description="Filtrar por coincidencia en el título"),
    autor: Optional[str] = Query(None, description="Filtrar por nombre parcial del autor (ej: Marquez)"),
    autor_id: Optional[int] = Query(None, description="Filtrar por ID exacto de autor"),
    isbn: Optional[str] = Query(None, description="Filtrar por ISBN exacto"),
    genero_id: Optional[int] = Query(None, description="Filtrar por ID de género"),
    editorial_id: Optional[int] = Query(None, description="Filtrar por ID de editorial"),
    saga_id: Optional[int] = Query(None, description="Filtrar por ID de saga"),
    ordenar_por: Literal["titulo", "autor", "fecha_publicacion", "id"] = Query("titulo", description="Criterio de orden (Regla 6.8)"),
    orden_dir: Literal["asc", "desc"] = Query("asc", description="Sentido del ordenamiento"),
    limit: int = Query(50, ge=1, le=100, description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    db: Session = Depends(get_db)
):
    """
    Lista y filtra libros del catálogo según las especificaciones de la Regla 6.8.
    """
    stmt = (
        select(Libro)
        .options(
            selectinload(Libro.autores),
            selectinload(Libro.generos),
            joinedload(Libro.editorial),
            joinedload(Libro.saga)
        )
    )

    # 1. Búsqueda por texto libre unificado (título, ISBN o autor)
    if buscar:
        termino = f"%{buscar.strip()}%"
        stmt = stmt.where(
            or_(
                Libro.titulo.ilike(termino),
                Libro.isbn.ilike(termino),
                Libro.autores.any(Autor.nombre.ilike(termino))
            )
        )

    # 2. Filtros específicos
    if titulo:
        stmt = stmt.where(Libro.titulo.ilike(f"%{titulo.strip()}%"))
    if autor:
        stmt = stmt.where(Libro.autores.any(Autor.nombre.ilike(f"%{autor.strip()}%")))
    if autor_id:
        stmt = stmt.where(Libro.autores.any(Autor.id == autor_id))
    if isbn:
        stmt = stmt.where(Libro.isbn == isbn.strip())
    if genero_id:
        stmt = stmt.where(Libro.generos.any(Genero.id == genero_id))
    if editorial_id:
        stmt = stmt.where(Libro.editorial_id == editorial_id)
    if saga_id:
        stmt = stmt.where(Libro.saga_id == saga_id)

    # 3. Criterios de ordenamiento dinámico
    if ordenar_por == "autor":
        stmt = stmt.outerjoin(Libro.autores)
        columna_orden = Autor.nombre
    else:
        columna_orden = getattr(Libro, ordenar_por)

    if orden_dir == "desc":
        stmt = stmt.order_by(columna_orden.desc())
    else:
        stmt = stmt.order_by(columna_orden.asc())

    # 4. Paginación y ejecución desduplicada
    stmt = stmt.limit(limit).offset(offset)
    libros = db.execute(stmt).scalars().unique().all()
    return libros


@router.get("/libros/{libro_id}", response_model=LibroResponse)
def obtener_libro(libro_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Libro)
        .options(
            selectinload(Libro.autores),
            selectinload(Libro.generos),
            joinedload(Libro.editorial),
            joinedload(Libro.saga)
        )
        .where(Libro.id == libro_id)
    )
    libro = db.execute(stmt).scalar_one_or_none()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El libro con ID {libro_id} no fue encontrado."
        )
    return libro

# ============================================================
# 5. GESTIÓN DE LIBROS POR ISBN
# ============================================================
@router.get(
    "/isbn/{isbn}",
    response_model=LibroISBNResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar metadatos bibliográficos por ISBN",
    description="Consulta un servicio externo (Google Books) para autocompletar metadatos de un libro. Si no existe o falla, devuelve códigos HTTP controlados para permitir la carga manual."
)
async def obtener_libro_por_isbn(
    isbn: str,
    current_user: Usuario = Depends(get_current_user)  
) -> LibroISBNResponse:
    return await isbn_service.consultar_por_isbn(isbn_raw=isbn)