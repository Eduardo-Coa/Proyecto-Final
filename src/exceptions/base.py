class PlataformaError(Exception):
    """Excepción base de la plataforma psicoeducativa.

    Args:
        mensaje: descripción del error.
        codigo_error: código identificador del error (ej. VAL001).
    """

    def __init__(self, mensaje: str, codigo_error: str | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self) -> str:
        if self.codigo_error:
            return f"[{self.codigo_error}] {self.mensaje}"
        return self.mensaje
