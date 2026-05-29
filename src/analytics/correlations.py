from __future__ import annotations

import pandas as pd


def emparejar_phq9_gad7(
    df_phq9: pd.DataFrame, df_gad7: pd.DataFrame
) -> pd.DataFrame:
    """Empareja el cuestionario más reciente de cada instrumento por estudiante.

    Para cada estudiante toma su PHQ-9 y su GAD-7 más recientes (por
    ``fecha_aplicacion``) y los une por ``codigo_estudiante``, de modo que cada
    fila resultante es un par comparable de puntajes del mismo estudiante.

    Args:
        df_phq9: DataFrame de cuestionarios PHQ-9 (columnas ``codigo_estudiante``,
            ``puntaje_total``, ``fecha_aplicacion`` y opcionalmente ``programa``).
        df_gad7: DataFrame de cuestionarios GAD-7 con las mismas columnas más
            ``nivel_severidad``.

    Returns:
        DataFrame con columnas ``codigo_estudiante``, ``puntaje_phq9``,
        ``puntaje_gad7``, ``severidad_gad7`` y ``programa``. DataFrame vacío si
        alguno de los instrumentos no tiene registros.
    """
    columnas = [
        "codigo_estudiante", "puntaje_phq9", "puntaje_gad7",
        "severidad_gad7", "programa",
    ]
    if df_phq9.empty or df_gad7.empty:
        return pd.DataFrame(columns=columnas)

    ultimos_phq9 = (
        df_phq9.sort_values("fecha_aplicacion")
        .groupby("codigo_estudiante", as_index=False)
        .last()
    )
    ultimos_gad7 = (
        df_gad7.sort_values("fecha_aplicacion")
        .groupby("codigo_estudiante", as_index=False)
        .last()
    )

    pares = ultimos_phq9.merge(
        ultimos_gad7, on="codigo_estudiante", suffixes=("_phq9", "_gad7")
    )
    if pares.empty:
        return pd.DataFrame(columns=columnas)

    # ``programa`` puede venir de cualquiera de los dos lados (es el mismo
    # estudiante); se prioriza el del PHQ-9 y se completa con el del GAD-7.
    programa = pares["programa_phq9"].fillna(pares["programa_gad7"])
    return pd.DataFrame({
        "codigo_estudiante": pares["codigo_estudiante"],
        "puntaje_phq9": pares["puntaje_total_phq9"],
        "puntaje_gad7": pares["puntaje_total_gad7"],
        "severidad_gad7": pares["nivel_severidad_gad7"],
        "programa": programa,
    })


def correlacion_phq9_gad7(
    df_phq9: pd.DataFrame, df_gad7: pd.DataFrame
) -> dict[str, object]:
    """Calcula la correlación de Pearson entre los puntajes PHQ-9 y GAD-7.

    Empareja los cuestionarios con :func:`emparejar_phq9_gad7` y aplica el
    coeficiente de Pearson sobre los pares resultantes. La correlación requiere
    al menos dos pares; con menos, ``r`` es ``None``.

    Args:
        df_phq9: DataFrame de cuestionarios PHQ-9.
        df_gad7: DataFrame de cuestionarios GAD-7.

    Returns:
        Diccionario con ``r`` (coeficiente de Pearson o ``None``), ``n`` (número
        de estudiantes emparejados) y ``pares`` (DataFrame de pares).
    """
    pares = emparejar_phq9_gad7(df_phq9, df_gad7)
    n = len(pares)
    if n < 2:
        return {"r": None, "n": n, "pares": pares}

    r = pares["puntaje_phq9"].corr(pares["puntaje_gad7"], method="pearson")
    r = None if pd.isna(r) else round(float(r), 3)
    return {"r": r, "n": n, "pares": pares}
