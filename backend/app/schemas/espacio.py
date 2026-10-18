from pydantic import BaseModel, Field
from typing import List, Optional

# --- SCHEMAS DE ESTANTE ---

class EstanteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre o número del estante")
    capacidad: int = Field(..., gt=0, description="Capacidad máxima de ejemplares (mayor a 0)")

class EstanteCreate(EstanteBase):
    pass

class EstanteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    capacidad: Optional[int] = Field(None, gt=0)
    
class EstanteResponse(EstanteBase):
    id: int
    biblioteca_id: int

    class Config:
        from_attributes = True


# --- SCHEMAS DE BIBLIOTECA ---

class BibliotecaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la biblioteca o espacio")

class BibliotecaCreate(BibliotecaBase):
    pass

class BibliotecaUpdate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)

class BibliotecaResponse(BibliotecaBase):
    id: int
    usuario_id: int
    estantes: List[EstanteResponse] = []

    class Config:
        from_attributes = True