# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.core.result import PipelineResult
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_result import (
    WorkflowResult,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)


class IWorkflowEngine(ABC):
    """Public workflow orchestration interface."""

    @abstractmethod
    async def start_workflow(
        self,
        workflow_definition: WorkflowDefinition,
    ) -> PipelineResult[WorkflowResult]:
        """Start execution of a workflow."""
        raise NotImplementedError

    @abstractmethod
    async def recover_workflow(
            self,
            workflow_id: str,
    ) -> PipelineResult[WorkflowResult]:
        """Recover a workflow from checkpoint state."""
        raise NotImplementedError

    @abstractmethod
    async def get_workflow_status(
        self,
        workflow_id: str,
    ) -> WorkflowExecutionStatus:
        """Return current workflow execution status."""
        raise NotImplementedError
