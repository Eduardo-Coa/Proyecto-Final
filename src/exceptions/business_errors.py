from src.exceptions.base import PlataformaError


class BusinessRuleError(PlataformaError):
    """Error base para violaciones de reglas de negocio."""


class ReaplicacionTempranaError(BusinessRuleError):
    """El cuestionario se intenta aplicar antes del período mínimo permitido."""

    def __init__(self, dias_restantes: int) -> None:
        super().__init__(
            f"No puede re-aplicar este cuestionario. Faltan {dias_restantes} días.",
            codigo_error="BR001",
        )


class RiesgoSeveroError(BusinessRuleError):
    """El puntaje indica riesgo severo y requiere atención inmediata."""

    def __init__(self, puntaje: int, umbral: int) -> None:
        super().__init__(
            f"Puntaje {puntaje} supera el umbral de riesgo severo ({umbral}).",
            codigo_error="BR002",
        )


class HorarioFueraDeRangoError(BusinessRuleError):
    """La hora de la sesión está fuera del horario de atención permitido."""

    def __init__(self, hora: str) -> None:
        super().__init__(
            f"La hora {hora} está fuera del horario permitido (08:00 - 18:00).",
            codigo_error="BR003",
        )


class SesionDuplicadaError(BusinessRuleError):
    """Ya existe una sesión agendada para el mismo estudiante en esa fecha."""

    def __init__(self, codigo_estudiante: str, fecha: str) -> None:
        super().__init__(
            f"Ya existe una sesión para {codigo_estudiante} el {fecha}.",
            codigo_error="BR004",
        )
