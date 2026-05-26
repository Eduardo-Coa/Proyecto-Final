from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.controllers.gad7_controller import GAD7Controller
from src.repositories.db_config import obtener_conexion
from src.repositories.gad7_mysql_repository import GAD7MySQLRepository
from src.services.gad7_business_service import GAD7BusinessService
from src.views.gad7_view import GAD7View


class AppController:
    """Controlador general de la aplicación (composition root).

    Responsabilidades:
        1. Instanciar y conectar todas las capas (repositorios, servicios,
           controladores, vistas).
        2. Crear la ventana principal con el menú de pestañas (Notebook).
        3. Lanzar el mainloop de Tkinter.

    No contiene lógica de negocio: solo orquesta. Cada integrante conecta
    su parte aquí (ver TODOs).
    """

    def __init__(self) -> None:
        self._conexion_db = obtener_conexion()
        self._construir_servicios_compartidos()
        self._construir_repositorios()
        self._construir_business_services()
        self._construir_controllers()

    # ─────────────────────────── Capas ───────────────────────────────────

    def _construir_servicios_compartidos(self) -> None:
        """Servicios usados por más de un BusinessService (Email, Alertas)."""
        # TODO (equipo): cuando se implemente src.services.email_service.EmailService,
        # reemplazar este stub por: EmailService(modo_simulacion=True)
        self._email_service = _EmailServiceStub()

        # TODO (equipo): cuando se implemente src.repositories.alerta_repository.AlertaRepository,
        # reemplazar este stub por: AlertaRepository()
        self._alerta_repo = _AlertaRepoStub()

    def _construir_repositorios(self) -> None:
        """Una entidad CRUD por integrante."""
        # TODO (Alejandro): from src.repositories.estudiante_repository import EstudianteRepository
        # self._estudiante_repo = EstudianteRepository()

        # TODO (Eduardo): from src.repositories.phq9_repository import PHQ9Repository
        # self._phq9_repo = PHQ9Repository()
        self._phq9_repo = _PHQ9RepoStub()  # temporal hasta que Eduardo agregue su repo

        # Diunis — GAD7 (MySQL)
        # Para volver a JSON local: usar GAD7JsonRepository(Path("data/cuestionarios_gad7.json"))
        self._gad7_repo = GAD7MySQLRepository(self._conexion_db)

        # TODO (Ceni): from src.repositories.sesion_repository import SesionRepository
        # self._sesion_repo = SesionRepository()

        # TODO (equipo): envolver los 4 repositorios CRUD con NotificacionDecorator
        # cuando se implemente (criterio 7 del proyecto).
        # Ejemplo:
        #   self._gad7_repo = NotificacionDecorator(
        #       self._gad7_repo, self._email_service,
        #       "bienestar@uni.edu", "GAD-7"
        #   )

    def _construir_business_services(self) -> None:
        """Reglas de negocio por integrante."""
        # TODO (Alejandro): EstudianteBusinessService — si aplica
        # TODO (Eduardo): PHQ9BusinessService(self._alerta_repo, self._email_service)
        # TODO (Ceni): SesionBusinessService(self._sesion_repo, self._phq9_repo, self._gad7_repo)

        # Diunis — GAD7
        self._gad7_business = GAD7BusinessService(
            phq9_repo=self._phq9_repo,
            alerta_repo=self._alerta_repo,
            email_service=self._email_service,
        )

    def _construir_controllers(self) -> None:
        """Un controller específico por entidad."""
        # TODO (Alejandro): self._estudiante_controller = EstudianteController(...)
        # TODO (Eduardo): self._phq9_controller = PHQ9Controller(...)
        # TODO (Ceni): self._sesion_controller = SesionController(...)

        # Diunis — GAD7
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

        # TODO (Alejandro): reemplazar el placeholder por EstudianteView
        # estudiante_view = EstudianteView(notebook, self._estudiante_controller)
        # notebook.add(estudiante_view, text="Estudiantes")
        self._agregar_placeholder(notebook, "Estudiantes", "Alejandro")

        # TODO (Eduardo): reemplazar el placeholder por PHQ9View
        # phq9_view = PHQ9View(notebook, self._phq9_controller)
        # notebook.add(phq9_view, text="PHQ-9")
        self._agregar_placeholder(notebook, "PHQ-9", "Eduardo")

        # Diunis — pestaña GAD-7 (funcional)
        gad7_view = GAD7View(notebook, self._gad7_controller)
        notebook.add(gad7_view, text="GAD-7")

        # TODO (Ceni): reemplazar el placeholder por SesionView
        # sesion_view = SesionView(notebook, self._sesion_controller)
        # notebook.add(sesion_view, text="Sesiones")
        self._agregar_placeholder(notebook, "Sesiones", "Ceni")

        # TODO (equipo): pestaña Dashboard analítico (analytics + ml)
        self._agregar_placeholder(notebook, "Dashboard", "equipo (analytics)")

        self._root.mainloop()

    def _agregar_placeholder(self, notebook: ttk.Notebook, nombre: str,
                             responsable: str) -> None:
        """Crea una pestaña vacía con un mensaje informativo."""
        frame = ttk.Frame(notebook)
        ttk.Label(
            frame,
            text=f"Sección «{nombre}» pendiente de implementación por {responsable}",
            font=("", 13),
            foreground="gray",
        ).pack(expand=True)
        notebook.add(frame, text=nombre)


# ─────────────────────────── Stubs temporales ────────────────────────────
# Estas clases existen solo para que la app arranque sin todas las piezas.
# Cada una debe ser reemplazada por su implementación real cuando esté lista.


class _EmailServiceStub:
    """Stub temporal de EmailService — imprime en consola en lugar de enviar."""

    def enviar(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        print(f"\n[EMAIL SIMULADO]\n  Para: {destinatario}\n  Asunto: {asunto}\n  {cuerpo}\n")


class _AlertaRepoStub:
    """Stub temporal de AlertaRepository — solo imprime en consola."""

    def crear(self, alerta) -> None:
        print(f"[ALERTA SIMULADA] tipo={alerta.tipo.value} estudiante={alerta.codigo_estudiante}")


class _PHQ9RepoStub:
    """Stub temporal de PHQ9Repository — siempre retorna lista vacía.

    Sin un PHQ-9 severo reciente, la regla de comorbilidad de GAD7BusinessService
    nunca se dispara, así que las alertas serán solo ANSIEDAD_SEVERA o NORMAL.
    Cuando Eduardo conecte el repo real, la regla completa funcionará.
    """

    def buscar_por_estudiante(self, codigo_estudiante: str) -> list:
        return []
