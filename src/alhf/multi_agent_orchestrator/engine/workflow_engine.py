# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the Runtime V1 workflow execution engine.
#
# Responsibilities:
# - Start workflow execution.
# - Recover workflow execution.
# - Expose workflow status.
# - Coordinate workflow lifecycle.
#
# Must Not:
# - Execute agents directly.
# - Perform scheduling.
# - Contain persistence implementation details.
# - Contain retry logic.

from __future__ import annotations

from alhf.core.result import PipelineResult
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_result import (
    WorkflowResult,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)
from alhf.multi_agent_orchestrator.interfaces.i_workflow_engine import (
    IWorkflowEngine,
)
from alhf.multi_agent_orchestrator.interfaces.i_workflow_repository import (
    IWorkflowRepository,
)

from alhf.multi_agent_orchestrator.execution.workflow_executor import (
    WorkflowExecutor,
)

class WorkflowEngine(IWorkflowEngine):
    """Runtime V1 workflow engine."""

    def __init__(
            self,
            workflow_repository: IWorkflowRepository,
            workflow_executor: WorkflowExecutor,
    ) -> None:
        self._workflow_repository = workflow_repository
        self._workflow_executor = workflow_executor

    async def start_workflow(
            self,
            workflow_definition: WorkflowDefinition,
    ) -> PipelineResult:
        """Start execution of a workflow."""

        workflow_context = WorkflowContext(
            workflow_id=workflow_definition.workflow_id,
            workflow_type=workflow_definition.workflow_type,
            workflow_state=WorkflowExecutionStatus.CREATED,
            metadata=dict(
                workflow_definition.metadata,
            ),
        )

        await self._workflow_repository.create(
            workflow_context,
        )

        try:
            workflow_context.workflow_state = (
                WorkflowExecutionStatus.RUNNING
            )

            await self._workflow_repository.update(
                workflow_context,
            )

            workflow_result = (
                await self._workflow_executor.execute(
                    workflow_definition,
                )
            )

            workflow_context.workflow_state = (
                WorkflowExecutionStatus.COMPLETED
            )

            await self._workflow_repository.update(
                workflow_context,
            )

            return PipelineResult.success(
                workflow_result,
            )

        except Exception as ex:
            workflow_context.workflow_state = (
                WorkflowExecutionStatus.FAILED
            )

            await self._workflow_repository.update(
                workflow_context,
            )

            return PipelineResult.failed_non_retryable(
                error_code="WORKFLOW_EXECUTION_FAILED",
                error_message=str(ex),
            )

    async def recover_workflow(
        self,
        workflow_id: str,
    ) -> PipelineResult:
        """Recover a workflow from checkpoint state."""
        workflow_context = await self._workflow_repository.get(
            workflow_id,
        )
        if workflow_context is None:
            return PipelineResult.failed_non_retryable(
                error_code="WORKFLOW_NOT_FOUND",
                error_message=f"Workflow not found: {workflow_id}",
            )
        workflow_result = WorkflowResult(
            workflow_id=workflow_context.workflow_id,
            workflow_type=workflow_context.workflow_type,
            final_status=workflow_context.workflow_state.value,
            metadata=workflow_context.metadata,
        )
        return PipelineResult.success(
            workflow_result,
        )

    async def get_workflow_status(
        self,
        workflow_id: str,
    ) -> WorkflowExecutionStatus:
        """Return current workflow execution status."""
        workflow_context = await self._workflow_repository.get(
            workflow_id,
        )
        if workflow_context is None:
            return WorkflowExecutionStatus.FAILED
        return workflow_context.workflow_state
