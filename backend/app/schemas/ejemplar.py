from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal
from enum import Enum
from app.schemas.catalogo import LibroResponse


# ============================================================
# ENUM DE ESTADO FÍSICO (Restricción CHECK de MySQL)
# ============================================================

class EstadoFisicoEnum(str, Enum):
    NUEVO = "NUEVO"
    MUY_BUENO = "MUY_BUENO"
    BUENO = "BUENO"
    REGULAR = "REGULAR"
    DETERIORADO = "DETERIORADO"


# ============================================================
# SCHEMAS DE EJEMPLAR
# ============================================================

class EjemplarBase(BaseModel):
    libro_id: int = Field(..., description="ID del libro del catálogo")
    estante_id: Optional[int] = Field(None, description="ID del estante donde se ubica físicamente (opcional)")
    fecha_adquisicion: Optional[date] = Field(None, description="Fecha de compra o incorporación")
    estado_fisico: Optional[EstadoFisicoEnum] = Field(None, description="Condición física de conservación")
    precio_compra: Optional[Decimal] = Field(None, ge=0, description="Precio pagado (no negativo)")
    moneda: Optional[str] = Field(None, max_length=10, description="Moneda (ej: ARS, USD)")
    observacion: Optional[str] = Field(None, description="Notas sobre dedicatorias, faltantes, etc.")

class EjemplarCreate(EjemplarBase):
    pass

class EjemplarUpdate(BaseModel):
    estante_id: Optional[int] = None
    fecha_adquisicion: Optional[date] = None
    estado_fisico: Optional[EstadoFisicoEnum] = None
    precio_compra: Optional[Decimal] = Field(None, ge=0)
    moneda: Optional[str] = Field(None, max_length=10)
    observacion: Optional[str] = None
    activo: Optional[bool] = None

class EjemplarResponse(EjemplarBase):
    id: int
    usuario_id: int
    activo: bool
    libro: Optional[LibroResponse] = None

    model_config = ConfigDict(from_attributes=True)