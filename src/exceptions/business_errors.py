from src.exceptions.base import PlataformaError


class BusinessRuleError(PlataformaError):
    """Error base para violaciones de reglas de negocio."""


class ReaplicacionTempranaError(BusinessRuleError):
    """El cuestionario se intenta aplicar antes del período mínimo permitido."""

    def __init__(self, mensaje: str = "No han transcurrido los días mínimos para reaplicar el cuestionario.") -> None:
        super().__init__(mensaje, "BR001")


class RiesgoSeveroError(BusinessRuleError):
    """El puntaje indica riesgo severo y requiere atención inmediata."""

    def __init__(self, mensaje: str = "Puntaje de riesgo severo detectado.") -> None:
        super().__init__(mensaje, "BR002")


class HorarioFueraDeRangoError(BusinessRuleError):
    """La hora de la sesión está fuera del horario de atención permitido."""

    def __init__(self, mensaje: str = "La hora está fuera del horario de atención (08:00–18:00).") -> None:
        super().__init__(mensaje, "BR003")


class SesionDuplicadaError(BusinessRuleError):
    """Ya existe una sesión agendada para el mismo estudiante en esa fecha."""

    def __init__(self, mensaje: str = "Ya existe una sesión agendada para ese día.") -> None:
        super().__init__(mensaje, "BR004")
