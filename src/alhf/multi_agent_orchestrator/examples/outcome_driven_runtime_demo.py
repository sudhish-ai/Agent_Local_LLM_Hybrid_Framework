# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Demonstrates end-to-end outcome driven workflow
# planning and execution.
#
# Responsibilities:
# - Demonstrate Outcome -> Planning -> Execution.
# - Demonstrate workflow generation.
# - Demonstrate runtime agent resolution.
# - Demonstrate business outcome generation.
#
# Must Not:
# - Act as production code.
# - Contain orchestration logic.
# - Duplicate runtime responsibilities.

from __future__ import annotations

import asyncio

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

from alhf.multi_agent_orchestrator.planner.domain_packs.domain_pack_registry import (
    DomainPackRegistry,
)

def print_banner() -> None:
    print(
        "\n"
        "====================================================\n"
        "ALHF Outcome Driven Runtime Demo\n"
        "===================================================="
    )


async def main() -> None:
    print_banner()

    print(
        "\n[STEP 1] Building Runtime Components..."
    )

    task_repository = (
        InMemoryTaskRepository()
    )

    scheduler = (
        InMemoryScheduler()
    )

    agent_runtime = (
        AgentRuntime()
    )

    print(
        "[SUCCESS] Runtime components initialized."
    )

    print(
        "\n[STEP 2] Registering Outcome Agents..."
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

    print(
        "[SUCCESS] Outcome agents registered."
    )

    print(
        "\n[STEP 3] Building Planner..."
    )

    workflow_planner = WorkflowPlanner(
        intent_detector=IntentDetector(),
        domain_detector=DomainDetector(),
        strategy_selector=StrategySelector(
            registry=DomainPackRegistry(),
        ),
    )

    print(
        "[SUCCESS] Planner created."
    )

    print(
        "\n[STEP 4] Creating Customer Outcome..."
    )

    outcome_request = OutcomeRequest(
        request_id="outcome_001",
        goal="Analyze repository build failure",
    )

    print(
        f"Goal: {outcome_request.goal}"
    )

    planning_result = (
        workflow_planner.plan(
            outcome_request,
        )
    )

    print(
        "\n=== PLANNING RESULT ==="
    )

    print(
        f"Intent   : {planning_result.intent}"
    )

    print(
        f"Domain   : {planning_result.domain}"
    )

    print(
        f"Strategy : {planning_result.strategy}"
    )

    print(
        "\nGenerated Workflow:"
    )

    for task in (
        planning_result
        .workflow_definition
        .tasks
    ):
        print(
            f" - {task.task_id}"
            f" [{task.capability}]"
        )

    print(
        "\n[STEP 5] Building Executors..."
    )

    task_executor = TaskExecutor(
        task_repository=task_repository,
        agent_runtime=agent_runtime,
    )

    workflow_executor = WorkflowExecutor(
        scheduler=scheduler,
        task_executor=task_executor,
    )

    print(
        "[SUCCESS] Executors initialized."
    )

    print(
        "\n[STEP 6] Executing Workflow..."
    )

    workflow_result = (
        await workflow_executor.execute(
            planning_result.workflow_definition,
        )
    )

    print(
        "\n=== EXECUTION RESULT ==="
    )

    print(
        f"Workflow Id   : "
        f"{workflow_result.workflow_id}"
    )

    print(
        f"Workflow Type : "
        f"{workflow_result.workflow_type}"
    )

    print(
        f"Status        : "
        f"{workflow_result.final_status}"
    )

    print(
        "\n=== BUSINESS OUTCOME ==="
    )

    for result in workflow_result.results:
        print(
            f"\nTask : {result['task_id']}"
        )

        print(
            f"Result : {result['result']}"
        )

    print(
        "\n===================================================="
    )

    print(
        "Outcome Successfully Achieved"
    )

    print(
        "===================================================="
    )


if __name__ == "__main__":
    asyncio.run(main())
