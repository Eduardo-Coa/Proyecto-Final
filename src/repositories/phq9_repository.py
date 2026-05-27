from __future__ import annotations

import json
from pathlib import Path

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.cuestionario_phq9 import CuestionarioPHQ9
from src.interfaces.interfaces import IRepository


class PHQ9JsonRepository(IRepository[CuestionarioPHQ9]):
    """Repositorio JSON para cuestionarios PHQ-9.

    Args:
        ruta: ruta al archivo JSON de persistencia.
    """

    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta

    def crear(self, entidad: CuestionarioPHQ9) -> CuestionarioPHQ9:
        """Persiste un nuevo cuestionario PHQ-9.

        Args:
            entidad: instancia validada de CuestionarioPHQ9.

        Returns:
            El mismo cuestionario persistido.

        Raises:
            DuplicateEntityError: si ya existe un cuestionario con ese id.
        """
        registros = self._cargar()
        if any(r["id"] == entidad.id for r in registros):
            raise DuplicateEntityError(f"Ya existe un cuestionario con id '{entidad.id}'.")
        registros.append(entidad.to_dict())
        self._guardar(registros)
        return entidad

    def listar(self) -> list[CuestionarioPHQ9]:
        """Retorna todos los cuestionarios PHQ-9 almacenados."""
        return [CuestionarioPHQ9.from_dict(r) for r in self._cargar()]

    def buscar_por_codigo(self, codigo: str) -> CuestionarioPHQ9:
        """Busca un cuestionario por su id.

        Args:
            codigo: id del cuestionario.

        Returns:
            El cuestionario encontrado.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        for r in self._cargar():
            if r["id"] == codigo:
                return CuestionarioPHQ9.from_dict(r)
        raise EntityNotFoundError(f"No se encontró el cuestionario PHQ-9 con id '{codigo}'.")

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[CuestionarioPHQ9]:
        """Retorna todos los cuestionarios PHQ-9 de un estudiante, ordenados por fecha.

        Args:
            codigo_estudiante: código institucional del estudiante.

        Returns:
            Lista ordenada por fecha descendente.
        """
        resultados = [
            CuestionarioPHQ9.from_dict(r)
            for r in self._cargar()
            if r["codigo_estudiante"] == codigo_estudiante
        ]
        return sorted(resultados, key=lambda c: c.fecha_aplicacion, reverse=True)

    def actualizar(self, entidad: CuestionarioPHQ9) -> CuestionarioPHQ9:
        """Actualiza un cuestionario PHQ-9 existente.

        Args:
            entidad: instancia con los datos actualizados.

        Returns:
            El cuestionario actualizado.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        registros = self._cargar()
        for i, r in enumerate(registros):
            if r["id"] == entidad.id:
                registros[i] = entidad.to_dict()
                self._guardar(registros)
                return entidad
        raise EntityNotFoundError(f"No se encontró el cuestionario PHQ-9 con id '{entidad.id}'.")

    def eliminar(self, codigo: str) -> None:
        """Elimina un cuestionario PHQ-9 por su id.

        Args:
            codigo: id del cuestionario a eliminar.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        registros = self._cargar()
        nuevos = [r for r in registros if r["id"] != codigo]
        if len(nuevos) == len(registros):
            raise EntityNotFoundError(f"No se encontró el cuestionario PHQ-9 con id '{codigo}'.")
        self._guardar(nuevos)

    def _cargar(self) -> list[dict]:
        if not self.ruta.exists():
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise ArchivoCorruptoError(f"No se pudo leer '{self.ruta}': {e}.")

    def _guardar(self, registros: list[dict]) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
