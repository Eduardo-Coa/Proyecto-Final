from src.exceptions.base import PlataformaError


class ValidationError(PlataformaError):
    """Error base para validaciones de dominio."""


class CodigoInvalidoError(ValidationError):
    """El código institucional no cumple el formato requerido."""

    def __init__(self, mensaje: str = "Código institucional inválido.") -> None:
        super().__init__(mensaje, "VAL001")


class EdadInvalidaError(ValidationError):
    """La edad no cumple el mínimo requerido."""

    def __init__(self, mensaje: str = "Edad inválida.") -> None:
        super().__init__(mensaje, "VAL002")


class SemestreInvalidoError(ValidationError):
    """El semestre está fuera del rango permitido."""

    def __init__(self, mensaje: str = "Semestre inválido.") -> None:
        super().__init__(mensaje, "VAL003")


class CorreoInvalidoError(ValidationError):
    """El correo electrónico no tiene un formato válido."""

    def __init__(self, mensaje: str = "Correo electrónico inválido.") -> None:
        super().__init__(mensaje, "VAL004")


class PuntajeInvalidoError(ValidationError):
    """Un puntaje o ítem está fuera del rango permitido."""

    def __init__(self, mensaje: str = "Puntaje inválido.") -> None:
        super().__init__(mensaje, "VAL005")


class FechaInvalidaError(ValidationError):
    """La fecha no es válida o está fuera del rango permitido."""

    def __init__(self, mensaje: str = "Fecha inválida.") -> None:
        super().__init__(mensaje, "VAL006")
