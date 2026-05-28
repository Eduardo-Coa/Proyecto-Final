from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Interfaz base para repositorios de la plataforma."""

    @abstractmethod
    def crear(self, entidad: T) -> T:
        """Persiste una nueva entidad."""

    @abstractmethod
    def listar(self) -> list[T]:
        """Retorna todas las entidades almacenadas."""

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> T:
        """Busca y retorna una entidad por su identificador único."""

    @abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente."""

    @abstractmethod
    def eliminar(self, codigo: str) -> None:
        """Elimina una entidad por su identificador único."""
