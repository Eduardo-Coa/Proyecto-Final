class PlataformaError(Exception):
    """Excepción base de la plataforma psicoeducativa.

    Args:
        mensaje: descripción del error.
        codigo: código identificador del error (ej. VAL001).
    """

    def __init__(self, mensaje: str, codigo: str = "") -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo

    def __str__(self) -> str:
        if self.codigo:
            return f"[{self.codigo}] {self.mensaje}"
        return self.mensaje
