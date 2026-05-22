from datetime import datetime, timedelta

import pytest

from src.exceptions.business_errors import HorarioFueraDeRangoError, SesionDuplicadaError
from src.models.sesion_seguimiento import SesionSeguimiento
from src.services.sesion_business_service import SesionBusinessService
from src.services.sesion_repository import SesionRepository


def test_agendar_sesion_valida_y_persistida(tmp_path) -> None:
    repo = SesionRepository(tmp_path / "sesiones.json")
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


def test_puede_agendar_rechaza_horario_fuera_de_rango(tmp_path) -> None:
    repo = SesionRepository(tmp_path / "sesiones.json")
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


def test_puede_agendar_rechaza_duplicidad(tmp_path) -> None:
    repo = SesionRepository(tmp_path / "sesiones.json")
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
