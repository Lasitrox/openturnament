import logging.config
import yaml
from pathlib import Path


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


def get_logging_config():
    """Load logging configuration from YAML file."""
    config_path = Path().cwd() / "src" / "logging.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


LOGGING_CONFIG = get_logging_config()


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
