---
name: entity-crud
description: Use this skill whenever the user wants to create, modify, debug, or review CRUD operations for any entity (Estudiante, CuestionarioPHQ9, CuestionarioGAD7, SesionSeguimiento). Triggers include "CRUD", "crear entidad", "guardar en JSON", "repositorio", "persistencia", "validar", "actualizar", "eliminar", "listar", "buscar por", "JSON file". Also use when adding validations to existing entities or designing the repository pattern for JSON persistence. Do NOT use for business rules (use business-rules) or exceptions (use custom-exceptions) — but DO reference how this skill expects them to be raised.
allowed-tools: Read Write Edit Grep
---

# CRUD con Validaciones y Persistencia JSON

## Patrón obligatorio: Repository

Cada entidad CRUD tiene su repositorio en `src/services/<entidad>_repository.py`. Los repositorios encapsulan toda la lectura/escritura del JSON. **Los modelos NUNCA tocan archivos.**

## Estructura de cada entidad

### 1. Modelo (`src/models/<entidad>.py`)

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.exceptions.validation_errors import ValidationError

@dataclass
class Estudiante:
    """Representa un estudiante registrado en la plataforma."""
    codigo: str
    nombre_completo: str
    edad: int
    semestre: int
    correo: str
    programa: str
    fecha_registro: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._validar()

    def _validar(self) -> None:
        if not self.codigo or len(self.codigo) < 4:
            raise ValidationError("El código debe tener al menos 4 caracteres.")
        if self.edad < 16:
            raise ValidationError("La edad mínima permitida es 16 años.")
        if not (1 <= self.semestre <= 12):
            raise ValidationError("El semestre debe estar entre 1 y 12.")
        if "@" not in self.correo or "." not in self.correo:
            raise ValidationError("Formato de correo inválido.")

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre_completo": self.nombre_completo,
            "edad": self.edad,
            "semestre": self.semestre,
            "correo": self.correo,
            "programa": self.programa,
            "fecha_registro": self.fecha_registro.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Estudiante":
        return cls(
            codigo=data["codigo"],
            nombre_completo=data["nombre_completo"],
            edad=data["edad"],
            semestre=data["semestre"],
            correo=data["correo"],
            programa=data["programa"],
            fecha_registro=datetime.fromisoformat(data["fecha_registro"]),
        )
```

### 2. Repositorio (`src/services/estudiante_repository.py`)

```python
import json
from pathlib import Path
from typing import Optional
from src.models.estudiante import Estudiante
from src.exceptions.persistence_errors import (
    EntityNotFoundError,
    DuplicateEntityError,
)


class EstudianteRepository:
    """Persistencia de estudiantes en archivo JSON."""

    def __init__(self, ruta_json: str = "data/estudiantes.json") -> None:
        self._ruta = Path(ruta_json)
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self._ruta.exists():
            self._ruta.write_text("[]", encoding="utf-8")

    def _cargar(self) -> list[dict]:
        with self._ruta.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _guardar(self, registros: list[dict]) -> None:
        with self._ruta.open("w", encoding="utf-8") as f:
            json.dump(registros, f, indent=2, ensure_ascii=False)

    def crear(self, estudiante: Estudiante) -> Estudiante:
        registros = self._cargar()
        if any(r["codigo"] == estudiante.codigo for r in registros):
            raise DuplicateEntityError(
                f"Ya existe un estudiante con código {estudiante.codigo}."
            )
        registros.append(estudiante.to_dict())
        self._guardar(registros)
        return estudiante

    def listar(self) -> list[Estudiante]:
        return [Estudiante.from_dict(r) for r in self._cargar()]

    def buscar_por_codigo(self, codigo: str) -> Estudiante:
        for r in self._cargar():
            if r["codigo"] == codigo:
                return Estudiante.from_dict(r)
        raise EntityNotFoundError(f"No existe estudiante con código {codigo}.")

    def actualizar(self, estudiante: Estudiante) -> Estudiante:
        registros = self._cargar()
        for i, r in enumerate(registros):
            if r["codigo"] == estudiante.codigo:
                registros[i] = estudiante.to_dict()
                self._guardar(registros)
                return estudiante
        raise EntityNotFoundError(
            f"No existe estudiante con código {estudiante.codigo}."
        )

    def eliminar(self, codigo: str) -> None:
        registros = self._cargar()
        nuevos = [r for r in registros if r["codigo"] != codigo]
        if len(nuevos) == len(registros):
            raise EntityNotFoundError(f"No existe estudiante con código {codigo}.")
        self._guardar(nuevos)
```

## Validaciones por entidad (criterio 3)

### Estudiante
- `codigo`: no vacío, longitud ≥ 4, único en el sistema.
- `edad`: entero, ≥ 16.
- `semestre`: entero, entre 1 y 12.
- `correo`: contiene `@` y `.`.
- `nombre_completo`: no vacío, mínimo 2 palabras.

### CuestionarioPHQ9
- 9 respuestas obligatorias, cada una entre 0 y 3.
- `codigo_estudiante` debe existir en el repositorio de estudiantes.
- `fecha_aplicacion` no puede ser futura.

### CuestionarioGAD7
- 7 respuestas obligatorias, cada una entre 0 y 3.
- Mismas reglas de estudiante y fecha que PHQ-9.

### SesionSeguimiento
- `fecha_hora` entre 8:00 y 18:00.
- `duracion_minutos` entre 30 y 120.
- `codigo_estudiante` y `id_psicologo` deben existir.

## Reglas universales del CRUD

1. **Crear**: valida en el modelo + repositorio chequea duplicados.
2. **Leer**: si no existe, lanza `EntityNotFoundError`.
3. **Actualizar**: valida en el modelo + repositorio chequea existencia.
4. **Eliminar**: lanza `EntityNotFoundError` si no existe.
5. **JSON**: siempre con `indent=2` y `ensure_ascii=False`.
6. **Encoding**: siempre `utf-8` explícito.

## Controlador (`src/controllers/<entidad>_controller.py`)

El controlador NO repite validaciones del modelo. Solo:
- Recibe datos crudos de la vista.
- Construye el modelo (esto dispara validaciones).
- Llama al repositorio (envuelto por el EmailService decorado).
- Captura excepciones y las retorna como resultado para la vista.

```python
class EstudianteController:
    def __init__(self, repo, email_service):
        self._repo = repo
        self._email = email_service

    def crear(self, datos: dict) -> tuple[bool, str]:
        try:
            estudiante = Estudiante(**datos)
            self._repo.crear(estudiante)
            self._email.notificar_creacion(estudiante)
            return True, f"Estudiante {estudiante.codigo} creado."
        except (ValidationError, DuplicateEntityError) as e:
            return False, str(e)
```
