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

Referir a la documentación de CLAUDE.md o consultar el archivo en el repositorio.

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

**Si la correlación es < 0.5 o > 0.85**, ajustar el ruido del factor latente.

## Reglas

1. **Siempre usar `SEED`** para reproducibilidad. Cambiar solo si se necesita un dataset nuevo.
2. **Nunca subir datos reales** al repo, ni siquiera anonimizados.
3. **Versionar el generador**, no el output. El equipo regenera localmente.
4. **Datos en `data/`** son artefactos de desarrollo, no parte del código.
