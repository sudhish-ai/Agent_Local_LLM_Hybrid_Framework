# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides an in-memory workflow repository implementation
# for Runtime V1.
#
# Responsibilities:
# - Store workflow state.
# - Retrieve workflow state.
# - Update workflow state.
# - Support local execution and testing.
#
# Must Not:
# - Execute workflows.
# - Perform scheduling.
# - Contain business logic.

from __future__ import annotations

from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_workflow_repository import (
    IWorkflowRepository,
)


class InMemoryWorkflowRepository(IWorkflowRepository):
    """In-memory workflow repository."""

    def __init__(self) -> None:
        self._store: dict[str, WorkflowContext] = {}

    async def create(
        self,
        workflow_context: WorkflowContext,
    ) -> None:
        self._store[
            workflow_context.workflow_id
        ] = workflow_context

    async def get(
        self,
        workflow_id: str,
    ) -> WorkflowContext | None:
        return self._store.get(workflow_id)

    async def update(
        self,
        workflow_context: WorkflowContext,
    ) -> None:
        self._store[
            workflow_context.workflow_id
        ] = workflow_context

    async def archive(
        self,
        workflow_id: str,
    ) -> None:
        self._store.pop(workflow_id, None)
