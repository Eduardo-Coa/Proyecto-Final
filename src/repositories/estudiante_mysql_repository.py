from __future__ import annotations

from datetime import datetime
from typing import Any

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.estudiante import Estudiante
from src.repositories.interfaces import IRepository


class EstudianteMySQLRepository(IRepository[Estudiante]):
    """Repositorio MySQL para estudiantes.

    Implementa la misma interfaz IRepository que la versión JSON, de modo que
    el resto del sistema (controller, vista) no necesita saber cuál de las dos
    implementaciones se está usando.

    Args:
        conexion: conexión activa a MySQL (mysql.connector.MySQLConnection).
    """

    _TABLA = "estudiantes"

    def __init__(self, conexion: Any) -> None:
        self.conexion = conexion

    def crear(self, entidad: Estudiante) -> Estudiante:
        """Inserta un nuevo estudiante.

        Aplica la regla de negocio del integrante 1: no pueden existir dos
        estudiantes con el mismo código institucional.

        Raises:
            DuplicateEntityError: si ya existe un estudiante con ese código.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
        """
        sql = (
            f"INSERT INTO {self._TABLA} "
            "(codigo, nombre_completo, edad, semestre, correo, programa, "
            "fecha_registro) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        valores = (
            entidad.codigo,
            entidad.nombre_completo,
            entidad.edad,
            entidad.semestre,
            entidad.correo,
            entidad.programa,
            entidad.fecha_registro,
        )
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, valores)
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            if "Duplicate entry" in str(e):
                raise DuplicateEntityError(
                    f"Ya existe un estudiante con el código '{entidad.codigo}'."
                )
            raise ArchivoCorruptoError(f"Error al insertar en MySQL: {e}.")
        finally:
            cursor.close()
        return entidad

    def listar(self) -> list[Estudiante]:
        """Retorna todos los estudiantes almacenados."""
        sql = f"SELECT * FROM {self._TABLA} ORDER BY fecha_registro DESC"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            filas = cursor.fetchall()
        finally:
            cursor.close()
        return [self._fila_a_modelo(fila) for fila in filas]

    def buscar_por_codigo(self, codigo: str) -> Estudiante:
        """Busca un estudiante por su código institucional.

        Raises:
            EntityNotFoundError: si no existe el estudiante.
        """
        sql = f"SELECT * FROM {self._TABLA} WHERE codigo = %s"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, (codigo,))
            fila = cursor.fetchone()
        finally:
            cursor.close()
        if fila is None:
            raise EntityNotFoundError(
                f"No se encontró el estudiante con código '{codigo}'."
            )
        return self._fila_a_modelo(fila)

    def actualizar(self, entidad: Estudiante) -> Estudiante:
        """Actualiza un estudiante existente.

        Raises:
            EntityNotFoundError: si no existe el estudiante.
        """
        sql = (
            f"UPDATE {self._TABLA} SET nombre_completo = %s, edad = %s, "
            "semestre = %s, correo = %s, programa = %s WHERE codigo = %s"
        )
        valores = (
            entidad.nombre_completo,
            entidad.edad,
            entidad.semestre,
            entidad.correo,
            entidad.programa,
            entidad.codigo,
        )
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, valores)
            if cursor.rowcount == 0:
                raise EntityNotFoundError(
                    f"No se encontró el estudiante con código '{entidad.codigo}'."
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
        """Elimina un estudiante por su código institucional.

        Raises:
            EntityNotFoundError: si no existe el estudiante.
        """
        sql = f"DELETE FROM {self._TABLA} WHERE codigo = %s"
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, (codigo,))
            if cursor.rowcount == 0:
                raise EntityNotFoundError(
                    f"No se encontró el estudiante con código '{codigo}'."
                )
            self.conexion.commit()
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.conexion.rollback()
            raise ArchivoCorruptoError(f"Error al eliminar en MySQL: {e}.")
        finally:
            cursor.close()

    def _fila_a_modelo(self, fila: dict) -> Estudiante:
        """Convierte una fila de MySQL (dict) a Estudiante."""
        fecha = fila["fecha_registro"]
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        return Estudiante(
            codigo=fila["codigo"],
            nombre_completo=fila["nombre_completo"],
            edad=fila["edad"],
            semestre=fila["semestre"],
            correo=fila["correo"],
            programa=fila["programa"],
            fecha_registro=fecha,
        )
