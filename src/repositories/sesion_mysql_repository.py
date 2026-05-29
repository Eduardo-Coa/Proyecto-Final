from __future__ import annotations

from datetime import datetime
from typing import Any

from src.exceptions.persistence_errors import (
    ArchivoCorruptoError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.models.sesion_seguimiento import EstadoSesion, SesionSeguimiento
from src.repositories.interfaces import IRepository


class SesionMySQLRepository(IRepository[SesionSeguimiento]):
    """Repositorio MySQL para sesiones de seguimiento.

    Implementa la misma interfaz IRepository que la versión JSON, de modo que
    el controller y el business service no necesitan saber cuál implementación
    se está usando.

    Args:
        conexion: conexión activa a MySQL (mysql.connector.MySQLConnection).
    """

    _TABLA = "sesiones_seguimiento"

    def __init__(self, conexion: Any) -> None:
        self.conexion = conexion

    def crear(self, entidad: SesionSeguimiento) -> SesionSeguimiento:
        """Inserta una nueva sesión.

        Raises:
            DuplicateEntityError: si ya existe una sesión con ese id.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
        """
        sql = (
            f"INSERT INTO {self._TABLA} "
            "(id, codigo_estudiante, id_psicologo, fecha_hora, duracion_minutos, "
            "motivo, estado, nota) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        valores = (
            entidad.id,
            entidad.codigo_estudiante,
            entidad.id_psicologo,
            entidad.fecha_hora,
            entidad.duracion_minutos,
            entidad.motivo,
            entidad.estado.value,
            entidad.nota,
        )
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, valores)
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            if "Duplicate entry" in str(e):
                raise DuplicateEntityError(f"Ya existe una sesión con id '{entidad.id}'.")
            raise ArchivoCorruptoError(f"Error al insertar en MySQL: {e}.")
        finally:
            cursor.close()
        return entidad

    def listar(self) -> list[SesionSeguimiento]:
        """Retorna todas las sesiones almacenadas."""
        sql = f"SELECT * FROM {self._TABLA}"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            filas = cursor.fetchall()
        finally:
            cursor.close()
        return [self._fila_a_modelo(fila) for fila in filas]

    def buscar_por_codigo(self, codigo: str) -> SesionSeguimiento:
        """Busca una sesión por su id.

        Raises:
            EntityNotFoundError: si no existe la sesión.
        """
        sql = f"SELECT * FROM {self._TABLA} WHERE id = %s"
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, (codigo.strip(),))
            fila = cursor.fetchone()
        finally:
            cursor.close()
        if fila is None:
            raise EntityNotFoundError(f"No existe una sesión con id '{codigo}'.")
        return self._fila_a_modelo(fila)

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list[SesionSeguimiento]:
        """Retorna todas las sesiones de un estudiante, ordenadas por fecha."""
        sql = (
            f"SELECT * FROM {self._TABLA} WHERE codigo_estudiante = %s "
            "ORDER BY fecha_hora DESC"
        )
        cursor = self.conexion.cursor(dictionary=True)
        try:
            cursor.execute(sql, (codigo_estudiante.strip(),))
            filas = cursor.fetchall()
        finally:
            cursor.close()
        return [self._fila_a_modelo(fila) for fila in filas]

    def actualizar(self, entidad: SesionSeguimiento) -> SesionSeguimiento:
        """Actualiza una sesión existente.

        Raises:
            EntityNotFoundError: si no existe la sesión.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
        """
        sql = (
            f"UPDATE {self._TABLA} SET codigo_estudiante = %s, id_psicologo = %s, "
            "fecha_hora = %s, duracion_minutos = %s, motivo = %s, estado = %s, nota = %s "
            "WHERE id = %s"
        )
        valores = (
            entidad.codigo_estudiante,
            entidad.id_psicologo,
            entidad.fecha_hora,
            entidad.duracion_minutos,
            entidad.motivo,
            entidad.estado.value,
            entidad.nota,
            entidad.id,
        )
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, valores)
            if cursor.rowcount == 0:
                raise EntityNotFoundError(f"No existe una sesión con id '{entidad.id}'.")
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
        """Elimina una sesión por su id.

        Raises:
            EntityNotFoundError: si no existe la sesión.
            ArchivoCorruptoError: si MySQL retorna un error inesperado.
        """
        sql = f"DELETE FROM {self._TABLA} WHERE id = %s"
        cursor = self.conexion.cursor()
        try:
            cursor.execute(sql, (codigo.strip(),))
            if cursor.rowcount == 0:
                raise EntityNotFoundError(f"No existe una sesión con id '{codigo}'.")
            self.conexion.commit()
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.conexion.rollback()
            raise ArchivoCorruptoError(f"Error al eliminar en MySQL: {e}.")
        finally:
            cursor.close()

    def _fila_a_modelo(self, fila: dict) -> SesionSeguimiento:
        """Convierte una fila de MySQL (dict) a SesionSeguimiento."""
        fecha = fila["fecha_hora"]
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        return SesionSeguimiento(
            id=fila["id"],
            codigo_estudiante=fila["codigo_estudiante"],
            id_psicologo=fila["id_psicologo"],
            fecha_hora=fecha,
            duracion_minutos=fila["duracion_minutos"],
            motivo=fila["motivo"] or "",
            estado=EstadoSesion(fila["estado"]),
            nota=fila["nota"] or "",
        )
