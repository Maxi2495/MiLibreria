
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EstadoLecturaEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_CURSO = "EN_CURSO"
    LEIDO = "LEIDO"
    ABANDONADO = "ABANDONADO"


class LecturaBase(BaseModel):
    estado: EstadoLecturaEnum = EstadoLecturaEnum.PENDIENTE
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    calificacion: Optional[int] = Field(default=None, ge=1, le=5)
    resena: Optional[str] = None

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha de finalización no puede ser anterior a la de inicio"
            )
        return self


class LecturaCreate(LecturaBase):
    ejemplar_id: int = Field(..., gt=0)



class LecturaUpdate(BaseModel):
    estado: Optional[EstadoLecturaEnum] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    calificacion: Optional[int] = Field(default=None, ge=1, le=5)
    resena: Optional[str] = None

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError(
                "La fecha de finalización no puede ser anterior a la de inicio"
            )
        return self


class LecturaResponse(LecturaBase):
    id: int
    ejemplar_id: int

    model_config = ConfigDict(from_attributes=True)
