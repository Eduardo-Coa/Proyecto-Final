from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Interfaz base para todos los repositorios de la plataforma.

    Define las operaciones CRUD estándar que cada repositorio debe implementar.
    También es el tipo que recibe el NotificacionDecorator (patrón GoF).
    """

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

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[T]:
        """Retorna todas las entidades asociadas a un estudiante.

        Implementación opcional: por defecto retorna lista vacía.
        Los repositorios cuyas entidades tienen 'codigo_estudiante' (GAD7, PHQ9,
        Sesion) deben sobreescribir este método.
        """
        return []
