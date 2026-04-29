"""Logging configuration for Task 2."""

from __future__ import annotations

import logging
from pathlib import Path


def get_logger() -> logging.Logger:
    logger = logging.getLogger("task2_data_fetcher")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_path = Path(__file__).with_name("app.log")
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger