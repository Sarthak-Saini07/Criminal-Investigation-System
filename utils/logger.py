"""
Logger module for CICMS.
Configures file and console logging, and provides utilities for execution timing.
"""

import logging
import os
import time
import configparser
from pathlib import Path
from typing import Callable, Any

# Ensure logs directory exists
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "cicms.log"

def setup_logger(name: str = "CICMS") -> logging.Logger:
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "[%(levelname)s] [%(name)s] %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Execution of {func.__name__} took {elapsed:.2f} ms")
        return result
    return wrapper
