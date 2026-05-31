from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.cuestionario_gad7 import CuestionarioGAD7
from src.repositories.interfaces import IRepository


class GAD7MySQLRepository(IRepository[CuestionarioGAD7]):
    """Repositorio MySQL para cuestionarios GAD-7.

    Implementa la misma interfaz IRepository que la versión JSON, de modo que
    el resto del sistema (controller, business service, vista) no necesita
    saber cuál de las dos implementaciones se está usando.

    Args:
        conexion: conexión activa a MySQL (mysql.connector.MySQLConnection).
    """

    _TABLA = "cuestionarios_gad7"

    def __init__(self, conexion: Any) -> None:
        self.conexion = conexion

    def crear(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Inserta un nuevo cuestionario GAD-7.

        Raises:
            DuplicateEntityError: si ya existe un cuestionario con ese id.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
        """
        sql = (
            f"INSERT INTO {self._TABLA} "
            "(id, codigo_estudiante, respuestas, puntaje_total, "
            "nivel_severidad, fecha_aplicacion) VALUES (%s, %s, %s, %s, %s, %s)"
        )
        valores = (
            entidad.id,
            entidad.codigo_estudiante,
            json.dumps(entidad.respuestas),
            entidad.puntaje_total,
            entidad.nivel_severidad,
            entidad.fecha_aplicacion,
        )
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, valores)
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            if "Duplicate entry" in str(e):
                raise DuplicateEntityError(
                    f"Ya existe un cuestionario con id '{entidad.id}'."
                )
            raise ArchivoCorruptoError(f"Error al insertar en MySQL: {e}.")
        finally:
            cursor.close()
        return entidad

    def listar(self) -> list[CuestionarioGAD7]:
        """Retorna todos los cuestionarios GAD-7 almacenados."""
        sql = f"SELECT * FROM {self._TABLA}"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            filas = cursor.fetchall()
        finally:
            cursor.close()
        return [self._fila_a_modelo(fila) for fila in filas]

    def buscar_por_codigo(self, codigo: str) -> CuestionarioGAD7:
        """Busca un cuestionario por su id.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        sql = f"SELECT * FROM {self._TABLA} WHERE id = %s"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, (codigo,))
            fila = cursor.fetchone()
        finally:
            cursor.close()
        if fila is None:
            raise EntityNotFoundError(
                f"No se encontró el cuestionario GAD-7 con id '{codigo}'."
            )
        return self._fila_a_modelo(fila)

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[CuestionarioGAD7]:
        """Retorna todos los cuestionarios GAD-7 de un estudiante."""
        sql = (
            f"SELECT * FROM {self._TABLA} WHERE codigo_estudiante = %s "
            "ORDER BY fecha_aplicacion DESC"
        )
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, (codigo_estudiante,))
            filas = cursor.fetchall()
        finally:
            cursor.close()
        return [self._fila_a_modelo(fila) for fila in filas]

    def actualizar(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Actualiza un cuestionario GAD-7 existente.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        sql = (
            f"UPDATE {self._TABLA} SET codigo_estudiante = %s, respuestas = %s, "
            "puntaje_total = %s, nivel_severidad = %s, fecha_aplicacion = %s "
            "WHERE id = %s"
        )
        valores = (
            entidad.codigo_estudiante,
            json.dumps(entidad.respuestas),
            entidad.puntaje_total,
            entidad.nivel_severidad,
            entidad.fecha_aplicacion,
            entidad.id,
        )
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, valores)
            if cursor.rowcount == 0:
                raise EntityNotFoundError(
                    f"No se encontró el cuestionario GAD-7 con id '{entidad.id}'."
                )
            self.conexion.commit()
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.conexion.rollback()
            raise ArchivoCorruptoError(f"Error al actualizar en MySQL: {e}.")
        finally:
            cursor.close()
        return entidad

    def eliminar(self, codigo: str) -> None:
        """Elimina un cuestionario GAD-7 por su id.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
        """
        sql = f"DELETE FROM {self._TABLA} WHERE id = %s"
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, (codigo,))
            if cursor.rowcount == 0:
                raise EntityNotFoundError(
                    f"No se encontró el cuestionario GAD-7 con id '{codigo}'."
                )
            self.conexion.commit()
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.conexion.rollback()
            raise ArchivoCorruptoError(f"Error al eliminar en MySQL: {e}.")
        finally:
            cursor.close()

    def _fila_a_modelo(self, fila: dict) -> CuestionarioGAD7:
        """Convierte una fila de MySQL (dict) a CuestionarioGAD7."""
        respuestas = fila["respuestas"]
        if isinstance(respuestas, str):
            respuestas = json.loads(respuestas)
        fecha = fila["fecha_aplicacion"]
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        return CuestionarioGAD7(
            id=fila["id"],
            codigo_estudiante=fila["codigo_estudiante"],
            respuestas=respuestas,
            fecha_aplicacion=fecha,
        )
