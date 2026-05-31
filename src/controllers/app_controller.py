from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.controllers.estudiante_controller import EstudianteController
from src.controllers.gad7_controller import GAD7Controller
from src.controllers.phq9_controller import PHQ9Controller
from src.controllers.sesion_controller import SesionController
from src.repositories.db_config import obtener_conexion
from src.repositories.estudiante_mysql_repository import EstudianteMySQLRepository
from src.repositories.gad7_mysql_repository import GAD7MySQLRepository
from src.repositories.phq9_mysql_repository import PHQ9MySQLRepository
from src.repositories.sesion_mysql_repository import SesionMySQLRepository
from src.services.email_service import EmailService
from src.services.gad7_business_service import GAD7BusinessService
from src.services.notificacion_decorator import NotificacionDecorator
from src.services.phq9_business_service import PHQ9BusinessService
from src.services.sesion_business_service import SesionBusinessService
from src.views.dashboard_view import DashboardView
from src.views.estudiante_view import EstudianteView
from src.views.gad7_view import GAD7View
from src.views.phq9_view import PHQ9View
from src.views.sesion_view import SesionView


class AppController:
    """Controlador general de la aplicación (composition root).

    Responsabilidades:
        1. Instanciar y conectar todas las capas (repositorios, servicios,
           controladores, vistas).
        2. Crear la ventana principal con el menú de pestañas (Notebook).
        3. Lanzar el mainloop de Tkinter.

    No contiene lógica de negocio: solo orquesta. Cada integrante conecta
    su parte aquí.
    """

    def __init__(self) -> None:
        self._construir_servicios_compartidos()
        self._construir_repositorios()
        self._construir_business_services()
        self._construir_controllers()

    # ─────────────────────────── Capas ───────────────────────────────────

    def _construir_servicios_compartidos(self) -> None:
        """EmailService (modo simulación), AlertaRepository stub y conexión MySQL."""
        self._email_service = EmailService(modo_simulacion=True)
        self._alerta_repo = _AlertaRepoStub()
        self._conexion_db = obtener_conexion()

    def _construir_repositorios(self) -> None:
        """Repositorios MySQL envueltos en NotificacionDecorator (patrón GoF)."""
        # Alejandro — Estudiantes
        repo_estudiante = EstudianteMySQLRepository(self._conexion_db)
        self._estudiante_repo = NotificacionDecorator(
            repositorio=repo_estudiante,
            email_service=self._email_service,
            destinatario="bienestar@uni.edu",
            nombre_entidad="Estudiante",
        )

        # Eduardo — PHQ-9
        repo_phq9 = PHQ9MySQLRepository(self._conexion_db)
        self._phq9_repo = NotificacionDecorator(
            repositorio=repo_phq9,
            email_service=self._email_service,
            destinatario="bienestar@uni.edu",
            nombre_entidad="PHQ-9",
        )

        # Ceni — Sesiones
        repo_sesion = SesionMySQLRepository(self._conexion_db)
        self._sesion_repo = NotificacionDecorator(
            repositorio=repo_sesion,
            email_service=self._email_service,
            destinatario="bienestar@uni.edu",
            nombre_entidad="Sesion",
        )

        # Diunis — GAD-7
        repo_gad7 = GAD7MySQLRepository(self._conexion_db)
        self._gad7_repo = NotificacionDecorator(
            repositorio=repo_gad7,
            email_service=self._email_service,
            destinatario="bienestar@uni.edu",
            nombre_entidad="GAD-7",
        )

    def _construir_business_services(self) -> None:
        """Reglas de negocio por integrante."""
        # Eduardo — PHQ-9
        self._phq9_business = PHQ9BusinessService(
            alerta_repo=self._alerta_repo,
            email_service=self._email_service,
        )

        # Ceni — Sesiones
        self._sesion_business = SesionBusinessService(sesion_repo=self._sesion_repo)

        # Diunis — GAD-7 (comorbilidad: necesita PHQ-9 reciente del estudiante)
        self._gad7_business = GAD7BusinessService(
            phq9_repo=self._phq9_repo,
            alerta_repo=self._alerta_repo,
            email_service=self._email_service,
        )

    def _construir_controllers(self) -> None:
        """Un controller específico por entidad."""
        # Alejandro — Estudiantes
        self._estudiante_controller = EstudianteController(
            repositorio=self._estudiante_repo,
        )

        # Eduardo — PHQ-9
        self._phq9_controller = PHQ9Controller(
            repositorio=self._phq9_repo,
            business_service=self._phq9_business,
        )

        # Ceni — Sesiones
        self._sesion_controller = SesionController(
            repositorio=self._sesion_repo,
            business_service=self._sesion_business,
        )

        # Diunis — GAD-7
        self._gad7_controller = GAD7Controller(
            repositorio=self._gad7_repo,
            business_service=self._gad7_business,
        )

    # ─────────────────────────── Menú principal ──────────────────────────

    def run(self) -> None:
        """Crea la ventana principal con el menú y lanza el mainloop."""
        self._root = tk.Tk()
        self._root.title("Plataforma de Apoyo Psicoeducativo — Bienestar Universitario")
        self._root.geometry("1200x800")

        notebook = ttk.Notebook(self._root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        # Alejandro — Estudiantes (funcional)
        estudiante_view = EstudianteView(notebook, self._estudiante_controller)
        notebook.add(estudiante_view, text="Estudiantes")

        # Eduardo — PHQ-9 (funcional)
        phq9_view = PHQ9View(notebook, self._phq9_controller)
        notebook.add(phq9_view, text="PHQ-9")

        # Diunis — GAD-7 (funcional)
        gad7_view = GAD7View(notebook, self._gad7_controller)
        notebook.add(gad7_view, text="GAD-7")

        # Ceni — Sesiones (funcional)
        sesion_view = SesionView(notebook, self._sesion_controller)
        notebook.add(sesion_view, text="Sesiones")

        # Dashboard analítico del equipo.
        dashboard_view = DashboardView(notebook)
        notebook.add(dashboard_view, text="Dashboard")

        self._root.mainloop()


# ─────────────────────────── Stubs temporales ────────────────────────────

class _AlertaRepoStub:
    """Stub de AlertaRepository — imprime en consola hasta que se implemente el real."""

    def crear(self, alerta) -> None:
        print(f"[ALERTA] tipo={alerta.tipo.value} estudiante={alerta.codigo_estudiante}")
