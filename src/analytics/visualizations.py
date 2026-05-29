"""Graficas del dashboard analitico."""

from __future__ import annotations

import unicodedata

import pandas as pd
from matplotlib.figure import Figure

_ORDEN_SEVERIDAD = ["Minimo", "Leve", "Moderado", "Moderadamente severo", "Severo"]
_COLORES_SEVERIDAD = {
    "Minimo": "#27ae60",
    "Leve": "#f1c40f",
    "Moderado": "#e67e22",
    "Moderadamente severo": "#e74c3c",
    "Severo": "#c0392b",
}
_COLORES_INSTRUMENTOS = {
    "PHQ-9": _COLORES_SEVERIDAD["Moderadamente severo"],
    "GAD-7": "#2980b9",
}


def grafica_severidad_phq9(df: pd.DataFrame) -> Figure:
    """Construye un grafico de barras con la severidad PHQ-9.

    Args:
        df: DataFrame con la columna ``nivel_severidad``.

    Returns:
        Figura de matplotlib lista para incrustar en Tkinter.
    """
    fig = Figure(figsize=(5, 3.4), dpi=100)
    ax = fig.add_subplot(111)

    if df.empty or "nivel_severidad" not in df.columns:
        _dibujar_sin_datos(ax, fig)
        return fig

    conteos = df["nivel_severidad"].dropna().map(_normalizar_texto).value_counts()
    valores = [int(conteos.get(nivel, 0)) for nivel in _ORDEN_SEVERIDAD]
    colores = [_COLORES_SEVERIDAD[nivel] for nivel in _ORDEN_SEVERIDAD]

    barras = ax.bar(_ORDEN_SEVERIDAD, valores, color=colores)
    ax.set_title("Distribucion de severidad PHQ-9", fontsize=11, fontweight="bold")
    ax.set_ylabel("No. de cuestionarios")
    ax.tick_params(axis="x", labelrotation=20, labelsize=8)

    for barra, valor in zip(barras, valores):
        if valor > 0:
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                valor,
                str(valor),
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()
    return fig


def grafica_evolucion_sesiones(df: pd.DataFrame) -> Figure:
    """Construye la serie temporal de puntajes en estudiantes con seguimiento.

    Args:
        df: DataFrame con ``instrumento``, ``puntaje_total`` y
            ``fecha_aplicacion``.

    Returns:
        Figura de matplotlib lista para incrustar en Tkinter.
    """
    fig = Figure(figsize=(5, 3.4), dpi=100)
    ax = fig.add_subplot(111)

    columnas = {"instrumento", "puntaje_total", "fecha_aplicacion"}
    if df.empty or not columnas.issubset(df.columns):
        _dibujar_sin_datos(ax, fig)
        return fig

    datos = df.copy()
    datos["fecha_aplicacion"] = pd.to_datetime(datos["fecha_aplicacion"])
    datos["periodo"] = datos["fecha_aplicacion"].dt.to_period("W").dt.start_time
    serie = (
        datos.groupby(["periodo", "instrumento"])["puntaje_total"]
        .mean()
        .reset_index()
        .sort_values("periodo")
    )

    for instrumento, grupo in serie.groupby("instrumento"):
        ax.plot(
            grupo["periodo"],
            grupo["puntaje_total"],
            marker="o",
            linewidth=2,
            label=instrumento,
            color=_COLORES_INSTRUMENTOS.get(instrumento),
        )

    ax.set_title("Evolucion de puntajes con seguimiento", fontsize=11, fontweight="bold")
    ax.set_ylabel("Puntaje promedio")
    ax.set_xlabel("Semana de aplicacion")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    ax.tick_params(axis="x", labelrotation=25, labelsize=8)
    fig.tight_layout()
    return fig


def _dibujar_sin_datos(ax, fig: Figure) -> None:
    ax.text(
        0.5,
        0.5,
        "Sin datos disponibles",
        ha="center",
        va="center",
        fontsize=11,
        color="gray",
    )
    ax.axis("off")
    fig.tight_layout()


def _normalizar_texto(valor: object) -> str:
    texto = str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
