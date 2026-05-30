"""Modelo de dominio para psicólogos del sistema."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.exceptions.validation_errors import CampoRequeridoError, CorreoInvalidoError


CORREO_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(slots=True)
class Psicologo:
    """Representa a un profesional que realiza sesiones de seguimiento."""

    id: str
    nombre: str
    correo: str
    especialidad: str

    def __post_init__(self) -> None:
        self.id = self.id.strip()
        self.nombre = self.nombre.strip()
        self.correo = self.correo.strip()
        self.especialidad = self.especialidad.strip()
        self._validar()

    def _validar(self) -> None:
        if not self.id:
            raise CampoRequeridoError("id")
        if not self.nombre:
            raise CampoRequeridoError("nombre")
        if not self.especialidad:
            raise CampoRequeridoError("especialidad")
        if not CORREO_REGEX.match(self.correo):
            raise CorreoInvalidoError(self.correo)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "especialidad": self.especialidad,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Psicologo":
        return cls(
            id=str(data["id"]),
            nombre=str(data["nombre"]),
            correo=str(data["correo"]),
            especialidad=str(data["especialidad"]),
        )
