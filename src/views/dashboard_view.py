from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.analytics.data_loader import cargar_phq9, listar_programas
from src.analytics.descriptive_stats import kpis_phq9
from src.analytics.visualizations import grafica_severidad_phq9
from src.exceptions.persistence_errors import PersistenceError

_TODOS = "Todos los programas"


class DashboardView(ttk.Frame):
    """Dashboard analítico de la plataforma (vista transversal, no MVC).

    Layout: barra de filtros + tarjetas KPI + grid 2x2 de gráficas.
    Implementada la sección PHQ-9 (Eduardo); las demás son placeholders que
    cada integrante reemplazará con su contribución analítica.

    Args:
        parent: widget padre (notebook o ventana principal).
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._df_phq9: pd.DataFrame = pd.DataFrame()
        self._canvas_phq9: FigureCanvasTkAgg | None = None
        self._kpi_labels: dict[str, ttk.Label] = {}
        self._construir_ui()
        self._refrescar()

    # ------------------------------------------------------------------ UI

    def _construir_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._construir_barra_filtros()
        self._construir_kpis()
        self._construir_graficas()
        self._lbl_estado = ttk.Label(self, text="", foreground="gray")
        self._lbl_estado.grid(row=3, column=0, sticky="w", padx=12, pady=(0, 6))

    def _construir_barra_filtros(self) -> None:
        barra = ttk.Frame(self)
        barra.grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        ttk.Label(barra, text="Programa:").pack(side="left", padx=(0, 4))
        self._var_programa = tk.StringVar(value=_TODOS)
        self._cmb_programa = ttk.Combobox(
            barra, textvariable=self._var_programa, state="readonly", width=30
        )
        self._cmb_programa.pack(side="left", padx=(0, 8))
        self._cmb_programa.bind(
            "<<ComboboxSelected>>", lambda _e: self._actualizar_vista()
        )
        ttk.Button(barra, text="Refrescar", command=self._refrescar).pack(side="left")

    def _construir_kpis(self) -> None:
        cont = ttk.Frame(self)
        cont.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
        for i in range(4):
            cont.columnconfigure(i, weight=1)
        self._kpi_labels["total"] = self._tarjeta_kpi(cont, 0, "Cuestionarios PHQ-9")
        self._kpi_labels["promedio"] = self._tarjeta_kpi(cont, 1, "Puntaje promedio")
        self._kpi_labels["mediana"] = self._tarjeta_kpi(cont, 2, "Puntaje mediano")
        self._kpi_labels["pct_severo"] = self._tarjeta_kpi(cont, 3, "% Riesgo severo")

    def _tarjeta_kpi(self, parent: ttk.Frame, col: int, titulo: str) -> ttk.Label:
        tarjeta = ttk.LabelFrame(parent, text=titulo, padding=8)
        tarjeta.grid(row=0, column=col, sticky="ew", padx=4)
        lbl = ttk.Label(tarjeta, text="—", font=("", 20, "bold"))
        lbl.pack()
        return lbl

    def _construir_graficas(self) -> None:
        grid = ttk.Frame(self)
        grid.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        for i in range(2):
            grid.columnconfigure(i, weight=1)
            grid.rowconfigure(i, weight=1)

        self._placeholder(grid, 0, 0, "Distribución demográfica", "Alejandro")

        self._frame_phq9 = ttk.LabelFrame(grid, text="PHQ-9 — Eduardo", padding=4)
        self._frame_phq9.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self._frame_phq9.columnconfigure(0, weight=1)
        self._frame_phq9.rowconfigure(0, weight=1)

        self._placeholder(grid, 1, 0, "Correlación PHQ-9 ↔ GAD-7", "Diuniz")
        self._placeholder(grid, 1, 1, "Evolución temporal", "Cenaida")

    def _placeholder(
        self, parent: ttk.Frame, row: int, col: int, titulo: str, responsable: str
    ) -> None:
        frame = ttk.LabelFrame(parent, text=titulo, padding=4)
        frame.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        ttk.Label(
            frame, text=f"Pendiente de implementación — {responsable}",
            foreground="gray",
        ).pack(expand=True)

    # ------------------------------------------------------------------ Datos

    def _refrescar(self) -> None:
        try:
            self._df_phq9 = cargar_phq9()
            programas = listar_programas()
        except PersistenceError as e:
            self._mostrar_estado(str(e), "red")
            return
        opciones = [_TODOS] + programas
        self._cmb_programa["values"] = opciones
        if self._var_programa.get() not in opciones:
            self._var_programa.set(_TODOS)
        self._actualizar_vista()
        self._mostrar_estado(
            f"Datos actualizados. {len(self._df_phq9)} cuestionarios PHQ-9 cargados.",
            "green",
        )

    def _actualizar_vista(self) -> None:
        df = self._filtrar(self._df_phq9)
        kpis = kpis_phq9(df)
        self._kpi_labels["total"].config(text=str(kpis["total"]))
        self._kpi_labels["promedio"].config(text=str(kpis["promedio"]))
        self._kpi_labels["mediana"].config(text=str(kpis["mediana"]))
        self._kpi_labels["pct_severo"].config(text=f"{kpis['pct_severo']}%")
        self._dibujar_phq9(df)

    def _filtrar(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        programa = self._var_programa.get()
        if programa and programa != _TODOS and "programa" in df.columns:
            return df[df["programa"] == programa]
        return df

    def _dibujar_phq9(self, df: pd.DataFrame) -> None:
        if self._canvas_phq9 is not None:
            self._canvas_phq9.get_tk_widget().destroy()
        figura = grafica_severidad_phq9(df)
        self._canvas_phq9 = FigureCanvasTkAgg(figura, master=self._frame_phq9)
        self._canvas_phq9.draw()
        self._canvas_phq9.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _mostrar_estado(self, mensaje: str, color: str) -> None:
        self._lbl_estado.config(text=mensaje, foreground=color)
