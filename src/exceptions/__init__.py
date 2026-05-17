from src.exceptions.base import PlataformaError
from src.exceptions.validation_errors import (
    ValidationError,
    CodigoInvalidoError,
    EdadInvalidaError,
    SemestreInvalidoError,
    CorreoInvalidoError,
    PuntajeInvalidoError,
    FechaInvalidaError,
)
from src.exceptions.persistence_errors import (
    PersistenceError,
    EntityNotFoundError,
    DuplicateEntityError,
    ArchivoCorruptoError,
)
from src.exceptions.business_errors import (
    BusinessRuleError,
    ReaplicacionTempranaError,
    RiesgoSeveroError,
    HorarioFueraDeRangoError,
    SesionDuplicadaError,
)
from src.exceptions.notification_errors import (
    NotificacionError,
    EmailEnvioError,
)
