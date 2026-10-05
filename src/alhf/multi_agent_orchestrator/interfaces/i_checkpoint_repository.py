# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the checkpoint persistence boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Persist workflow checkpoints.
# - Retrieve workflow checkpoints.
# - Delete obsolete checkpoints.
#
# Must Not:
# - Execute workflows.
# - Execute recovery logic.
# - Perform scheduling.
# - Contain business logic.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class ICheckpointRepository(ABC):
    """Checkpoint repository interface."""

    @abstractmethod
    async def save(
        self,
        workflow_id: str,
        checkpoint_data: dict[str, Any],
    ) -> None:
        """Persist a workflow checkpoint."""
        raise NotImplementedError

    @abstractmethod
    async def load(
        self,
        workflow_id: str,
    ) -> dict[str, Any] | None:
        """Load a workflow checkpoint."""
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        workflow_id: str,
    ) -> None:
        """Delete a workflow checkpoint."""
        raise NotImplementedError
