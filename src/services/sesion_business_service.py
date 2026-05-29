"""Reglas de negocio para sesiones de seguimiento."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from src.exceptions.business_errors import HorarioFueraDeRangoError, SesionDuplicadaError
from src.exceptions.validation_errors import FechaInvalidaError
from src.models.sesion_seguimiento import EstadoSesion, SesionSeguimiento
from src.utils.constantes_negocio import HORA_FIN_ATENCION, HORA_INICIO_ATENCION


class SesionBusinessService:
    """Valida y agenda sesiones de seguimiento."""

    def __init__(self, sesion_repo, phq9_repo=None, gad7_repo=None) -> None:
        self._sesion_repo = sesion_repo
        self._phq9_repo = phq9_repo
        self._gad7_repo = gad7_repo

    def puede_agendar(self, datos: dict[str, Any] | SesionSeguimiento) -> None:
        sesion = self._normalizar_sesion(datos)
        self._validar_fecha_futura(sesion)
        self._validar_horario(sesion)
        self._validar_sesion_duplicada(sesion)

    def agendar_sesion(self, datos: dict[str, Any] | SesionSeguimiento) -> SesionSeguimiento:
        sesion = self._normalizar_sesion(datos)
        self.puede_agendar(sesion)
        return self._sesion_repo.crear(sesion)

    def listar_sesiones_estudiante(self, codigo_estudiante: str) -> list[SesionSeguimiento]:
        if hasattr(self._sesion_repo, "buscar_por_estudiante"):
            return self._sesion_repo.buscar_por_estudiante(codigo_estudiante)
        return [
            sesion
            for sesion in self._sesion_repo.listar()
            if sesion.codigo_estudiante == codigo_estudiante.strip()
        ]

    @staticmethod
    def _normalizar_sesion(datos: dict[str, Any] | SesionSeguimiento) -> SesionSeguimiento:
        if isinstance(datos, SesionSeguimiento):
            return datos
        return SesionSeguimiento.from_dict(datos)

    @staticmethod
    def _validar_fecha_futura(sesion: SesionSeguimiento) -> None:
        if sesion.estado == EstadoSesion.AGENDADA and sesion.fecha_hora <= datetime.now():
            raise FechaInvalidaError("La sesión agendada debe programarse en una fecha futura.")

    @staticmethod
    def _validar_horario(sesion: SesionSeguimiento) -> None:
        hora_inicio = sesion.fecha_hora.time()
        hora_fin = (sesion.fecha_hora + timedelta(minutes=sesion.duracion_minutos)).time()
        inicio_permitido = time(hour=HORA_INICIO_ATENCION)
        fin_permitido = time(hour=HORA_FIN_ATENCION)

        if hora_inicio < inicio_permitido or hora_fin > fin_permitido:
            raise HorarioFueraDeRangoError(hora_inicio.strftime("%H:%M"))

    def _validar_sesion_duplicada(self, sesion: SesionSeguimiento) -> None:
        for existente in self._sesion_repo.listar():
            if existente.id == sesion.id:
                continue
            if existente.estado == EstadoSesion.CANCELADA:
                continue
            if (
                existente.codigo_estudiante == sesion.codigo_estudiante
                and existente.fecha_hora == sesion.fecha_hora
            ):
                raise SesionDuplicadaError(
                    sesion.codigo_estudiante,
                    sesion.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                )
