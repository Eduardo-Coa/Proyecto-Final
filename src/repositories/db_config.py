"""Configuracion de conexion MySQL."""

from __future__ import annotations

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error as MySQLError
from mysql.connector import MySQLConnection

from src.exceptions.persistence_errors import DatabaseConnectionError


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
DEFAULT_DATABASE = "bienestar_universitario"


def obtener_conexion() -> MySQLConnection:
    """Crea una conexion MySQL usando variables de entorno."""
    load_dotenv(ENV_PATH)

    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", DEFAULT_DATABASE),
    }

    try:
        return mysql.connector.connect(**config)
    except MySQLError as exc:
        raise DatabaseConnectionError(
            "No se pudo conectar a MySQL. Verifica que el servidor este activo, "
            "que exista la base de datos y que las credenciales de .env sean correctas."
        ) from exc
