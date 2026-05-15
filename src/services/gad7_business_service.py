from __future__ import annotations

from datetime import datetime, timedelta

from src.exceptions.business_errors import RiesgoSeveroError
from src.models.alerta_riesgo import AlertaRiesgo, NivelPrioridad, TipoAlerta
from src.models.cuestionario_gad7 import CuestionarioGAD7
from src.utils.constantes_negocio import (
    DIAS_VENTANA_COMORBILIDAD,
    PUNTAJE_RIESGO_SEVERO_GAD7,
    PUNTAJE_RIESGO_SEVERO_PHQ9,
)


class GAD7BusinessService:
    """Servicio de reglas de negocio para el cuestionario GAD-7.

    Args:
        phq9_repo: repositorio de cuestionarios PHQ-9 (para verificar comorbilidad).
        alerta_repo: repositorio de alertas de riesgo.
        email_service: servicio de notificaciones por correo.
    """

    def __init__(self, phq9_repo, alerta_repo, email_service) -> None:
        self._phq9_repo = phq9_repo
        self._alerta_repo = alerta_repo
        self._email_service = email_service

    def evaluar_riesgo(self, cuestionario: CuestionarioGAD7) -> str:
        """Evalúa el riesgo del cuestionario GAD-7 y aplica las reglas de negocio.

        Regla de comorbilidad: si GAD-7 ≥ 15 Y existe un PHQ-9 con puntaje ≥ 20
        aplicado en los últimos 30 días, se genera una AlertaRiesgo de tipo
        COMORBILIDAD y se notifica por correo.

        Args:
            cuestionario: cuestionario GAD-7 ya persistido.

        Returns:
            Nivel de riesgo detectado: 'COMORBILIDAD', 'ANSIEDAD_SEVERA' o 'NORMAL'.

        Raises:
            RiesgoSeveroError: si se detecta comorbilidad severa.
        """
        if cuestionario.puntaje_total >= PUNTAJE_RIESGO_SEVERO_GAD7:
            if self._tiene_phq9_severo_reciente(cuestionario.codigo_estudiante,
                                                cuestionario.fecha_aplicacion):
                alerta = AlertaRiesgo(
                    codigo_estudiante=cuestionario.codigo_estudiante,
                    tipo=TipoAlerta.COMORBILIDAD,
                    puntaje=cuestionario.puntaje_total,
                    prioridad=NivelPrioridad.ALTA,
                )
                self._alerta_repo.crear(alerta)
                self._notificar_comorbilidad(cuestionario, alerta)
                raise RiesgoSeveroError(
                    f"Comorbilidad detectada: GAD-7={cuestionario.puntaje_total} "
                    f"con PHQ-9 severo reciente. Alerta generada."
                )
            alerta = AlertaRiesgo(
                codigo_estudiante=cuestionario.codigo_estudiante,
                tipo=TipoAlerta.ANSIEDAD_SEVERA,
                puntaje=cuestionario.puntaje_total,
                prioridad=NivelPrioridad.ALTA,
            )
            self._alerta_repo.crear(alerta)
            self._notificar_ansiedad_severa(cuestionario, alerta)
            return "ANSIEDAD_SEVERA"

        return "NORMAL"

    def _tiene_phq9_severo_reciente(self, codigo_estudiante: str,
                                    fecha_referencia: datetime) -> bool:
        """Verifica si el estudiante tiene un PHQ-9 severo en los últimos 30 días."""
        ventana = fecha_referencia - timedelta(days=DIAS_VENTANA_COMORBILIDAD)
        cuestionarios_phq9 = self._phq9_repo.buscar_por_estudiante(codigo_estudiante)
        return any(
            c.puntaje_total >= PUNTAJE_RIESGO_SEVERO_PHQ9
            and ventana <= c.fecha_aplicacion <= fecha_referencia
            for c in cuestionarios_phq9
        )

    def _notificar_comorbilidad(self, cuestionario: CuestionarioGAD7,
                                alerta: AlertaRiesgo) -> None:
        asunto = f"ALERTA COMORBILIDAD — Estudiante {cuestionario.codigo_estudiante}"
        cuerpo = (
            f"Se detectó comorbilidad en el estudiante {cuestionario.codigo_estudiante}.\n"
            f"GAD-7: {cuestionario.puntaje_total} (Severo) con PHQ-9 severo en los últimos "
            f"{DIAS_VENTANA_COMORBILIDAD} días.\n"
            f"Alerta ID: {alerta.id}\nFecha: {alerta.fecha.strftime('%Y-%m-%d %H:%M')}"
        )
        self._email_service.enviar("bienestar@uni.edu", asunto, cuerpo)

    def _notificar_ansiedad_severa(self, cuestionario: CuestionarioGAD7,
                                   alerta: AlertaRiesgo) -> None:
        asunto = f"ALERTA ANSIEDAD SEVERA — Estudiante {cuestionario.codigo_estudiante}"
        cuerpo = (
            f"El estudiante {cuestionario.codigo_estudiante} obtuvo un puntaje GAD-7 de "
            f"{cuestionario.puntaje_total} (Severo).\n"
            f"Alerta ID: {alerta.id}\nFecha: {alerta.fecha.strftime('%Y-%m-%d %H:%M')}"
        )
        self._email_service.enviar("bienestar@uni.edu", asunto, cuerpo)
