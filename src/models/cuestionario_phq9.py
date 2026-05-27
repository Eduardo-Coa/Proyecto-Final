from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.exceptions.validation_errors import FechaInvalidaError, PuntajeInvalidoError
from src.utils.constantes_negocio import (
    NUM_ITEMS_PHQ9,
    PUNTAJE_MAXIMO_ITEM,
    PUNTAJE_MINIMO_ITEM,
    PUNTAJE_RIESGO_LEVE_PHQ9,
    PUNTAJE_RIESGO_MODERADO_PHQ9,
    PUNTAJE_RIESGO_MODSEVERO_PHQ9,
    PUNTAJE_RIESGO_SEVERO_PHQ9,
)

TEXTOS_ITEMS_PHQ9 = [
    "1. Poco interés o placer en hacer las cosas",
    "2. Sentirse decaído, deprimido o sin esperanza",
    "3. Problemas para dormir o permanecer dormido",
    "4. Cansancio o poca energía",
    "5. Poco apetito o comer en exceso",
    "6. Sentirse mal consigo mismo o que es un fracaso",
    "7. Problemas para concentrarse en actividades",
    "8. Moverse o hablar tan lento que otras personas lo notan",
    "9. Pensamientos de hacerse daño o de que estaría mejor muerto",
]

OPCIONES_RESPUESTA = [
    "0 - Nunca",
    "1 - Varios días",
    "2 - Más de la mitad de los días",
    "3 - Casi todos los días",
]


@dataclass
class CuestionarioPHQ9:
    """Representa una aplicación del cuestionario PHQ-9 (depresión).

    Args:
        codigo_estudiante: código institucional del estudiante evaluado.
        respuestas: lista de 9 valores enteros entre 0 y 3.
        fecha_aplicacion: fecha y hora de aplicación del cuestionario.
        id: identificador único (generado automáticamente si no se provee).
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
        if len(self.respuestas) != NUM_ITEMS_PHQ9:
            raise PuntajeInvalidoError(len(self.respuestas), (NUM_ITEMS_PHQ9, NUM_ITEMS_PHQ9))
        for i, valor in enumerate(self.respuestas, start=1):
            if not (PUNTAJE_MINIMO_ITEM <= valor <= PUNTAJE_MAXIMO_ITEM):
                raise PuntajeInvalidoError(valor, (PUNTAJE_MINIMO_ITEM, PUNTAJE_MAXIMO_ITEM))

    def _calcular_puntaje(self) -> int:
        return sum(self.respuestas)

    def _clasificar_severidad(self) -> str:
        if self.puntaje_total >= PUNTAJE_RIESGO_SEVERO_PHQ9:
            return "Severo"
        if self.puntaje_total >= PUNTAJE_RIESGO_MODSEVERO_PHQ9:
            return "Moderadamente severo"
        if self.puntaje_total >= PUNTAJE_RIESGO_MODERADO_PHQ9:
            return "Moderado"
        if self.puntaje_total >= PUNTAJE_RIESGO_LEVE_PHQ9:
            return "Leve"
        return "Mínimo"

    @property
    def es_riesgo_severo(self) -> bool:
        """True si el puntaje supera el umbral de riesgo severo (≥ 20)."""
        return self.puntaje_total >= PUNTAJE_RIESGO_SEVERO_PHQ9

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
    def from_dict(cls, datos: dict) -> CuestionarioPHQ9:
        """Reconstruye un CuestionarioPHQ9 desde un diccionario JSON."""
        return cls(
            id=datos["id"],
            codigo_estudiante=datos["codigo_estudiante"],
            respuestas=datos["respuestas"],
            fecha_aplicacion=datetime.fromisoformat(datos["fecha_aplicacion"]),
        )
