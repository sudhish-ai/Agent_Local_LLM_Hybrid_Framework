# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides correlation identifiers for ALHF execution
# tracking and observability.
#
# Responsibilities:
# - Generate correlation ids.
# - Standardize execution tracking.
# - Support workflow tracing.
# - Support observability foundations.
#
# Must Not:
# - Contain business logic.
# - Contain orchestration logic.

from __future__ import annotations

import uuid


class CorrelationId:
    """Correlation identifier utility."""

    @staticmethod
    def create() -> str:
        """Generate correlation identifier."""

        return str(
            uuid.uuid4(),
        )
