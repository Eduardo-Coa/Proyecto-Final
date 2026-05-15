---
name: custom-exceptions
description: Use this skill whenever the user writes raise statements, try/except blocks, error handling, or asks about exceptions in this project. Triggers include "excepcion", "raise", "try except", "error", "ValidationError", "manejo de errores", "lanzar error", "capturar". Also use proactively when reviewing CRUD or business rule code to ensure custom exceptions are used instead of generic ones. Do NOT use generic Exception or ValueError — this project requires custom exceptions per criterion 4.
allowed-tools: Read Write Edit
---

# Excepciones Personalizadas (Criterio 4)

## Regla absoluta

**NUNCA usar `Exception`, `ValueError`, `TypeError` genéricos en el código de negocio.** Siempre usar las excepciones personalizadas definidas en `src/exceptions/`. El profesor evalúa este criterio explícitamente.

## Jerarquía obligatoria

```
PlataformaError (base)
├── ValidationError              # Datos inválidos del usuario
│   ├── CodigoInvalidoError
│   ├── EdadInvalidaError
│   ├── SemestreInvalidoError
│   ├── CorreoInvalidoError
│   ├── PuntajeInvalidoError
│   └── FechaInvalidaError
├── PersistenceError             # Problemas con archivos JSON
│   ├── EntityNotFoundError
│   ├── DuplicateEntityError
│   └── ArchivoCorruptoError
├── BusinessRuleError            # Violación de reglas de negocio
│   ├── ReaplicacionTempranaError
│   ├── RiesgoSeveroError
│   ├── HorarioFueraDeRangoError
│   └── SesionDuplicadaError
└── NotificacionError            # Fallos en EmailService
    └── EmailEnvioError
```

## Estructura de archivos

```
src/exceptions/
├── __init__.py
├── base.py                  # PlataformaError
├── validation_errors.py     # ValidationError y subclases
├── persistence_errors.py    # PersistenceError y subclases
├── business_errors.py       # BusinessRuleError y subclases
└── notification_errors.py   # NotificacionError
```

## Implementación base (`src/exceptions/base.py`)

```python
class PlataformaError(Exception):
    """Excepción base de la plataforma psicoeducativa."""

    def __init__(self, mensaje: str, codigo_error: str | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self) -> str:
        if self.codigo_error:
            return f"[{self.codigo_error}] {self.mensaje}"
        return self.mensaje
```

## Validation errors (`src/exceptions/validation_errors.py`)

```python
from src.exceptions.base import PlataformaError


class ValidationError(PlataformaError):
    """Error genérico de validación de datos."""


class CodigoInvalidoError(ValidationError):
    def __init__(self, codigo: str) -> None:
        super().__init__(
            f"El código '{codigo}' no es válido. Debe tener al menos 4 caracteres.",
            codigo_error="VAL001",
        )


class EdadInvalidaError(ValidationError):
    def __init__(self, edad: int) -> None:
        super().__init__(
            f"La edad {edad} no es válida. Debe ser ≥ 16 años.",
            codigo_error="VAL002",
        )


class SemestreInvalidoError(ValidationError):
    def __init__(self, semestre: int) -> None:
        super().__init__(
            f"El semestre {semestre} no es válido. Debe estar entre 1 y 12.",
            codigo_error="VAL003",
        )


class CorreoInvalidoError(ValidationError):
    def __init__(self, correo: str) -> None:
        super().__init__(
            f"El correo '{correo}' tiene formato inválido.",
            codigo_error="VAL004",
        )


class PuntajeInvalidoError(ValidationError):
    def __init__(self, valor: int, rango: tuple[int, int]) -> None:
        super().__init__(
            f"Puntaje {valor} fuera del rango permitido {rango}.",
            codigo_error="VAL005",
        )


class FechaInvalidaError(ValidationError):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo, codigo_error="VAL006")
```

## Business errors (`src/exceptions/business_errors.py`)

```python
from src.exceptions.base import PlataformaError


class BusinessRuleError(PlataformaError):
    """Violación de una regla de negocio."""


class ReaplicacionTempranaError(BusinessRuleError):
    def __init__(self, dias_restantes: int) -> None:
        super().__init__(
            f"No puede re-aplicar este cuestionario. Faltan {dias_restantes} días.",
            codigo_error="BR001",
        )


class RiesgoSeveroError(BusinessRuleError):
    """No es un error per se, sino una señal de negocio."""
    def __init__(self, puntaje: int, umbral: int) -> None:
        super().__init__(
            f"Puntaje {puntaje} supera el umbral de riesgo severo ({umbral}).",
            codigo_error="BR002",
        )


class HorarioFueraDeRangoError(BusinessRuleError):
    def __init__(self, hora: str) -> None:
        super().__init__(
            f"La hora {hora} está fuera del horario permitido (08:00 - 18:00).",
            codigo_error="BR003",
        )


class SesionDuplicadaError(BusinessRuleError):
    def __init__(self, codigo_estudiante: str, fecha: str) -> None:
        super().__init__(
            f"Ya existe una sesión para {codigo_estudiante} el {fecha}.",
            codigo_error="BR004",
        )
```

## Patrón de uso

### Al lanzar una excepción
```python
# ❌ MAL
if edad < 16:
    raise ValueError("Edad inválida")

# ✅ BIEN
if edad < 16:
    raise EdadInvalidaError(edad)
```

### Al capturar en el controlador
```python
try:
    estudiante = Estudiante(**datos)
    self._repo.crear(estudiante)
except ValidationError as e:
    # Captura cualquier validación específica
    return False, f"Datos inválidos: {e.mensaje}"
except DuplicateEntityError as e:
    return False, str(e)
except PlataformaError as e:
    # Captura cualquier otra del dominio
    return False, f"Error en la operación: {e}"
```

## Reglas

1. **Captura específica antes que general**: primero las subclases, luego las padre.
2. **No capturar `Exception` genérico** salvo en el entry point (main).
3. **Toda excepción del dominio debe tener `codigo_error`** para trazabilidad.
4. **Logs antes de re-lanzar**: si decides re-lanzar, registra el error primero.
5. **No silenciar excepciones**: nunca `except: pass` o `except Exception: pass`.
