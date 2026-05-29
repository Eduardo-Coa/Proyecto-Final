"""Carga de datos desde MySQL para el dashboard analitico."""

from __future__ import annotations

import pandas as pd
from mysql.connector import Error as MySQLError

from src.exceptions.persistence_errors import ArchivoCorruptoError
from src.repositories.db_config import obtener_conexion


def cargar_phq9() -> pd.DataFrame:
    """Carga los cuestionarios PHQ-9 desde MySQL como DataFrame.

    Incluye la columna ``programa`` mediante un LEFT JOIN con la tabla de
    estudiantes, de modo que el dashboard pueda filtrar por programa academico.

    Returns:
        DataFrame con columnas de cuestionarios PHQ-9 mas ``programa``.

    Raises:
        ArchivoCorruptoError: si falla la consulta a MySQL.
        PersistenceError: si falla la conexion configurada.
    """
    sql = (
        "SELECT q.id, q.codigo_estudiante, q.respuestas, q.puntaje_total, "
        "q.nivel_severidad, q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_phq9 q "
        "LEFT JOIN estudiantes e ON q.codigo_estudiante = e.codigo"
    )
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()
    except MySQLError as exc:
        raise ArchivoCorruptoError(f"Error al leer PHQ-9 de MySQL: {exc}.") from exc
    finally:
        conexion.close()
    return pd.DataFrame(filas)


def cargar_evolucion_sesiones() -> pd.DataFrame:
    """Carga puntajes clinicos de estudiantes con sesiones de seguimiento.

    La consulta toma los estudiantes que tienen al menos una sesion registrada
    y reune sus puntajes PHQ-9 y GAD-7 en una sola serie temporal. El dashboard
    usa estos datos para mostrar la evolucion promedio del grupo atendido.

    Returns:
        DataFrame con ``instrumento``, ``codigo_estudiante``, ``puntaje_total``,
        ``fecha_aplicacion`` y ``programa``.

    Raises:
        ArchivoCorruptoError: si falla la consulta a MySQL.
        PersistenceError: si falla la conexion configurada.
    """
    sql = (
        "SELECT 'PHQ-9' AS instrumento, q.codigo_estudiante, q.puntaje_total, "
        "q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_phq9 q "
        "INNER JOIN estudiantes e ON q.codigo_estudiante = e.codigo "
        "WHERE EXISTS ("
        "    SELECT 1 FROM sesiones_seguimiento s "
        "    WHERE s.codigo_estudiante = q.codigo_estudiante"
        ") "
        "UNION ALL "
        "SELECT 'GAD-7' AS instrumento, q.codigo_estudiante, q.puntaje_total, "
        "q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_gad7 q "
        "INNER JOIN estudiantes e ON q.codigo_estudiante = e.codigo "
        "WHERE EXISTS ("
        "    SELECT 1 FROM sesiones_seguimiento s "
        "    WHERE s.codigo_estudiante = q.codigo_estudiante"
        ") "
        "ORDER BY fecha_aplicacion"
    )
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()
    except MySQLError as exc:
        mensaje = f"Error al leer evolucion de sesiones de MySQL: {exc}."
        raise ArchivoCorruptoError(mensaje) from exc
    finally:
        conexion.close()
    return pd.DataFrame(filas)


def listar_programas() -> list[str]:
    """Retorna los programas academicos distintos registrados.

    Returns:
        Lista ordenada de nombres de programa.

    Raises:
        ArchivoCorruptoError: si falla la consulta a MySQL.
        PersistenceError: si falla la conexion configurada.
    """
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT DISTINCT programa FROM estudiantes "
            "WHERE programa IS NOT NULL ORDER BY programa"
        )
        filas = cursor.fetchall()
        cursor.close()
    except MySQLError as exc:
        raise ArchivoCorruptoError(f"Error al leer programas de MySQL: {exc}.") from exc
    finally:
        conexion.close()
    return [fila[0] for fila in filas]
