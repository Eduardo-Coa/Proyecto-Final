"""Vista Tkinter para el CRUD de sesiones de seguimiento."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from src.controllers.sesion_controller import SesionController
from src.models.sesion_seguimiento import SesionSeguimiento
from src.utils.constantes_negocio import HORA_FIN_ATENCION, HORA_INICIO_ATENCION


PSICOLOGOS_DISPONIBLES = ["PSI001", "PSI002", "PSI003", "PSI004"]
DURACIONES_DISPONIBLES = ["30", "45", "60", "90"]
HORAS_DISPONIBLES = [
    f"{h:02d}:{m:02d}"
    for h in range(HORA_INICIO_ATENCION, HORA_FIN_ATENCION)
    for m in (0, 30)
]


class SesionView(ttk.Frame):
    """Vista Tkinter para agendar y administrar sesiones de seguimiento."""

    def __init__(self, parent: tk.Widget, controller: SesionController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._id_seleccionado: str | None = None
        self._sesiones_por_id: dict[str, SesionSeguimiento] = {}
        self._construir_ui()
        self._cargar_tabla()

    # ─────────────────────────── UI ──────────────────────────────────────

    def _construir_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        self._construir_formulario()
        self._construir_tabla()
        self._construir_estado()

    def _construir_formulario(self) -> None:
        frame = ttk.LabelFrame(self, text="Agendar sesión", padding=10)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame, text="Código estudiante:").grid(row=0, column=0, sticky="w", pady=4)
        self._ent_codigo = ttk.Entry(frame, width=25)
        self._ent_codigo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Psicólogo:").grid(row=1, column=0, sticky="w", pady=4)
        self._var_psicologo = tk.StringVar(value=PSICOLOGOS_DISPONIBLES[0])
        ttk.Combobox(
            frame,
            textvariable=self._var_psicologo,
            values=PSICOLOGOS_DISPONIBLES,
            state="readonly",
            width=23,
        ).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Fecha (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=4)
        self._ent_fecha = ttk.Entry(frame, width=25)
        self._ent_fecha.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Hora:").grid(row=3, column=0, sticky="w", pady=4)
        self._var_hora = tk.StringVar(value=HORAS_DISPONIBLES[0])
        ttk.Combobox(
            frame,
            textvariable=self._var_hora,
            values=HORAS_DISPONIBLES,
            state="readonly",
            width=23,
        ).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Duración (min):").grid(row=4, column=0, sticky="w", pady=4)
        self._var_duracion = tk.StringVar(value=DURACIONES_DISPONIBLES[0])
        ttk.Combobox(
            frame,
            textvariable=self._var_duracion,
            values=DURACIONES_DISPONIBLES,
            state="readonly",
            width=23,
        ).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Motivo:").grid(row=5, column=0, sticky="nw", pady=4)
        self._txt_motivo = tk.Text(frame, height=3, width=25)
        self._txt_motivo.grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Nota (opcional):").grid(row=6, column=0, sticky="nw", pady=4)
        self._txt_nota = tk.Text(frame, height=2, width=25)
        self._txt_nota.grid(row=6, column=1, sticky="ew", pady=4)

        frame_botones = ttk.Frame(frame)
        frame_botones.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(frame_botones, text="Agendar", command=self._agendar).pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Cancelar", command=self._cancelar).pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Eliminar", command=self._eliminar).pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=4)

    def _construir_tabla(self) -> None:
        frame = ttk.LabelFrame(self, text="Sesiones registradas", padding=10)
        frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columnas = ("id", "estudiante", "psicologo", "fecha_hora", "duracion", "estado")
        self._tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=18)

        self._tabla.heading("id", text="ID")
        self._tabla.heading("estudiante", text="Estudiante")
        self._tabla.heading("psicologo", text="Psicólogo")
        self._tabla.heading("fecha_hora", text="Fecha y hora")
        self._tabla.heading("duracion", text="Duración")
        self._tabla.heading("estado", text="Estado")

        self._tabla.column("id", width=80, anchor="center")
        self._tabla.column("estudiante", width=90, anchor="center")
        self._tabla.column("psicologo", width=80, anchor="center")
        self._tabla.column("fecha_hora", width=140, anchor="center")
        self._tabla.column("duracion", width=70, anchor="center")
        self._tabla.column("estado", width=100, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        self._tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _construir_estado(self) -> None:
        self._lbl_estado = ttk.Label(self, text="", foreground="gray")
        self._lbl_estado.grid(row=2, column=0, columnspan=2, pady=(0, 6), padx=10, sticky="w")

    # ─────────────────────────── Eventos ─────────────────────────────────

    def _al_seleccionar(self, _event) -> None:
        seleccion = self._tabla.selection()
        if not seleccion:
            return
        self._id_seleccionado = seleccion[0]
        self._mostrar_estado(
            f"Sesión {self._id_seleccionado[:8]}... seleccionada.", "gray"
        )

    # ─────────────────────────── Acciones ────────────────────────────────

    def _agendar(self) -> None:
        try:
            fecha_hora = datetime.strptime(
                f"{self._ent_fecha.get().strip()} {self._var_hora.get()}",
                "%Y-%m-%d %H:%M",
            )
        except ValueError:
            self._mostrar_estado("Fecha inválida. Usa el formato YYYY-MM-DD.", "red")
            return

        exito, mensaje = self._controller.agendar(
            codigo_estudiante=self._ent_codigo.get().strip(),
            id_psicologo=self._var_psicologo.get(),
            fecha_hora=fecha_hora,
            duracion_minutos=int(self._var_duracion.get()),
            motivo=self._txt_motivo.get("1.0", "end").strip(),
            nota=self._txt_nota.get("1.0", "end").strip(),
        )
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _cancelar(self) -> None:
        if not self._id_seleccionado:
            self._mostrar_estado("Selecciona una sesión de la tabla para cancelarla.", "red")
            return
        confirmar = messagebox.askyesno(
            "Confirmar cancelación",
            "¿Estás segura de cancelar esta sesión?",
        )
        if not confirmar:
            return
        exito, mensaje = self._controller.cancelar(self._id_seleccionado)
        self._mostrar_estado(mensaje, "green" if exito else "red")
        if exito:
            self._cargar_tabla()

    def _eliminar(self) -> None:
        if not self._id_seleccionado:
            self._mostrar_estado("Selecciona una sesión de la tabla para eliminarla.", "red")
            return
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Estás segura de eliminar permanentemente esta sesión?",
        )
        if not confirmar:
            return
        exito, mensaje = self._controller.eliminar(self._id_seleccionado)
        self._mostrar_estado(mensaje, "green" if exito else "red")
        if exito:
            self._limpiar()
            self._cargar_tabla()

    def _limpiar(self) -> None:
        self._ent_codigo.delete(0, tk.END)
        self._ent_fecha.delete(0, tk.END)
        self._var_psicologo.set(PSICOLOGOS_DISPONIBLES[0])
        self._var_hora.set(HORAS_DISPONIBLES[0])
        self._var_duracion.set(DURACIONES_DISPONIBLES[0])
        self._txt_motivo.delete("1.0", tk.END)
        self._txt_nota.delete("1.0", tk.END)
        self._id_seleccionado = None
        self._tabla.selection_remove(self._tabla.selection())

    def _cargar_tabla(self) -> None:
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        self._sesiones_por_id.clear()
        exito, resultado = self._controller.listar()
        if not exito:
            self._mostrar_estado(str(resultado), "red")
            return
        assert isinstance(resultado, list)
        for sesion in resultado:
            self._tabla.insert("", "end", iid=sesion.id, values=(
                sesion.id[:8] + "...",
                sesion.codigo_estudiante,
                sesion.id_psicologo,
                sesion.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                f"{sesion.duracion_minutos} min",
                sesion.estado.value,
            ))
            self._sesiones_por_id[sesion.id] = sesion

    def _mostrar_estado(self, mensaje: str, color: str) -> None:
        self._lbl_estado.config(text=mensaje, foreground=color)
