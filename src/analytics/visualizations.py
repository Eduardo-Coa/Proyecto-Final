from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

# Orden clínico de severidad y paleta consistente con la vista PHQ-9.
_ORDEN_SEVERIDAD = ["Mínimo", "Leve", "Moderado", "Moderadamente severo", "Severo"]
_COLORES_SEVERIDAD = {
    "Mínimo": "#27ae60",
    "Leve": "#f1c40f",
    "Moderado": "#e67e22",
    "Moderadamente severo": "#e74c3c",
    "Severo": "#c0392b",
}


def grafica_severidad_phq9(df: pd.DataFrame) -> Figure:
    """Construye un gráfico de barras con la distribución de severidad PHQ-9.

    Cada barra es un nivel de severidad (Mínimo a Severo) coloreado según la
    paleta clínica del proyecto. Devuelve una ``Figure`` para incrustarla con
    ``FigureCanvasTkAgg`` (nunca usa ``plt.show()``).

    Args:
        df: DataFrame con la columna ``nivel_severidad``.

    Returns:
        Figura de matplotlib lista para incrustar en Tkinter.
    """
    fig = Figure(figsize=(5, 3.4), dpi=100)
    ax = fig.add_subplot(111)

    if df.empty or "nivel_severidad" not in df.columns:
        ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center",
                fontsize=11, color="gray")
        ax.axis("off")
        fig.tight_layout()
        return fig

    conteos = df["nivel_severidad"].value_counts()
    valores = [int(conteos.get(nivel, 0)) for nivel in _ORDEN_SEVERIDAD]
    colores = [_COLORES_SEVERIDAD[nivel] for nivel in _ORDEN_SEVERIDAD]

    barras = ax.bar(_ORDEN_SEVERIDAD, valores, color=colores)
    ax.set_title("Distribución de severidad PHQ-9", fontsize=11, fontweight="bold")
    ax.set_ylabel("Nº de cuestionarios")
    ax.tick_params(axis="x", labelrotation=20, labelsize=8)

    for barra, valor in zip(barras, valores):
        if valor > 0:
            ax.text(barra.get_x() + barra.get_width() / 2, valor,
                    str(valor), ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    return fig


def grafica_demografica(df: pd.DataFrame) -> Figure:
    """Construye un gráfico de barras con estudiantes por programa.

    Args:
        df: DataFrame con la columna ``programa``.

    Returns:
        Figura de matplotlib lista para incrustar en Tkinter.
    """
    fig = Figure(figsize=(5, 3.4), dpi=100)
    ax = fig.add_subplot(111)

    if df.empty or "programa" not in df.columns:
        ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center",
                fontsize=11, color="gray")
        ax.axis("off")
        fig.tight_layout()
        return fig

    conteos = df["programa"].fillna("Sin programa").value_counts().sort_values()
    barras = ax.barh(conteos.index, conteos.values, color="#3498db")
    ax.set_title("Distribución demográfica", fontsize=11, fontweight="bold")
    ax.set_xlabel("Nº de estudiantes")
    ax.tick_params(axis="y", labelsize=8)

    for barra, valor in zip(barras, conteos.values):
        if valor > 0:
            ax.text(valor, barra.get_y() + barra.get_height() / 2,
                    str(int(valor)), ha="left", va="center", fontsize=8)

    fig.tight_layout()
    return fig
