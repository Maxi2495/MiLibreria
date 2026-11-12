from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WishlistCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=255)
    autor_referencia: Optional[str] = Field(default=None, max_length=500)
    isbn: Optional[str] = Field(default=None, max_length=20)
    libro_id: Optional[int] = None


class WishlistResponse(BaseModel):
    id: int
    usuario_id: int
    libro_id: Optional[int]
    titulo: str
    autor_referencia: Optional[str]
    isbn: Optional[str]
    estado: str
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)

class WishlistAdquirir(BaseModel):
    libro_id: Optional[int] = None
    estante_id: Optional[int] = None