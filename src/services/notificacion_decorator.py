from __future__ import annotations

from typing import Generic, TypeVar

from src.repositories.interfaces import IRepository
from src.services.email_service import EmailService

T = TypeVar("T")


class NotificacionDecorator(IRepository[T], Generic[T]):
    """Decorator GoF que añade notificación por correo a un IRepository.

    Envuelve cualquier repositorio que implemente IRepository y, tras un
    crear/actualizar exitoso, dispara un correo al destinatario configurado.
    El resto de operaciones (listar, buscar, eliminar) se delegan tal cual.

    Implementa el patrón Decorator por composición (no herencia), envolviendo
    el repositorio en lugar de extenderlo.

    Args:
        repositorio: instancia concreta de IRepository (la que se envuelve).
        email_service: servicio de correo que realiza el envío.
        destinatario: dirección que recibirá las notificaciones.
        nombre_entidad: nombre humano de la entidad (ej. 'GAD-7'), para los asuntos.
    """

    def __init__(
        self,
        repositorio: IRepository[T],
        email_service: EmailService,
        destinatario: str,
        nombre_entidad: str,
    ) -> None:
        self._repositorio = repositorio
        self._email_service = email_service
        self._destinatario = destinatario
        self._nombre_entidad = nombre_entidad

    def crear(self, entidad: T) -> T:
        """Delega la creación y notifica por correo si fue exitosa."""
        resultado = self._repositorio.crear(entidad)
        self._notificar("creado", entidad)
        return resultado

    def actualizar(self, entidad: T) -> T:
        """Delega la actualización y notifica por correo si fue exitosa."""
        resultado = self._repositorio.actualizar(entidad)
        self._notificar("actualizado", entidad)
        return resultado

    def listar(self) -> list[T]:
        return self._repositorio.listar()

    def buscar_por_codigo(self, codigo: str) -> T:
        return self._repositorio.buscar_por_codigo(codigo)

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[T]:
        return self._repositorio.buscar_por_estudiante(codigo_estudiante)

    def eliminar(self, codigo: str) -> None:
        self._repositorio.eliminar(codigo)

    def _notificar(self, operacion: str, entidad: T) -> None:
        identificador = getattr(entidad, "id", None) or getattr(entidad, "codigo", "—")
        asunto = f"[Bienestar] {self._nombre_entidad} {operacion}"
        cuerpo = (
            f"Se ha {operacion} un registro de {self._nombre_entidad}.\n"
            f"Identificador: {identificador}\n"
        )
        self._email_service.enviar(self._destinatario, asunto, cuerpo)
