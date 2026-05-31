from __future__ import annotations

import pandas as pd

from src.exceptions.persistence_errors import ArchivoCorruptoError
from src.repositories.db_config import obtener_conexion


def cargar_phq9() -> pd.DataFrame:
    """Carga los cuestionarios PHQ-9 desde MySQL como DataFrame.

    Incluye la columna ``programa`` mediante un LEFT JOIN con la tabla de
    estudiantes, de modo que el dashboard pueda filtrar por programa académico.
    Los cuestionarios sin estudiante asociado conservan ``programa`` nulo.

    Returns:
        DataFrame con las columnas de cuestionarios_phq9 más ``programa``.
        DataFrame vacío si no hay registros.

    Raises:
        ArchivoCorruptoError: si falla la conexión o la consulta a MySQL.
    """
    sql = (
        "SELECT q.id, q.codigo_estudiante, q.respuestas, q.puntaje_total, "
        "q.nivel_severidad, q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_phq9 q "
        "LEFT JOIN estudiantes e ON q.codigo_estudiante = e.codigo"
    )
    try:
        conexion = obtener_conexion()
    except Exception as e:
        raise ArchivoCorruptoError(f"No se pudo conectar a MySQL: {e}.")
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        filas = cursor.fetchall()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer PHQ-9 de MySQL: {e}.")
    finally:
        cursor.close()
    return pd.DataFrame(filas)


def cargar_gad7() -> pd.DataFrame:
    """Carga los cuestionarios GAD-7 desde MySQL como DataFrame.

    Incluye la columna ``programa`` mediante un LEFT JOIN con la tabla de
    estudiantes, de modo que el dashboard pueda filtrar por programa académico.
    Los cuestionarios sin estudiante asociado conservan ``programa`` nulo.

    Returns:
        DataFrame con las columnas de cuestionarios_gad7 más ``programa``.
        DataFrame vacío si no hay registros.

    Raises:
        ArchivoCorruptoError: si falla la conexión o la consulta a MySQL.
    """
    sql = (
        "SELECT q.id, q.codigo_estudiante, q.respuestas, q.puntaje_total, "
        "q.nivel_severidad, q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_gad7 q "
        "LEFT JOIN estudiantes e ON q.codigo_estudiante = e.codigo"
    )
    try:
        conexion = obtener_conexion()
    except Exception as e:
        raise ArchivoCorruptoError(f"No se pudo conectar a MySQL: {e}.")
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        filas = cursor.fetchall()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer GAD-7 de MySQL: {e}.")
    finally:
        cursor.close()
    return pd.DataFrame(filas)


def cargar_estudiantes() -> pd.DataFrame:
    """Carga los estudiantes desde MySQL como DataFrame.

    Returns:
        DataFrame con los datos demográficos de la tabla ``estudiantes``.
        DataFrame vacío si no hay registros.

    Raises:
        ArchivoCorruptoError: si falla la conexión o la consulta a MySQL.
    """
    sql = (
        "SELECT codigo, nombre_completo, edad, semestre, correo, programa, "
        "fecha_registro FROM estudiantes"
    )
    try:
        conexion = obtener_conexion()
    except Exception as e:
        raise ArchivoCorruptoError(f"No se pudo conectar a MySQL: {e}.")
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        filas = cursor.fetchall()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer estudiantes de MySQL: {e}.")
    finally:
        cursor.close()
    return pd.DataFrame(filas)


def listar_programas() -> list[str]:
    """Retorna los programas académicos distintos registrados en estudiantes.

    Returns:
        Lista ordenada de nombres de programa. Lista vacía si no hay datos.

    Raises:
        ArchivoCorruptoError: si falla la conexión o la consulta a MySQL.
    """
    try:
        conexion = obtener_conexion()
    except Exception as e:
        raise ArchivoCorruptoError(f"No se pudo conectar a MySQL: {e}.")
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "SELECT DISTINCT programa FROM estudiantes "
            "WHERE programa IS NOT NULL ORDER BY programa"
        )
        filas = cursor.fetchall()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer programas de MySQL: {e}.")
    finally:
        cursor.close()
    return [fila[0] for fila in filas]
