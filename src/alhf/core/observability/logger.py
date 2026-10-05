# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides ALHF-wide structured logging.
#
# Responsibilities:
# - Standardize logging.
# - Provide reusable observability foundation.
# - Support correlation and tracing.
# - Write logs to console and file.
#
# Must Not:
# - Contain business logic.
# - Contain orchestration logic.

from __future__ import annotations

import logging
from pathlib import Path


class ALHFLogger:
    """ALHF structured logger."""

    _LOG_DIRECTORY = Path("logs")
    _LOG_FILE = _LOG_DIRECTORY / "alhf.log"

    def __init__(
        self,
        component: str,
    ) -> None:
        self._logger = logging.getLogger(
            component,
        )

        self._logger.setLevel(
            logging.INFO,
        )

        if not self._logger.handlers:
            self._LOG_DIRECTORY.mkdir(
                parents=True,
                exist_ok=True,
            )

            formatter = logging.Formatter(
                (
                    "%(asctime)s | "
                    "%(name)s | "
                    "%(levelname)s | "
                    "%(message)s"
                )
            )

            console_handler = logging.StreamHandler()

            console_handler.setFormatter(
                formatter,
            )

            file_handler = logging.FileHandler(
                self._LOG_FILE,
                encoding="utf-8",
            )

            file_handler.setFormatter(
                formatter,
            )

            self._logger.addHandler(
                console_handler,
            )

            self._logger.addHandler(
                file_handler,
            )

            self._logger.propagate = False

    def info(
        self,
        message: str,
    ) -> None:
        self._logger.info(
            message,
        )

    def warning(
        self,
        message: str,
    ) -> None:
        self._logger.warning(
            message,
        )

    def error(
        self,
        message: str,
    ) -> None:
        self._logger.error(
            message,
        )
