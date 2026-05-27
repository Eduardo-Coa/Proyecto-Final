"""Fixtures compartidas para todos los tests del proyecto."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def email_mock():
    """Mock del EmailService."""
    return MagicMock()


@pytest.fixture
def alerta_repo_mock():
    """Mock del AlertaRepository."""
    return MagicMock()


@pytest.fixture
def phq9_repo_mock():
    """Mock del PHQ9Repository — por defecto retorna lista vacía."""
    mock = MagicMock()
    mock.buscar_por_estudiante.return_value = []
    return mock


@pytest.fixture
def gad7_repo_mock():
    """Mock del GAD7Repository."""
    return MagicMock()
