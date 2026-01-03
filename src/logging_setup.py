import logging.config


class ColorFormatter(logging.Formatter):
    """Custom logging formatter to support colored output."""

    COLORS = {
        "DEBUG": "\033[97m",     # White
        "INFO": "\033[97m",      # White
        "WARNING": "\033[97m",   # White
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[31m",  # Red
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        log_fmt = f"{color}%(asctime)s - %(name)s - %(levelname)s - %(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": ColorFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
