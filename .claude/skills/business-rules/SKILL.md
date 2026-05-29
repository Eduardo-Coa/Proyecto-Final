---
name: business-rules
description: Use this skill whenever the user implements, modifies, or discusses business logic, business rules, BPMN flows, automatic alerts, score thresholds, or domain decisions. Triggers include "regla de negocio", "BPMN", "umbral", "alerta", "riesgo severo", "PHQ", "GAD", "puntaje", "automatico", "valida que", "no puede", "solo si". Each integrante has one specific business rule — apply the one matching the entity in context. Do NOT use for generic validations (use entity-crud for those).
allowed-tools: Read Write Edit Grep
---

# Reglas de Negocio (Criterio 5)

## Diferencia crítica: Validación vs Regla de negocio

- **Validación**: chequea que un dato individual sea correcto (edad ≥ 16, semestre 1-12).
- **Regla de negocio**: lógica del dominio que cruza datos, depende del estado del sistema o dispara acciones automáticas.

Las reglas de negocio van en `src/services/` (no en los modelos) porque pueden requerir consultar repositorios.

## Reglas por integrante (una por persona, según criterio 5)

### Integrante 1 — Estudiante: Unicidad de código institucional
**Regla**: No se puede registrar un estudiante con código duplicado en el sistema.
**Por qué es regla de negocio y no validación**: requiere consultar el repositorio.
**Implementación**: el repositorio chequea contra registros existentes y lanza `DuplicateEntityError`.
**Evidencia en BPMN**: gateway exclusivo "¿Código ya existe?" después de "Registrar estudiante".

### Integrante 2 — CuestionarioPHQ9: Riesgo severo de depresión
**Regla**: Si el puntaje total del PHQ-9 ≥ 20, el cuestionario se marca como `RIESGO_SEVERO`, se crea automáticamente una `AlertaRiesgo`, y se dispara EmailService al psicólogo asignado.
**Umbral**: `PUNTAJE_RIESGO_SEVERO_PHQ9 = 20` (rango total: 0-27).
**Evidencia en BPMN**: gateway "¿Puntaje ≥ 20?" → tarea automática "Crear alerta + notificar psicólogo".

```python
PUNTAJE_RIESGO_SEVERO_PHQ9 = 20

class PHQ9BusinessService:
    """Aplica las reglas de negocio del cuestionario PHQ-9."""

    def __init__(
        self,
        alerta_repo: "AlertaRepository",
        email_service: "EmailService",
    ) -> None:
        # Dependencias inyectadas por constructor (NO se crean dentro)
        self._alerta_repo = alerta_repo
        self._email_service = email_service

    def evaluar_riesgo(self, cuestionario: CuestionarioPHQ9) -> EstadoRiesgo:
        if cuestionario.puntaje_total >= PUNTAJE_RIESGO_SEVERO_PHQ9:
            alerta = AlertaRiesgo(
                codigo_estudiante=cuestionario.codigo_estudiante,
                tipo=TipoAlerta.DEPRESION_SEVERA,
                puntaje=cuestionario.puntaje_total,
                prioridad=NivelPrioridad.ALTA,
                fecha=datetime.now(),
            )
            self._alerta_repo.crear(alerta)
            self._email_service.enviar(
                destinatario="bienestar@uni.edu",
                asunto="Alerta: PHQ-9 severo",
                cuerpo=f"Estudiante {cuestionario.codigo_estudiante} requiere atención.",
            )
            return EstadoRiesgo.SEVERO
        return EstadoRiesgo.NORMAL
```

### Integrante 3 — CuestionarioGAD7: Ansiedad severa + correlación con PHQ-9
**Regla**: Si el puntaje GAD-7 ≥ 15, marcar como ansiedad severa. **Adicionalmente**, si el mismo estudiante tiene un PHQ-9 con riesgo severo en los últimos 30 días, generar una `AlertaRiesgo` de tipo `COMORBILIDAD` con prioridad alta.
**Umbral**: `PUNTAJE_RIESGO_SEVERO_GAD7 = 15` (rango total: 0-21).
**Evidencia en BPMN**: dos gateways en secuencia: "¿GAD ≥ 15?" → "¿Tiene PHQ severo reciente?" → "Alerta de comorbilidad".

```python
class GAD7BusinessService:
    """Aplica las reglas de negocio del cuestionario GAD-7 incluyendo comorbilidad."""

    def __init__(
        self,
        phq9_repo: "PHQ9Repository",       # Para chequear comorbilidad
        alerta_repo: "AlertaRepository",
        email_service: "EmailService",
    ) -> None:
        self._phq9_repo = phq9_repo
        self._alerta_repo = alerta_repo
        self._email_service = email_service

    def evaluar_riesgo(self, cuestionario: CuestionarioGAD7) -> EstadoRiesgo:
        if cuestionario.puntaje_total < PUNTAJE_RIESGO_SEVERO_GAD7:
            return EstadoRiesgo.NORMAL

        # Chequear comorbilidad con PHQ-9 reciente
        tipo = TipoAlerta.ANSIEDAD_SEVERA
        if self._tiene_phq9_severo_reciente(cuestionario.codigo_estudiante):
            tipo = TipoAlerta.COMORBILIDAD

        self._alerta_repo.crear(AlertaRiesgo(
            codigo_estudiante=cuestionario.codigo_estudiante,
            tipo=tipo,
            puntaje=cuestionario.puntaje_total,
            prioridad=NivelPrioridad.ALTA,
            fecha=datetime.now(),
        ))
        return EstadoRiesgo.SEVERO
```

### Integrante 4 — SesionSeguimiento: Restricciones de agendamiento
**Regla**: Solo se puede agendar una sesión si:
1. El estudiante tiene al menos un cuestionario aplicado (PHQ-9 o GAD-7).
2. No tiene otra sesión el mismo día.
3. La hora está entre 08:00 y 18:00.
**Por qué es regla de negocio**: requiere consultar múltiples repositorios.
**Evidencia en BPMN**: tres gateways previos al "Agendar sesión".

```python
class SesionBusinessService:
    """Valida las reglas de agendamiento de sesiones."""

    def __init__(
        self,
        sesion_repo: "SesionRepository",
        phq9_repo: "PHQ9Repository",
        gad7_repo: "GAD7Repository",
    ) -> None:
        self._sesion_repo = sesion_repo
        self._phq9_repo = phq9_repo
        self._gad7_repo = gad7_repo

    def puede_agendar(self, datos: dict) -> None:
        # Regla 1
        if not self._tiene_cuestionario_aplicado(datos["codigo_estudiante"]):
            raise BusinessRuleError(
                "El estudiante debe tener al menos un cuestionario aplicado."
            )
        # Regla 2
        if self._tiene_sesion_ese_dia(datos["codigo_estudiante"], datos["fecha_hora"]):
            raise SesionDuplicadaError(
                datos["codigo_estudiante"], datos["fecha_hora"]
            )
        # Regla 3
        hora = datos["fecha_hora"].hour
        if not (8 <= hora < 18):
            raise HorarioFueraDeRangoError(str(datos["fecha_hora"].time()))
```

## Constantes de negocio (centralizadas)

Crear `src/utils/constantes_negocio.py`:

```python
# Umbrales PHQ-9 (depresión)
PUNTAJE_MINIMO_ITEM = 0
PUNTAJE_MAXIMO_ITEM = 3
PUNTAJE_MAXIMO_PHQ9 = 27
PUNTAJE_RIESGO_SEVERO_PHQ9 = 20

# Umbrales GAD-7 (ansiedad)
PUNTAJE_MAXIMO_GAD7 = 21
PUNTAJE_RIESGO_SEVERO_GAD7 = 15

# Sesiones
HORA_INICIO_ATENCION = 8
HORA_FIN_ATENCION = 18
DURACION_MIN_SESION = 30
DURACION_MAX_SESION = 120

# Reaplicación
DIAS_MINIMOS_REAPLICACION = 14

# Comorbilidad
DIAS_VENTANA_COMORBILIDAD = 30
```

## Reglas universales

1. **Una regla de negocio = un método con nombre descriptivo** en una clase `*BusinessService`.
2. **Las reglas viven en `src/services/`**, no en los modelos.
3. **Cada regla debe poder testearse en aislamiento** — recibe sus dependencias por inyección.
4. **Cada regla del criterio 5 DEBE tener al menos 1 test específico** (incluido dentro de los 10 tests del integrante).
5. **El BPMN debe mostrar cada regla como un gateway o tarea automática.**

## Inyección de dependencias (OBLIGATORIO)

Los `BusinessServices` **NUNCA** instancian sus dependencias adentro. Las reciben por constructor:

```python
# ❌ MAL — acopla la clase a implementaciones concretas
class PHQ9BusinessService:
    def __init__(self):
        self._alerta_repo = AlertaRepository()   # ¡prohibido!

# ✅ BIEN — las dependencias entran por el constructor
class PHQ9BusinessService:
    def __init__(self, alerta_repo, email_service):
        self._alerta_repo = alerta_repo
        self._email_service = email_service
```

Esto se hace para que en los tests puedas inyectar mocks fácilmente:

```python
service = PHQ9BusinessService(
    alerta_repo=Mock(spec=AlertaRepository),
    email_service=Mock(spec=EmailService),
)
```

## Resumen de dependencias por BusinessService

| BusinessService | Dependencias en su `__init__` |
|---|---|
| `PHQ9BusinessService` | `AlertaRepository`, `EmailService` |
| `GAD7BusinessService` | `PHQ9Repository`, `AlertaRepository`, `EmailService` |
| `SesionBusinessService` | `SesionRepository`, `PHQ9Repository`, `GAD7Repository` |

## AlertaRepository (importante)

`AlertaRiesgo` se persiste en `data/alertas.json`, por lo que necesita un repositorio propio (`AlertaRepository`) que implementa `IRepository[AlertaRiesgo]`. Aunque no es un CRUD asignado a ningún integrante (las alertas se generan automáticamente), el repositorio es necesario para que los `BusinessServices` puedan crear alertas siguiendo el mismo patrón.

**Wiring en `main.py`**:
```python
alerta_repo = AlertaRepository()
email = EmailService(modo_simulacion=True)

phq9_service = PHQ9BusinessService(alerta_repo=alerta_repo, email_service=email)
gad7_service = GAD7BusinessService(
    phq9_repo=phq9_repo,
    alerta_repo=alerta_repo,
    email_service=email,
)
```
