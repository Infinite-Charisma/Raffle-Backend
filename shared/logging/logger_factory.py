import logging
from .logger_config import LoggerConfig
from .cloud_json_renderer import CloudJsonRenderer
import structlog


def configure_logger(config: LoggerConfig):
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            *([
                structlog.processors.CallsiteParameterAdder(),
                CloudJsonRenderer()
            ] if config.use_json_logs else [
                structlog.dev.ConsoleRenderer()
            ])
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )
