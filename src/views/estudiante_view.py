from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from src.controllers.estudiante_controller import EstudianteController
from src.models.estudiante import Estudiante
from src.utils.constantes_negocio import (
    EDAD_MINIMA,
    SEMESTRE_MAXIMO,
    SEMESTRE_MINIMO,
)

PROGRAMAS = [
    "Ciencias de Datos",
    "Ingeniería de Sistemas",
    "Psicología",
    "Administración",
    "Medicina",
    "Derecho",
    "Ingeniería Industrial",
    "Diseño Gráfico",
    "Comunicación Social",
    "Contaduría",
]


class EstudianteView(ttk.Frame):
    """Vista Tkinter para el CRUD de estudiantes.

    Args:
        parent: widget padre (notebook o ventana principal).
        controller: controlador Estudiante inyectado.
    """

    def __init__(self, parent: tk.Widget, controller: EstudianteController) -> None:
        super().__init__(parent)
        self._controller = controller
        self._codigo_seleccionado: str | None = None
        self._estudiantes_por_codigo: dict[str, Estudiante] = {}
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
        frame = ttk.LabelFrame(self, text="Registro de Estudiante", padding=10)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Código institucional:").grid(
            row=0, column=0, sticky="w", pady=4
        )
        self._ent_codigo = ttk.Entry(frame, width=24)
        self._ent_codigo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Nombre completo:").grid(row=1, column=0, sticky="w", pady=4)
        self._ent_nombre = ttk.Entry(frame, width=24)
        self._ent_nombre.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Edad:").grid(row=2, column=0, sticky="w", pady=4)
        self._ent_edad = ttk.Spinbox(frame, from_=EDAD_MINIMA, to=100, width=6)
        self._ent_edad.set(EDAD_MINIMA)
        self._ent_edad.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(frame, text=f"Semestre ({SEMESTRE_MINIMO}-{SEMESTRE_MAXIMO}):").grid(
            row=3, column=0, sticky="w", pady=4
        )
        self._ent_semestre = ttk.Spinbox(
            frame, from_=SEMESTRE_MINIMO, to=SEMESTRE_MAXIMO, width=6
        )
        self._ent_semestre.set(SEMESTRE_MINIMO)
        self._ent_semestre.grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Correo:").grid(row=4, column=0, sticky="w", pady=4)
        self._ent_correo = ttk.Entry(frame, width=24)
        self._ent_correo.grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Programa:").grid(row=5, column=0, sticky="w", pady=4)
        self._var_programa = tk.StringVar(value=PROGRAMAS[0])
        self._cb_programa = ttk.Combobox(
            frame,
            textvariable=self._var_programa,
            values=PROGRAMAS,
            state="readonly",
            width=22,
        )
        self._cb_programa.grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(
            frame,
            text=(
                "Nota: el código debe tener formato 'EST' + 3 a 6 dígitos "
                f"(ej. EST0001). Edad mínima: {EDAD_MINIMA} años."
            ),
            foreground="gray",
            wraplength=320,
            justify="left",
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 4))

        frame_botones = ttk.Frame(frame)
        frame_botones.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(frame_botones, text="Guardar", command=self._guardar).pack(
            side="left", padx=4
        )
        self._btn_actualizar = ttk.Button(
            frame_botones, text="Actualizar", command=self._actualizar, state="disabled"
        )
        self._btn_actualizar.pack(side="left", padx=4)
        ttk.Button(frame_botones, text="Eliminar", command=self._eliminar).pack(
            side="left", padx=4
        )
        ttk.Button(frame_botones, text="Limpiar", command=self._limpiar).pack(
            side="left", padx=4
        )

    def _construir_tabla(self) -> None:
        frame = ttk.LabelFrame(self, text="Estudiantes registrados", padding=10)
        frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "edad", "semestre", "programa", "correo")
        self._tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=18)

        self._tabla.heading("codigo", text="Código")
        self._tabla.heading("nombre", text="Nombre completo")
        self._tabla.heading("edad", text="Edad")
        self._tabla.heading("semestre", text="Sem.")
        self._tabla.heading("programa", text="Programa")
        self._tabla.heading("correo", text="Correo")

        self._tabla.column("codigo", width=80, anchor="center")
        self._tabla.column("nombre", width=180, anchor="w")
        self._tabla.column("edad", width=50, anchor="center")
        self._tabla.column("semestre", width=50, anchor="center")
        self._tabla.column("programa", width=150, anchor="w")
        self._tabla.column("correo", width=180, anchor="w")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)

        self._tabla.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _construir_estado(self) -> None:
        self._lbl_estado = ttk.Label(self, text="", foreground="gray")
        self._lbl_estado.grid(row=2, column=0, columnspan=2, pady=(0, 6), padx=10, sticky="w")

    # ------------------------------------------------------------------ Eventos

    def _al_seleccionar(self, _event) -> None:
        seleccion = self._tabla.selection()
        if not seleccion:
            return
        self._codigo_seleccionado = seleccion[0]
        estudiante = self._estudiantes_por_codigo.get(self._codigo_seleccionado)
        if estudiante is None:
            return

        self._ent_codigo.delete(0, tk.END)
        self._ent_codigo.insert(0, estudiante.codigo)
        self._ent_codigo.config(state="readonly")

        self._ent_nombre.delete(0, tk.END)
        self._ent_nombre.insert(0, estudiante.nombre_completo)

        self._ent_edad.delete(0, tk.END)
        self._ent_edad.insert(0, str(estudiante.edad))

        self._ent_semestre.delete(0, tk.END)
        self._ent_semestre.insert(0, str(estudiante.semestre))

        self._ent_correo.delete(0, tk.END)
        self._ent_correo.insert(0, estudiante.correo)

        self._var_programa.set(estudiante.programa)

        self._btn_actualizar.config(state="normal")
        self._mostrar_estado(f"Estudiante {estudiante.codigo} seleccionado.", "gray")

    # ------------------------------------------------------------------ Acciones CRUD

    def _leer_formulario(self) -> tuple[str, str, int, int, str, str] | None:
        codigo = self._ent_codigo.get().strip()
        nombre = self._ent_nombre.get().strip()
        correo = self._ent_correo.get().strip()
        programa = self._var_programa.get().strip()
        try:
            edad = int(self._ent_edad.get())
            semestre = int(self._ent_semestre.get())
        except ValueError:
            self._mostrar_estado("Edad y semestre deben ser números enteros.", "red")
            return None
        return codigo, nombre, edad, semestre, correo, programa

    def _guardar(self) -> None:
        datos = self._leer_formulario()
        if datos is None:
            return
        exito, mensaje = self._controller.registrar(*datos)
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _actualizar(self) -> None:
        if not self._codigo_seleccionado:
            self._mostrar_estado("Selecciona un estudiante para actualizar.", "red")
            return
        datos = self._leer_formulario()
        if datos is None:
            return
        exito, mensaje = self._controller.actualizar(*datos)
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _eliminar(self) -> None:
        if not self._codigo_seleccionado:
            self._mostrar_estado(
                "Selecciona un estudiante de la tabla para eliminar.", "red"
            )
            return
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar al estudiante "
            f"{self._codigo_seleccionado}?",
        )
        if not confirmar:
            return
        exito, mensaje = self._controller.eliminar(self._codigo_seleccionado)
        if exito:
            self._mostrar_estado(mensaje, "green")
            self._limpiar()
            self._cargar_tabla()
        else:
            self._mostrar_estado(mensaje, "red")

    def _limpiar(self) -> None:
        self._ent_codigo.config(state="normal")
        self._ent_codigo.delete(0, tk.END)
        self._ent_nombre.delete(0, tk.END)
        self._ent_edad.delete(0, tk.END)
        self._ent_edad.insert(0, str(EDAD_MINIMA))
        self._ent_semestre.delete(0, tk.END)
        self._ent_semestre.insert(0, str(SEMESTRE_MINIMO))
        self._ent_correo.delete(0, tk.END)
        self._var_programa.set(PROGRAMAS[0])
        self._codigo_seleccionado = None
        self._tabla.selection_remove(self._tabla.selection())
        self._btn_actualizar.config(state="disabled")

    def _cargar_tabla(self) -> None:
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        self._estudiantes_por_codigo.clear()
        exito, resultado = self._controller.listar()
        if not exito:
            self._mostrar_estado(str(resultado), "red")
            return
        assert isinstance(resultado, list)
        for e in resultado:
            self._tabla.insert(
                "",
                "end",
                iid=e.codigo,
                values=(e.codigo, e.nombre_completo, e.edad, e.semestre, e.programa, e.correo),
            )
            self._estudiantes_por_codigo[e.codigo] = e

    def _mostrar_estado(self, mensaje: str, color: str) -> None:
        self._lbl_estado.config(text=mensaje, foreground=color)
