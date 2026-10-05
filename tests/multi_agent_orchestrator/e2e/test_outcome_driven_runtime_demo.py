# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# End-to-end validation of outcome driven planning
# and execution.
#
# Responsibilities:
# - Validate planner execution.
# - Validate workflow generation.
# - Validate runtime execution.
# - Validate business outcome production.
#
# Must Not:
# - Mock planner behavior.
# - Mock workflow behavior.
# - Mock runtime execution.
# - Duplicate production logic.

from __future__ import annotations

import pytest

from alhf.multi_agent_orchestrator.agents.build_log_analysis_agent import (
    BuildLogAnalysisAgent,
)
from alhf.multi_agent_orchestrator.agents.repository_inspection_agent import (
    RepositoryInspectionAgent,
)
from alhf.multi_agent_orchestrator.agents.root_cause_report_generation_agent import (
    RootCauseReportGenerationAgent,
)
from alhf.multi_agent_orchestrator.contracts.outcome_request import (
    OutcomeRequest,
)
from alhf.multi_agent_orchestrator.execution.task_executor import (
    TaskExecutor,
)
from alhf.multi_agent_orchestrator.execution.workflow_executor import (
    WorkflowExecutor,
)
from alhf.multi_agent_orchestrator.planner.domain_detector import (
    DomainDetector,
)
from alhf.multi_agent_orchestrator.planner.domain_packs.domain_pack_registry import (
    DomainPackRegistry,
)
from alhf.multi_agent_orchestrator.planner.intent_detector import (
    IntentDetector,
)
from alhf.multi_agent_orchestrator.planner.strategy_selector import (
    StrategySelector,
)
from alhf.multi_agent_orchestrator.planner.workflow_planner import (
    WorkflowPlanner,
)
from alhf.multi_agent_orchestrator.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from alhf.multi_agent_orchestrator.runtime.agent_runtime import (
    AgentRuntime,
)
from alhf.multi_agent_orchestrator.scheduler.in_memory_scheduler import (
    InMemoryScheduler,
)


@pytest.mark.asyncio
async def test_outcome_driven_runtime_workflow() -> None:
    """
    Validate complete outcome driven flow.

    Outcome Request
        ↓
    Planning
        ↓
    Workflow Generation
        ↓
    Runtime Execution
        ↓
    Business Results
    """

    task_repository = (
        InMemoryTaskRepository()
    )

    scheduler = (
        InMemoryScheduler()
    )

    agent_runtime = (
        AgentRuntime()
    )

    await agent_runtime.register_agent(
        RepositoryInspectionAgent(),
    )

    await agent_runtime.register_agent(
        BuildLogAnalysisAgent(),
    )

    await agent_runtime.register_agent(
        RootCauseReportGenerationAgent(),
    )

    workflow_planner = WorkflowPlanner(
        intent_detector=IntentDetector(),
        domain_detector=DomainDetector(),
        strategy_selector=StrategySelector(
            registry=DomainPackRegistry(),
        ),
    )

    outcome_request = OutcomeRequest(
        request_id="outcome_001",
        goal="Analyze repository build failure",
    )

    planning_result = (
        workflow_planner.plan(
            outcome_request,
        )
    )

    assert (
        planning_result.intent
        == "build_failure_analysis"
    )

    assert (
        planning_result.domain
        == "software_engineering"
    )

    assert (
        planning_result.strategy
        == "root_cause_analysis"
    )

    assert (
        len(
            planning_result.workflow_definition.tasks
        )
        == 3
    )

    task_executor = TaskExecutor(
        task_repository=task_repository,
        agent_runtime=agent_runtime,
    )

    workflow_executor = WorkflowExecutor(
        scheduler=scheduler,
        task_executor=task_executor,
    )

    workflow_result = (
        await workflow_executor.execute(
            planning_result.workflow_definition,
        )
    )

    assert (
        workflow_result.final_status
        == "COMPLETED"
    )

    assert (
        len(workflow_result.results)
        == 3
    )

    task_ids = {
        result["task_id"]
        for result in workflow_result.results
    }

    assert (
        "repository_inspection"
        in task_ids
    )

    assert (
        "build_log_analysis"
        in task_ids
    )

    assert (
        "root_cause_report_generation"
        in task_ids
    )
