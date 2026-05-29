from src.exceptions.base import PlataformaError


class PersistenceError(PlataformaError):
    """Error base para operaciones de persistencia."""


class EntityNotFoundError(PersistenceError):
    """La entidad solicitada no existe en el repositorio."""

    def __init__(self, mensaje: str = "Entidad no encontrada.") -> None:
        super().__init__(mensaje, codigo_error="PER001")


class DuplicateEntityError(PersistenceError):
    """Ya existe una entidad con el mismo identificador único."""

    def __init__(self, mensaje: str = "Entidad duplicada.") -> None:
        super().__init__(mensaje, codigo_error="PER002")


class ArchivoCorruptoError(PersistenceError):
    """El archivo JSON no puede leerse o tiene un formato inválido."""

    def __init__(self, mensaje: str = "Archivo de datos corrupto.") -> None:
        super().__init__(mensaje, codigo_error="PER003")


class DatabaseConnectionError(PersistenceError):
    """No se pudo establecer conexion con la base de datos."""

    def __init__(self, mensaje: str = "Error de conexion a la base de datos.") -> None:
        super().__init__(mensaje, codigo_error="PER004")
