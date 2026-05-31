from datetime import datetime, timedelta

import pytest

from src.exceptions.business_errors import HorarioFueraDeRangoError, SesionDuplicadaError
from src.exceptions.persistence_errors import DuplicateEntityError
from src.models.sesion_seguimiento import SesionSeguimiento
from src.services.sesion_business_service import SesionBusinessService


class _SesionRepoEnMemoria:
    """Repositorio de sesiones en memoria para pruebas (sin disco ni MySQL).

    Implementa los métodos que usa SesionBusinessService: crear, listar y
    buscar_por_estudiante, replicando el contrato de IRepository.
    """

    def __init__(self) -> None:
        self._sesiones: dict[str, SesionSeguimiento] = {}

    def crear(self, sesion: SesionSeguimiento) -> SesionSeguimiento:
        if sesion.id in self._sesiones:
            raise DuplicateEntityError(f"Ya existe una sesión con id '{sesion.id}'.")
        self._sesiones[sesion.id] = sesion
        return sesion

    def listar(self) -> list[SesionSeguimiento]:
        return list(self._sesiones.values())

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[SesionSeguimiento]:
        codigo = codigo_estudiante.strip()
        return [s for s in self._sesiones.values() if s.codigo_estudiante == codigo]


def test_agendar_sesion_valida_y_persistida() -> None:
    repo = _SesionRepoEnMemoria()
    service = SesionBusinessService(repo)
    sesion = SesionSeguimiento(
        codigo_estudiante="20241234",
        id_psicologo="psi-01",
        fecha_hora=_proxima_fecha_valida(hour=10),
        duracion_minutos=45,
        motivo="Seguimiento por ansiedad",
    )

    creada = service.agendar_sesion(sesion)

    assert creada.id == sesion.id
    assert len(repo.listar()) == 1


def test_puede_agendar_rechaza_horario_fuera_de_rango() -> None:
    repo = _SesionRepoEnMemoria()
    service = SesionBusinessService(repo)
    sesion = SesionSeguimiento(
        codigo_estudiante="20241234",
        id_psicologo="psi-01",
        fecha_hora=_proxima_fecha_valida(hour=7),
        duracion_minutos=45,
        motivo="Seguimiento por ansiedad",
    )

    with pytest.raises(HorarioFueraDeRangoError):
        service.puede_agendar(sesion)


def test_puede_agendar_rechaza_duplicidad() -> None:
    repo = _SesionRepoEnMemoria()
    service = SesionBusinessService(repo)
    fecha = _proxima_fecha_valida(hour=11)
    repo.crear(
        SesionSeguimiento(
            codigo_estudiante="20241234",
            id_psicologo="psi-01",
            fecha_hora=fecha,
            duracion_minutos=45,
            motivo="Primera sesión",
        )
    )

    repetida = SesionSeguimiento(
        codigo_estudiante="20241234",
        id_psicologo="psi-02",
        fecha_hora=fecha,
        duracion_minutos=45,
        motivo="Segunda sesión",
    )

    with pytest.raises(SesionDuplicadaError):
        service.puede_agendar(repetida)


def _proxima_fecha_valida(hour: int) -> datetime:
    base = datetime.now() + timedelta(days=1)
    return base.replace(hour=hour, minute=0, second=0, microsecond=0)
