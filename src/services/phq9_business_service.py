from __future__ import annotations

from src.models.alerta_riesgo import AlertaRiesgo, NivelPrioridad, TipoAlerta
from src.models.cuestionario_phq9 import CuestionarioPHQ9
from src.utils.constantes_negocio import PUNTAJE_RIESGO_SEVERO_PHQ9


class PHQ9BusinessService:
    """Servicio de reglas de negocio para el cuestionario PHQ-9.

    Regla: si puntaje_total ≥ 20 → crear AlertaRiesgo de tipo DEPRESION_SEVERA
    y notificar por correo al equipo de bienestar.

    Args:
        alerta_repo: repositorio de alertas de riesgo.
        email_service: servicio de notificaciones por correo.
        destinatario: correo del equipo de bienestar que recibe las alertas.
    """

    def __init__(self, alerta_repo, email_service,
                 destinatario: str = "bienestar@uni.edu") -> None:
        self._alerta_repo = alerta_repo
        self._email_service = email_service
        self._destinatario = destinatario

    def evaluar_riesgo(self, cuestionario: CuestionarioPHQ9) -> str:
        """Evalúa el riesgo del cuestionario PHQ-9 y aplica la regla de negocio.

        Args:
            cuestionario: cuestionario PHQ-9 ya persistido.

        Returns:
            Nivel de riesgo detectado: 'DEPRESION_SEVERA' o 'NORMAL'.
        """
        if cuestionario.puntaje_total >= PUNTAJE_RIESGO_SEVERO_PHQ9:
            alerta = AlertaRiesgo(
                codigo_estudiante=cuestionario.codigo_estudiante,
                tipo=TipoAlerta.DEPRESION_SEVERA,
                puntaje=cuestionario.puntaje_total,
                prioridad=NivelPrioridad.ALTA,
            )
            self._alerta_repo.crear(alerta)
            self._notificar_depresion_severa(cuestionario, alerta)
            return "DEPRESION_SEVERA"

        return "NORMAL"

    def _notificar_depresion_severa(
        self, cuestionario: CuestionarioPHQ9, alerta: AlertaRiesgo
    ) -> None:
        asunto = f"ALERTA DEPRESIÓN SEVERA — Estudiante {cuestionario.codigo_estudiante}"
        cuerpo = (
            f"El estudiante {cuestionario.codigo_estudiante} obtuvo un puntaje PHQ-9 de "
            f"{cuestionario.puntaje_total} ({cuestionario.nivel_severidad}).\n"
            f"Alerta ID: {alerta.id}\nFecha: {alerta.fecha.strftime('%Y-%m-%d %H:%M')}"
        )
        self._email_service.enviar(self._destinatario, asunto, cuerpo)
