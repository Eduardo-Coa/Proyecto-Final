from __future__ import annotations

from datetime import datetime

from src.exceptions.business_errors import BusinessRuleError
from src.exceptions.persistence_errors import EntityNotFoundError, PersistenceError
from src.exceptions.validation_errors import ValidationError
from src.models.cuestionario_phq9 import CuestionarioPHQ9
from src.Interfaces.interfaces import IRepository


class PHQ9Controller:
    """Controlador MVC para el cuestionario PHQ-9.

    Recibe datos crudos de la vista, construye el modelo, delega al repositorio
    y al servicio de negocio, y traduce excepciones a tuplas (bool, str).

    Args:
        repositorio: repositorio de cuestionarios PHQ-9 (puede estar decorado).
        business_service: servicio de reglas de negocio PHQ-9.
    """

    def __init__(self, repositorio: IRepository[CuestionarioPHQ9], business_service) -> None:
        self._repo = repositorio
        self._business = business_service

    def registrar(
        self,
        codigo_estudiante: str,
        respuestas: list[int],
        fecha_aplicacion: datetime | None = None,
    ) -> tuple[bool, str]:
        """Registra un nuevo cuestionario PHQ-9 y evalúa el riesgo.

        Args:
            codigo_estudiante: código institucional del estudiante.
            respuestas: lista de 9 valores enteros entre 0 y 3.
            fecha_aplicacion: fecha de aplicación (por defecto, ahora).

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            kwargs: dict = {"codigo_estudiante": codigo_estudiante, "respuestas": respuestas}
            if fecha_aplicacion:
                kwargs["fecha_aplicacion"] = fecha_aplicacion
            cuestionario = CuestionarioPHQ9(**kwargs)
            self._repo.crear(cuestionario)
            self._business.evaluar_riesgo(cuestionario)
            return True, (
                f"PHQ-9 registrado correctamente. "
                f"Puntaje: {cuestionario.puntaje_total} — {cuestionario.nivel_severidad}."
            )
        except ValidationError as e:
            return False, str(e)
        except BusinessRuleError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def listar(self) -> tuple[bool, str | list[CuestionarioPHQ9]]:
        """Retorna todos los cuestionarios PHQ-9 registrados.

        Returns:
            (True, lista_de_cuestionarios) o (False, mensaje_error).
        """
        try:
            return True, self._repo.listar()
        except PersistenceError as e:
            return False, str(e)

    def buscar(self, id_cuestionario: str) -> tuple[bool, str | CuestionarioPHQ9]:
        """Busca un cuestionario PHQ-9 por su id.

        Args:
            id_cuestionario: id del cuestionario.

        Returns:
            (True, cuestionario) o (False, mensaje_error).
        """
        try:
            return True, self._repo.buscar_por_codigo(id_cuestionario)
        except EntityNotFoundError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def buscar_por_estudiante(
        self, codigo_estudiante: str
    ) -> tuple[bool, str | list[CuestionarioPHQ9]]:
        """Retorna todos los cuestionarios PHQ-9 de un estudiante.

        Args:
            codigo_estudiante: código institucional del estudiante.

        Returns:
            (True, lista_de_cuestionarios) o (False, mensaje_error).
        """
        try:
            return True, self._repo.buscar_por_estudiante(codigo_estudiante)
        except PersistenceError as e:
            return False, str(e)

    def actualizar(
        self,
        id_cuestionario: str,
        codigo_estudiante: str,
        respuestas: list[int],
        fecha_aplicacion: datetime | None = None,
    ) -> tuple[bool, str]:
        """Actualiza un cuestionario PHQ-9 existente y re-evalúa el riesgo.

        Args:
            id_cuestionario: id del cuestionario a actualizar.
            codigo_estudiante: nuevo (o mismo) código institucional.
            respuestas: nuevas respuestas (9 enteros entre 0 y 3).
            fecha_aplicacion: nueva fecha de aplicación (opcional).

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            kwargs: dict = {
                "id": id_cuestionario,
                "codigo_estudiante": codigo_estudiante,
                "respuestas": respuestas,
            }
            if fecha_aplicacion:
                kwargs["fecha_aplicacion"] = fecha_aplicacion
            cuestionario = CuestionarioPHQ9(**kwargs)
            self._repo.actualizar(cuestionario)
            self._business.evaluar_riesgo(cuestionario)
            return True, (
                f"PHQ-9 actualizado correctamente. "
                f"Puntaje: {cuestionario.puntaje_total} — {cuestionario.nivel_severidad}."
            )
        except ValidationError as e:
            return False, str(e)
        except BusinessRuleError as e:
            return False, str(e)
        except EntityNotFoundError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def eliminar(self, id_cuestionario: str) -> tuple[bool, str]:
        """Elimina un cuestionario PHQ-9 por su id.

        Args:
            id_cuestionario: id del cuestionario a eliminar.

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            self._repo.eliminar(id_cuestionario)
            return True, "Cuestionario PHQ-9 eliminado correctamente."
        except EntityNotFoundError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)
