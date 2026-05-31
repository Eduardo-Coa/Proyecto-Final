"""12 tests para la entidad Estudiante (Alejandro).

Cobertura:
    1-6   Modelo: validaciones (código, edad, semestre, correo, nombre)
    7-9   Repositorio JSON + regla de negocio (código único)
    10-11 Controller: registro y eliminación con manejo de errores
    12    Decorator: notificación por correo tras crear
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.controllers.estudiante_controller import EstudianteController
from src.exceptions.persistence_errors import (
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.exceptions.validation_errors import (
    CodigoInvalidoError,
    CorreoInvalidoError,
    EdadInvalidaError,
    SemestreInvalidoError,
    ValidationError,
)
from src.models.estudiante import Estudiante
from src.repositories.estudiante_mysql_repository import EstudianteMySQLRepository
from src.services.email_service import EmailService
from src.services.notificacion_decorator import NotificacionDecorator


# ─────────────────────────── Modelo (1-6) ────────────────────────────────


def _estudiante_valido(**override) -> Estudiante:
    """Crea un Estudiante válido permitiendo sobreescribir campos."""
    datos = dict(
        codigo="EST0001",
        nombre_completo="Alejandro Pérez García",
        edad=20,
        semestre=4,
        correo="alejandro.perez@uni.edu.co",
        programa="Ciencias de Datos",
    )
    datos.update(override)
    return Estudiante(**datos)


def test_modelo_crea_estudiante_valido():
    """Un Estudiante con datos válidos se crea correctamente y serializa a dict."""
    estudiante = _estudiante_valido()

    assert estudiante.codigo == "EST0001"
    assert estudiante.edad == 20
    dic = estudiante.to_dict()
    assert dic["codigo"] == "EST0001"
    assert "fecha_registro" in dic


def test_modelo_rechaza_codigo_con_formato_invalido():
    """El modelo lanza CodigoInvalidoError si el código no cumple 'EST' + 3-6 dígitos."""
    with pytest.raises(CodigoInvalidoError):
        _estudiante_valido(codigo="ABC123")


def test_modelo_rechaza_edad_menor_a_16():
    """El modelo lanza EdadInvalidaError si la edad es < 16 (regla del integrante 1)."""
    with pytest.raises(EdadInvalidaError):
        _estudiante_valido(edad=15)


def test_modelo_rechaza_semestre_fuera_de_rango():
    """El modelo lanza SemestreInvalidoError si el semestre es 0 o > 12."""
    with pytest.raises(SemestreInvalidoError):
        _estudiante_valido(semestre=0)
    with pytest.raises(SemestreInvalidoError):
        _estudiante_valido(semestre=13)


def test_modelo_rechaza_correo_con_formato_invalido():
    """El modelo lanza CorreoInvalidoError si el correo no tiene formato válido."""
    with pytest.raises(CorreoInvalidoError):
        _estudiante_valido(correo="correo-sin-arroba")


def test_modelo_rechaza_nombre_vacio_o_corto():
    """El modelo lanza ValidationError si el nombre está vacío o tiene < 3 caracteres."""
    with pytest.raises(ValidationError):
        _estudiante_valido(nombre_completo="")
    with pytest.raises(ValidationError):
        _estudiante_valido(nombre_completo="Al")


# ─────────────────────── Regla de negocio (7-9) ──────────────────────────


def test_regla_negocio_repo_lanza_duplicate_si_codigo_existente(conexion_mock):
    """Regla del integrante 1: no pueden existir dos estudiantes con el mismo código.

    El repositorio MySQL traduce el error de clave duplicada de MySQL
    ('Duplicate entry') en una DuplicateEntityError del dominio.
    """
    cursor = conexion_mock.cursor.return_value
    cursor.execute.side_effect = Exception("1062 (23000): Duplicate entry 'EST0010'")
    repo = EstudianteMySQLRepository(conexion_mock)

    with pytest.raises(DuplicateEntityError):
        repo.crear(_estudiante_valido(codigo="EST0010"))


def test_repo_persiste_y_recupera_estudiante(conexion_mock):
    """El repositorio MySQL persiste (crear) y recupera (buscar_por_codigo) un estudiante."""
    cursor = conexion_mock.cursor.return_value
    cursor.fetchone.return_value = {
        "codigo": "EST0020",
        "nombre_completo": "Alejandro Pérez García",
        "edad": 20,
        "semestre": 4,
        "correo": "alejandro.perez@uni.edu.co",
        "programa": "Ciencias de Datos",
        "fecha_registro": datetime(2026, 1, 1, 10, 0, 0),
    }
    repo = EstudianteMySQLRepository(conexion_mock)

    creado = repo.crear(_estudiante_valido(codigo="EST0020"))
    recuperado = repo.buscar_por_codigo("EST0020")

    assert recuperado.codigo == creado.codigo
    assert recuperado.nombre_completo == creado.nombre_completo
    assert recuperado.edad == creado.edad


def test_repo_eliminar_codigo_inexistente_lanza_excepcion(conexion_mock):
    """Eliminar un código que no existe lanza EntityNotFoundError (rowcount == 0)."""
    cursor = conexion_mock.cursor.return_value
    cursor.rowcount = 0
    repo = EstudianteMySQLRepository(conexion_mock)

    with pytest.raises(EntityNotFoundError):
        repo.eliminar("EST9999")


# ─────────────────────────── Controller (10-11) ──────────────────────────


def test_controller_registrar_exito_con_datos_validos(estudiante_repo_mock):
    """El controlador registra correctamente y retorna (True, mensaje_éxito)."""
    controller = EstudianteController(repositorio=estudiante_repo_mock)

    exito, mensaje = controller.registrar(
        codigo="EST0030",
        nombre_completo="María González",
        edad=22,
        semestre=6,
        correo="maria.gonzalez@uni.edu.co",
        programa="Psicología",
    )

    assert exito is True
    assert "EST0030" in mensaje
    estudiante_repo_mock.crear.assert_called_once()


def test_controller_registrar_falla_con_edad_invalida(estudiante_repo_mock):
    """El controlador retorna (False, mensaje) si la edad es inválida (VAL002)."""
    controller = EstudianteController(repositorio=estudiante_repo_mock)

    exito, mensaje = controller.registrar(
        codigo="EST0031",
        nombre_completo="Pedro Ruiz",
        edad=14,
        semestre=2,
        correo="pedro@uni.edu.co",
        programa="Medicina",
    )

    assert exito is False
    assert "VAL002" in mensaje
    estudiante_repo_mock.crear.assert_not_called()


# ────────────────────────── Decorator GoF (12) ───────────────────────────


def test_decorator_envia_email_tras_crear_estudiante(estudiante_repo_mock):
    """NotificacionDecorator envía email tras un crear exitoso (patrón GoF)."""
    email_service = MagicMock(spec=EmailService)
    decorator = NotificacionDecorator(
        repositorio=estudiante_repo_mock,
        email_service=email_service,
        destinatario="bienestar@uni.edu",
        nombre_entidad="Estudiante",
    )
    estudiante = _estudiante_valido(codigo="EST0040")

    decorator.crear(estudiante)

    estudiante_repo_mock.crear.assert_called_once()
    email_service.enviar.assert_called_once()
    asunto = email_service.enviar.call_args[0][1]
    assert "Estudiante" in asunto
    assert "creado" in asunto
