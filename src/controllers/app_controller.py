"""Controlador general de la aplicación (composition root)."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from src.controllers.sesion_controller import SesionController
from src.repositories.sesion_repository import SesionRepository
from src.services.email_service import EmailService
from src.services.notificacion_decorator import NotificacionDecorator
from src.services.sesion_business_service import SesionBusinessService
from src.views.dashboard_view import DashboardView
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
        """Servicios usados por más de un BusinessService (Email, Alertas)."""
        self._email_service = EmailService(modo_simulacion=True)

    def _construir_repositorios(self) -> None:
        """Ceni — Sesion (JSON) envuelto en NotificacionDecorator (patrón GoF, criterio 7)."""
        # TODO (Alejandro): self._estudiante_repo = EstudianteRepository()
        # TODO (Eduardo):   self._phq9_repo = PHQ9Repository()
        # TODO (Diunis):    self._gad7_repo = GAD7Repository()

        # Ceni — Sesion
        repo_base = SesionRepository(Path("data/sesiones.json"))
        self._sesion_repo = NotificacionDecorator(
            repositorio=repo_base,
            email_service=self._email_service,
            destinatario="bienestar@uni.edu",
            nombre_entidad="Sesion",
        )

    def _construir_business_services(self) -> None:
        """Reglas de negocio por integrante."""
        # TODO (Alejandro): EstudianteBusinessService — si aplica
        # TODO (Eduardo):   PHQ9BusinessService(...)
        # TODO (Diunis):    GAD7BusinessService(...)

        # Ceni — Sesion
        self._sesion_business = SesionBusinessService(sesion_repo=self._sesion_repo)

    def _construir_controllers(self) -> None:
        """Un controller específico por entidad."""
        # TODO (Alejandro): self._estudiante_controller = EstudianteController(...)
        # TODO (Eduardo):   self._phq9_controller = PHQ9Controller(...)
        # TODO (Diunis):    self._gad7_controller = GAD7Controller(...)

        # Ceni — Sesion
        self._sesion_controller = SesionController(
            repositorio=self._sesion_repo,
            business_service=self._sesion_business,
        )

    # ─────────────────────────── Menú principal ──────────────────────────

    def run(self) -> None:
        """Crea la ventana principal con el menú y lanza el mainloop."""
        self._root = tk.Tk()
        self._root.title("Plataforma de Apoyo Psicoeducativo — Bienestar Universitario")
        self._root.geometry("1200x800")

        notebook = ttk.Notebook(self._root)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        # TODO (Alejandro): EstudianteView
        self._agregar_placeholder(notebook, "Estudiantes", "Alejandro")

        # TODO (Eduardo): PHQ9View
        self._agregar_placeholder(notebook, "PHQ-9", "Eduardo")

        # TODO (Diunis): GAD7View
        self._agregar_placeholder(notebook, "GAD-7", "Diunis")

        # Ceni — pestaña Sesiones (funcional)
        sesion_view = SesionView(notebook, self._sesion_controller)
        notebook.add(sesion_view, text="Sesiones")

        dashboard_view = DashboardView(notebook)
        notebook.add(dashboard_view, text="Dashboard")

        self._root.mainloop()

    def _agregar_placeholder(self, notebook: ttk.Notebook, nombre: str,
                             responsable: str) -> None:
        frame = ttk.Frame(notebook)
        ttk.Label(
            frame,
            text=f"Sección «{nombre}» pendiente de implementación por {responsable}",
            font=("", 13),
            foreground="gray",
        ).pack(expand=True)
        notebook.add(frame, text=nombre)
