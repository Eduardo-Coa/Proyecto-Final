---
name: project-architecture
description: Use this skill whenever the user asks to create new files, modules, or features in this project, mentions MVC, file structure, where to put code, or asks about Python conventions. Triggers include "donde pongo", "nuevo modulo", "nueva clase", "MVC", "estructura", "PEP8", "clean code", "refactorizar", "analytics", "ml", "carpeta". Also use when reviewing existing code for style issues. Do NOT use for test writing (use testing-pytest skill instead).
allowed-tools: Read Grep Glob
---

# Arquitectura del Proyecto - Plataforma de Apoyo Psicoeducativo

## Contexto del proyecto
Sistema en Python 3.10+ para registrar y analizar niveles de estrés y ansiedad académica usando instrumentos PHQ-9 y GAD-7 en entorno universitario. Persistencia en JSON, UI en Tkinter, patrón arquitectónico MVC.

## Estructura de carpetas (OBLIGATORIA)

```
proyecto-psicoeducativo/
├── src/
│   ├── models/          # Entidades del dominio (Estudiante, CuestionarioPHQ9, etc.)
│   ├── views/           # Vistas Tkinter (una por entidad CRUD + dashboard analítico)
│   ├── controllers/     # Controladores MVC (uno por entidad)
│   ├── services/        # EmailService, repositorios JSON, lógica transversal
│   ├── exceptions/      # Excepciones personalizadas
│   ├── analytics/       # Análisis de datos: data_loader, descriptive_stats, correlations, visualizations
│   ├── ml/              # Machine Learning: features, train_classifier, predictor, evaluation
│   │   └── models/      # Modelos entrenados (.joblib) — NO commitear al repo
│   └── utils/           # Helpers (validadores genéricos, constantes de negocio)
├── scripts/
│   └── generar_datos_sinteticos.py   # Genera datos sintéticos realistas
├── data/                # Archivos JSON de persistencia (generados localmente)
├── tests/               # Tests con pytest (espejo de src/)
├── docs/                # Diagramas BPMN, clases, estados
└── main.py              # Entry point
```

## Reglas MVC en este proyecto

**Model (`src/models/`)**:
- Cada entidad es un `@dataclass` o clase normal con atributos + validaciones en `__post_init__` o setters.
- NO conoce a la vista ni al controlador.
- NO accede al sistema de archivos directamente (eso es del repositorio en `services/`).

**View (`src/views/`)**:
- Solo Tkinter. UI únicamente, sin lógica de negocio.
- Recibe el controlador por inyección y llama métodos como `controller.crear_estudiante(...)`.
- Una vista por entidad CRUD: `estudiante_view.py`, `phq9_view.py`, etc.

**Controller (`src/controllers/`)**:
- Orquesta: recibe datos de la vista, valida con el modelo, invoca el servicio de persistencia y el EmailService.
- Captura excepciones del dominio y las traduce a mensajes para la vista.
- Un controlador por entidad CRUD.

## Convenciones de naming

- Archivos y módulos: `snake_case.py` → `estudiante_controller.py`
- Clases: `PascalCase` → `EstudianteController`, `CuestionarioPHQ9`
- Funciones y variables: `snake_case` → `crear_estudiante`, `puntaje_total`
- Constantes: `UPPER_SNAKE_CASE` → `PUNTAJE_MAXIMO_PHQ9 = 27`
- Privados/internos: prefijo `_` → `_validar_codigo()`
- Tests: archivo `test_<modulo>.py`, función `test_<comportamiento>_<condicion>()`

## PEP8 (NO negociable)

- Indentación: 4 espacios, NUNCA tabs.
- Longitud de línea máxima: 100 caracteres (relajación PEP8, más legible que 79).
- Dos líneas en blanco entre clases y funciones top-level, una entre métodos.
- Imports: stdlib → terceros → locales, separados por línea en blanco.
- Docstrings estilo Google en todas las clases y métodos públicos.
- Type hints obligatorios en firmas de funciones públicas.

## Clean Code aplicado aquí

- Funciones cortas (máx ~20 líneas). Si crece, extraer método.
- Nombres descriptivos en español (es proyecto académico en ese idioma).
- NO números mágicos: usar constantes con nombre (`PUNTAJE_RIESGO_SEVERO = 20`).
- NO comentarios obvios. Comentar el "por qué", no el "qué".
- Una responsabilidad por clase/función (SRP).
- DRY: si copias código dos veces, refactoriza a la tercera.

## Entidades del proyecto

### CRUD (una por integrante):
1. **Estudiante** — Integrante 1 | Analítica: dashboard demográfico
2. **CuestionarioPHQ9** — Integrante 2 | Analítica: modelo ML de clasificación
3. **CuestionarioGAD7** — Integrante 3 | Analítica: correlación PHQ-9 ↔ GAD-7
4. **SesionSeguimiento** — Integrante 4 | Analítica: series temporales de evolución

### Auxiliares (sin CRUD propio):
5. **Psicologo** — catálogo en JSON precargado
6. **AlertaRiesgo** — generada automáticamente por reglas de negocio
7. **Respuesta** — componente interno de los cuestionarios

## Módulos adicionales (no MVC, capas transversales)

- **`src/analytics/`** — No es parte del MVC. Es una capa de servicios de análisis que consume los JSONs directamente vía pandas. Las vistas del dashboard la usan directamente sin pasar por controllers.
- **`src/ml/`** — Pipeline de scikit-learn. Se entrena offline (`python -m src.ml.train_classifier`) y se consume en la vista PHQ-9 vía `PHQ9Predictor`.
- **`scripts/`** — Scripts de utilidad ejecutables directamente, no importados por la app.

## Antes de crear código nuevo

1. Verifica si ya existe un módulo similar con `Grep` o `Glob`.
2. Identifica a qué capa MVC pertenece.
3. Revisa naming conventions arriba.
4. Si el módulo tendrá lógica de negocio compleja, considera si debe ir en `services/` en vez de en el modelo.
