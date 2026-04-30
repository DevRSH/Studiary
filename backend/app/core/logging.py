import logging
import sys
import structlog

def configure_logging(debug: bool = False) -> None:
    """Configura el sistema de logs para la aplicación, compatible con pytest."""
    
    # Procesador custom para evitar fallos con PrintLogger en Pytest
    def add_logger_name_safe(logger, method_name, event_dict):
        if hasattr(logger, "name"):
            event_dict["logger"] = logger.name
        else:
            event_dict["logger"] = "test_logger"
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            add_logger_name_safe, # Usamos la versión segura
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configuración base para que los logs lleguen a stdout según el entorno
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )