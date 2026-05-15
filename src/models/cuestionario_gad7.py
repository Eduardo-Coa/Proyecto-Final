from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.exceptions.validation_errors import PuntajeInvalidoError, FechaInvalidaError
from src.utils.constantes_negocio import (
    NUM_ITEMS_GAD7,
    PUNTAJE_MINIMO_ITEM,
    PUNTAJE_MAXIMO_ITEM,
    PUNTAJE_RIESGO_SEVERO_GAD7,
    PUNTAJE_RIESGO_MODERADO_GAD7,
    PUNTAJE_RIESGO_LEVE_GAD7,
)


@dataclass
class CuestionarioGAD7:
    """Representa una aplicación del cuestionario GAD-7 (ansiedad generalizada).

    Args:
        codigo_estudiante: código institucional del estudiante evaluado.
        respuestas: lista de 7 valores enteros entre 0 y 3.
        fecha_aplicacion: fecha y hora de aplicación del cuestionario.
        id: identificador único del cuestionario (generado automáticamente).
        puntaje_total: suma de respuestas (calculado automáticamente).
        nivel_severidad: clasificación textual de severidad (calculada automáticamente).
    """

    codigo_estudiante: str
    respuestas: list[int]
    fecha_aplicacion: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    puntaje_total: int = field(init=False)
    nivel_severidad: str = field(init=False)

    def __post_init__(self) -> None:
        self._validar_fecha()
        self._validar_respuestas()
        self.puntaje_total = self._calcular_puntaje()
        self.nivel_severidad = self._clasificar_severidad()

    def _validar_fecha(self) -> None:
        if self.fecha_aplicacion > datetime.now():
            raise FechaInvalidaError("La fecha de aplicación no puede ser futura.")

    def _validar_respuestas(self) -> None:
        if len(self.respuestas) != NUM_ITEMS_GAD7:
            raise PuntajeInvalidoError(
                f"El GAD-7 requiere exactamente {NUM_ITEMS_GAD7} respuestas, "
                f"se recibieron {len(self.respuestas)}."
            )
        for i, valor in enumerate(self.respuestas, start=1):
            if not (PUNTAJE_MINIMO_ITEM <= valor <= PUNTAJE_MAXIMO_ITEM):
                raise PuntajeInvalidoError(
                    f"El ítem {i} tiene valor {valor}. "
                    f"Debe estar entre {PUNTAJE_MINIMO_ITEM} y {PUNTAJE_MAXIMO_ITEM}."
                )

    def _calcular_puntaje(self) -> int:
        return sum(self.respuestas)

    def _clasificar_severidad(self) -> str:
        if self.puntaje_total >= PUNTAJE_RIESGO_SEVERO_GAD7:
            return "Severo"
        if self.puntaje_total >= PUNTAJE_RIESGO_MODERADO_GAD7:
            return "Moderado"
        if self.puntaje_total >= PUNTAJE_RIESGO_LEVE_GAD7:
            return "Leve"
        return "Mínimo"

    def to_dict(self) -> dict:
        """Serializa el cuestionario a diccionario para persistencia JSON."""
        return {
            "id": self.id,
            "codigo_estudiante": self.codigo_estudiante,
            "respuestas": self.respuestas,
            "puntaje_total": self.puntaje_total,
            "nivel_severidad": self.nivel_severidad,
            "fecha_aplicacion": self.fecha_aplicacion.isoformat(),
        }

    @classmethod
    def from_dict(cls, datos: dict) -> CuestionarioGAD7:
        """Reconstruye un CuestionarioGAD7 desde un diccionario JSON."""
        return cls(
            id=datos["id"],
            codigo_estudiante=datos["codigo_estudiante"],
            respuestas=datos["respuestas"],
            fecha_aplicacion=datetime.fromisoformat(datos["fecha_aplicacion"]),
        )
