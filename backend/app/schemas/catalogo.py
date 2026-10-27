from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from typing import Optional, List
from datetime import date
from decimal import Decimal


# ============================================================
# SCHEMAS DE AUTOR
# ============================================================

class AutorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre completo del autor")

class AutorCreate(AutorBase):
    pass

class AutorResponse(AutorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SCHEMAS DE EDITORIAL
# ============================================================

class EditorialBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre de la editorial")

class EditorialCreate(EditorialBase):
    pass

class EditorialResponse(EditorialBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SCHEMAS DE GENERO
# ============================================================

class GeneroBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del género literario")

class GeneroCreate(GeneroBase):
    pass

class GeneroResponse(GeneroBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SCHEMAS DE SAGA
# ============================================================

class SagaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre de la saga o serie")

class SagaCreate(SagaBase):
    pass

class SagaResponse(SagaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SCHEMAS DE LIBRO (CATÁLOGO BIBLIOGRÁFICO)
# ============================================================

class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255, description="Título de la obra")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN de la edición")
    fecha_publicacion: Optional[date] = Field(None, description="Fecha de publicación de la edición")
    sinopsis: Optional[str] = Field(None, description="Sinopsis o resumen de la obra")
    portada_url: Optional[str] = Field(None, max_length=500, description="URL pública de la portada")
    editorial_id: Optional[int] = Field(None, description="ID de la editorial asociada")
    saga_id: Optional[int] = Field(None, description="ID de la saga asociada")
    posicion_saga: Optional[Decimal] = Field(None, description="Número de libro en la saga (ej: 1.5)")

class LibroCreate(LibroBase):
    # Regla de negocio 6.2: La carga manual requiere al menos un autor
    autores_ids: List[int] = Field(..., min_length=1, description="Lista de IDs de autores vinculados (mínimo 1)")
    generos_ids: Optional[List[int]] = Field(default_factory=list, description="Lista de IDs de géneros literarios")

class LibroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    fecha_publicacion: Optional[date] = None
    sinopsis: Optional[str] = None
    portada_url: Optional[str] = Field(None, max_length=500)
    editorial_id: Optional[int] = None
    saga_id: Optional[int] = None
    posicion_saga: Optional[Decimal] = None
    autores_ids: Optional[List[int]] = Field(None, min_length=1)
    generos_ids: Optional[List[int]] = None

class LibroResponse(LibroBase):
    id: int
    editorial: Optional[EditorialResponse] = None
    saga: Optional[SagaResponse] = None
    autores: List[AutorResponse] = []
    generos: List[GeneroResponse] = []

    model_config = ConfigDict(from_attributes=True)
    
# ============================================================
# SCHEMAS DE ISBN
# ============================================================
class LibroISBNResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    isbn: str
    titulo: str
    autores: List[str] = []
    editorial: Optional[str] = None
    fecha_publicacion: Optional[str] = None
    sinopsis: Optional[str] = None
    generos: List[str] = []
    portada_url: Optional[str] = None