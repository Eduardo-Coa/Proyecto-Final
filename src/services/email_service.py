from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from src.exceptions.notification_errors import EmailEnvioError


class EmailService:
    """Servicio de envío de correos electrónicos.

    En modo simulación (por defecto) imprime el correo en consola, lo que evita
    depender de credenciales SMTP reales durante el desarrollo y las pruebas.
    En modo real, envía a través de SMTP usando las credenciales provistas.

    Args:
        modo_simulacion: si es True, no se conecta a SMTP, solo imprime.
        host: servidor SMTP (solo se usa si modo_simulacion=False).
        puerto: puerto SMTP.
        usuario: usuario para autenticación SMTP.
        password: contraseña para autenticación SMTP.
        remitente: dirección que aparece como "From".
    """

    def __init__(
        self,
        modo_simulacion: bool = True,
        host: str = "smtp.gmail.com",
        puerto: int = 587,
        usuario: str = "",
        password: str = "",
        remitente: str = "bienestar@uni.edu",
    ) -> None:
        self.modo_simulacion = modo_simulacion
        self.host = host
        self.puerto = puerto
        self.usuario = usuario
        self.password = password
        self.remitente = remitente

    def enviar(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        """Envía un correo electrónico.

        Args:
            destinatario: dirección de correo del destinatario.
            asunto: asunto del mensaje.
            cuerpo: cuerpo del mensaje en texto plano.

        Raises:
            EmailEnvioError: si falla el envío SMTP real.
        """
        if self.modo_simulacion:
            self._enviar_simulado(destinatario, asunto, cuerpo)
            return
        self._enviar_smtp(destinatario, asunto, cuerpo)

    def _enviar_simulado(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        print("\n[EMAIL SIMULADO]")
        print(f"  De:      {self.remitente}")
        print(f"  Para:    {destinatario}")
        print(f"  Asunto:  {asunto}")
        print(f"  Cuerpo:  {cuerpo}\n")

    def _enviar_smtp(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        mensaje = EmailMessage()
        mensaje["From"] = self.remitente
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto
        mensaje.set_content(cuerpo)
        try:
            with smtplib.SMTP(self.host, self.puerto) as servidor:
                servidor.starttls()
                if self.usuario and self.password:
                    servidor.login(self.usuario, self.password)
                servidor.send_message(mensaje)
        except (smtplib.SMTPException, OSError) as e:
            raise EmailEnvioError(f"No se pudo enviar el correo a '{destinatario}': {e}.")

    @classmethod
    def desde_env(cls) -> EmailService:
        """Crea un EmailService leyendo la configuración del entorno (.env).

        Si existen EMAIL_USUARIO y EMAIL_PASSWORD, activa el envío SMTP real;
        en caso contrario, cae en modo simulación (imprime en consola). Así el
        equipo y la evaluación pueden ejecutar la app sin credenciales.

        Returns:
            Instancia configurada de EmailService.
        """
        usuario = os.environ.get("EMAIL_USUARIO", "").strip()
        password = os.environ.get("EMAIL_PASSWORD", "").strip()
        modo_real = bool(usuario and password)
        return cls(
            modo_simulacion=not modo_real,
            host=os.environ.get("EMAIL_HOST", "smtp.gmail.com"),
            puerto=int(os.environ.get("EMAIL_PUERTO", "587")),
            usuario=usuario,
            password=password,
            remitente=os.environ.get("EMAIL_REMITENTE", usuario or "bienestar@uni.edu"),
        )
