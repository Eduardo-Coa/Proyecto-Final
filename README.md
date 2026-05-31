# Plataforma de Apoyo Psicoeducativo

Aplicación de escritorio en Python para **Bienestar Universitario**. Registra y monitorea
el estado emocional de estudiantes mediante los instrumentos clínicos validados **PHQ-9**
(depresión) y **GAD-7** (ansiedad): gestiona la información, aplica reglas clínicas
automáticas, notifica por correo y analiza los datos con estadística descriptiva.

## Stack técnico
- **Python 3.10+**
- **Tkinter + ttk** (UI; gráficas embebidas con `FigureCanvasTkAgg`)
- **pandas + matplotlib** (analítica y visualización)
- **MySQL** (persistencia, vía `mysql-connector-python`)
- **python-dotenv** (credenciales en `.env`)
- **pytest** (testing)
- Arquitectura **MVC** · Patrón GoF: **Decorator** (EmailService)

## Rama para revisar el sistema
El proyecto integrado vive en la rama **`develop`**. Ubícate ahí para ejecutarlo:
```bash
git checkout develop
```

## Requisitos previos
- Python 3.10 o superior
- Un servidor **MySQL** corriendo localmente

## Instalación y ejecución
```bash
# 1. Clonar y ubicarse en la rama integrada
git clone https://github.com/Eduardo-Coa/Proyecto-Final.git
cd Proyecto-Final
git checkout develop

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Configurar credenciales: copiar la plantilla a .env y completarla
cp .env.example .env             # Windows: copy .env.example .env
#    Editar .env con tus credenciales de MySQL

# 5. Crear la base de datos y las tablas
#    Ejecutar scripts/crear_schema.sql en MySQL Workbench o consola

# 6. Generar datos de prueba
python scripts/generar_datos_sinteticos.py --n-estudiantes 100

# 7. Ejecutar la aplicación
python main.py
```

> **Nota sobre el `.env`:** el archivo `.env` **no se versiona** porque contiene
> credenciales. Por eso se incluye `.env.example` como plantilla — cópialo a `.env`
> y completa tus datos:
> ```
> MYSQL_HOST=localhost
> MYSQL_PORT=3306
> MYSQL_USER=root
> MYSQL_PASSWORD=tu_password
> MYSQL_DATABASE=bienestar_universitario
> ```

## Tests
```bash
pytest -v
pytest --cov=src --cov-report=term-missing
```

## Estructura del proyecto
```
Proyecto-Final/
├── main.py                     # Punto de entrada (composition root)
├── requirements.txt
├── .env.example                # Plantilla de credenciales (copiar a .env)
├── scripts/
│   ├── crear_schema.sql        # Crea la BD bienestar_universitario y sus tablas
│   └── generar_datos_sinteticos.py
├── src/
│   ├── models/                 # Entidades del dominio
│   ├── views/                  # Vistas Tkinter (incluye dashboard analítico)
│   ├── controllers/            # Controladores MVC + app_controller (Notebook)
│   ├── repositories/           # Persistencia MySQL + db_config + IRepository
│   ├── services/               # EmailService + Decorator + reglas de negocio
│   ├── exceptions/             # Excepciones personalizadas
│   ├── analytics/              # data_loader, descriptive_stats, correlations, visualizations
│   └── utils/                  # Constantes de negocio
├── tests/                      # pytest
└── docs/                       # Diagramas (BPMN, clases, estados)
```

## Equipo
| Integrante | Entidad CRUD | Regla de negocio | Contribución analítica |
|---|---|---|---|
| Alejandro | `Estudiante` | Código único + edad ≥ 16 + semestre 1-12 | Dashboard demográfico (por programa/semestre) |
| Eduardo | `CuestionarioPHQ9` | Puntaje ≥ 20 → riesgo severo + EmailService | Estadística descriptiva: severidad PHQ-9 |
| Diunis | `CuestionarioGAD7` | GAD ≥ 15 → severa; comorbilidad con PHQ-9 reciente | Correlación PHQ-9 ↔ GAD-7 |
| Cenaida | `SesionSeguimiento` | Agendar solo si: tiene cuestionario + sin otra sesión ese día + hora 08–18 | Series temporales: evolución del puntaje |

Entidades auxiliares (sin CRUD propio): `Psicologo` (catálogo) y `AlertaRiesgo` (generada automáticamente).

## Arquitectura
- **MVC**: modelos (entidades + validaciones), vistas (Tkinter), controladores (orquestan).
- **Analytics**: capa transversal (no MVC) que consume el dashboard. Las visualizaciones
  devuelven `Figure` (nunca `plt.show()`) y se embeben con `FigureCanvasTkAgg`.
- **Decorator GoF**: `NotificacionDecorator` envuelve los repositorios y notifica por correo
  tras crear/actualizar.
- **Persistencia**: MySQL; la conexión se obtiene con `obtener_conexion()` de
  `src/repositories/db_config.py`, leyendo las credenciales del `.env`.
