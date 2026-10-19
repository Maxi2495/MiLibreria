from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EstadoPrestamo(str, Enum):
    ACTIVO = "ACTIVO"
    VENCIDO = "VENCIDO"
    DEVUELTO = "DEVUELTO"
    CANCELADO = "CANCELADO"


class PrestamoBase(BaseModel):
    nombre_destinatario: str = Field(..., min_length=2, max_length=100, description="Nombre de quien recibe el ejemplar")
    apellido_destinatario: str = Field(..., min_length=2, max_length=100, description="Apellido de quien recibe el ejemplar")
    telefono_destinatario: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto opcional")
    email_destinatario: Optional[EmailStr] = Field(None, description="Correo electrónico opcional")
    fecha_prevista_devolucion: Optional[date] = Field(None, description="Fecha pactada de devolución")


class PrestamoCreate(PrestamoBase):
    ejemplar_id: int = Field(..., gt=0, description="ID del ejemplar físico a prestar")

    @field_validator("fecha_prevista_devolucion")
    @classmethod
    def validar_fecha_prevista(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise ValueError("La fecha prevista de devolución no puede ser anterior a la fecha actual.")
        return v


class PrestamoDevolucion(BaseModel):
    fecha_devolucion: Optional[date] = Field(default_factory=date.today, description="Fecha efectiva de devolución")
    estante_id: Optional[int] = Field(
        None, gt=0, description="ID del estante donde se ubicará. Enviar null si queda sin ubicación asignada."
    )

    @field_validator("fecha_devolucion")
    @classmethod
    def validar_fecha_devolucion(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("La fecha de devolución no puede ser una fecha futura.")
        return v


class PrestamoResponse(PrestamoBase):
    id: int
    ejemplar_id: int
    fecha_prestamo: date
    fecha_devolucion: Optional[date] = None
    estado: EstadoPrestamo

    model_config = ConfigDict(from_attributes=True)