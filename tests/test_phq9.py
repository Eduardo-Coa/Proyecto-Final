"""Pruebas unitarias del módulo PHQ-9 (Integrante: Eduardo Coa).

Cubre:
    - Modelo CuestionarioPHQ9 (cálculo de puntaje, clasificación, validaciones).
    - Regla de negocio PHQ9BusinessService (alerta + email si puntaje ≥ 20).
    - NotificacionDecorator (patrón GoF: notifica solo si crear/actualizar funciona).
    - PHQ9Controller (CRUD + manejo de errores).

Total: 14 tests. Mínimo exigido por el criterio 6: 10 tests.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.controllers.phq9_controller import PHQ9Controller
from src.exceptions.persistence_errors import DuplicateEntityError, EntityNotFoundError
from src.exceptions.validation_errors import FechaInvalidaError, PuntajeInvalidoError
from src.models.alerta_riesgo import TipoAlerta
from src.models.cuestionario_phq9 import CuestionarioPHQ9
from src.services.notificacion_decorator import NotificacionDecorator


# ════════════════════════════════════════════════════════════════════════════
# MODELO — Cálculo de puntaje y clasificación de severidad
# ════════════════════════════════════════════════════════════════════════════


def test_modelo_calcula_puntaje_total_correctamente(respuestas_moderadas):
    # Arrange + Act
    cuestionario = CuestionarioPHQ9(
        codigo_estudiante="EST001",
        respuestas=respuestas_moderadas,
    )
    # Assert
    assert cuestionario.puntaje_total == sum(respuestas_moderadas) == 11


def test_modelo_clasifica_severidad_minima(respuestas_minimas):
    # Arrange + Act
    cuestionario = CuestionarioPHQ9(
        codigo_estudiante="EST001",
        respuestas=respuestas_minimas,
    )
    # Assert
    assert cuestionario.puntaje_total == 0
    assert cuestionario.nivel_severidad == "Mínimo"


def test_modelo_clasifica_severidad_severa(respuestas_severas):
    # Arrange + Act
    cuestionario = CuestionarioPHQ9(
        codigo_estudiante="EST001",
        respuestas=respuestas_severas,
    )
    # Assert
    assert cuestionario.puntaje_total == 27
    assert cuestionario.nivel_severidad == "Severo"
    assert cuestionario.es_riesgo_severo is True


# ════════════════════════════════════════════════════════════════════════════
# MODELO — Validaciones de dominio (criterio 3)
# ════════════════════════════════════════════════════════════════════════════


def test_modelo_rechaza_numero_incorrecto_de_respuestas():
    # Arrange + Act + Assert
    with pytest.raises(PuntajeInvalidoError):
        CuestionarioPHQ9(
            codigo_estudiante="EST001",
            respuestas=[0, 1, 2],  # solo 3, deben ser 9
        )


def test_modelo_rechaza_valor_fuera_de_rango_0_a_3():
    # Arrange + Act + Assert
    with pytest.raises(PuntajeInvalidoError):
        CuestionarioPHQ9(
            codigo_estudiante="EST001",
            respuestas=[0, 1, 2, 3, 4, 0, 0, 0, 0],  # el 4 es inválido
        )


def test_modelo_rechaza_fecha_futura(respuestas_minimas):
    # Arrange + Act + Assert
    with pytest.raises(FechaInvalidaError):
        CuestionarioPHQ9(
            codigo_estudiante="EST001",
            respuestas=respuestas_minimas,
            fecha_aplicacion=datetime.now() + timedelta(days=5),
        )


# ════════════════════════════════════════════════════════════════════════════
# REGLA DE NEGOCIO — puntaje ≥ 20 → AlertaRiesgo + Email (criterio 5)
# ════════════════════════════════════════════════════════════════════════════


def test_regla_negocio_dispara_alerta_si_puntaje_severo(
    phq9_business_service, alerta_repo_mock, cuestionario_severo
):
    # Act
    resultado = phq9_business_service.evaluar_riesgo(cuestionario_severo)
    # Assert
    assert resultado == "DEPRESION_SEVERA"
    alerta_repo_mock.crear.assert_called_once()
    alerta_creada = alerta_repo_mock.crear.call_args[0][0]
    assert alerta_creada.tipo == TipoAlerta.DEPRESION_SEVERA
    assert alerta_creada.codigo_estudiante == "EST001"
    assert alerta_creada.puntaje == 27


def test_regla_negocio_envia_email_si_puntaje_severo(
    phq9_business_service, email_service_mock, cuestionario_severo
):
    # Act
    phq9_business_service.evaluar_riesgo(cuestionario_severo)
    # Assert
    email_service_mock.enviar.assert_called_once()
    destinatario, asunto, cuerpo = email_service_mock.enviar.call_args[0]
    assert destinatario == "bienestar@uni.edu"
    assert "DEPRESIÓN SEVERA" in asunto
    assert "EST001" in cuerpo
    assert "27" in cuerpo


def test_regla_negocio_no_dispara_alerta_si_puntaje_normal(
    phq9_business_service, alerta_repo_mock, email_service_mock, cuestionario_normal
):
    # Act
    resultado = phq9_business_service.evaluar_riesgo(cuestionario_normal)
    # Assert
    assert resultado == "NORMAL"
    alerta_repo_mock.crear.assert_not_called()
    email_service_mock.enviar.assert_not_called()


# ════════════════════════════════════════════════════════════════════════════
# DECORATOR — patrón GoF, EmailService envuelve IRepository (criterio 7)
# ════════════════════════════════════════════════════════════════════════════


def test_decorator_envia_email_tras_crear(
    email_service_mock, cuestionario_severo
):
    # Arrange
    repo_interno = MagicMock()
    repo_interno.crear.return_value = cuestionario_severo
    decorator = NotificacionDecorator(
        repositorio=repo_interno,
        email_service=email_service_mock,
        destinatario="bienestar@uni.edu",
        nombre_entidad="PHQ-9",
    )
    # Act
    decorator.crear(cuestionario_severo)
    # Assert
    repo_interno.crear.assert_called_once_with(cuestionario_severo)
    email_service_mock.enviar.assert_called_once()
    _, asunto, _ = email_service_mock.enviar.call_args[0]
    assert "PHQ-9" in asunto
    assert "creado" in asunto


def test_decorator_no_envia_email_si_crear_falla(
    email_service_mock, cuestionario_severo
):
    # Arrange
    repo_interno = MagicMock()
    repo_interno.crear.side_effect = DuplicateEntityError("Ya existe.")
    decorator = NotificacionDecorator(
        repositorio=repo_interno,
        email_service=email_service_mock,
        destinatario="bienestar@uni.edu",
        nombre_entidad="PHQ-9",
    )
    # Act + Assert
    with pytest.raises(DuplicateEntityError):
        decorator.crear(cuestionario_severo)
    email_service_mock.enviar.assert_not_called()


# ════════════════════════════════════════════════════════════════════════════
# CONTROLLER — CRUD con manejo de errores (criterio 2)
# ════════════════════════════════════════════════════════════════════════════


def test_controller_registrar_exito_con_respuestas_validas(respuestas_minimas):
    # Arrange
    repo_mock = MagicMock()
    business_mock = MagicMock()
    repo_mock.crear.side_effect = lambda c: c
    controller = PHQ9Controller(repositorio=repo_mock, business_service=business_mock)
    # Act
    exito, mensaje = controller.registrar("EST001", respuestas_minimas)
    # Assert
    assert exito is True
    assert "PHQ-9 registrado correctamente" in mensaje
    repo_mock.crear.assert_called_once()
    business_mock.evaluar_riesgo.assert_called_once()


def test_controller_registrar_falla_con_respuestas_invalidas():
    # Arrange
    repo_mock = MagicMock()
    business_mock = MagicMock()
    controller = PHQ9Controller(repositorio=repo_mock, business_service=business_mock)
    # Act
    exito, mensaje = controller.registrar("EST001", [0, 1])  # solo 2 respuestas
    # Assert
    assert exito is False
    assert "VAL005" in mensaje
    repo_mock.crear.assert_not_called()


def test_controller_eliminar_id_inexistente_retorna_error():
    # Arrange
    repo_mock = MagicMock()
    business_mock = MagicMock()
    repo_mock.eliminar.side_effect = EntityNotFoundError("No existe el id 'XXX'.")
    controller = PHQ9Controller(repositorio=repo_mock, business_service=business_mock)
    # Act
    exito, mensaje = controller.eliminar("XXX")
    # Assert
    assert exito is False
    assert "PER001" in mensaje
