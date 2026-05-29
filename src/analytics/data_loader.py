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
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer PHQ-9 de MySQL: {e}.")
    finally:
        conexion.close()
    return pd.DataFrame(filas)


def cargar_sesiones() -> pd.DataFrame:
    """Carga puntajes de estudiantes con sesiones de seguimiento desde MySQL.

    Reune puntajes PHQ-9 y GAD-7 de estudiantes que tienen al menos una sesion
    registrada. Incluye ``programa`` mediante LEFT JOIN con estudiantes para
    mantener el filtro del dashboard.

    Returns:
        DataFrame con instrumento, codigo_estudiante, puntaje_total,
        fecha_aplicacion y programa. DataFrame vacio si no hay registros.

    Raises:
        ArchivoCorruptoError: si falla la conexion o la consulta a MySQL.
    """
    sql = (
        "SELECT 'PHQ-9' AS instrumento, q.codigo_estudiante, q.puntaje_total, "
        "q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_phq9 q "
        "LEFT JOIN estudiantes e ON q.codigo_estudiante = e.codigo "
        "WHERE EXISTS ("
        "    SELECT 1 FROM sesiones_seguimiento s "
        "    WHERE s.codigo_estudiante = q.codigo_estudiante"
        ") "
        "UNION ALL "
        "SELECT 'GAD-7' AS instrumento, q.codigo_estudiante, q.puntaje_total, "
        "q.fecha_aplicacion, e.programa "
        "FROM cuestionarios_gad7 q "
        "LEFT JOIN estudiantes e ON q.codigo_estudiante = e.codigo "
        "WHERE EXISTS ("
        "    SELECT 1 FROM sesiones_seguimiento s "
        "    WHERE s.codigo_estudiante = q.codigo_estudiante"
        ") "
        "ORDER BY fecha_aplicacion"
    )
    try:
        conexion = obtener_conexion()
    except Exception as e:
        raise ArchivoCorruptoError(f"No se pudo conectar a MySQL: {e}.")
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer sesiones de MySQL: {e}.")
    finally:
        conexion.close()
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
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT DISTINCT programa FROM estudiantes "
            "WHERE programa IS NOT NULL ORDER BY programa"
        )
        filas = cursor.fetchall()
        cursor.close()
    except Exception as e:
        raise ArchivoCorruptoError(f"Error al leer programas de MySQL: {e}.")
    finally:
        conexion.close()
    return [fila[0] for fila in filas]
