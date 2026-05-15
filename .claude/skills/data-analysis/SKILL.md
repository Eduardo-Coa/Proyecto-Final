---
name: data-analysis
description: Use this skill whenever the user works on data analysis, statistics, descriptive analytics, exploratory data analysis (EDA), pandas operations, or matplotlib visualizations for this project. Triggers include "pandas", "dataframe", "estadistica", "EDA", "exploratorio", "describe", "histograma", "grafico", "matplotlib", "distribucion", "correlacion", "groupby", "media", "mediana", "boxplot", "scatter", "heatmap", "dashboard", "visualizar datos". Apply when integrating analytics into Tkinter views with matplotlib backends. Do NOT use for ML models (use ml-pipeline) or data generation (use synthetic-data).
allowed-tools: Read Write Edit Bash Grep
---

# Análisis de Datos con pandas + matplotlib

## Stack del módulo analítico

```bash
pip install pandas matplotlib seaborn
```

Agregar a `requirements.txt`:
```
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

## Arquitectura del módulo `src/analytics/`

```
src/analytics/
├── __init__.py
├── data_loader.py          # Carga JSON → DataFrame
├── descriptive_stats.py    # Estadística descriptiva
├── correlations.py         # Análisis bivariado (PHQ-9 ↔ GAD-7)
├── temporal_analysis.py    # Series temporales por estudiante
└── visualizations.py       # Funciones de gráficas matplotlib
```

## Reglas críticas para Tkinter + matplotlib

**NUNCA hacer `plt.show()`** dentro de la app. Eso abre una ventana separada y bloquea Tkinter.

**SIEMPRE usar `FigureCanvasTkAgg`** para embeber gráficos en la UI:

```python
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def crear_grafico_en_frame(parent_frame, df):
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.hist(df["puntaje_total"], bins=15)
    ax.set_title("Distribución de puntajes PHQ-9")

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas
```

## Patrón estándar de carga (`data_loader.py`)

```python
import json
from pathlib import Path
import pandas as pd


def cargar_estudiantes(ruta: str = "data/estudiantes.json") -> pd.DataFrame:
    """Carga estudiantes desde JSON y devuelve DataFrame tipado."""
    with Path(ruta).open(encoding="utf-8") as f:
        datos = json.load(f)
    df = pd.DataFrame(datos)
    if not df.empty:
        df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
        df["edad"] = df["edad"].astype(int)
        df["semestre"] = df["semestre"].astype(int)
    return df


def cargar_phq9(ruta: str = "data/cuestionarios_phq9.json") -> pd.DataFrame:
    with Path(ruta).open(encoding="utf-8") as f:
        datos = json.load(f)
    df = pd.DataFrame(datos)
    if not df.empty:
        df["fecha_aplicacion"] = pd.to_datetime(df["fecha_aplicacion"])
        df["puntaje_total"] = df["puntaje_total"].astype(int)
        # Expandir respuestas a columnas individuales si se necesita
        respuestas_df = pd.DataFrame(
            df["respuestas"].tolist(),
            columns=[f"item_{i+1}" for i in range(9)],
        )
        df = pd.concat([df.drop(columns=["respuestas"]), respuestas_df], axis=1)
    return df


def cargar_gad7(ruta: str = "data/cuestionarios_gad7.json") -> pd.DataFrame:
    # Similar a cargar_phq9 pero con 7 columnas
    ...
```

## Estadística descriptiva (`descriptive_stats.py`)

```python
import pandas as pd


def resumen_phq9(df_phq9: pd.DataFrame) -> dict:
    """Estadísticas clave del puntaje total."""
    if df_phq9.empty:
        return {"n": 0}
    s = df_phq9["puntaje_total"]
    return {
        "n": len(s),
        "media": round(s.mean(), 2),
        "mediana": float(s.median()),
        "desv_std": round(s.std(), 2),
        "minimo": int(s.min()),
        "maximo": int(s.max()),
        "q1": float(s.quantile(0.25)),
        "q3": float(s.quantile(0.75)),
    }


def clasificar_puntajes_phq9(df: pd.DataFrame) -> pd.Series:
    """
    Clasifica cada puntaje según los rangos clínicos del PHQ-9.

    0-4:   Mínima/Ninguna
    5-9:   Leve
    10-14: Moderada
    15-19: Moderadamente severa
    20-27: Severa
    """
    bins = [-1, 4, 9, 14, 19, 27]
    labels = ["Mínima", "Leve", "Moderada", "Mod. Severa", "Severa"]
    return pd.cut(df["puntaje_total"], bins=bins, labels=labels)


def distribucion_por_programa(df_estudiantes: pd.DataFrame) -> pd.DataFrame:
    """Conteo de estudiantes por programa académico."""
    return (
        df_estudiantes["programa"]
        .value_counts()
        .reset_index(name="cantidad")
        .rename(columns={"index": "programa"})
    )


def estadisticas_por_semestre(df_estudiantes: pd.DataFrame, df_phq9: pd.DataFrame) -> pd.DataFrame:
    """Puntaje promedio PHQ-9 por semestre."""
    merged = df_phq9.merge(
        df_estudiantes[["codigo", "semestre"]],
        left_on="codigo_estudiante", right_on="codigo",
    )
    return (
        merged.groupby("semestre")["puntaje_total"]
        .agg(["mean", "median", "std", "count"])
        .round(2)
        .reset_index()
    )
```

## Correlaciones (`correlations.py`)

```python
import pandas as pd


def correlacion_phq9_gad7(df_phq9: pd.DataFrame, df_gad7: pd.DataFrame) -> dict:
    """Calcula correlación de Pearson entre puntajes PHQ-9 y GAD-7."""
    # Tomar la última aplicación por estudiante (por si hay varias)
    phq_latest = df_phq9.sort_values("fecha_aplicacion").groupby("codigo_estudiante").tail(1)
    gad_latest = df_gad7.sort_values("fecha_aplicacion").groupby("codigo_estudiante").tail(1)

    merged = phq_latest[["codigo_estudiante", "puntaje_total"]].merge(
        gad_latest[["codigo_estudiante", "puntaje_total"]],
        on="codigo_estudiante",
        suffixes=("_phq", "_gad"),
    )

    if len(merged) < 10:
        return {"n": len(merged), "coeficiente": None, "interpretacion": "Datos insuficientes"}

    r = merged["puntaje_total_phq"].corr(merged["puntaje_total_gad"])

    if abs(r) < 0.3:
        interpretacion = "Débil"
    elif abs(r) < 0.6:
        interpretacion = "Moderada"
    else:
        interpretacion = "Fuerte"

    return {
        "n": len(merged),
        "coeficiente": round(r, 3),
        "interpretacion": interpretacion,
        "datos_para_grafico": merged,
    }
```

## Visualizaciones (`visualizations.py`)

```python
from matplotlib.figure import Figure
import pandas as pd


def histograma_puntajes(df_phq9: pd.DataFrame, fig: Figure | None = None) -> Figure:
    """Histograma de puntajes con umbrales de riesgo marcados."""
    fig = fig or Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    ax.hist(df_phq9["puntaje_total"], bins=15, edgecolor="black", alpha=0.7)
    ax.axvline(20, color="red", linestyle="--", label="Umbral severo (≥20)")
    ax.axvline(10, color="orange", linestyle="--", label="Umbral moderado (≥10)")
    ax.set_xlabel("Puntaje total PHQ-9")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de puntajes PHQ-9")
    ax.legend()
    fig.tight_layout()
    return fig


def barras_distribucion_categorias(serie_categorias: pd.Series, fig: Figure | None = None) -> Figure:
    """Barras de niveles de severidad."""
    fig = fig or Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    conteos = serie_categorias.value_counts()
    colores = ["#4CAF50", "#FFC107", "#FF9800", "#FF5722", "#D32F2F"]
    ax.bar(conteos.index.astype(str), conteos.values, color=colores[:len(conteos)])
    ax.set_xlabel("Nivel de severidad")
    ax.set_ylabel("Cantidad de estudiantes")
    ax.set_title("Clasificación PHQ-9 por severidad")
    fig.tight_layout()
    return fig


def scatter_phq_vs_gad(datos_correlacion: pd.DataFrame, fig: Figure | None = None) -> Figure:
    """Scatter plot PHQ-9 vs GAD-7 con línea de tendencia."""
    fig = fig or Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    x = datos_correlacion["puntaje_total_phq"]
    y = datos_correlacion["puntaje_total_gad"]
    ax.scatter(x, y, alpha=0.5)

    # Línea de tendencia simple
    import numpy as np
    if len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(sorted(x), p(sorted(x)), "r--", label=f"Tendencia: y={z[0]:.2f}x+{z[1]:.2f}")
        ax.legend()

    ax.set_xlabel("Puntaje PHQ-9 (depresión)")
    ax.set_ylabel("Puntaje GAD-7 (ansiedad)")
    ax.set_title("Comorbilidad: Depresión vs Ansiedad")
    fig.tight_layout()
    return fig


def serie_temporal_estudiante(df_phq9_estudiante: pd.DataFrame, fig: Figure | None = None) -> Figure:
    """Evolución temporal del puntaje de un estudiante."""
    fig = fig or Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    df_sorted = df_phq9_estudiante.sort_values("fecha_aplicacion")
    ax.plot(df_sorted["fecha_aplicacion"], df_sorted["puntaje_total"], marker="o")
    ax.axhline(20, color="red", linestyle="--", alpha=0.5, label="Umbral severo")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Puntaje PHQ-9")
    ax.set_title("Evolución temporal del puntaje")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig
```

## Vista de dashboard analítico en Tkinter

```python
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.analytics.data_loader import cargar_estudiantes, cargar_phq9
from src.analytics.descriptive_stats import resumen_phq9, clasificar_puntajes_phq9
from src.analytics.visualizations import histograma_puntajes, barras_distribucion_categorias


class DashboardAnaliticoView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._construir()

    def _construir(self):
        df_phq = cargar_phq9()

        # Panel de métricas (lado izquierdo)
        metricas_frame = ttk.LabelFrame(self, text="Métricas PHQ-9", padding=10)
        metricas_frame.grid(row=0, column=0, sticky="nsew", padx=5)

        resumen = resumen_phq9(df_phq)
        for fila, (clave, valor) in enumerate(resumen.items()):
            ttk.Label(metricas_frame, text=f"{clave}:", font=("Arial", 10, "bold"))\
                .grid(row=fila, column=0, sticky="e", padx=5, pady=2)
            ttk.Label(metricas_frame, text=str(valor))\
                .grid(row=fila, column=1, sticky="w", padx=5)

        # Panel de gráficas (lado derecho)
        graficas_frame = ttk.Frame(self)
        graficas_frame.grid(row=0, column=1, sticky="nsew", padx=5)

        fig_hist = histograma_puntajes(df_phq)
        canvas1 = FigureCanvasTkAgg(fig_hist, master=graficas_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # Botón recargar (heurística 1: feedback)
        ttk.Button(self, text="↻ Recargar datos", command=self._recargar)\
            .grid(row=1, column=0, columnspan=2, pady=10)

    def _recargar(self):
        for w in self.winfo_children():
            w.destroy()
        self._construir()
```

## Reglas

1. **Toda función de análisis recibe DataFrames, no archivos.** Separar I/O de lógica.
2. **Las funciones de visualización devuelven Figure**, no la dibujan ellas.
3. **DataFrames vacíos** son válidos — chequear `df.empty` antes de operar.
4. **Tipar las columnas explícitamente** después de cargar JSON (fechas, ints).
5. **Cada función analítica DEBE tener un test** que la cubra (criterio 6).
6. **No mezclar el módulo analytics con MVC**: es una capa transversal, los controllers no la usan.
