from __future__ import annotations

from src.exceptions.persistence_errors import EntityNotFoundError, PersistenceError
from src.exceptions.validation_errors import ValidationError
from src.models.estudiante import Estudiante
from src.repositories.interfaces import IRepository


class EstudianteController:
    """Controlador MVC para la entidad Estudiante.

    Recibe datos crudos de la vista, construye el modelo, delega al repositorio
    y traduce excepciones a tuplas (bool, str).

    Args:
        repositorio: repositorio de estudiantes (puede estar decorado).
    """

    def __init__(self, repositorio: IRepository) -> None:
        self._repo = repositorio

    def registrar(
        self,
        codigo: str,
        nombre_completo: str,
        edad: int,
        semestre: int,
        correo: str,
        programa: str,
    ) -> tuple[bool, str]:
        """Registra un nuevo estudiante.

        Args:
            codigo: código institucional único.
            nombre_completo: nombre y apellidos.
            edad: edad (>= 16).
            semestre: semestre (1-12).
            correo: correo institucional.
            programa: programa académico.

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            estudiante = Estudiante(
                codigo=codigo,
                nombre_completo=nombre_completo,
                edad=edad,
                semestre=semestre,
                correo=correo,
                programa=programa,
            )
            self._repo.crear(estudiante)
            return True, f"Estudiante '{estudiante.codigo}' registrado correctamente."
        except ValidationError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def listar(self) -> tuple[bool, str | list[Estudiante]]:
        """Retorna todos los estudiantes registrados.

        Returns:
            (True, lista_de_estudiantes) o (False, mensaje_error).
        """
        try:
            return True, self._repo.listar()
        except PersistenceError as e:
            return False, str(e)

    def buscar(self, codigo: str) -> tuple[bool, str | Estudiante]:
        """Busca un estudiante por su código institucional.

        Args:
            codigo: código del estudiante.

        Returns:
            (True, estudiante) o (False, mensaje_error).
        """
        try:
            return True, self._repo.buscar_por_codigo(codigo)
        except EntityNotFoundError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def actualizar(
        self,
        codigo: str,
        nombre_completo: str,
        edad: int,
        semestre: int,
        correo: str,
        programa: str,
    ) -> tuple[bool, str]:
        """Actualiza un estudiante existente.

        El código no se puede modificar (es la clave primaria).

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            existente = self._repo.buscar_por_codigo(codigo)
            estudiante = Estudiante(
                codigo=codigo,
                nombre_completo=nombre_completo,
                edad=edad,
                semestre=semestre,
                correo=correo,
                programa=programa,
                fecha_registro=existente.fecha_registro,
            )
            self._repo.actualizar(estudiante)
            return True, f"Estudiante '{estudiante.codigo}' actualizado correctamente."
        except EntityNotFoundError as e:
            return False, str(e)
        except ValidationError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)

    def eliminar(self, codigo: str) -> tuple[bool, str]:
        """Elimina un estudiante por su código institucional.

        Args:
            codigo: código del estudiante a eliminar.

        Returns:
            (True, mensaje_éxito) o (False, mensaje_error).
        """
        try:
            self._repo.eliminar(codigo)
            return True, f"Estudiante '{codigo}' eliminado correctamente."
        except EntityNotFoundError as e:
            return False, str(e)
        except PersistenceError as e:
            return False, str(e)
