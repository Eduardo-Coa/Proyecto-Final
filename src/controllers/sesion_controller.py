"""Controlador MVC para sesiones de seguimiento."""

from __future__ import annotations

from datetime import datetime

from src.exceptions.business_errors import BusinessRuleError
from src.exceptions.persistence_errors import EntityNotFoundError, PersistenceError
from src.exceptions.validation_errors import ValidationError
from src.models.sesion_seguimiento import EstadoSesion, SesionSeguimiento


class SesionController:
    """Coordina la vista con el servicio de negocio y el repositorio.

    Captura excepciones del dominio y las traduce a tuplas (bool, mensaje|datos)
    para que la vista nunca reciba un traceback.
    """

    def __init__(self, repositorio, business_service) -> None:
        self._repo = repositorio
        self._business = business_service

    def agendar(
        self,
        codigo_estudiante: str,
        id_psicologo: str,
        fecha_hora: datetime,
        duracion_minutos: int,
        motivo: str,
        nota: str = "",
    ) -> tuple[bool, str]:
        """Crea y persiste una nueva sesión aplicando las reglas de negocio."""
        try:
            sesion = SesionSeguimiento(
                codigo_estudiante=codigo_estudiante,
                id_psicologo=id_psicologo,
                fecha_hora=fecha_hora,
                duracion_minutos=duracion_minutos,
                motivo=motivo,
                nota=nota,
            )
            self._business.agendar_sesion(sesion)
            return True, f"Sesión agendada correctamente para {sesion.fecha_hora.strftime('%Y-%m-%d %H:%M')}."
        except BusinessRuleError as exc:
            return False, str(exc)
        except ValidationError as exc:
            return False, str(exc)
        except PersistenceError as exc:
            return False, str(exc)

    def listar(self) -> tuple[bool, str | list[SesionSeguimiento]]:
        """Retorna todas las sesiones registradas."""
        try:
            return True, self._repo.listar()
        except PersistenceError as exc:
            return False, str(exc)

    def listar_por_estudiante(
        self, codigo_estudiante: str
    ) -> tuple[bool, str | list[SesionSeguimiento]]:
        """Retorna las sesiones asociadas a un estudiante específico."""
        try:
            return True, self._business.listar_sesiones_estudiante(codigo_estudiante)
        except PersistenceError as exc:
            return False, str(exc)

    def cancelar(self, id_sesion: str) -> tuple[bool, str]:
        """Marca una sesión como CANCELADA (no la elimina del repositorio)."""
        try:
            sesion = self._repo.buscar_por_codigo(id_sesion)
            sesion_cancelada = SesionSeguimiento(
                id=sesion.id,
                codigo_estudiante=sesion.codigo_estudiante,
                id_psicologo=sesion.id_psicologo,
                fecha_hora=sesion.fecha_hora,
                duracion_minutos=sesion.duracion_minutos,
                motivo=sesion.motivo,
                estado=EstadoSesion.CANCELADA,
                nota=sesion.nota,
            )
            self._repo.actualizar(sesion_cancelada)
            return True, "Sesión cancelada correctamente."
        except EntityNotFoundError as exc:
            return False, str(exc)
        except ValidationError as exc:
            return False, str(exc)
        except PersistenceError as exc:
            return False, str(exc)

    def eliminar(self, id_sesion: str) -> tuple[bool, str]:
        """Elimina una sesión por su id."""
        try:
            self._repo.eliminar(id_sesion)
            return True, "Sesión eliminada correctamente."
        except EntityNotFoundError as exc:
            return False, str(exc)
        except PersistenceError as exc:
            return False, str(exc)
