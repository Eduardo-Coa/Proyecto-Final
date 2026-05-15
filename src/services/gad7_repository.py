from __future__ import annotations

import json
from pathlib import Path

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.cuestionario_gad7 import CuestionarioGAD7
from src.services.interfaces import IRepository


class GAD7Repository(IRepository[CuestionarioGAD7]):
    """Repositorio JSON para cuestionarios GAD-7.

    Args:
        ruta: ruta al archivo JSON de persistencia.
    """

    def __init__(self, ruta: Path = Path("data/cuestionarios_gad7.json")) -> None:
        self.ruta = ruta

    def crear(self, cuestionario: CuestionarioGAD7) -> CuestionarioGAD7:
        """Persiste un nuevo cuestionario GAD-7.

        Args:
            cuestionario: instancia validada de CuestionarioGAD7.

        Returns:
            El mismo cuestionario persistido.

        Raises:
            DuplicateEntityError: si ya existe un cuestionario con ese id.
        """
        registros = self._cargar()
        if any(r["id"] == cuestionario.id for r in registros):
            raise DuplicateEntityError(f"Ya existe un cuestionario con id '{cuestionario.id}'.")
        registros.append(cuestionario.to_dict())
        self._guardar(registros)
        return cuestionario

    def listar(self) -> list[CuestionarioGAD7]:
        """Retorna todos los cuestionarios GAD-7 almacenados."""
        return [CuestionarioGAD7.from_dict(r) for r in self._cargar()]

    def buscar_por_codigo(self, codigo: str) -> CuestionarioGAD7:
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
                return CuestionarioGAD7.from_dict(r)
        raise EntityNotFoundError(f"No se encontró el cuestionario GAD-7 con id '{codigo}'.")

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[CuestionarioGAD7]:
        """Retorna todos los cuestionarios GAD-7 de un estudiante.

        Args:
            codigo_estudiante: código institucional del estudiante.

        Returns:
            Lista de cuestionarios del estudiante, ordenados por fecha descendente.
        """
        resultados = [
            CuestionarioGAD7.from_dict(r)
            for r in self._cargar()
            if r["codigo_estudiante"] == codigo_estudiante
        ]
        return sorted(resultados, key=lambda c: c.fecha_aplicacion, reverse=True)

    def actualizar(self, cuestionario: CuestionarioGAD7) -> CuestionarioGAD7:
        """Actualiza un cuestionario GAD-7 existente.

        Args:
            cuestionario: instancia con los datos actualizados.

        Returns:
            El cuestionario actualizado.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        registros = self._cargar()
        for i, r in enumerate(registros):
            if r["id"] == cuestionario.id:
                registros[i] = cuestionario.to_dict()
                self._guardar(registros)
                return cuestionario
        raise EntityNotFoundError(f"No se encontró el cuestionario GAD-7 con id '{cuestionario.id}'.")

    def eliminar(self, codigo: str) -> None:
        """Elimina un cuestionario GAD-7 por su id.

        Args:
            codigo: id del cuestionario a eliminar.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        registros = self._cargar()
        nuevos = [r for r in registros if r["id"] != codigo]
        if len(nuevos) == len(registros):
            raise EntityNotFoundError(f"No se encontró el cuestionario GAD-7 con id '{codigo}'.")
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
