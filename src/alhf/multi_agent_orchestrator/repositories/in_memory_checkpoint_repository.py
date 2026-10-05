# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides an in-memory checkpoint repository
# implementation for Runtime V1.
#
# Responsibilities:
# - Store workflow checkpoints.
# - Retrieve workflow checkpoints.
# - Delete checkpoints.
#
# Must Not:
# - Execute workflows.
# - Execute recovery logic.
# - Perform scheduling.
# - Contain business logic.

from __future__ import annotations

from typing import Any

from alhf.multi_agent_orchestrator.interfaces.i_checkpoint_repository import (
    ICheckpointRepository,
)


class InMemoryCheckpointRepository(
    ICheckpointRepository,
):
    """In-memory checkpoint repository."""

    def __init__(self) -> None:
        self._checkpoints: dict[
            str,
            dict[str, Any],
        ] = {}

    async def save(
        self,
        workflow_id: str,
        checkpoint_data: dict[str, Any],
    ) -> None:
        self._checkpoints[
            workflow_id
        ] = checkpoint_data

    async def load(
        self,
        workflow_id: str,
    ) -> dict[str, Any] | None:
        return self._checkpoints.get(
            workflow_id
        )

    async def delete(
        self,
        workflow_id: str,
    ) -> None:
        self._checkpoints.pop(
            workflow_id,
            None,
        )

