from __future__ import annotations

import json
from pathlib import Path

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.estudiante import Estudiante
from src.repositories.interfaces import IRepository


class EstudianteJsonRepository(IRepository[Estudiante]):
    """Repositorio JSON para estudiantes.

    Args:
        ruta: ruta al archivo JSON de persistencia (sin valor por defecto para
            no acoplar la clase a una ubicación específica).
    """

    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta

    def crear(self, entidad: Estudiante) -> Estudiante:
        """Persiste un nuevo estudiante.

        Aplica la regla de negocio del integrante 1: no pueden existir dos
        estudiantes con el mismo código institucional.

        Args:
            entidad: instancia validada de Estudiante.

        Returns:
            El mismo estudiante persistido.

        Raises:
            DuplicateEntityError: si ya existe un estudiante con ese código.
        """
        registros = self._cargar()
        if any(r["codigo"] == entidad.codigo for r in registros):
            raise DuplicateEntityError(
                f"Ya existe un estudiante con el código '{entidad.codigo}'."
            )
        registros.append(entidad.to_dict())
        self._guardar(registros)
        return entidad

    def listar(self) -> list[Estudiante]:
        """Retorna todos los estudiantes almacenados."""
        return [Estudiante.from_dict(r) for r in self._cargar()]

    def buscar_por_codigo(self, codigo: str) -> Estudiante:
        """Busca un estudiante por su código institucional.

        Args:
            codigo: código del estudiante.

        Returns:
            El estudiante encontrado.

        Raises:
            EntityNotFoundError: si no existe el estudiante.
        """
        for r in self._cargar():
            if r["codigo"] == codigo:
                return Estudiante.from_dict(r)
        raise EntityNotFoundError(f"No se encontró el estudiante con código '{codigo}'.")

    def actualizar(self, entidad: Estudiante) -> Estudiante:
        """Actualiza un estudiante existente.

        Args:
            entidad: instancia con los datos actualizados.

        Returns:
            El estudiante actualizado.

        Raises:
            EntityNotFoundError: si no existe el estudiante.
        """
        registros = self._cargar()
        for i, r in enumerate(registros):
            if r["codigo"] == entidad.codigo:
                registros[i] = entidad.to_dict()
                self._guardar(registros)
                return entidad
        raise EntityNotFoundError(
            f"No se encontró el estudiante con código '{entidad.codigo}'."
        )

    def eliminar(self, codigo: str) -> None:
        """Elimina un estudiante por su código institucional.

        Args:
            codigo: código del estudiante a eliminar.

        Raises:
            EntityNotFoundError: si no existe el estudiante.
        """
        registros = self._cargar()
        nuevos = [r for r in registros if r["codigo"] != codigo]
        if len(nuevos) == len(registros):
            raise EntityNotFoundError(
                f"No se encontró el estudiante con código '{codigo}'."
            )
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
