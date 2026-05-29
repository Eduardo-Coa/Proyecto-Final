from __future__ import annotations

import pandas as pd

from src.utils.constantes_negocio import PUNTAJE_RIESGO_SEVERO_PHQ9


def kpis_phq9(df: pd.DataFrame) -> dict[str, float | int]:
    """Calcula los indicadores clave (KPIs) de los cuestionarios PHQ-9.

    Args:
        df: DataFrame con al menos la columna ``puntaje_total``.

    Returns:
        Diccionario con: total de cuestionarios, puntaje promedio, puntaje
        mediano y porcentaje de estudiantes en riesgo severo (puntaje ≥ 20).
        Todos en cero si el DataFrame está vacío.
    """
    if df.empty:
        return {"total": 0, "promedio": 0.0, "mediana": 0.0, "pct_severo": 0.0}

    total = len(df)
    severos = int((df["puntaje_total"] >= PUNTAJE_RIESGO_SEVERO_PHQ9).sum())
    return {
        "total": total,
        "promedio": round(float(df["puntaje_total"].mean()), 1),
        "mediana": round(float(df["puntaje_total"].median()), 1),
        "pct_severo": round(severos / total * 100, 1),
    }
