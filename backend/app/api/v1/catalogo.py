from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.catalogo import Autor, Editorial, Genero, Saga, Libro
from app.schemas.catalogo import (
    AutorCreate, AutorResponse,
    EditorialCreate, EditorialResponse,
    GeneroCreate, GeneroResponse,
    SagaCreate, SagaResponse,
    LibroCreate, LibroResponse
)

router = APIRouter(prefix="/catalogo", tags=["Catálogo de Libros"])


# ============================================================
# 1. GESTIÓN DE AUTORES
# ============================================================

@router.post("/autores", response_model=AutorResponse, status_code=status.HTTP_201_CREATED)
def crear_autor(autor_in: AutorCreate, db: Session = Depends(get_db)):
    # Validación de unicidad de nombre de autor
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
# 5. GESTIÓN DE LIBROS (EDICIONES BIBLIOGRÁFICAS)
# ============================================================

@router.post("/libros", response_model=LibroResponse, status_code=status.HTTP_201_CREATED)
def crear_libro(libro_in: LibroCreate, db: Session = Depends(get_db)):
    # A. Validar que la Editorial exista si se proporcionó
    if libro_in.editorial_id is not None:
        editorial = db.query(Editorial).filter(Editorial.id == libro_in.editorial_id).first()
        if not editorial:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La editorial con ID {libro_in.editorial_id} no existe."
            )

    # B. Validar que la Saga exista si se proporcionó
    if libro_in.saga_id is not None:
        saga = db.query(Saga).filter(Saga.id == libro_in.saga_id).first()
        if not saga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La saga con ID {libro_in.saga_id} no existe."
            )

    # C. Validar existencia de Autores (Regla 6.2: Mínimo un autor)
    autores_encontrados = db.query(Autor).filter(Autor.id.in_(libro_in.autores_ids)).all()
    if len(autores_encontrados) != len(set(libro_in.autores_ids)):
        ids_encontrados = {a.id for a in autores_encontrados}
        ids_faltantes = set(libro_in.autores_ids) - ids_encontrados
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Los siguientes IDs de autores no existen: {list(ids_faltantes)}"
        )

    # D. Validar existencia de Géneros si se enviaron
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

    # E. Instanciar y persistir el Libro
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

    # Asignación de relaciones N:M
    nuevo_libro.autores = autores_encontrados
    nuevo_libro.generos = generos_encontrados

    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)
    return nuevo_libro


@router.get("/libros", response_model=List[LibroResponse])
def listar_libros(
    titulo: Optional[str] = Query(None, description="Filtrar por coincidencia en el título"),
    isbn: Optional[str] = Query(None, description="Filtrar por ISBN exacto"),
    autor_id: Optional[int] = Query(None, description="Filtrar libros por autor"),
    genero_id: Optional[int] = Query(None, description="Filtrar libros por género"),
    db: Session = Depends(get_db)
):
    query = db.query(Libro)

    # Filtros según Regla de negocio 6.8
    if titulo:
        query = query.filter(Libro.titulo.ilike(f"%{titulo}%"))
    if isbn:
        query = query.filter(Libro.isbn == isbn.strip())
    if autor_id:
        query = query.filter(Libro.autores.any(Autor.id == autor_id))
    if genero_id:
        query = query.filter(Libro.generos.any(Genero.id == genero_id))

    return query.order_by(Libro.titulo.asc()).all()


@router.get("/libros/{libro_id}", response_model=LibroResponse)
def obtener_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El libro con ID {libro_id} no fue encontrado."
        )
    return libro