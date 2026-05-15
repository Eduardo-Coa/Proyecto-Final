---
name: ui-tkinter-nielsen
description: Use this skill whenever the user works on UI, views, Tkinter windows, forms, screens, user interaction, layouts, or asks about Nielsen heuristics. Triggers include "Tkinter", "interfaz", "ventana", "formulario", "boton", "vista", "UI", "UX", "Nielsen", "heuristica", "label", "Entry", "grid", "pack", "Frame", "Toplevel", "messagebox". The UI must respect Nielsen's 10 heuristics per criterion 9. Apply this skill proactively when reviewing view files.
allowed-tools: Read Write Edit Grep
---

# UI con Tkinter aplicando Heurísticas de Nielsen (Criterio 9)

## Stack obligatorio
- **Tkinter** (incluido en stdlib, no requiere instalación).
- Una vista por entidad CRUD en `src/views/`.
- La vista recibe el controlador por inyección. La vista NO contiene lógica de negocio.

## Las 10 heurísticas de Nielsen aplicadas

### 1. Visibilidad del estado del sistema
Toda acción debe dar feedback inmediato.

```python
def _on_crear_click(self):
    self.lbl_estado.config(text="Guardando...", fg="blue")
    self.update()  # Forzar refresco antes de la operación
    ok, msg = self._controller.crear(self._leer_formulario())
    self.lbl_estado.config(text=msg, fg="green" if ok else "red")
```

### 2. Coincidencia entre sistema y mundo real
- Usar términos del dominio: "Estudiante", "Cuestionario", "Sesión" — no "Registro", "Item".
- Etiquetas claras: "Código institucional" en vez de "ID".
- Fechas en formato local: `DD/MM/YYYY HH:MM`.

### 3. Control y libertad del usuario
- Botón "Cancelar" o "Limpiar formulario" en cada vista.
- Confirmación antes de eliminar:
  ```python
  from tkinter import messagebox
  if not messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
      return
  ```

### 4. Consistencia y estándares
- Mismos colores en toda la app (definir paleta).
- Mismo orden de botones: `[Guardar] [Cancelar]` siempre en ese orden.
- Mismos nombres: si en una vista es "Guardar", no usar "Crear" en otra para la misma acción.

### 5. Prevención de errores
- Validar **mientras** el usuario escribe (no solo al enviar):
  ```python
  vcmd = (self.register(self._es_numero), "%P")
  self.entry_edad = ttk.Entry(self, validate="key", validatecommand=vcmd)
  ```
- Usar `ttk.Combobox` para opciones cerradas (semestre 1-12, programas).
- Deshabilitar el botón "Guardar" hasta que el formulario sea válido.

### 6. Reconocer en lugar de recordar
- Mostrar los campos disponibles, no exigir que el usuario los recuerde.
- Listas desplegables, no campos libres cuando hay opciones limitadas.
- Placeholder o ejemplo: `entry.insert(0, "Ej: 20231234")` con borrado al enfocar.

### 7. Flexibilidad y eficiencia de uso
- Atajos de teclado para usuarios frecuentes:
  ```python
  self.bind("<Control-n>", lambda e: self._on_nuevo())
  self.bind("<Control-s>", lambda e: self._on_guardar())
  ```
- Doble clic en una fila de la tabla para editar.

### 8. Diseño estético y minimalista
- Espaciado generoso (padx=10, pady=8 mínimo).
- Una sola tarea principal por ventana.
- No saturar con bordes, colores fuertes o textos innecesarios.

### 9. Ayuda al usuario a reconocer, diagnosticar y recuperarse de errores
- Mensajes específicos: "El código debe tener al menos 4 caracteres" — no "Error de validación".
- Color rojo + ícono + texto claro.
- NUNCA mostrar el traceback de Python al usuario.

### 10. Ayuda y documentación
- Menú "Ayuda" con descripción de cada cuestionario (PHQ-9, GAD-7).
- Tooltips en campos no obvios.
- Sección "Acerca de" con créditos y versión.

## Estructura estándar de una vista

```python
import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.estudiante_controller import EstudianteController


class EstudianteView(ttk.Frame):
    """Vista CRUD para la entidad Estudiante."""

    def __init__(self, parent: tk.Widget, controller: EstudianteController) -> None:
        super().__init__(parent, padding=20)
        self._controller = controller
        self._construir_widgets()
        self._cargar_tabla()

    def _construir_widgets(self) -> None:
        # Título
        ttk.Label(self, text="Gestión de Estudiantes", font=("Arial", 16, "bold"))\
            .grid(row=0, column=0, columnspan=4, pady=(0, 15))

        # Formulario
        form = ttk.LabelFrame(self, text="Datos del estudiante", padding=10)
        form.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)

        self._campos = {}
        for i, (clave, etiqueta) in enumerate([
            ("codigo", "Código:"),
            ("nombre_completo", "Nombre completo:"),
            ("edad", "Edad:"),
            ("semestre", "Semestre:"),
            ("correo", "Correo institucional:"),
            ("programa", "Programa:"),
        ]):
            ttk.Label(form, text=etiqueta).grid(row=i, column=0, sticky="e", padx=5, pady=3)
            entry = ttk.Entry(form, width=35)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=3)
            self._campos[clave] = entry

        # Botones (orden consistente en toda la app)
        botones = ttk.Frame(self)
        botones.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(botones, text="Guardar", command=self._on_guardar).pack(side="left", padx=5)
        ttk.Button(botones, text="Actualizar", command=self._on_actualizar).pack(side="left", padx=5)
        ttk.Button(botones, text="Eliminar", command=self._on_eliminar).pack(side="left", padx=5)
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=5)

        # Tabla de resultados
        cols = ("codigo", "nombre", "edad", "semestre", "programa")
        self._tabla = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c in cols:
            self._tabla.heading(c, text=c.capitalize())
            self._tabla.column(c, width=120)
        self._tabla.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=10)
        self._tabla.bind("<Double-1>", self._on_doble_click_fila)

        # Barra de estado (heurística 1: visibilidad)
        self._lbl_estado = ttk.Label(self, text="Listo", foreground="gray")
        self._lbl_estado.grid(row=4, column=0, columnspan=4, sticky="w")

    def _leer_formulario(self) -> dict:
        datos = {k: e.get().strip() for k, e in self._campos.items()}
        # Conversión segura de numéricos
        try:
            datos["edad"] = int(datos["edad"])
            datos["semestre"] = int(datos["semestre"])
        except ValueError:
            datos["edad"] = -1
            datos["semestre"] = -1
        return datos

    def _on_guardar(self) -> None:
        ok, msg = self._controller.crear(self._leer_formulario())
        self._mostrar_estado(msg, ok)
        if ok:
            self._cargar_tabla()
            self._limpiar()

    def _on_actualizar(self) -> None:
        ok, msg = self._controller.actualizar(self._leer_formulario())
        self._mostrar_estado(msg, ok)
        if ok:
            self._cargar_tabla()

    def _on_eliminar(self) -> None:
        codigo = self._campos["codigo"].get().strip()
        if not codigo:
            self._mostrar_estado("Selecciona un estudiante para eliminar.", False)
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar estudiante {codigo}?"):
            return
        ok, msg = self._controller.eliminar(codigo)
        self._mostrar_estado(msg, ok)
        if ok:
            self._cargar_tabla()
            self._limpiar()

    def _on_doble_click_fila(self, _evento) -> None:
        sel = self._tabla.selection()
        if not sel:
            return
        valores = self._tabla.item(sel[0])["values"]
        # Carga los datos al formulario para editar
        # ...

    def _cargar_tabla(self) -> None:
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        for e in self._controller.listar():
            self._tabla.insert("", "end", values=(
                e.codigo, e.nombre_completo, e.edad, e.semestre, e.programa,
            ))

    def _limpiar(self) -> None:
        for entry in self._campos.values():
            entry.delete(0, tk.END)

    def _mostrar_estado(self, mensaje: str, exito: bool) -> None:
        color = "green" if exito else "red"
        self._lbl_estado.config(text=mensaje, foreground=color)
```

## Ventana principal (`main.py`)

```python
import tkinter as tk
from tkinter import ttk
from src.views.estudiante_view import EstudianteView
# ...

def main() -> None:
    root = tk.Tk()
    root.title("Plataforma de Apoyo Psicoeducativo")
    root.geometry("900x600")

    # Pestañas para cada entidad CRUD
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    notebook.add(EstudianteView(notebook, controller_estudiante), text="Estudiantes")
    notebook.add(PHQ9View(notebook, controller_phq9), text="PHQ-9")
    notebook.add(GAD7View(notebook, controller_gad7), text="GAD-7")
    notebook.add(SesionView(notebook, controller_sesion), text="Sesiones")

    root.mainloop()

if __name__ == "__main__":
    main()
```

## Checklist antes de entregar la UI

- [ ] Cada acción muestra feedback (heurística 1).
- [ ] Confirmaciones antes de eliminar (heurística 3).
- [ ] Mismos botones, mismos colores en todas las vistas (heurística 4).
- [ ] Validaciones en vivo evitan errores (heurística 5).
- [ ] Combobox/dropdowns para opciones cerradas (heurística 6).
- [ ] Mensajes de error específicos, sin tracebacks (heurística 9).
- [ ] Menú Ayuda y tooltips donde haga falta (heurística 10).
