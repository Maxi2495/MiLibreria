from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    fecha_registro: datetime
    estado: str

    model_config = ConfigDict(from_attributes=True)