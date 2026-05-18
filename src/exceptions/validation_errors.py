from src.exceptions.base import PlataformaError


class ValidationError(PlataformaError):
    """Error base para validaciones de dominio."""


class CodigoInvalidoError(ValidationError):
    """El código institucional no cumple el formato requerido."""

    def __init__(self, codigo: str) -> None:
        super().__init__(
            f"El código '{codigo}' no es válido. Debe tener al menos 4 caracteres.",
            codigo_error="VAL001",
        )


class EdadInvalidaError(ValidationError):
    """La edad no cumple el mínimo requerido."""

    def __init__(self, edad: int) -> None:
        super().__init__(
            f"La edad {edad} no es válida. Debe ser ≥ 16 años.",
            codigo_error="VAL002",
        )


class SemestreInvalidoError(ValidationError):
    """El semestre está fuera del rango permitido."""

    def __init__(self, semestre: int) -> None:
        super().__init__(
            f"El semestre {semestre} no es válido. Debe estar entre 1 y 12.",
            codigo_error="VAL003",
        )


class CorreoInvalidoError(ValidationError):
    """El correo electrónico no tiene un formato válido."""

    def __init__(self, correo: str) -> None:
        super().__init__(
            f"El correo '{correo}' tiene formato inválido.",
            codigo_error="VAL004",
        )


class PuntajeInvalidoError(ValidationError):
    """Un puntaje o ítem está fuera del rango permitido."""

    def __init__(self, valor: int, rango: tuple[int, int]) -> None:
        super().__init__(
            f"Puntaje {valor} fuera del rango permitido {rango}.",
            codigo_error="VAL005",
        )


class FechaInvalidaError(ValidationError):
    """La fecha no es válida o está fuera del rango permitido."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo, codigo_error="VAL006")
