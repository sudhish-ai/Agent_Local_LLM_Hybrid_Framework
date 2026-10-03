# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the workflow persistence boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Create workflow records.
# - Retrieve workflow records.
# - Update workflow records.
# - Archive workflow records.
#
# Must Not:
# - Execute workflows.
# - Perform scheduling.
# - Execute agents.
# - Perform business logic.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)


class IWorkflowRepository(ABC):
    """Workflow repository interface."""

    @abstractmethod
    async def create(
        self,
        workflow_context: WorkflowContext,
    ) -> None:
        """Create a workflow record."""
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        workflow_id: str,
    ) -> WorkflowContext | None:
        """Retrieve a workflow record."""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        workflow_context: WorkflowContext,
    ) -> None:
        """Update a workflow record."""
        raise NotImplementedError

    @abstractmethod
    async def archive(
        self,
        workflow_id: str,
    ) -> None:
        """Archive a workflow record."""
        raise NotImplementedError
