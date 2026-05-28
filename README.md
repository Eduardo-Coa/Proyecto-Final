# Plataforma de Apoyo Psicoeducativo con Analítica

Sistema de gestión y monitoreo del bienestar emocional enfocado en el entorno universitario, con un **módulo analítico embebido** que aplica ciencia de datos y machine learning sobre los instrumentos validados **PHQ-9** (depresión) y **GAD-7** (ansiedad).

## Stack técnico

- **Python 3.10+**
- **Tkinter** (UI con matplotlib embebido)
- **JSON** (persistencia de entidades)
- **pandas + matplotlib** (analítica y visualización)
- **scikit-learn** (clasificador de riesgo)
- **pytest** (testing)
- Patrón arquitectónico: **MVC**
- Patrón GoF: **Decorator** (para EmailService)

## Estructura del proyecto

```
proyecto-psicoeducativo/
├── .claude/skills/                # 10 skills de Claude Code
│   ├── project-architecture/
│   ├── entity-crud/
│   ├── custom-exceptions/
│   ├── business-rules/
│   ├── testing-pytest/
│   ├── email-decorator/
│   ├── ui-tkinter-nielsen/
│   ├── synthetic-data/            # ⭐ Generación de datos
│   ├── data-analysis/             # ⭐ pandas + matplotlib
│   └── ml-pipeline/               # ⭐ scikit-learn
├── src/
│   ├── models/                    # Entidades CRUD
│   ├── views/                     # Vistas Tkinter (incluye dashboard analítico)
│   ├── controllers/
│   ├── services/                  # Repositorios JSON + EmailService + Decorator
│   ├── exceptions/                # Excepciones personalizadas
│   ├── analytics/                 # ⭐ Análisis de datos
│   │   ├── data_loader.py
│   │   ├── descriptive_stats.py
│   │   ├── correlations.py
│   │   └── visualizations.py
│   ├── ml/                        # ⭐ Machine Learning
│   │   ├── features.py
│   │   ├── train_classifier.py
│   │   ├── predictor.py
│   │   ├── evaluation.py
│   │   └── models/                # Modelos entrenados (.joblib)
│   └── utils/
├── scripts/
│   └── generar_datos_sinteticos.py
├── data/                          # JSONs (generados localmente)
├── tests/
├── docs/                          # BPMN, diagrama de clases, diagrama de estados
├── main.py
├── requirements.txt
└── README.md
```

## Reparto del equipo (4 integrantes)

Cada integrante implementa su **CRUD** + contribuye al **módulo analítico**.

| Integrante | Entidad CRUD | Regla de negocio | Contribución analítica |
|---|---|---|---|
| **1** | `Estudiante` | Código único + edad ≥ 16 + semestre 1-12 | Dashboard demográfico: distribución por programa/semestre |
| **2** | `CuestionarioPHQ9` | Puntaje ≥ 20 → riesgo severo + EmailService | **Modelo ML**: Regresión Logística para clasificar severidad |
| **3** | `CuestionarioGAD7` | GAD ≥ 15 → severa; comorbilidad con PHQ-9 | **Correlación**: análisis bivariado PHQ-9 vs GAD-7 |
| **4** | `SesionSeguimiento` | Solo agendar si: tiene cuestionario + no hay otra sesión + hora 8-18 | **Series temporales**: evolución del puntaje del estudiante |

### Entidades auxiliares (sin CRUD propio)
- `Psicologo` (catálogo precargado)
- `AlertaRiesgo` (generada automáticamente)
- `Respuesta` (componente interno de cuestionarios)

## Mapeo de criterios

| # | Criterio | Skill responsable | Quién lo hace |
|---|---|---|---|
| 1 | MVC + Clean Code + PEP8 | `project-architecture` | Todos |
| 2 | CRUD por integrante | `entity-crud` | Cada uno |
| 3 | Validaciones por dominio | `entity-crud` | Cada uno |
| 4 | Excepciones personalizadas | `custom-exceptions` | Todos |
| 5 | Regla de negocio por integrante | `business-rules` | Cada uno |
| 6 | 10 tests por integrante | `testing-pytest` | Cada uno |
| 7 | EmailService con Decorator | `email-decorator` | Líder técnico |
| 8 | Persistencia JSON | `entity-crud` | Cada uno |
| 9 | UI Tkinter + heurísticas Nielsen | `ui-tkinter-nielsen` | Cada uno |
| 10 | Clean Code + PEP8 | `project-architecture` | Todos |
| ⭐ | Datos sintéticos | `synthetic-data` | Integrante 1 lidera |
| ⭐ | Análisis estadístico | `data-analysis` | Integrantes 1, 3, 4 |
| ⭐ | Modelo ML | `ml-pipeline` | Integrante 2 lidera |

## Instalación y ejecución

```bash
# Clonar
git clone <url-del-repo>
cd proyecto-psicoeducativo

# Entorno virtual
python -m venv .venv
source .venv/bin/activate           # Linux/Mac
.venv\Scripts\activate              # Windows

# Dependencias
pip install -r requirements.txt

# Configurar MySQL
copy .env.example .env                # Windows
# cp .env.example .env                # Linux/Mac
# Editar .env con el usuario y password de MySQL
mysql -u root -p < scripts/crear_schema.sql

# 1. Generar datos sintéticos (necesario para que la app tenga datos)
python scripts/generar_datos_sinteticos.py --n-estudiantes 500

# 2. Entrenar modelo ML (opcional pero recomendado)
python -m src.ml.train_classifier

# 3. Ejecutar la aplicación
python main.py

# Correr tests
pytest -v --tb=short

# Cobertura
pytest --cov=src --cov-report=term-missing
```

## Cómo usar los skills de Claude Code

Los 10 skills viven en `.claude/skills/`. Claude Code los carga automáticamente. Ejemplos de prompts:

| Lo que escribes | Skill que se activa |
|---|---|
| *"Implementa el CRUD de Estudiante"* | `entity-crud` + `custom-exceptions` |
| *"Cómo aplico el Decorator al repositorio?"* | `email-decorator` |
| *"Necesito generar 500 estudiantes con sus PHQ-9"* | `synthetic-data` |
| *"Crea el dashboard con histograma de puntajes"* | `data-analysis` + `ui-tkinter-nielsen` |
| *"Entrena el clasificador de riesgo"* | `ml-pipeline` |
| *"Escribe los 10 tests para el modelo"* | `testing-pytest` + `ml-pipeline` |

Verificar skills cargados: dentro de Claude Code ejecuta `/skills`.

## Flujo de trabajo Git

```bash
git checkout -b feature/integrante-1-estudiante
git checkout -b feature/integrante-2-phq9
git checkout -b feature/integrante-3-gad7
git checkout -b feature/integrante-4-sesion

git commit -m "feat(estudiante): añade modelo y validaciones"
git commit -m "feat(estudiante): implementa CRUD con JSON"
git commit -m "feat(analytics): dashboard demográfico"
```

## Diagramas requeridos (criterio habilitante b)

Carpeta `docs/`:
- `bpmn_procesos.png` — Mapa de procesos BPMN con las 4 reglas de negocio
- `diagrama_clases.png` — UML con las 7 clases del dominio
- `diagrama_estados.png` — Estados de `CuestionarioPHQ9`: NORMAL → LEVE → MODERADO → SEVERO

## Plan de aprendizaje sugerido (si no saben pandas/sklearn)

**Semana 1**: pandas básico — DataFrames, filtrado, groupby.

**Semana 2**: matplotlib — Figure/Axes, tipos de gráficos. Practicar con los datos sintéticos generados.

**Semana 3**: sklearn — train/test split, Pipeline, LogisticRegression. Hacer el modelo del proyecto.

**Semana 4**: Integración en Tkinter — FigureCanvasTkAgg, refresco de datos.

## Checklist final antes de entregar

### CRUD y arquitectura
- [ ] Los 4 CRUDs funcionan desde la UI Tkinter
- [ ] Las 4 reglas de negocio están implementadas Y testeadas
- [ ] EmailService usa Decorator GoF auténtico
- [ ] No hay `except Exception` ni `ValueError` genéricos
- [ ] PEP8 limpio

### Analítica y ML
- [ ] Script de generación de datos sintéticos funciona
- [ ] Dashboard analítico muestra al menos 4 visualizaciones diferentes
- [ ] Modelo ML entrenado, persistido y cargable
- [ ] Matriz de confusión visible en la UI
- [ ] Análisis de correlación PHQ-9 ↔ GAD-7 reporta r ≈ 0.6-0.8

### Tests y entrega
- [ ] `pytest -v` muestra ≥ 40 tests pasando (10 × 4 integrantes)
- [ ] Cobertura > 70% sobre `src/`
- [ ] BPMN, diagrama de clases y diagrama de estados en `docs/`
- [ ] Cada integrante tiene ≥ 3 commits en su rama
- [ ] README actualizado con nombres reales del equipo
