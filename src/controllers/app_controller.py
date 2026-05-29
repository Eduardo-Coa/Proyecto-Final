from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.controllers.phq9_controller import PHQ9Controller
from src.repositories.db_config import obtener_conexion
from src.repositories.phq9_mysql_repository import PHQ9MySQLRepository
from src.services.email_service import EmailService
from src.services.notificacion_decorator import NotificacionDecorator
from src.services.phq9_business_service import PHQ9BusinessService
from src.views.dashboard_view import DashboardView
from src.views.phq9_view import PHQ9View


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
        """Servicios compartidos: EmailService real (modo simulación) y AlertaRepository stub."""
        self._email_service = EmailService(modo_simulacion=True)
        self._alerta_repo = _AlertaRepoStub()

    def _construir_repositorios(self) -> None:
        """Eduardo — PHQ-9 (MySQL) envuelto en NotificacionDecorator (patrón GoF)."""
        self._conexion_db = obtener_conexion()
        repo_base = PHQ9MySQLRepository(self._conexion_db)
        self._phq9_repo = NotificacionDecorator(
            repositorio=repo_base,
            email_service=self._email_service,
            destinatario="bienestar@uni.edu",
            nombre_entidad="PHQ-9",
        )
        # TODO (Alejandro): self._estudiante_repo = EstudianteRepository()
        # TODO (Diunis):    self._gad7_repo = GAD7JsonRepository(...)
        # TODO (Ceni):      self._sesion_repo = SesionRepository()

    def _construir_business_services(self) -> None:
        """Eduardo — PHQ-9. Los demás integrantes agregarán sus servicios aquí."""
        self._phq9_business = PHQ9BusinessService(
            alerta_repo=self._alerta_repo,
            email_service=self._email_service,
        )
        # TODO (Diunis): self._gad7_business = GAD7BusinessService(...)
        # TODO (Ceni):   self._sesion_business = SesionBusinessService(...)

    def _construir_controllers(self) -> None:
        """Eduardo — PHQ-9. Los demás integrantes agregarán sus controladores aquí."""
        self._phq9_controller = PHQ9Controller(
            repositorio=self._phq9_repo,
            business_service=self._phq9_business,
        )
        # TODO (Alejandro): self._estudiante_controller = EstudianteController(...)
        # TODO (Diunis):    self._gad7_controller = GAD7Controller(...)
        # TODO (Ceni):      self._sesion_controller = SesionController(...)

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

        # Eduardo — PHQ-9 (funcional)
        phq9_view = PHQ9View(notebook, self._phq9_controller)
        notebook.add(phq9_view, text="PHQ-9")

        # TODO (Diunis): GAD7View
        self._agregar_placeholder(notebook, "GAD-7", "Diunis")

        # TODO (Ceni): SesionView
        self._agregar_placeholder(notebook, "Sesiones", "Ceni")

        # Dashboard analítico (esqueleto de equipo; sección PHQ-9 funcional — Eduardo)
        dashboard_view = DashboardView(notebook)
        notebook.add(dashboard_view, text="Dashboard")

        self._root.mainloop()

    def _agregar_placeholder(self, notebook: ttk.Notebook, nombre: str,
                             responsable: str) -> None:
        frame = ttk.Frame(notebook)
        ttk.Label(
            frame,
            text=f"Seccion '{nombre}' pendiente de implementacion por {responsable}",
            font=("", 13),
            foreground="gray",
        ).pack(expand=True)
        notebook.add(frame, text=nombre)


# ─────────────────────────── Stubs temporales ────────────────────────────

class _AlertaRepoStub:
    """Stub de AlertaRepository — imprime en consola hasta que se implemente el real."""

    def crear(self, alerta) -> None:
        print(f"[ALERTA] tipo={alerta.tipo.value} estudiante={alerta.codigo_estudiante}")
