from __future__ import annotations

from datetime import datetime

from src.exceptions.business_errors import BusinessRuleError
from src.exceptions.persistence_errors import EntityNotFoundError, PersistenceError
from src.exceptions.validation_errors import ValidationError
from src.models.cuestionario_gad7 import CuestionarioGAD7
from src.repositories.interfaces import IRepository


class GAD7Controller:
    """Controlador MVC para el cuestionario GAD-7.

    Recibe datos crudos de la vista, construye el modelo, delega al repositorio
    y al servicio de negocio, y traduce excepciones a tuplas (bool, str).

    Args:
        repositorio: repositorio de cuestionarios GAD-7 (puede estar decorado).
        business_service: servicio de reglas de negocio GAD-7.
    """

    def __init__(self, repositorio: IRepository, business_service) -> None:
        self._repo = repositorio
        self._business = business_service

    def registrar(
        self,
        codigo_estudiante: str,
        respuestas: list[int],
        fecha_aplicacion: datetime | None = None,
    ) -> tuple[bool, str]:
        """Registra un nuevo cuestionario GAD-7 y evalúa el riesgo.

        Args:
            codigo_estudiante: código institucional del estudiante.
            respuestas: lista de 7 valores enteros entre 0 y 3.
            fecha_aplicacion: fecha de aplicación (por defecto, ahora).

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            kwargs = {"codigo_estudiante": codigo_estudiante, "respuestas": respuestas}
            if fecha_aplicacion:
                kwargs["fecha_aplicacion"] = fecha_aplicacion
            cuestionario = CuestionarioGAD7(**kwargs)
            self._repo.crear(cuestionario)
            self._business.evaluar_riesgo(cuestionario)
            return True, (
                f"GAD-7 registrado correctamente. "
                f"Puntaje: {cuestionario.puntaje_total} — {cuestionario.nivel_severidad}."
            )
        except BusinessRuleError as e:
            return False, str(e)
        except ValidationError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def listar(self) -> tuple[bool, str | list[CuestionarioGAD7]]:
        """Retorna todos los cuestionarios GAD-7 registrados.

        Returns:
            (True, lista_de_cuestionarios) o (False, mensaje_error).
        """
        try:
            return True, self._repo.listar()
        except PersistenceError as e:
            return False, str(e)

    def buscar(self, id_cuestionario: str) -> tuple[bool, str | CuestionarioGAD7]:
        """Busca un cuestionario GAD-7 por su id.

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
    ) -> tuple[bool, str | list[CuestionarioGAD7]]:
        """Retorna todos los cuestionarios GAD-7 de un estudiante.

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
    ) -> tuple[bool, str]:
        """Actualiza un cuestionario GAD-7 existente.

        Args:
            id_cuestionario: id del cuestionario a actualizar.
            codigo_estudiante: nuevo código institucional.
            respuestas: nueva lista de 7 valores enteros entre 0 y 3.

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            cuestionario = CuestionarioGAD7(
                id=id_cuestionario,
                codigo_estudiante=codigo_estudiante,
                respuestas=respuestas,
            )
            self._repo.actualizar(cuestionario)
            return True, (
                f"GAD-7 actualizado correctamente. "
                f"Puntaje: {cuestionario.puntaje_total} — {cuestionario.nivel_severidad}."
            )
        except EntityNotFoundError as e:
            return False, str(e)
        except ValidationError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def eliminar(self, id_cuestionario: str) -> tuple[bool, str]:
        """Elimina un cuestionario GAD-7 por su id.

        Args:
            id_cuestionario: id del cuestionario a eliminar.

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            self._repo.eliminar(id_cuestionario)
            return True, "Cuestionario GAD-7 eliminado correctamente."
        except EntityNotFoundError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)
