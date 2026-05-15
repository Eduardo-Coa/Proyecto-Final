---
name: ml-pipeline
description: Use this skill whenever the user works on machine learning, classification models, scikit-learn, training, prediction, or model evaluation in this project. Triggers include "modelo", "machine learning", "ML", "sklearn", "scikit-learn", "entrenar", "prediccion", "clasificador", "regresion logistica", "train_test_split", "accuracy", "precision", "recall", "F1", "matriz de confusion", "feature", "joblib", "pickle modelo". The project uses ONE simple model: Logistic Regression for PHQ-9 severity classification. Do NOT propose complex models (Random Forest, XGBoost, neural networks) — keep it simple and explainable.
allowed-tools: Read Write Edit Bash Grep
---

# Pipeline de Machine Learning (Simple y Explicable)

## Por qué Regresión Logística (y solo eso)

El equipo está aprendiendo ML desde cero. Para un proyecto académico:

- ✅ **Regresión Logística**: simple, interpretable, explicable al profesor.
- ❌ **Random Forest, XGBoost, redes neuronales**: difíciles de defender si te preguntan "¿por qué funciona?".

**Regla**: si te preguntan "¿qué hace tu modelo?" debes poder explicarlo en una frase. Con Regresión Logística puedes: "Combina linealmente las 9 respuestas del PHQ-9 con pesos aprendidos, aplica la función sigmoide y obtiene la probabilidad de cada clase de severidad."

## Stack

```bash
pip install scikit-learn joblib numpy
```

Agregar a `requirements.txt`:
```
scikit-learn>=1.3.0
joblib>=1.3.0
numpy>=1.24.0
```

## Estructura del módulo `src/ml/`

```
src/ml/
├── __init__.py
├── features.py             # Construcción de features
├── train_classifier.py     # Entrena y guarda modelo
├── predictor.py            # Carga modelo y predice
├── evaluation.py           # Métricas y matriz de confusión
└── models/                 # Modelos serializados (.joblib)
    └── phq9_classifier.joblib
```

## Definición del problema

**Tarea**: Clasificación multiclase
**Input**: 9 respuestas del PHQ-9 (cada una en [0, 3])
**Output**: Una de 5 clases de severidad

```python
CLASES = ["Mínima", "Leve", "Moderada", "Mod. Severa", "Severa"]
```

**Ground truth**: derivado del puntaje total (suma de respuestas) según los rangos clínicos del PHQ-9.

## Features (`features.py`)

```python
import pandas as pd
import numpy as np


def construir_features_phq9(df_phq9: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Construye matriz de features y vector de etiquetas a partir del DataFrame PHQ-9.

    Returns:
        X: (n_muestras, 9) - respuestas individuales
        y: (n_muestras,) - clase de severidad
    """
    columnas_items = [f"item_{i+1}" for i in range(9)]

    # Si las respuestas están en una columna 'respuestas' (lista), expandir
    if "respuestas" in df_phq9.columns and columnas_items[0] not in df_phq9.columns:
        respuestas_df = pd.DataFrame(
            df_phq9["respuestas"].tolist(),
            columns=columnas_items,
            index=df_phq9.index,
        )
        df = pd.concat([df_phq9, respuestas_df], axis=1)
    else:
        df = df_phq9

    X = df[columnas_items].values
    y = df["puntaje_total"].apply(_clase_por_puntaje).values
    return X, y


def _clase_por_puntaje(puntaje: int) -> str:
    """Mapea puntaje total a clase de severidad clínica."""
    if puntaje <= 4:
        return "Mínima"
    elif puntaje <= 9:
        return "Leve"
    elif puntaje <= 14:
        return "Moderada"
    elif puntaje <= 19:
        return "Mod. Severa"
    else:
        return "Severa"
```

## Entrenamiento (`train_classifier.py`)

```python
"""
Entrena el clasificador PHQ-9 y guarda el modelo.
Uso: python -m src.ml.train_classifier
"""
import joblib
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

from src.analytics.data_loader import cargar_phq9
from src.ml.features import construir_features_phq9


RUTA_MODELO = Path("src/ml/models/phq9_classifier.joblib")
RANDOM_STATE = 42


def entrenar() -> dict:
    """Entrena el modelo y devuelve métricas de evaluación."""
    # 1. Cargar datos
    df = cargar_phq9()
    if len(df) < 30:
        raise ValueError(
            "Datos insuficientes. Ejecuta primero el generador de datos sintéticos."
        )

    # 2. Construir features
    X, y = construir_features_phq9(df)

    # 3. Split train/test (80/20 estratificado)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y,
    )

    # 4. Pipeline: escalado + modelo
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            multi_class="multinomial",
            solver="lbfgs",
            max_iter=1000,
            random_state=RANDOM_STATE,
        )),
    ])

    # 5. Entrenar
    pipeline.fit(X_train, y_train)

    # 6. Evaluar
    y_pred = pipeline.predict(X_test)
    reporte = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    matriz = confusion_matrix(y_test, y_pred, labels=pipeline.classes_)

    # 7. Persistir modelo
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, RUTA_MODELO)

    print("✓ Modelo entrenado y guardado en:", RUTA_MODELO)
    print(f"Accuracy global: {reporte['accuracy']:.3f}")
    print(f"F1 macro: {reporte['macro avg']['f1-score']:.3f}")

    return {
        "accuracy": reporte["accuracy"],
        "f1_macro": reporte["macro avg"]["f1-score"],
        "matriz_confusion": matriz.tolist(),
        "clases": pipeline.classes_.tolist(),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }


if __name__ == "__main__":
    entrenar()
```

## Predicción (`predictor.py`)

```python
import joblib
import numpy as np
from pathlib import Path

from src.exceptions.base import PlataformaError


RUTA_MODELO = Path("src/ml/models/phq9_classifier.joblib")


class ModeloNoEntrenadoError(PlataformaError):
    """El modelo no ha sido entrenado y persistido."""


class PHQ9Predictor:
    """Wrapper para usar el modelo entrenado en producción."""

    def __init__(self, ruta_modelo: Path = RUTA_MODELO) -> None:
        if not ruta_modelo.exists():
            raise ModeloNoEntrenadoError(
                f"No se encontró el modelo en {ruta_modelo}. "
                "Ejecuta: python -m src.ml.train_classifier"
            )
        self._pipeline = joblib.load(ruta_modelo)

    def predecir(self, respuestas: list[int]) -> dict:
        """
        Predice severidad a partir de las 9 respuestas.

        Args:
            respuestas: lista de 9 enteros entre 0 y 3.

        Returns:
            dict con 'clase_predicha' y 'probabilidades' por clase.
        """
        if len(respuestas) != 9:
            raise ValueError("Se requieren exactamente 9 respuestas.")
        if any(not (0 <= r <= 3) for r in respuestas):
            raise ValueError("Cada respuesta debe estar entre 0 y 3.")

        X = np.array([respuestas])
        clase = self._pipeline.predict(X)[0]
        probas = self._pipeline.predict_proba(X)[0]
        clases = self._pipeline.classes_

        return {
            "clase_predicha": str(clase),
            "probabilidades": {
                str(c): round(float(p), 3) for c, p in zip(clases, probas)
            },
        }
```

## Evaluación visual (`evaluation.py`)

```python
import numpy as np
from matplotlib.figure import Figure


def graficar_matriz_confusion(
    matriz: list[list[int]],
    clases: list[str],
    fig: Figure | None = None,
) -> Figure:
    """Visualiza matriz de confusión como heatmap."""
    fig = fig or Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)

    matriz_np = np.array(matriz)
    im = ax.imshow(matriz_np, cmap="Blues")

    ax.set_xticks(np.arange(len(clases)))
    ax.set_yticks(np.arange(len(clases)))
    ax.set_xticklabels(clases, rotation=45, ha="right")
    ax.set_yticklabels(clases)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    ax.set_title("Matriz de Confusión - Clasificador PHQ-9")

    # Anotar valores en celdas
    for i in range(len(clases)):
        for j in range(len(clases)):
            color = "white" if matriz_np[i, j] > matriz_np.max() / 2 else "black"
            ax.text(j, i, str(matriz_np[i, j]), ha="center", va="center", color=color)

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    return fig
```

## Reglas

1. **NUNCA inventar datos**: si no hay datos, lanzar excepción clara.
2. **Siempre estratificar el split** para mantener proporciones de clases.
3. **Random seed fijo** (`random_state=42`) para reproducibilidad.
4. **El modelo se entrena offline**, no en cada arranque de la app.
5. **Persistir con joblib**, no con pickle directo (joblib es la recomendación de sklearn).
6. **No mostrar nunca raw probabilities sin contexto** en la UI.
7. **Evaluar con métricas múltiples**: accuracy sola engaña.
