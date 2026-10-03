# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)


class IWorkflowPlanner(ABC):
    """Workflow planning interface."""

    @abstractmethod
    async def build_workflow(
        self,
        intent_result: object,
    ) -> WorkflowDefinition:
        """Build a workflow definition from an intent result."""
        raise NotImplementedError
