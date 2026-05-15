---
name: synthetic-data
description: Use this skill whenever the user needs to generate, modify, or validate synthetic/fake data for the project — including student records, PHQ-9 responses, GAD-7 responses, or sessions. Triggers include "datos sinteticos", "fake data", "generar datos", "poblar", "seed", "data dummy", "datos de prueba", "Faker", "numpy random", "datos realistas". Use proactively when the user mentions needing data to test analytics or ML models. Do NOT use for production data — only synthetic.
allowed-tools: Read Write Edit Bash
---

# Generación de Datos Sintéticos Realistas

## Por qué este skill existe

El proyecto NO tiene acceso a datos reales (ética + privacidad médica). Para que el módulo analítico y el modelo ML tengan sentido, necesitamos **generar datos sintéticos que respeten las distribuciones reales conocidas** de PHQ-9 y GAD-7 en poblaciones universitarias.

## Volumen mínimo recomendado

- **Estudiantes**: 200-500 (para que las gráficas tengan forma)
- **Cuestionarios PHQ-9**: 1.5x el número de estudiantes (algunos repiten)
- **Cuestionarios GAD-7**: similar a PHQ-9
- **Sesiones**: 1x estudiantes (no todos requieren sesión)

Menos de 100 filas y los gráficos se ven vacíos; el modelo ML tendrá overfitting.

## Distribuciones realistas (basadas en literatura clínica)

### Edad de estudiantes universitarios
- Distribución normal: media=21, desv=3, truncar a [16, 35]

### Puntajes PHQ-9 en población universitaria (Kroenke et al.)
- **40%** NORMAL (0-4)
- **30%** LEVE (5-9)
- **18%** MODERADO (10-14)
- **8%** MODERADAMENTE SEVERO (15-19)
- **4%** SEVERO (20-27)

### Puntajes GAD-7
- **45%** NORMAL (0-4)
- **30%** LEVE (5-9)
- **15%** MODERADO (10-14)
- **10%** SEVERO (15-21)

### Correlación PHQ-9 ↔ GAD-7
En la realidad **r ≈ 0.65-0.75** (comorbilidad alta). Los datos sintéticos deben replicar esto, no ser independientes.

## Script: `scripts/generar_datos_sinteticos.py`

```python
"""
Genera datos sintéticos realistas para poblar la plataforma.
Uso: python scripts/generar_datos_sinteticos.py --n-estudiantes 300
"""
import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np


# ----- CONFIGURACIÓN -----
SEED = 42  # Para reproducibilidad
PROGRAMAS = [
    "Ingeniería de Sistemas", "Psicología", "Medicina", "Derecho",
    "Administración", "Diseño Gráfico", "Comunicación Social",
    "Ingeniería Industrial", "Contaduría", "Arquitectura",
]
NOMBRES = [
    "María", "Juan", "Sofía", "Carlos", "Valentina", "Andrés", "Camila",
    "Sebastián", "Isabella", "Mateo", "Lucía", "Daniel", "Manuela", "Samuel",
]
APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Pérez",
    "Sánchez", "Ramírez", "Torres", "Flores", "Castillo", "Vargas",
]
DOMINIO_CORREO = "uni.edu.co"


def generar_estudiantes(n: int) -> list[dict]:
    """Genera n estudiantes con distribuciones realistas."""
    np.random.seed(SEED)
    random.seed(SEED)

    estudiantes = []
    for i in range(n):
        # Edad: normal truncada
        edad = int(np.clip(np.random.normal(21, 3), 16, 35))

        # Semestre correlacionado con edad
        semestre_base = max(1, min(12, edad - 17))
        semestre = int(np.clip(np.random.normal(semestre_base, 1.5), 1, 12))

        nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
        codigo = f"EST{20230000 + i:08d}"
        correo = f"{codigo.lower()}@{DOMINIO_CORREO}"

        fecha_registro = datetime.now() - timedelta(days=random.randint(0, 180))

        estudiantes.append({
            "codigo": codigo,
            "nombre_completo": nombre,
            "edad": edad,
            "semestre": semestre,
            "correo": correo,
            "programa": random.choice(PROGRAMAS),
            "fecha_registro": fecha_registro.isoformat(),
        })
    return estudiantes


def generar_factor_latente() -> float:
    """
    Genera un 'factor latente' de salud mental por estudiante.
    Este factor se usa para correlacionar PHQ-9 y GAD-7 (comorbilidad realista).
    Rango: 0 (excelente salud mental) a 1 (severamente afectado).
    """
    # Distribución sesgada hacia la izquierda (mayoría sanos)
    return float(np.clip(np.random.beta(2, 5), 0, 1))


def generar_phq9(codigo_estudiante: str, factor_latente: float) -> dict:
    """
    Genera respuestas PHQ-9 correlacionadas con el factor latente del estudiante.
    Las 9 respuestas suman entre 0 y 27.
    """
    # Cada ítem tiene mayor probabilidad de valores altos si factor_latente es alto
    respuestas = []
    for _ in range(9):
        if factor_latente < 0.2:
            valor = np.random.choice([0, 1], p=[0.7, 0.3])
        elif factor_latente < 0.4:
            valor = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
        elif factor_latente < 0.7:
            valor = np.random.choice([0, 1, 2, 3], p=[0.2, 0.3, 0.3, 0.2])
        else:
            valor = np.random.choice([1, 2, 3], p=[0.2, 0.4, 0.4])
        respuestas.append(int(valor))

    fecha = datetime.now() - timedelta(days=random.randint(0, 120))
    return {
        "id": f"PHQ9-{random.randint(100000, 999999)}",
        "codigo_estudiante": codigo_estudiante,
        "respuestas": respuestas,
        "puntaje_total": sum(respuestas),
        "fecha_aplicacion": fecha.isoformat(),
    }


def generar_gad7(codigo_estudiante: str, factor_latente: float) -> dict:
    """
    Genera respuestas GAD-7 correlacionadas con el MISMO factor latente.
    Esto produce la correlación PHQ-9 ↔ GAD-7 realista (~0.7).
    """
    # Pequeña variación independiente para que no sean clones de PHQ-9
    factor_gad = float(np.clip(factor_latente + np.random.normal(0, 0.1), 0, 1))

    respuestas = []
    for _ in range(7):
        if factor_gad < 0.2:
            valor = np.random.choice([0, 1], p=[0.7, 0.3])
        elif factor_gad < 0.4:
            valor = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
        elif factor_gad < 0.7:
            valor = np.random.choice([0, 1, 2, 3], p=[0.2, 0.3, 0.3, 0.2])
        else:
            valor = np.random.choice([1, 2, 3], p=[0.2, 0.4, 0.4])
        respuestas.append(int(valor))

    fecha = datetime.now() - timedelta(days=random.randint(0, 120))
    return {
        "id": f"GAD7-{random.randint(100000, 999999)}",
        "codigo_estudiante": codigo_estudiante,
        "respuestas": respuestas,
        "puntaje_total": sum(respuestas),
        "fecha_aplicacion": fecha.isoformat(),
    }


def generar_dataset_completo(n_estudiantes: int = 300) -> dict:
    """Genera el dataset completo con correlaciones realistas."""
    estudiantes = generar_estudiantes(n_estudiantes)
    phq9_list = []
    gad7_list = []

    for est in estudiantes:
        # Cada estudiante tiene un factor latente único
        factor = generar_factor_latente()

        # ~80% completa PHQ-9, ~75% completa GAD-7
        if random.random() < 0.80:
            phq9_list.append(generar_phq9(est["codigo"], factor))
        if random.random() < 0.75:
            gad7_list.append(generar_gad7(est["codigo"], factor))

        # ~25% tiene un segundo PHQ-9 (seguimiento) con factor levemente distinto
        if random.random() < 0.25:
            factor_seguimiento = float(np.clip(factor + np.random.normal(0, 0.15), 0, 1))
            phq9_list.append(generar_phq9(est["codigo"], factor_seguimiento))

    return {
        "estudiantes": estudiantes,
        "phq9": phq9_list,
        "gad7": gad7_list,
    }


def guardar(dataset: dict, carpeta: str = "data") -> None:
    """Persiste cada lista en su archivo JSON correspondiente."""
    base = Path(carpeta)
    base.mkdir(exist_ok=True)

    archivos = {
        "estudiantes.json": dataset["estudiantes"],
        "cuestionarios_phq9.json": dataset["phq9"],
        "cuestionarios_gad7.json": dataset["gad7"],
    }
    for nombre, datos in archivos.items():
        with (base / nombre).open("w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print(f"✓ {nombre}: {len(datos)} registros")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de datos sintéticos")
    parser.add_argument("--n-estudiantes", type=int, default=300)
    parser.add_argument("--carpeta", default="data")
    args = parser.parse_args()

    print(f"Generando {args.n_estudiantes} estudiantes y datos asociados...")
    dataset = generar_dataset_completo(args.n_estudiantes)
    guardar(dataset, args.carpeta)
    print("✓ Generación completa.")
```

## Validación: comprobar que las distribuciones son realistas

Después de generar, ejecuta este check rápido:

```python
import json
import numpy as np

with open("data/cuestionarios_phq9.json") as f:
    phq9 = json.load(f)
with open("data/cuestionarios_gad7.json") as f:
    gad7 = json.load(f)

puntajes_phq = [c["puntaje_total"] for c in phq9]
puntajes_gad = [c["puntaje_total"] for c in gad7]

print(f"PHQ-9: media={np.mean(puntajes_phq):.1f}, std={np.std(puntajes_phq):.1f}")
print(f"GAD-7: media={np.mean(puntajes_gad):.1f}, std={np.std(puntajes_gad):.1f}")

# Correlación (solo estudiantes con ambos)
phq_por_est = {c["codigo_estudiante"]: c["puntaje_total"] for c in phq9}
gad_por_est = {c["codigo_estudiante"]: c["puntaje_total"] for c in gad7}
comunes = set(phq_por_est) & set(gad_por_est)
pares = [(phq_por_est[c], gad_por_est[c]) for c in comunes]
if pares:
    r = np.corrcoef([p[0] for p in pares], [p[1] for p in pares])[0, 1]
    print(f"Correlación PHQ-9 ↔ GAD-7: r={r:.2f} (esperado: 0.6-0.8)")
```

**Si la correlación es < 0.5 o > 0.85**, ajustar el ruido del `factor_gad` en `generar_gad7()`.

## Reglas

1. **Siempre usar `SEED`** para reproducibilidad. Cambiar solo si se necesita un dataset nuevo.
2. **Nunca subir datos reales** al repo, ni siquiera anonimizados.
3. **Versionar el generador**, no el output. El equipo regenera localmente.
4. **Datos en `data/`** son artefactos de desarrollo, no parte del código.
