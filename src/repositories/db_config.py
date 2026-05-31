from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mysql.connector
from dotenv import load_dotenv


_ENV_LOADED = False
_CONEXION = None


def _cargar_env() -> None:
    """Carga el archivo .env (solo una vez por ejecución)."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    ruta_env = Path(__file__).resolve().parent.parent.parent / ".env"
    if not ruta_env.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo .env en '{ruta_env}'. "
            "Copia .env.example a .env y completa tus credenciales."
        )
    load_dotenv(ruta_env)
    _ENV_LOADED = True


def obtener_conexion() -> Any:
    """Retorna la conexión a MySQL reutilizando la activa (patrón Singleton).

    Mantiene una única conexión a nivel de módulo: si ya existe y sigue
    activa, la reutiliza; en caso contrario crea una nueva con las
    credenciales del .env y la almacena para futuras llamadas.

    Returns:
        Objeto de conexión activo a MySQL.

    Raises:
        FileNotFoundError: si no existe el archivo .env.
        mysql.connector.Error: si falla la conexión a MySQL.
    """
    global _CONEXION
    _cargar_env()
    if _CONEXION is not None and _CONEXION.is_connected():
        return _CONEXION
    _CONEXION = mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )
    return _CONEXION
