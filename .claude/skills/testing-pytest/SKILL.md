---
name: testing-pytest
description: Use this skill whenever the user wants to write, run, debug, or review tests for this project. Triggers include "test", "pytest", "prueba unitaria", "casos de prueba", "fixture", "mock", "cobertura", "10 tests", "test fallando", "AAA pattern", "test de regla de negocio". Each integrante MUST have at least 10 tests including one for their business rule (criterion 6). Apply this skill proactively when reviewing new code without tests.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Testing con Pytest (Criterio 6)

## Requisito del criterio

**Cada integrante debe escribir al menos 10 casos de prueba**, incluyendo obligatoriamente **la prueba de su regla de negocio** del criterio 5.

## Comandos del proyecto

```bash
# Correr todos los tests con salida verbosa
pytest -v --tb=short

# Correr tests de un integrante específico
pytest tests/test_estudiante.py -v

# Cobertura (debe ser instalable: pip install pytest-cov)
pytest --cov=src --cov-report=term-missing

# Generar reporte para el entregable
pytest -v --tb=short > docs/reporte_pruebas.txt
```

## Estructura de tests

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures compartidas
├── test_estudiante.py             # Integrante 1 (10+ tests)
├── test_phq9.py                   # Integrante 2 (10+ tests)
├── test_gad7.py                   # Integrante 3 (10+ tests)
├── test_sesion_seguimiento.py     # Integrante 4 (10+ tests)
├── test_email_service.py          # EmailService + Decorator
└── test_repositorios.py           # Tests transversales (opcional)
```

## Patrón AAA (Arrange-Act-Assert)

Todo test debe seguir esta estructura:

```python
def test_crear_estudiante_con_codigo_valido_lo_persiste(repo_estudiante):
    # Arrange
    datos = {
        "codigo": "EST001",
        "nombre_completo": "María Pérez",
        "edad": 20,
        "semestre": 4,
        "correo": "maria@uni.edu",
        "programa": "Psicología",
    }
    estudiante = Estudiante(**datos)

    # Act
    resultado = repo_estudiante.crear(estudiante)

    # Assert
    assert resultado.codigo == "EST001"
    assert len(repo_estudiante.listar()) == 1
```

## Plantilla de 10 tests por entidad

Cubre estos casos para llegar a 10:

1. **Creación válida** (happy path).
2. **Validación falla**: campo individual inválido (ej. edad < 16).
3. **Validación falla**: otro campo (ej. semestre fuera de rango).
4. **Duplicado**: crear dos veces el mismo código → `DuplicateEntityError`.
5. **Buscar existente**: devuelve la entidad correcta.
6. **Buscar inexistente**: lanza `EntityNotFoundError`.
7. **Actualizar existente**: cambios persisten.
8. **Actualizar inexistente**: lanza `EntityNotFoundError`.
9. **Eliminar existente**: ya no aparece en `listar()`.
10. **REGLA DE NEGOCIO** del integrante (criterio 5, OBLIGATORIO).

Si quieres ir más allá:
- Listar vacío devuelve `[]`.
- Persistencia entre instancias del repositorio (cargar de JSON existente).
- Caracteres especiales / UTF-8 (acentos, ñ).

## Fixtures en `conftest.py`

```python
import json
import pytest
from pathlib import Path
from src.services.estudiante_repository import EstudianteRepository
from src.models.estudiante import Estudiante


@pytest.fixture
def ruta_json_temporal(tmp_path) -> Path:
    """Provee una ruta JSON temporal limpia para cada test."""
    return tmp_path / "test_estudiantes.json"


@pytest.fixture
def repo_estudiante(ruta_json_temporal) -> EstudianteRepository:
    return EstudianteRepository(ruta_json=str(ruta_json_temporal))


@pytest.fixture
def estudiante_valido() -> Estudiante:
    return Estudiante(
        codigo="EST001",
        nombre_completo="Juan García",
        edad=20,
        semestre=4,
        correo="juan@uni.edu",
        programa="Ingeniería",
    )
```

## Test obligatorio de regla de negocio

### Integrante 2 (PHQ-9, riesgo severo)
```python
def test_phq9_puntaje_severo_dispara_alerta_y_email(
    repo_phq9, repo_alerta, email_service_mock
):
    # Arrange: respuestas que sumen ≥ 20
    respuestas = [3, 3, 3, 3, 3, 3, 2, 0, 0]  # suma = 20
    cuestionario = CuestionarioPHQ9(
        codigo_estudiante="EST001",
        respuestas=respuestas,
        fecha_aplicacion=datetime.now(),
    )
    service = PHQ9BusinessService(repo_alerta, email_service_mock)

    # Act
    estado = service.evaluar_riesgo(cuestionario)

    # Assert
    assert estado == EstadoRiesgo.SEVERO
    assert len(repo_alerta.listar()) == 1
    email_service_mock.notificar_riesgo.assert_called_once()
```

## Parametrize para validaciones

Útil para probar múltiples casos inválidos en pocas líneas:

```python
@pytest.mark.parametrize("edad_invalida", [-1, 0, 10, 15])
def test_estudiante_con_edad_invalida_lanza_excepcion(edad_invalida):
    with pytest.raises(EdadInvalidaError):
        Estudiante(
            codigo="EST001",
            nombre_completo="Test",
            edad=edad_invalida,
            semestre=4,
            correo="t@u.edu",
            programa="X",
        )
```

## Reglas

1. **Un test = una assertion conceptual** (puede haber varios `assert` relacionados).
2. **Nombres descriptivos**: `test_<sujeto>_<accion>_<resultado_esperado>`.
3. **NO tests que dependan del orden** de ejecución.
4. **NO escribir/leer archivos reales** — usa `tmp_path` de pytest.
5. **Mockear servicios externos** (EmailService) con `unittest.mock.Mock` o `MagicMock`.
6. **El reporte final** (criterio 6) debe mostrar TODOS los tests pasando: `pytest -v` y capturar la salida completa.

## Antes de entregar

```bash
# Verifica que pasen todos
pytest -v

# Verifica cobertura mínima del 70% sobre src/
pytest --cov=src --cov-report=term-missing

# Genera reporte para el documento entregable
pytest -v --tb=short > docs/reporte_pruebas.txt
```
