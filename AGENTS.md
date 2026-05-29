# AGENTS.md — Plataforma de Apoyo Psicoeducativo

> Este archivo es leído por Codex (y otros agentes que usan el estándar `AGENTS.md`) al inicio de cada sesión. Contiene todo el contexto necesario para continuar el desarrollo sin repetir instrucciones. Es el equivalente al `CLAUDE.md` del proyecto: si modificas uno, mantén el otro sincronizado. **No modificar sin consenso del equipo.**

---

## 1. ¿Qué es este proyecto?

Una aplicación de escritorio en Python para el área de **Bienestar Universitario**. Permite registrar y monitorear el estado emocional de estudiantes mediante los instrumentos clínicos validados **PHQ-9** (depresión) y **GAD-7** (ansiedad). El sistema gestiona la información, aplica reglas clínicas automáticas, notifica por correo y analiza los datos con estadística descriptiva.

**Es un proyecto académico de programación** con criterios de evaluación específicos. Cada decisión técnica (MVC, Decorator, Tkinter) fue tomada en función de esos criterios.

---

## 2. Equipo

| Integrante | Entidad CRUD | Regla de negocio | Contribución analítica |
|---|---|---|---|
| **1** | `Estudiante` | Código único + edad ≥ 16 + semestre 1-12 | Dashboard demográfico (distribución por programa/semestre) |
| **2** | `CuestionarioPHQ9` | Puntaje ≥ 20 → riesgo severo + dispara EmailService | Estadística descriptiva: distribución de puntajes y severidad PHQ-9 |
| **3** | `CuestionarioGAD7` | GAD ≥ 15 → severa; comorbilidad si PHQ-9 severo reciente | Análisis bivariado: correlación PHQ-9 ↔ GAD-7 |
| **4** | `SesionSeguimiento` | Solo agendar si: tiene cuestionario + no hay otra sesión ese día + hora 08-18 | Series temporales: evolución del puntaje del estudiante |

---

## 3. Stack técnico

| Área | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| UI | Tkinter + ttk |
| Visualización | matplotlib (embebido con `FigureCanvasTkAgg`) |
| Análisis de datos | pandas |
| Persistencia | MySQL (mysql-connector-python) + credenciales en `.env` |
| Testing | pytest + pytest-cov |
| Patrón arquitectónico | MVC |
| Patrón GoF | Decorator (EmailService) |
| Estilo | PEP8, Clean Code, type hints, docstrings Google-style |

---

## 4. Estructura de carpetas

```
proyecto-psicoeducativo/
├── AGENTS.md                          ← Este archivo (instrucciones para Codex)
├── CLAUDE.md                          ← Equivalente para Claude Code (mantener sincronizado)
├── README.md                          ← Para el equipo humano
├── requirements.txt
├── main.py                            ← Entry point de la app
│
├── src/
│   ├── models/                        ← Entidades del dominio
│   │   ├── estudiante.py
│   │   ├── cuestionario_phq9.py
│   │   ├── cuestionario_gad7.py
│   │   ├── sesion_seguimiento.py
│   │   ├── psicologo.py               ← Solo lectura, sin CRUD
│   │   └── alerta_riesgo.py           ← Generada automáticamente
│   │
│   ├── views/                         ← Vistas Tkinter (MVC)
│   │   ├── estudiante_view.py
│   │   ├── phq9_view.py
│   │   ├── gad7_view.py
│   │   ├── sesion_view.py
│   │   └── dashboard_view.py          ← Vista analítica con gráficas
│   │
│   ├── controllers/                   ← Controladores MVC
│   │   ├── estudiante_controller.py
│   │   ├── phq9_controller.py
│   │   ├── gad7_controller.py
│   │   └── sesion_controller.py
│   │
│   ├── repositories/                  ← Persistencia MySQL + interfaz + conexión
│   │   ├── interfaces.py              ← IRepository (ABC) — necesario para Decorator
│   │   ├── db_config.py              ← obtener_conexion() lee credenciales del .env
│   │   ├── estudiante_repository.py
│   │   ├── phq9_mysql_repository.py
│   │   ├── gad7_mysql_repository.py
│   │   ├── sesion_repository.py
│   │   └── alerta_repository.py       ← Persiste AlertaRiesgo (no CRUD calificable)
│   │
│   ├── services/                      ← EmailService + Decorator + reglas de negocio
│   │   ├── email_service.py           ← EmailService (modo simulación por defecto)
│   │   ├── notificacion_decorator.py  ← Decorator GoF que envuelve IRepository
│   │   ├── phq9_business_service.py   ← Regla del integrante 2
│   │   ├── gad7_business_service.py   ← Regla del integrante 3
│   │   └── sesion_business_service.py ← Regla del integrante 4
│   │
│   ├── exceptions/                    ← Excepciones personalizadas (criterio 4)
│   │   ├── base.py                    ← PlataformaError
│   │   ├── validation_errors.py       ← ValidationError y subclases (VAL001-VAL006)
│   │   ├── persistence_errors.py      ← EntityNotFoundError, DuplicateEntityError
│   │   ├── business_errors.py         ← BusinessRuleError y subclases (BR001-BR004)
│   │   └── notification_errors.py     ← EmailEnvioError
│   │
│   ├── analytics/                     ← Capa transversal de análisis (NO es MVC)
│   │   ├── data_loader.py             ← MySQL → DataFrame tipado
│   │   ├── descriptive_stats.py       ← media, mediana, distribuciones, clasificaciones
│   │   ├── correlations.py            ← correlación Pearson PHQ-9 ↔ GAD-7
│   │   └── visualizations.py          ← Funciones que devuelven Figure (nunca plt.show())
│   │
│   └── utils/
│       └── constantes_negocio.py      ← TODAS las constantes clínicas y de negocio
│
├── scripts/
│   ├── crear_schema.sql               ← Crea la BD bienestar_universitario y sus tablas
│   └── generar_datos_sinteticos.py    ← Inserta datos en MySQL: --n-estudiantes 500
│
├── .env                               ← Credenciales MySQL (NO commitear, está en .gitignore)
│
├── tests/
│   ├── conftest.py                    ← Fixtures compartidas (mocks)
│   ├── test_estudiante.py             ← 10+ tests — Integrante 1
│   ├── test_phq9.py                   ← 10+ tests — Integrante 2
│   ├── test_gad7.py                   ← 10+ tests — Integrante 3
│   ├── test_sesion.py                 ← 10+ tests — Integrante 4
│   └── test_email_decorator.py        ← Tests del Decorator GoF
│
└── docs/
    ├── bpmn_procesos.png              ← Mapa de procesos BPMN
    ├── diagrama_clases.png            ← Diagrama UML de las 7 clases
    └── diagrama_estados.png           ← Estados de CuestionarioPHQ9
```

> Nota: existe también una carpeta `.claude/skills/` con guías específicas de Claude Code (usadas por integrantes que trabajan con Claude). No afectan a Codex; puedes ignorarla.

---

## 5. Reglas de arquitectura MVC (NO negociables)

**Model** (`src/models/`):
- Solo atributos + validaciones en `__post_init__` o setters.
- Lanza excepciones de `src/exceptions/validation_errors.py`.
- Nunca toca la base de datos ni conoce la vista ni el controlador.
- Implementa `to_dict()` y `from_dict()` para conversión desde/hacia filas de MySQL.

**View** (`src/views/`):
- Solo Tkinter. Cero lógica de negocio.
- Recibe el controlador por inyección en `__init__`.
- Llama métodos del controlador y muestra el resultado.
- Para gráficas: usa `FigureCanvasTkAgg`. **NUNCA `plt.show()`**.

**Controller** (`src/controllers/`):
- Recibe datos crudos de la vista, construye el modelo, llama al repositorio (decorado).
- Captura excepciones del dominio y las traduce a `(bool, str)` para la vista.
- Nunca contiene lógica de negocio propia: delega al modelo y a `services/`.

**Analytics** (`src/analytics/`):
- Capa transversal, NO es parte del MVC.
- El dashboard view la consume directamente.
- Las funciones de analytics reciben DataFrames, no archivos.
- Las funciones de visualización devuelven `Figure`, nunca dibujan ellas mismas.

---

## 6. Convenciones de código

### Naming
```python
# Archivos y módulos
estudiante_controller.py        # snake_case

# Clases
class EstudianteController      # PascalCase
class CuestionarioPHQ9          # PascalCase

# Funciones y variables
def crear_estudiante()          # snake_case
puntaje_total = 0               # snake_case

# Constantes (en utils/constantes_negocio.py)
PUNTAJE_RIESGO_SEVERO_PHQ9 = 20  # UPPER_SNAKE_CASE

# Privados
def _validar_codigo()           # prefijo _
```

### Type hints y docstrings (obligatorios en funciones públicas)
```python
def crear(self, estudiante: Estudiante) -> Estudiante:
    """Persiste un nuevo estudiante.

    Args:
        estudiante: instancia validada de Estudiante.

    Returns:
        El mismo estudiante persistido.

    Raises:
        DuplicateEntityError: si ya existe el código.
    """
```

### PEP8
- Indentación: 4 espacios.
- Longitud máxima de línea: 100 caracteres.
- Dos líneas en blanco entre clases/funciones top-level.
- Imports: stdlib → terceros → locales, separados por línea en blanco.
- NUNCA `import *`.

---

## 7. Constantes clínicas (no usar números mágicos)

Todas en `src/utils/constantes_negocio.py`:

```python
# PHQ-9 (depresión) — rango 0 a 27
PUNTAJE_MAXIMO_PHQ9 = 27
PUNTAJE_RIESGO_SEVERO_PHQ9 = 20      # ≥ 20 → Severo
PUNTAJE_RIESGO_MODSEVERO_PHQ9 = 15  # ≥ 15 → Moderadamente severo
PUNTAJE_RIESGO_MODERADO_PHQ9 = 10   # ≥ 10 → Moderado
PUNTAJE_RIESGO_LEVE_PHQ9 = 5        # ≥  5 → Leve

# GAD-7 (ansiedad) — rango 0 a 21
PUNTAJE_MAXIMO_GAD7 = 21
PUNTAJE_RIESGO_SEVERO_GAD7 = 15     # ≥ 15 → Severo
PUNTAJE_RIESGO_MODERADO_GAD7 = 10
PUNTAJE_RIESGO_LEVE_GAD7 = 5

# Ítems
PUNTAJE_MINIMO_ITEM = 0
PUNTAJE_MAXIMO_ITEM = 3
NUM_ITEMS_PHQ9 = 9
NUM_ITEMS_GAD7 = 7

# Estudiantes
EDAD_MINIMA = 16
SEMESTRE_MINIMO = 1
SEMESTRE_MAXIMO = 12

# Sesiones
HORA_INICIO_ATENCION = 8            # 08:00
HORA_FIN_ATENCION = 18              # 18:00
DURACION_MIN_SESION = 30            # minutos
DURACION_MAX_SESION = 120

# Reglas de negocio
DIAS_MINIMOS_REAPLICACION = 14
DIAS_VENTANA_COMORBILIDAD = 30
```

---

## 8. Excepciones (jerarquía completa)

```
PlataformaError (base)
├── ValidationError
│   ├── CodigoInvalidoError         VAL001
│   ├── EdadInvalidaError           VAL002
│   ├── SemestreInvalidoError       VAL003
│   ├── CorreoInvalidoError         VAL004
│   ├── PuntajeInvalidoError        VAL005
│   └── FechaInvalidaError          VAL006
├── PersistenceError
│   ├── EntityNotFoundError         PER001
│   ├── DuplicateEntityError        PER002
│   └── ArchivoCorruptoError        PER003
├── BusinessRuleError
│   ├── ReaplicacionTempranaError   BR001
│   ├── RiesgoSeveroError           BR002
│   ├── HorarioFueraDeRangoError    BR003
│   └── SesionDuplicadaError        BR004
└── NotificacionError
    └── EmailEnvioError             NOT001
```

**Regla**: nunca capturar `Exception` genérico en el código de negocio. Usar siempre la excepción más específica disponible.

---

## 9. Reglas de negocio (una por integrante — criterio 5)

Los `BusinessServices` viven en `src/services/` y reciben sus dependencias por **inyección en el constructor** (nunca las instancian internamente).

### Integrante 1 — Estudiante
- **Regla**: No pueden existir dos estudiantes con el mismo código institucional.
- **Dónde**: `EstudianteRepository.crear()` lanza `DuplicateEntityError`.
- **BPMN**: gateway "¿Código duplicado?" tras "Ingresar datos del estudiante".

### Integrante 2 — CuestionarioPHQ9
- **Regla**: Si `puntaje_total ≥ 20`, crear `AlertaRiesgo` de tipo `DEPRESION_SEVERA` y notificar por email.
- **Dónde**: `PHQ9BusinessService.evaluar_riesgo()`.
- **Dependencias del `__init__`**: `AlertaRepository`, `EmailService`.
- **BPMN**: gateway "¿Puntaje ≥ 20?" tras "Calcular puntaje PHQ-9".

### Integrante 3 — CuestionarioGAD7
- **Regla**: Si `puntaje_total ≥ 15` Y el estudiante tiene un PHQ-9 con `puntaje ≥ 20` en los últimos 30 días → `AlertaRiesgo` de tipo `COMORBILIDAD`.
- **Dónde**: `GAD7BusinessService.evaluar_riesgo()`.
- **Dependencias del `__init__`**: `PHQ9Repository`, `AlertaRepository`, `EmailService`.
- **BPMN**: dos gateways en secuencia.

### Integrante 4 — SesionSeguimiento
- **Regla**: Solo agendar si: (1) estudiante tiene ≥ 1 cuestionario aplicado; (2) no hay otra sesión ese mismo día; (3) hora entre 08:00 y 18:00.
- **Dónde**: `SesionBusinessService.puede_agendar()`.
- **Dependencias del `__init__`**: `SesionRepository`, `PHQ9Repository`, `GAD7Repository`.
- **BPMN**: tres gateways previos al "Agendar sesión".

### Resumen de dependencias

| BusinessService | Recibe en `__init__` |
|---|---|
| `PHQ9BusinessService` | `alerta_repo`, `email_service` |
| `GAD7BusinessService` | `phq9_repo`, `alerta_repo`, `email_service` |
| `SesionBusinessService` | `sesion_repo`, `phq9_repo`, `gad7_repo` |

---

## 10. Patrón Decorator GoF (criterio 7)

El `NotificacionDecorator` envuelve cualquier `IRepository` y añade email tras crear/actualizar. El controlador recibe `IRepository` y no sabe si está decorado o no.

```
IRepository (ABC)
├── EstudianteRepository       ← Implementación concreta
└── NotificacionDecorator      ← También implementa IRepository
    └── contiene un IRepository internamente
```

**Wiring en `main.py` / `AppController`**:
```python
email = EmailService(modo_simulacion=True)
repo_base = EstudianteRepository(conexion)
repo = NotificacionDecorator(repo_base, email, "bienestar@uni.edu", "Estudiante")
controller = EstudianteController(repositorio=repo, business_service=...)
```

**EmailService en modo simulación** (por defecto): imprime en consola en lugar de enviar SMTP real. Cambiar a `modo_simulacion=False` solo para demo con credenciales configuradas.

**Qué repositorios se decoran**: solo los **4 repositorios CRUD** (Estudiante, PHQ9, GAD7, Sesion) que cubre el criterio 7. **NO** decorar `AlertaRepository` — los BusinessServices ya envían email manualmente al crear alertas, y decorarlo causaría emails duplicados.

---

## 11. Testing

- **Framework**: pytest
- **Mínimo por integrante**: 10 tests (criterio 6), incluyendo el test de su regla de negocio.
- **Patrón**: AAA (Arrange-Act-Assert).
- **Naming**: `test_<sujeto>_<accion>_<resultado_esperado>`.
- **Fixtures en `conftest.py`**: `Mock`/`MagicMock` para repositorios, EmailService y conexión MySQL.
- **NUNCA** conectar a MySQL real en tests — mockear el repositorio o la conexión.

**Comandos**:
```bash
pytest -v --tb=short                          # Todos los tests
pytest tests/test_estudiante.py -v            # Solo Integrante 1
pytest --cov=src --cov-report=term-missing    # Cobertura
pytest -v --tb=short > docs/reporte_tests.txt # Reporte para entrega
```

---

## 12. UI Tkinter

- Ventana principal: `ttk.Notebook` con 5 pestañas (4 CRUDs + Dashboard analítico).
- **SIEMPRE** feedback inmediato en `lbl_estado` (heurística Nielsen #1).
- **SIEMPRE** confirmación antes de eliminar (heurística #3).
- **NUNCA** mostrar tracebacks al usuario (heurística #9).
- **NUNCA** `plt.show()` — usar `FigureCanvasTkAgg` para gráficas.
- Orden de botones consistente en toda la app: `[Guardar] [Actualizar] [Eliminar] [Limpiar]`.

---

## 13. Datos sintéticos

- Script: `scripts/generar_datos_sinteticos.py` (inserta directamente en MySQL).
- Seed fijo: `SEED = 42` (reproducible).
- Correlación PHQ-9 ↔ GAD-7 esperada: r ≈ 0.65-0.75.
- Distribuciones basadas en literatura clínica para poblaciones universitarias.
- Requiere haber ejecutado antes `scripts/crear_schema.sql` para crear las tablas.
- Cada integrante ejecuta el script contra su MySQL local antes de arrancar la app.

---

## 14. Comandos de referencia rápida

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear el esquema de la base de datos (una vez por integrante)
# Ejecutar scripts/crear_schema.sql en MySQL Workbench o cliente equivalente

# Generar datos
python scripts/generar_datos_sinteticos.py --n-estudiantes 500

# Ejecutar app
python main.py

# Tests
pytest -v --tb=short
pytest --cov=src --cov-report=term-missing

# Linting
flake8 src/ --max-line-length=100
```

---

## 15. Mapeo de criterios de evaluación

| # | Criterio | Área de referencia | Estado |
|---|---|---|---|
| 1 | MVC + Clean Code + PEP8 | Arquitectura del proyecto | ⬜ Pendiente |
| 2 | CRUD por integrante | Entidad + repositorio | ⬜ Pendiente |
| 3 | Validaciones por dominio | Modelo de la entidad | ⬜ Pendiente |
| 4 | Excepciones personalizadas | `src/exceptions/` | ⬜ Pendiente |
| 5 | Regla de negocio por integrante | `BusinessService` | ⬜ Pendiente |
| 6 | 10 tests por integrante | `tests/` | ⬜ Pendiente |
| 7 | EmailService con Decorator GoF | `services/` | ⬜ Pendiente |
| 8 | Persistencia MySQL | `repositories/` | ⬜ Pendiente |
| 9 | UI Tkinter + Nielsen | `views/` | ⬜ Pendiente |
| 10 | Clean Code + PEP8 | Todo el código | ⬜ Pendiente |

Cambiar ⬜ a ✅ a medida que cada criterio quede implementado y testeado.

---

## 16. Lo que el agente NO debe hacer en este proyecto

- Proponer frameworks distintos a Tkinter para la UI (no Streamlit, no Flask, no PyQt5).
- Usar herencia para implementar el Decorator GoF (eso NO es Decorator).
- Usar `plt.show()` en ninguna función de visualización.
- Capturar `Exception` genérico en código de negocio.
- Poner lógica de negocio en las vistas o en los modelos (MVC estricto).
- Acceder a MySQL directamente desde los controladores (eso es del repositorio).
- Commitear el archivo `.env` con credenciales al repo.
