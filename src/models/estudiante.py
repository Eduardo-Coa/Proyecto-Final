from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from src.exceptions.validation_errors import (
    CodigoInvalidoError,
    CorreoInvalidoError,
    EdadInvalidaError,
    SemestreInvalidoError,
    ValidationError,
)
from src.utils.constantes_negocio import (
    EDAD_MINIMA,
    SEMESTRE_MAXIMO,
    SEMESTRE_MINIMO,
)


_REGEX_CODIGO = re.compile(r"^EST\d{3,6}$")
_REGEX_CORREO = re.compile(r"^[\w\.\-]+@[\w\-]+\.[\w\.\-]+$")


@dataclass
class Estudiante:
    """Representa un estudiante registrado en la plataforma de bienestar.

    Args:
        codigo: código institucional único (ej. 'EST0001').
        nombre_completo: nombre y apellidos del estudiante.
        edad: edad en años cumplidos (debe ser >= 16).
        semestre: semestre académico actual (entre 1 y 12).
        correo: correo institucional con formato válido.
        programa: programa académico que cursa.
        fecha_registro: fecha y hora de registro (por defecto, ahora).
    """

    codigo: str
    nombre_completo: str
    edad: int
    semestre: int
    correo: str
    programa: str
    fecha_registro: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._validar_codigo()
        self._validar_nombre()
        self._validar_edad()
        self._validar_semestre()
        self._validar_correo()
        self._validar_programa()

    def _validar_codigo(self) -> None:
        if not self.codigo or not isinstance(self.codigo, str):
            raise ValidationError("El código institucional es obligatorio.")
        if not _REGEX_CODIGO.match(self.codigo):
            raise CodigoInvalidoError(self.codigo)

    def _validar_nombre(self) -> None:
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValidationError("El nombre completo es obligatorio.")
        if len(self.nombre_completo.strip()) < 3:
            raise ValidationError("El nombre completo debe tener al menos 3 caracteres.")

    def _validar_edad(self) -> None:
        if not isinstance(self.edad, int) or isinstance(self.edad, bool):
            raise ValidationError("La edad debe ser un número entero.")
        if self.edad < EDAD_MINIMA:
            raise EdadInvalidaError(self.edad)
        if self.edad > 100:
            raise EdadInvalidaError(self.edad)

    def _validar_semestre(self) -> None:
        if not isinstance(self.semestre, int) or isinstance(self.semestre, bool):
            raise ValidationError("El semestre debe ser un número entero.")
        if not (SEMESTRE_MINIMO <= self.semestre <= SEMESTRE_MAXIMO):
            raise SemestreInvalidoError(self.semestre)

    def _validar_correo(self) -> None:
        if not self.correo or not isinstance(self.correo, str):
            raise ValidationError("El correo es obligatorio.")
        if not _REGEX_CORREO.match(self.correo):
            raise CorreoInvalidoError(self.correo)

    def _validar_programa(self) -> None:
        if not self.programa or not self.programa.strip():
            raise ValidationError("El programa académico es obligatorio.")

    def to_dict(self) -> dict:
        """Serializa el estudiante a diccionario para persistencia JSON."""
        return {
            "codigo": self.codigo,
            "nombre_completo": self.nombre_completo,
            "edad": self.edad,
            "semestre": self.semestre,
            "correo": self.correo,
            "programa": self.programa,
            "fecha_registro": self.fecha_registro.isoformat(),
        }

    @classmethod
    def from_dict(cls, datos: dict) -> Estudiante:
        """Reconstruye un Estudiante desde un diccionario JSON."""
        return cls(
            codigo=datos["codigo"],
            nombre_completo=datos["nombre_completo"],
            edad=datos["edad"],
            semestre=datos["semestre"],
            correo=datos["correo"],
            programa=datos["programa"],
            fecha_registro=datetime.fromisoformat(datos["fecha_registro"]),
        )
