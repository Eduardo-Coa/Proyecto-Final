from datetime import datetime, timedelta

import pytest

from src.exceptions.validation_errors import CampoRequeridoError, DuracionInvalidaError
from src.models.sesion_seguimiento import EstadoSesion, SesionSeguimiento


def test_sesion_seguimiento_serializa_y_reconstruye() -> None:
    sesion = SesionSeguimiento(
        codigo_estudiante="20241234",
        id_psicologo="psi-01",
        fecha_hora=datetime.now() + timedelta(days=1),
        duracion_minutos=45,
        motivo="Seguimiento por ansiedad",
        estado=EstadoSesion.AGENDADA,
        nota="Primera sesión",
    )

    reconstruida = SesionSeguimiento.from_dict(sesion.to_dict())

    assert reconstruida.codigo_estudiante == sesion.codigo_estudiante
    assert reconstruida.id_psicologo == sesion.id_psicologo
    assert reconstruida.estado == EstadoSesion.AGENDADA
    assert reconstruida.nota == "Primera sesión"


def test_sesion_rechaza_motivo_vacio() -> None:
    with pytest.raises(CampoRequeridoError):
        SesionSeguimiento(
            codigo_estudiante="20241234",
            id_psicologo="psi-01",
            fecha_hora=datetime.now() + timedelta(days=1),
            duracion_minutos=45,
            motivo="   ",
        )


def test_sesion_rechaza_duracion_invalida() -> None:
    with pytest.raises(DuracionInvalidaError):
        SesionSeguimiento(
            codigo_estudiante="20241234",
            id_psicologo="psi-01",
            fecha_hora=datetime.now() + timedelta(days=1),
            duracion_minutos=10,
            motivo="Seguimiento",
        )
