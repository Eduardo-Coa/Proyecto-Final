from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.cuestionario_phq9 import CuestionarioPHQ9
from src.repositories.interfaces import IRepository


class PHQ9MySQLRepository(IRepository[CuestionarioPHQ9]):
    """Repositorio MySQL para cuestionarios PHQ-9.

    Implementa la misma interfaz IRepository que la version JSON, de modo que
    el controller y el business service no necesitan saber cual implementacion
    se esta usando.

    Args:
        conexion: conexion activa a MySQL (mysql.connector.MySQLConnection).
    """

    _TABLA = "cuestionarios_phq9"

    def __init__(self, conexion: Any) -> None:
        self.conexion = conexion

    def crear(self, entidad: CuestionarioPHQ9) -> CuestionarioPHQ9:
        """Inserta un nuevo cuestionario PHQ-9.

        Args:
            entidad: instancia validada de CuestionarioPHQ9.

        Returns:
            El mismo cuestionario persistido.

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

    def listar(self) -> list[CuestionarioPHQ9]:
        """Retorna todos los cuestionarios PHQ-9 almacenados."""
        sql = f"SELECT * FROM {self._TABLA}"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            filas = cursor.fetchall()
        finally:
            cursor.close()
        return [self._fila_a_modelo(fila) for fila in filas]

    def buscar_por_codigo(self, codigo: str) -> CuestionarioPHQ9:
        """Busca un cuestionario por su id.

        Args:
            codigo: id del cuestionario.

        Returns:
            El cuestionario encontrado.

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
                f"No se encontro el cuestionario PHQ-9 con id '{codigo}'."
            )
        return self._fila_a_modelo(fila)

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[CuestionarioPHQ9]:
        """Retorna todos los cuestionarios PHQ-9 de un estudiante, ordenados por fecha.

        Args:
            codigo_estudiante: codigo institucional del estudiante.

        Returns:
            Lista ordenada por fecha descendente.
        """
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

    def actualizar(self, entidad: CuestionarioPHQ9) -> CuestionarioPHQ9:
        """Actualiza un cuestionario PHQ-9 existente.

        Args:
            entidad: instancia con los datos actualizados.

        Returns:
            El cuestionario actualizado.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
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
                    f"No se encontro el cuestionario PHQ-9 con id '{entidad.id}'."
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
        """Elimina un cuestionario PHQ-9 por su id.

        Args:
            codigo: id del cuestionario a eliminar.

        Raises:
            EntityNotFoundError: si no existe el cuestionario.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
        """
        sql = f"DELETE FROM {self._TABLA} WHERE id = %s"
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, (codigo,))
            if cursor.rowcount == 0:
                raise EntityNotFoundError(
                    f"No se encontro el cuestionario PHQ-9 con id '{codigo}'."
                )
            self.conexion.commit()
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.conexion.rollback()
            raise ArchivoCorruptoError(f"Error al eliminar en MySQL: {e}.")
        finally:
            cursor.close()

    def _fila_a_modelo(self, fila: dict) -> CuestionarioPHQ9:
        """Convierte una fila de MySQL (dict) a CuestionarioPHQ9."""
        respuestas = fila["respuestas"]
        if isinstance(respuestas, str):
            respuestas = json.loads(respuestas)
        fecha = fila["fecha_aplicacion"]
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        return CuestionarioPHQ9(
            id=fila["id"],
            codigo_estudiante=fila["codigo_estudiante"],
            respuestas=respuestas,
            fecha_aplicacion=fecha,
        )
