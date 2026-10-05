# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the result aggregation boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Aggregate task results.
# - Produce workflow results.
# - Build execution summaries.
#
# Must Not:
# - Execute tasks.
# - Execute agents.
# - Persist data.
# - Modify workflow state.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.task_result import (
    TaskResult,
)
from alhf.multi_agent_orchestrator.contracts.workflow_result import (
    WorkflowResult,
)


class IResultAggregator(ABC):
    """Result aggregation interface."""

    @abstractmethod
    async def aggregate(
        self,
        workflow_id: str,
        task_results: list[TaskResult],
    ) -> WorkflowResult:
        """Aggregate task results into a workflow result."""
        raise NotImplementedError
