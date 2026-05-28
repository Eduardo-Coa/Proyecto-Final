"""Repositorio JSON para sesiones de seguimiento."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.sesion_seguimiento import SesionSeguimiento
from src.services.interfaces import IRepository


class SesionRepository(IRepository[SesionSeguimiento]):
    """Gestiona la persistencia de sesiones en un archivo JSON."""

    def __init__(self, ruta: Path | str = "data/sesiones.json") -> None:
        self.ruta = Path(ruta)

    def crear(self, entidad: SesionSeguimiento) -> SesionSeguimiento:
        sesiones = self._cargar()
        if any(sesion.id == entidad.id for sesion in sesiones):
            raise DuplicateEntityError(f"Ya existe una sesión con id '{entidad.id}'.")

        sesiones.append(entidad)
        self._guardar(sesiones)
        return entidad

    def listar(self) -> list[SesionSeguimiento]:
        return self._cargar()

    def buscar_por_codigo(self, codigo: str) -> SesionSeguimiento:
        codigo_normalizado = codigo.strip()
        for sesion in self._cargar():
            if sesion.id == codigo_normalizado:
                return sesion

        raise EntityNotFoundError(f"No existe una sesión con id '{codigo_normalizado}'.")

    def actualizar(self, entidad: SesionSeguimiento) -> SesionSeguimiento:
        sesiones = self._cargar()
        for indice, actual in enumerate(sesiones):
            if actual.id == entidad.id:
                sesiones[indice] = entidad
                self._guardar(sesiones)
                return entidad

        raise EntityNotFoundError(f"No existe una sesión con id '{entidad.id}'.")

    def eliminar(self, codigo: str) -> None:
        codigo_normalizado = codigo.strip()
        sesiones = self._cargar()
        filtradas = [sesion for sesion in sesiones if sesion.id != codigo_normalizado]

        if len(filtradas) == len(sesiones):
            raise EntityNotFoundError(f"No existe una sesión con id '{codigo_normalizado}'.")

        self._guardar(filtradas)

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[SesionSeguimiento]:
        codigo_normalizado = codigo_estudiante.strip()
        return [
            sesion
            for sesion in self._cargar()
            if sesion.codigo_estudiante == codigo_normalizado
        ]

    def _cargar(self) -> list[SesionSeguimiento]:
        if not self.ruta.exists():
            return []

        try:
            with self.ruta.open("r", encoding="utf-8") as archivo:
                datos: Any = json.load(archivo)
        except JSONDecodeError as exc:
            raise ArchivoCorruptoError(
                f"El archivo '{self.ruta}' no contiene JSON válido."
            ) from exc

        if not isinstance(datos, list):
            raise ArchivoCorruptoError(
                f"El archivo '{self.ruta}' debe contener una lista de sesiones."
            )

        return [SesionSeguimiento.from_dict(item) for item in datos]

    def _guardar(self, sesiones: list[SesionSeguimiento]) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("w", encoding="utf-8") as archivo:
            json.dump(
                [sesion.to_dict() for sesion in sesiones],
                archivo,
                ensure_ascii=False,
                indent=2,
            )
