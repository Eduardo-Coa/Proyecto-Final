from src.exceptions.base import PlataformaError


class NotificacionError(PlataformaError):
    """Error base para fallos en el sistema de notificaciones."""


class EmailEnvioError(NotificacionError):
    """No se pudo enviar el correo electrónico de notificación."""

    def __init__(self, mensaje: str = "Error al enviar el correo electrónico.") -> None:
        super().__init__(mensaje, codigo_error="NOT001")
