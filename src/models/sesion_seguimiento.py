"""Modelo de dominio para sesiones de seguimiento psicológico."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from src.exceptions.validation_errors import (
    CampoRequeridoError,
    DuracionInvalidaError,
    FechaInvalidaError,
)
from src.utils.constantes_negocio import DURACION_MINIMA_SESION


class EstadoSesion(str, Enum):
    """Estados posibles de una sesión de seguimiento."""

    AGENDADA = "AGENDADA"
    REALIZADA = "REALIZADA"
    CANCELADA = "CANCELADA"


@dataclass(slots=True)
class SesionSeguimiento:
    """Representa una sesión programada entre un estudiante y un psicólogo."""

    codigo_estudiante: str
    id_psicologo: str
    fecha_hora: datetime
    duracion_minutos: int
    motivo: str
    estado: EstadoSesion = EstadoSesion.AGENDADA
    nota: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.codigo_estudiante = self.codigo_estudiante.strip()
        self.id_psicologo = self.id_psicologo.strip()
        self.motivo = self.motivo.strip()
        self.nota = self.nota.strip()
        self.estado = self._normalizar_estado(self.estado)
        self._validar()

    def _validar(self) -> None:
        if not self.id.strip():
            raise CampoRequeridoError("id")
        if not self.codigo_estudiante:
            raise CampoRequeridoError("codigo_estudiante")
        if not self.id_psicologo:
            raise CampoRequeridoError("id_psicologo")
        if not self.motivo:
            raise CampoRequeridoError("motivo")
        if not isinstance(self.fecha_hora, datetime):
            raise FechaInvalidaError("La fecha y hora de la sesión debe ser un datetime válido.")
        if self.duracion_minutos < DURACION_MINIMA_SESION:
            raise DuracionInvalidaError(self.duracion_minutos, DURACION_MINIMA_SESION)

    @staticmethod
    def _normalizar_estado(estado: EstadoSesion | str) -> EstadoSesion:
        if isinstance(estado, EstadoSesion):
            return estado
        try:
            return EstadoSesion(str(estado).upper())
        except ValueError as exc:
            raise FechaInvalidaError(
                "El estado de la sesión debe ser AGENDADA, REALIZADA o CANCELADA."
            ) from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "codigo_estudiante": self.codigo_estudiante,
            "id_psicologo": self.id_psicologo,
            "fecha_hora": self.fecha_hora.isoformat(),
            "duracion_minutos": self.duracion_minutos,
            "motivo": self.motivo,
            "estado": self.estado.value,
            "nota": self.nota,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SesionSeguimiento":
        fecha_hora = data["fecha_hora"]
        if isinstance(fecha_hora, str):
            fecha_hora = datetime.fromisoformat(fecha_hora)

        return cls(
            id=str(data["id"]),
            codigo_estudiante=str(data["codigo_estudiante"]),
            id_psicologo=str(data["id_psicologo"]),
            fecha_hora=fecha_hora,
            duracion_minutos=int(data["duracion_minutos"]),
            motivo=str(data["motivo"]),
            estado=data.get("estado", EstadoSesion.AGENDADA.value),
            nota=str(data.get("nota", "")),
        )
