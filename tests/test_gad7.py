"""14 tests para la entidad GAD-7 (Diunis Pérez).

Cobertura:
    1-3   Modelo: cálculo y clasificación de severidad
    4-6   Modelo: validaciones (cantidad de respuestas, rango, fecha)
    7-9   Regla de negocio: comorbilidad (GAD ≥ 15 + PHQ-9 severo reciente)
    10-11 Decorator: notificación por correo tras crear/falla
    12-14 Controller: registro y eliminación con manejo de errores
"""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.controllers.gad7_controller import GAD7Controller
from src.exceptions.business_errors import RiesgoSeveroError
from src.exceptions.persistence_errors import EntityNotFoundError
from src.exceptions.validation_errors import FechaInvalidaError, PuntajeInvalidoError
from src.models.alerta_riesgo import TipoAlerta
from src.models.cuestionario_gad7 import CuestionarioGAD7
from src.services.email_service import EmailService
from src.services.gad7_business_service import GAD7BusinessService
from src.services.notificacion_decorator import NotificacionDecorator


# ─────────────────────────── Modelo (1-6) ────────────────────────────────


def test_modelo_calcula_puntaje_total_correctamente():
    """El puntaje total es la suma exacta de las 7 respuestas."""
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST001", respuestas=[1, 2, 1, 3, 2, 0, 1]
    )

    assert cuestionario.puntaje_total == 10


def test_modelo_clasifica_severidad_minima():
    """Puntaje < 5 se clasifica como 'Mínimo'."""
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST002", respuestas=[0, 1, 0, 1, 0, 1, 1]
    )

    assert cuestionario.puntaje_total == 4
    assert cuestionario.nivel_severidad == "Mínimo"


def test_modelo_clasifica_severidad_severa():
    """Puntaje ≥ 15 se clasifica como 'Severo'."""
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST003", respuestas=[3, 3, 3, 3, 3, 0, 0]
    )

    assert cuestionario.puntaje_total == 15
    assert cuestionario.nivel_severidad == "Severo"


def test_modelo_rechaza_numero_incorrecto_de_respuestas():
    """El modelo lanza PuntajeInvalidoError si no hay exactamente 7 respuestas."""
    with pytest.raises(PuntajeInvalidoError):
        CuestionarioGAD7(codigo_estudiante="EST004", respuestas=[1, 2, 3])


def test_modelo_rechaza_valor_fuera_de_rango_0_a_3():
    """El modelo lanza PuntajeInvalidoError si una respuesta es > 3."""
    with pytest.raises(PuntajeInvalidoError):
        CuestionarioGAD7(codigo_estudiante="EST005", respuestas=[0, 0, 5, 0, 0, 0, 0])


def test_modelo_rechaza_fecha_futura():
    """El modelo lanza FechaInvalidaError si la fecha de aplicación es futura."""
    fecha_futura = datetime.now() + timedelta(days=3)

    with pytest.raises(FechaInvalidaError):
        CuestionarioGAD7(
            codigo_estudiante="EST006",
            respuestas=[0, 0, 0, 0, 0, 0, 0],
            fecha_aplicacion=fecha_futura,
        )


# ──────────────────── Regla de negocio: comorbilidad (7-9) ───────────────


def test_regla_negocio_dispara_alerta_si_puntaje_severo(
    phq9_repo_mock, alerta_repo_mock, email_mock
):
    """GAD-7 ≥ 15 con PHQ-9 severo reciente genera AlertaRiesgo de COMORBILIDAD."""
    phq9_severo_reciente = MagicMock()
    phq9_severo_reciente.puntaje_total = 22
    phq9_severo_reciente.fecha_aplicacion = datetime.now() - timedelta(days=5)
    phq9_repo_mock.buscar_por_estudiante.return_value = [phq9_severo_reciente]

    service = GAD7BusinessService(phq9_repo_mock, alerta_repo_mock, email_mock)
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST007", respuestas=[3, 3, 3, 3, 3, 0, 0]
    )

    with pytest.raises(RiesgoSeveroError):
        service.evaluar_riesgo(cuestionario)

    alerta_creada = alerta_repo_mock.crear.call_args[0][0]
    assert alerta_creada.tipo == TipoAlerta.COMORBILIDAD


def test_regla_negocio_envia_email_si_puntaje_severo(
    phq9_repo_mock, alerta_repo_mock, email_mock
):
    """Cuando se detecta riesgo severo (ansiedad o comorbilidad), se envía email."""
    phq9_repo_mock.buscar_por_estudiante.return_value = []
    service = GAD7BusinessService(phq9_repo_mock, alerta_repo_mock, email_mock)
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST008", respuestas=[3, 3, 3, 3, 3, 0, 0]
    )

    resultado = service.evaluar_riesgo(cuestionario)

    assert resultado == "ANSIEDAD_SEVERA"
    assert email_mock.enviar.called


def test_regla_negocio_no_dispara_alerta_si_puntaje_normal(
    phq9_repo_mock, alerta_repo_mock, email_mock
):
    """Puntaje GAD-7 < 15 no genera alerta ni envía email."""
    service = GAD7BusinessService(phq9_repo_mock, alerta_repo_mock, email_mock)
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST009", respuestas=[1, 1, 1, 1, 1, 0, 0]
    )

    resultado = service.evaluar_riesgo(cuestionario)

    assert resultado == "NORMAL"
    alerta_repo_mock.crear.assert_not_called()
    email_mock.enviar.assert_not_called()


# ────────────────────────── Decorator GoF (10-11) ────────────────────────


def test_decorator_envia_email_tras_crear(gad7_repo_mock):
    """NotificacionDecorator envía email tras una inserción exitosa."""
    email_service = MagicMock(spec=EmailService)
    decorator = NotificacionDecorator(
        repositorio=gad7_repo_mock,
        email_service=email_service,
        destinatario="bienestar@uni.edu",
        nombre_entidad="GAD-7",
    )
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST010", respuestas=[0, 0, 0, 0, 0, 0, 0]
    )

    decorator.crear(cuestionario)

    assert gad7_repo_mock.crear.called
    assert email_service.enviar.called
    asunto = email_service.enviar.call_args[0][1]
    assert "creado" in asunto


def test_decorator_no_envia_email_si_crear_falla(gad7_repo_mock):
    """Si el repositorio falla al crear, el decorator NO envía email."""
    gad7_repo_mock.crear.side_effect = RuntimeError("DB caída")
    email_service = MagicMock(spec=EmailService)
    decorator = NotificacionDecorator(
        repositorio=gad7_repo_mock,
        email_service=email_service,
        destinatario="bienestar@uni.edu",
        nombre_entidad="GAD-7",
    )
    cuestionario = CuestionarioGAD7(
        codigo_estudiante="EST011", respuestas=[0, 0, 0, 0, 0, 0, 0]
    )

    with pytest.raises(RuntimeError):
        decorator.crear(cuestionario)

    email_service.enviar.assert_not_called()


# ─────────────────────────── Controller (12-14) ──────────────────────────


def test_controller_registrar_exito_con_respuestas_validas(
    gad7_repo_mock, phq9_repo_mock, alerta_repo_mock, email_mock
):
    """El controlador registra correctamente con respuestas válidas."""
    business = GAD7BusinessService(phq9_repo_mock, alerta_repo_mock, email_mock)
    controller = GAD7Controller(repositorio=gad7_repo_mock, business_service=business)

    exito, mensaje = controller.registrar("EST012", [1, 1, 1, 1, 1, 1, 1])

    assert exito is True
    assert "GAD-7 registrado correctamente" in mensaje


def test_controller_registrar_falla_con_respuestas_invalidas(
    gad7_repo_mock, phq9_repo_mock, alerta_repo_mock, email_mock
):
    """El controlador retorna (False, mensaje) si las respuestas son inválidas."""
    business = GAD7BusinessService(phq9_repo_mock, alerta_repo_mock, email_mock)
    controller = GAD7Controller(repositorio=gad7_repo_mock, business_service=business)

    exito, mensaje = controller.registrar("EST013", [5, 0, 0, 0, 0, 0, 0])

    assert exito is False
    assert "VAL005" in mensaje


def test_controller_eliminar_id_inexistente_retorna_error(
    gad7_repo_mock, phq9_repo_mock, alerta_repo_mock, email_mock
):
    """Eliminar un id que no existe retorna (False, mensaje) sin lanzar excepción."""
    gad7_repo_mock.eliminar.side_effect = EntityNotFoundError(
        "No se encontró el cuestionario GAD-7 con id 'inexistente'."
    )
    business = GAD7BusinessService(phq9_repo_mock, alerta_repo_mock, email_mock)
    controller = GAD7Controller(repositorio=gad7_repo_mock, business_service=business)

    exito, mensaje = controller.eliminar("inexistente")

    assert exito is False
    assert "PER001" in mensaje
