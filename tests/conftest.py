from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.models.cuestionario_phq9 import CuestionarioPHQ9
from src.services.phq9_business_service import PHQ9BusinessService


@pytest.fixture
def respuestas_minimas() -> list[int]:
    """9 respuestas en cero → puntaje 0 → severidad Mínimo."""
    return [0] * 9


@pytest.fixture
def respuestas_severas() -> list[int]:
    """9 respuestas en 3 → puntaje 27 → severidad Severo."""
    return [3] * 9


@pytest.fixture
def respuestas_moderadas() -> list[int]:
    """Suma 11 → severidad Moderado."""
    return [2, 1, 2, 1, 1, 2, 1, 1, 0]


@pytest.fixture
def email_service_mock() -> MagicMock:
    """Mock del EmailService que registra los envíos sin hacer nada real."""
    return MagicMock()


@pytest.fixture
def alerta_repo_mock() -> MagicMock:
    """Mock del AlertaRepository."""
    return MagicMock()


@pytest.fixture
def phq9_business_service(alerta_repo_mock, email_service_mock) -> PHQ9BusinessService:
    """Instancia de PHQ9BusinessService con dependencias mockeadas."""
    return PHQ9BusinessService(
        alerta_repo=alerta_repo_mock,
        email_service=email_service_mock,
    )


@pytest.fixture
def cuestionario_severo(respuestas_severas) -> CuestionarioPHQ9:
    return CuestionarioPHQ9(
        codigo_estudiante="EST001",
        respuestas=respuestas_severas,
    )


@pytest.fixture
def cuestionario_normal(respuestas_minimas) -> CuestionarioPHQ9:
    return CuestionarioPHQ9(
        codigo_estudiante="EST002",
        respuestas=respuestas_minimas,
    )


# ----------------------------- Fixtures GAD-7 (Diunis) -----------------------------

@pytest.fixture
def email_mock() -> MagicMock:
    """Mock del EmailService."""
    return MagicMock()


@pytest.fixture
def phq9_repo_mock() -> MagicMock:
    """Mock del PHQ9Repository — por defecto retorna lista vacía."""
    mock = MagicMock()
    mock.buscar_por_estudiante.return_value = []
    return mock


@pytest.fixture
def gad7_repo_mock() -> MagicMock:
    """Mock del GAD7Repository."""
    return MagicMock()
