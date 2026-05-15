---
name: email-decorator
description: Use this skill whenever the user works on EmailService, notification logic, GoF Decorator pattern, sending emails on insert/update operations, or wraps any repository with notification behavior. Triggers include "EmailService", "decorator", "notificacion", "correo", "enviar email", "SMTP", "GoF", "decorador", "envolver repositorio", "notificar al crear". This pattern is criterion 7 — implementing it as inheritance or as a simple call is WRONG. Must be the GoF Decorator pattern.
allowed-tools: Read Write Edit Grep
---

# EmailService con Patrón Decorator GoF (Criterio 7)

## Lo que el criterio EXIGE

> "Implementar un servicio de notificación de correo electrónico llamado `EmailService` que permita enviar un mensaje de notificación cuando se realicen operaciones de inserción o modificación de los datos de la entidad. **Para esta funcionalidad usar el patrón GoF Decorator.**"

## Errores comunes que el profesor SÍ revisa

❌ **MAL — usar herencia**:
```python
class EstudianteRepositoryConEmail(EstudianteRepository):
    def crear(self, est):
        super().crear(est)
        enviar_email(...)
```

❌ **MAL — llamar al email desde el controlador**:
```python
def crear(self, datos):
    repo.crear(estudiante)
    email_service.enviar(...)  # Esto NO es Decorator
```

✅ **BIEN — Decorator GoF auténtico**: una clase decoradora envuelve al repositorio implementando la **misma interfaz**, delega la operación al objeto envuelto, y agrega comportamiento de notificación.

## Estructura del patrón

```
                ┌─────────────────────┐
                │  IRepository (ABC)  │  ← Interfaz común
                │  + crear()          │
                │  + actualizar()     │
                └─────────────────────┘
                    ▲              ▲
                    │              │
        ┌───────────┴──┐      ┌────┴───────────────────────┐
        │ Repository   │      │ NotificacionDecorator      │
        │ (Concrete)   │◄─────┤ - _repo: IRepository       │
        │              │      │ - _email: EmailService     │
        └──────────────┘      └────────────────────────────┘
```

## Implementación

### 1. Interfaz común (`src/services/interfaces.py`)

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Contrato común para todos los repositorios. Necesario para Decorator GoF."""

    @abstractmethod
    def crear(self, entidad: T) -> T: ...

    @abstractmethod
    def actualizar(self, entidad: T) -> T: ...

    @abstractmethod
    def eliminar(self, identificador: str) -> None: ...

    @abstractmethod
    def listar(self) -> list[T]: ...

    @abstractmethod
    def buscar_por_codigo(self, identificador: str) -> T: ...
```

Los repositorios concretos (`EstudianteRepository`, `PHQ9Repository`, etc.) deben **heredar de `IRepository`**.

### 2. EmailService (`src/services/email_service.py`)

```python
import logging
import smtplib
from email.message import EmailMessage
from src.exceptions.notification_errors import EmailEnvioError

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio responsable de enviar correos de notificación."""

    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        remitente: str = "noreply@plataforma.edu",
        password: str = "",
        modo_simulacion: bool = True,
    ) -> None:
        self._host = smtp_host
        self._port = smtp_port
        self._remitente = remitente
        self._password = password
        self._modo_simulacion = modo_simulacion

    def enviar(self, destinatario: str, asunto: str, cuerpo: str) -> None:
        if self._modo_simulacion:
            logger.info(f"[SIMULADO] Email a {destinatario} | {asunto}")
            print(f"[EMAIL SIMULADO] Para: {destinatario}\nAsunto: {asunto}\n{cuerpo}\n")
            return

        try:
            msg = EmailMessage()
            msg["From"] = self._remitente
            msg["To"] = destinatario
            msg["Subject"] = asunto
            msg.set_content(cuerpo)

            with smtplib.SMTP(self._host, self._port) as smtp:
                smtp.starttls()
                smtp.login(self._remitente, self._password)
                smtp.send_message(msg)
        except Exception as e:
            raise EmailEnvioError(f"Fallo al enviar correo: {e}") from e
```

**Nota**: el `modo_simulacion=True` por defecto evita necesitar credenciales reales para entregar. Para la demo se imprime en consola.

### 3. Decorator (`src/services/notificacion_decorator.py`)

```python
from typing import TypeVar, Generic
from src.services.interfaces import IRepository
from src.services.email_service import EmailService

T = TypeVar("T")


class NotificacionDecorator(IRepository[T], Generic[T]):
    """
    Decorator GoF que añade notificación por email a cualquier IRepository.

    Envuelve un repositorio existente y, tras cada operación de inserción
    o actualización, dispara un correo vía EmailService.
    """

    def __init__(
        self,
        repositorio: IRepository[T],
        email_service: EmailService,
        destinatario_default: str,
        nombre_entidad: str,
    ) -> None:
        self._repo = repositorio
        self._email = email_service
        self._destinatario = destinatario_default
        self._nombre_entidad = nombre_entidad

    def crear(self, entidad: T) -> T:
        resultado = self._repo.crear(entidad)
        self._notificar("creación", resultado)
        return resultado

    def actualizar(self, entidad: T) -> T:
        resultado = self._repo.actualizar(entidad)
        self._notificar("modificación", resultado)
        return resultado

    def eliminar(self, identificador: str) -> None:
        # No se notifica eliminación según criterio (solo insert/update),
        # pero delegamos igual.
        self._repo.eliminar(identificador)

    def listar(self) -> list[T]:
        return self._repo.listar()

    def buscar_por_codigo(self, identificador: str) -> T:
        return self._repo.buscar_por_codigo(identificador)

    def _notificar(self, operacion: str, entidad: T) -> None:
        asunto = f"[Plataforma Psicoeducativa] {operacion.capitalize()} de {self._nombre_entidad}"
        cuerpo = (
            f"Se realizó una operación de {operacion} sobre la entidad "
            f"'{self._nombre_entidad}'.\n\n"
            f"Datos:\n{entidad}\n"
        )
        self._email.enviar(self._destinatario, asunto, cuerpo)
```

### 4. Uso en el wiring (en `main.py`)

```python
from src.services.email_service import EmailService
from src.services.estudiante_repository import EstudianteRepository
from src.services.notificacion_decorator import NotificacionDecorator

# Cableado: el controlador NUNCA sabe si está usando el decorator o no.
email = EmailService(modo_simulacion=True)
repo_base = EstudianteRepository()
repo_notificado = NotificacionDecorator(
    repositorio=repo_base,
    email_service=email,
    destinatario_default="bienestar@uni.edu",
    nombre_entidad="Estudiante",
)
controller = EstudianteController(repo=repo_notificado, email_service=email)
```

**Esto es lo que hace que sea Decorator GoF**: el `EstudianteController` recibe `IRepository`, sin saber si es el repositorio plano o el decorado.

## Cómo defenderlo ante el profesor

Si te preguntan **"¿dónde está el Decorator?"**, debes señalar:

1. La interfaz común `IRepository`.
2. La clase concreta `EstudianteRepository` que la implementa.
3. La clase `NotificacionDecorator` que **también la implementa** y **además** recibe una instancia de `IRepository` en su constructor.
4. El wiring en `main.py` donde se envuelve.

Y explicarlo así:
> "El decorador `NotificacionDecorator` extiende el comportamiento del repositorio sin modificarlo, manteniendo la misma interfaz `IRepository`. Esto permite que cualquier consumidor del repositorio reciba transparentemente la funcionalidad de notificación. Podemos apilar otros decoradores (auditoría, caché) sin tocar el código existente, lo cual es el espíritu del patrón GoF Decorator y respeta el principio Abierto/Cerrado."

## Test del Decorator (forma parte del criterio 6)

```python
def test_decorator_dispara_email_al_crear():
    email_mock = Mock(spec=EmailService)
    repo_base = EstudianteRepository(ruta_json="tmp.json")
    repo_notificado = NotificacionDecorator(
        repositorio=repo_base,
        email_service=email_mock,
        destinatario_default="bienestar@uni.edu",
        nombre_entidad="Estudiante",
    )
    estudiante = Estudiante(...)

    repo_notificado.crear(estudiante)

    email_mock.enviar.assert_called_once()
    args, _ = email_mock.enviar.call_args
    assert "creación" in args[1].lower()
```
