from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from src.analytics.correlations import correlacion_phq9_gad7

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


def grafica_correlacion_phq9_gad7(
    df_phq9: pd.DataFrame, df_gad7: pd.DataFrame
) -> Figure:
    """Construye un diagrama de dispersión de la correlación PHQ-9 ↔ GAD-7.

    Cada punto es un estudiante (puntaje PHQ-9 en X, GAD-7 en Y) coloreado por
    su severidad GAD-7 según la paleta clínica compartida. Añade una recta de
    tendencia y anota el coeficiente de Pearson ``r`` y el tamaño muestral ``n``.
    Devuelve una ``Figure`` para incrustarla con ``FigureCanvasTkAgg`` (nunca
    usa ``plt.show()``).

    Args:
        df_phq9: DataFrame de cuestionarios PHQ-9.
        df_gad7: DataFrame de cuestionarios GAD-7.

    Returns:
        Figura de matplotlib lista para incrustar en Tkinter.
    """
    fig = Figure(figsize=(5, 3.4), dpi=100)
    ax = fig.add_subplot(111)

    resultado = correlacion_phq9_gad7(df_phq9, df_gad7)
    pares = resultado["pares"]

    if pares.empty:
        ax.text(0.5, 0.5, "Sin datos disponibles", ha="center", va="center",
                fontsize=11, color="gray")
        ax.axis("off")
        fig.tight_layout()
        return fig

    for nivel in _ORDEN_SEVERIDAD:
        grupo = pares[pares["severidad_gad7"] == nivel]
        if not grupo.empty:
            ax.scatter(grupo["puntaje_phq9"], grupo["puntaje_gad7"],
                       color=_COLORES_SEVERIDAD[nivel], label=nivel,
                       s=30, alpha=0.7, edgecolors="white", linewidths=0.5)

    # Recta de tendencia (solo si hay variación suficiente para ajustarla).
    if resultado["r"] is not None and pares["puntaje_phq9"].nunique() > 1:
        pendiente, intercepto = np.polyfit(
            pares["puntaje_phq9"], pares["puntaje_gad7"], 1
        )
        x_linea = np.array([pares["puntaje_phq9"].min(), pares["puntaje_phq9"].max()])
        ax.plot(x_linea, pendiente * x_linea + intercepto,
                color="#34495e", linestyle="--", linewidth=1.2)

    r = resultado["r"]
    texto_r = "n/d" if r is None else f"{r:.3f}"
    ax.set_title("Correlación PHQ-9 ↔ GAD-7", fontsize=11, fontweight="bold")
    ax.set_xlabel("Puntaje PHQ-9")
    ax.set_ylabel("Puntaje GAD-7")
    ax.text(0.05, 0.95, f"r = {texto_r}  (n = {resultado['n']})",
            transform=ax.transAxes, ha="left", va="top", fontsize=9,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))
    ax.legend(title="Severidad GAD-7", fontsize=7, title_fontsize=7,
              loc="lower right")

    fig.tight_layout()
    return fig
