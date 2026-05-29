from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TipoAlerta(str, Enum):
    DEPRESION_SEVERA = "DEPRESION_SEVERA"
    ANSIEDAD_SEVERA = "ANSIEDAD_SEVERA"
    COMORBILIDAD = "COMORBILIDAD"


class NivelPrioridad(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


@dataclass
class AlertaRiesgo:
    """Alerta generada automáticamente cuando se detecta riesgo clínico.

    Args:
        codigo_estudiante: código institucional del estudiante en riesgo.
        tipo: tipo de alerta (DEPRESION_SEVERA, ANSIEDAD_SEVERA, COMORBILIDAD).
        puntaje: puntaje que disparó la alerta.
        prioridad: nivel de prioridad de atención.
        id: identificador único (generado automáticamente).
        fecha: fecha y hora de generación (generada automáticamente).
        atendida: indica si el psicólogo ya atendió la alerta.
    """

    codigo_estudiante: str
    tipo: TipoAlerta
    puntaje: int
    prioridad: NivelPrioridad
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha: datetime = field(default_factory=datetime.now)
    atendida: bool = False

    def to_dict(self) -> dict:
        """Serializa la alerta a diccionario para persistencia JSON."""
        return {
            "id": self.id,
            "codigo_estudiante": self.codigo_estudiante,
            "tipo": self.tipo.value,
            "puntaje": self.puntaje,
            "prioridad": self.prioridad.value,
            "fecha": self.fecha.isoformat(),
            "atendida": self.atendida,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> AlertaRiesgo:
        """Reconstruye una AlertaRiesgo desde un diccionario JSON."""
        return cls(
            id=datos["id"],
            codigo_estudiante=datos["codigo_estudiante"],
            tipo=TipoAlerta(datos["tipo"]),
            puntaje=datos["puntaje"],
            prioridad=NivelPrioridad(datos["prioridad"]),
            fecha=datetime.fromisoformat(datos["fecha"]),
            atendida=datos["atendida"],
        )
