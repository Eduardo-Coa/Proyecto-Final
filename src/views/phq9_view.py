from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from src.controllers.phq9_controller import PHQ9Controller
from src.models.cuestionario_phq9 import CuestionarioPHQ9, OPCIONES_RESPUESTA, TEXTOS_ITEMS_PHQ9
from src.utils.constantes_negocio import (
    NUM_ITEMS_PHQ9,
    PUNTAJE_RIESGO_LEVE_PHQ9,
    PUNTAJE_RIESGO_MODERADO_PHQ9,
    PUNTAJE_RIESGO_MODSEVERO_PHQ9,
    PUNTAJE_RIESGO_SEVERO_PHQ9,
)


class PHQ9View(ttk.Frame):
    """Vista Tkinter para el CRUD del cuestionario PHQ-9.

    Args:
        parent: widget padre (notebook o ventana principal).
        controller: controlador PHQ9 inyectado.
    """

    def __init__(self, parent: tk.Widget, controller: PHQ9Controller) -> None:
        super().__init__(parent)
        self._controller = controller
        self._id_seleccionado: str | None = None
        self._cuestionarios_por_id: dict[str, CuestionarioPHQ9] = {}
        self._vars_respuestas: list[tk.StringVar] = [
            tk.StringVar(value=OPCIONES_RESPUESTA[0]) for _ in range(NUM_ITEMS_PHQ9)
        ]
        self._construir_ui()
        self._cargar_tabla()

    # ------------------------------------------------------------------ UI

    def _construir_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        self._construir_formulario()
        self._construir_tabla()
        self._construir_estado()

    def _construir_formulario(self) -> None:
        frame = ttk.LabelFrame(self, text="Registro PHQ-9", padding=10)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame, text="Codigo estudiante:").grid(row=0, column=0, sticky="w", pady=2)
        self._ent_codigo = ttk.Entry(frame, width=20)
        self._ent_codigo.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Separator(frame, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=6
        )
        ttk.Label(frame, text="Respuestas (0 = Nunca, 3 = Casi todos los dias):").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )

        for i, pregunta in enumerate(TEXTOS_ITEMS_PHQ9):
            ttk.Label(frame, text=pregunta, wraplength=280, justify="left").grid(
                row=3 + i, column=0, sticky="w", pady=2
            )
            cb = ttk.Combobox(
                frame,
                textvariable=self._vars_respuestas[i],
                values=OPCIONES_RESPUESTA,
                state="readonly",
                width=28,
            )
            cb.grid(row=3 + i, column=1, sticky="ew", pady=2)

        self._lbl_puntaje = ttk.Label(
            frame, text="Puntaje estimado: 0 - Minimo", foreground="gray"
        )
        self._lbl_puntaje.grid(
            row=3 + NUM_ITEMS_PHQ9, column=0, columnspan=2, pady=(8, 2)
        )

        for var in self._vars_respuestas:
            var.trace_add("write", lambda *_: self._actualizar_puntaje_estimado())

        frame_botones = ttk.Frame(frame)
        frame_botones.grid(row=4 + NUM_ITEMS_PHQ9, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(frame_botones, text="Guardar", command=self._guardar).pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Actualizar", command=self._actualizar).pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Eliminar", command=self._eliminar).pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=4)

    def _construir_tabla(self) -> None:
        frame = ttk.LabelFrame(self, text="Cuestionarios registrados", padding=10)
        frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columnas = ("id", "estudiante", "puntaje", "severidad", "fecha")
        self._tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=18)

        self._tabla.heading("id", text="ID")
        self._tabla.heading("estudiante", text="Estudiante")
        self._tabla.heading("puntaje", text="Puntaje")
        self._tabla.heading("severidad", text="Severidad")
        self._tabla.heading("fecha", text="Fecha")

        self._tabla.column("id", width=80, anchor="center")
        self._tabla.column("estudiante", width=100, anchor="center")
        self._tabla.column("puntaje", width=70, anchor="center")
        self._tabla.column("severidad", width=140, anchor="center")
        self._tabla.column("fecha", width=140, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)

        self._tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _construir_estado(self) -> None:
        self._lbl_estado = ttk.Label(self, text="", foreground="gray")
        self._lbl_estado.grid(row=2, column=0, columnspan=2, pady=(0, 6), padx=10, sticky="w")

    # ------------------------------------------------------------------ Eventos

    def _get_respuestas(self) -> list[int]:
        return [int(v.get()[0]) for v in self._vars_respuestas]

    def _actualizar_puntaje_estimado(self) -> None:
        total = sum(int(v.get()[0]) for v in self._vars_respuestas)
        if total >= PUNTAJE_RIESGO_SEVERO_PHQ9:
            nivel, color = "Severo", "#c0392b"
        elif total >= PUNTAJE_RIESGO_MODSEVERO_PHQ9:
            nivel, color = "Moderadamente severo", "#e74c3c"
        elif total >= PUNTAJE_RIESGO_MODERADO_PHQ9:
            nivel, color = "Moderado", "#e67e22"
        elif total >= PUNTAJE_RIESGO_LEVE_PHQ9:
            nivel, color = "Leve", "#f1c40f"
        else:
            nivel, color = "Minimo", "#27ae60"
        self._lbl_puntaje.config(text=f"Puntaje estimado: {total} - {nivel}", foreground=color)

    def _al_seleccionar(self, _event) -> None:
        seleccion = self._tabla.selection()
        if not seleccion:
            return
        self._id_seleccionado = seleccion[0]
        cuestionario = self._cuestionarios_por_id.get(self._id_seleccionado)
        if cuestionario is None:
            return
        self._ent_codigo.delete(0, tk.END)
        self._ent_codigo.insert(0, cuestionario.codigo_estudiante)
        for i, valor in enumerate(cuestionario.respuestas):
            self._vars_respuestas[i].set(OPCIONES_RESPUESTA[valor])
        self._mostrar_estado(
            f"Cuestionario {self._id_seleccionado[:8]}... cargado para edición.", "gray"
        )

    # ------------------------------------------------------------------ Acciones CRUD

    def _guardar(self) -> None:
        codigo = self._ent_codigo.get().strip()
        respuestas = self._get_respuestas()
        exito, mensaje = self._controller.registrar(codigo, respuestas)
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _actualizar(self) -> None:
        if not self._id_seleccionado:
            self._mostrar_estado(
                "Selecciona un cuestionario de la tabla para actualizar.", "red"
            )
            return
        codigo = self._ent_codigo.get().strip()
        respuestas = self._get_respuestas()
        exito, mensaje = self._controller.actualizar(
            self._id_seleccionado, codigo, respuestas
        )
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _eliminar(self) -> None:
        if not self._id_seleccionado:
            self._mostrar_estado("Selecciona un cuestionario de la tabla para eliminar.", "red")
            return
        confirmar = messagebox.askyesno(
            "Confirmar eliminacion",
            f"Deseas eliminar el cuestionario {self._id_seleccionado}?",
        )
        if not confirmar:
            return
        exito, mensaje = self._controller.eliminar(self._id_seleccionado)
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _limpiar(self) -> None:
        self._ent_codigo.delete(0, tk.END)
        for var in self._vars_respuestas:
            var.set(OPCIONES_RESPUESTA[0])
        self._id_seleccionado = None
        self._lbl_puntaje.config(text="Puntaje estimado: 0 - Minimo", foreground="gray")
        self._tabla.selection_remove(self._tabla.selection())

    def _cargar_tabla(self) -> None:
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        self._cuestionarios_por_id.clear()
        exito, resultado = self._controller.listar()
        if not exito:
            self._mostrar_estado(str(resultado), "red")
            return
        assert isinstance(resultado, list)
        for c in resultado:
            self._cuestionarios_por_id[c.id] = c
            self._tabla.insert("", "end", iid=c.id, values=(
                c.id[:8] + "...",
                c.codigo_estudiante,
                c.puntaje_total,
                c.nivel_severidad,
                c.fecha_aplicacion.strftime("%Y-%m-%d %H:%M"),
            ))

    def _mostrar_estado(self, mensaje: str, color: str) -> None:
        self._lbl_estado.config(text=mensaje, foreground=color)
