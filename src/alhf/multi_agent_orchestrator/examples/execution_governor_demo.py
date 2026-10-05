# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Demonstrates end-to-end execution governor behavior.
#
# Responsibilities:
# - Show workflow governance decisions.
# - Demonstrate evaluator chaining.
# - Act as executable documentation.
#
# Must Not:
# - Execute real workflows.
# - Execute real tasks.
# - Mutate runtime state.

from datetime import UTC
from datetime import datetime
from datetime import timedelta

from alhf.multi_agent_orchestrator.contracts.governor_policy import (
    GovernorPolicy,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)
from alhf.multi_agent_orchestrator.execution_governor.retry_evaluator import (
    RetryEvaluator,
)
from alhf.multi_agent_orchestrator.execution_governor.timeout_evaluator import (
    TimeoutEvaluator,
)
from alhf.multi_agent_orchestrator.execution_governor.workflow_execution_governor import (
    WorkflowExecutionGovernor,
)
from alhf.multi_agent_orchestrator.execution_governor.workflow_state_evaluator import (
    WorkflowStateEvaluator,
)


def print_banner() -> None:
    print(
        "\n"
        "========================================\n"
        "Execution Governor V1 Demo\n"
        "========================================"
    )


def scenario_ready_workflow() -> None:
    governor = WorkflowExecutionGovernor(
        evaluators=[
            WorkflowStateEvaluator(),
        ],
    )

    context = WorkflowContext(
        workflow_id="wf-ready",
        workflow_type="document-analysis",
        workflow_state=WorkflowExecutionStatus.READY,
    )

    decision = governor.pre_workflow_check(
        context
    )

    print(
        "\n[Scenario 1] READY Workflow"
    )
    print(
        f"Decision: {decision.action.value}"
    )


def scenario_failed_workflow() -> None:
    governor = WorkflowExecutionGovernor(
        evaluators=[
            WorkflowStateEvaluator(),
        ],
    )

    context = WorkflowContext(
        workflow_id="wf-failed",
        workflow_type="document-analysis",
        workflow_state=WorkflowExecutionStatus.FAILED,
    )

    decision = governor.pre_workflow_check(
        context
    )

    print(
        "\n[Scenario 2] FAILED Workflow"
    )
    print(
        f"Decision: {decision.action.value}"
    )


def scenario_retry_limit_exceeded() -> None:
    policy = GovernorPolicy(
        max_task_retries=3,
        escalation_enabled=True,
    )

    governor = WorkflowExecutionGovernor(
        evaluators=[
            RetryEvaluator(
                policy,
            ),
        ],
    )

    context = TaskContext(
        task_id="task-1",
        workflow_id="wf-retry",
        capability="analysis",
        attempt_number=5,
    )

    decision = governor.pre_task_check(
        context
    )

    print(
        "\n[Scenario 3] Retry Limit Exceeded"
    )
    print(
        f"Decision: {decision.action.value}"
    )

def scenario_timeout_exceeded() -> None:
    policy = GovernorPolicy(
        workflow_timeout_seconds=60,
        escalation_enabled=True,
    )

    governor = WorkflowExecutionGovernor(
        evaluators=[
            TimeoutEvaluator(
                policy,
            ),
        ],
    )

    context = WorkflowContext(
        workflow_id="wf-timeout",
        workflow_type="document-analysis",
        workflow_state=WorkflowExecutionStatus.RUNNING,
        execution_start_time_utc=(
            datetime.now(UTC)
            - timedelta(hours=2)
        ),
    )

    decision = governor.pre_workflow_check(
        context
    )

    print(
        "\n[Scenario 4] Timeout Exceeded"
    )
    print(
        f"Decision: {decision.action.value}"
    )


def scenario_full_governor_chain() -> None:
    policy = GovernorPolicy(
        max_task_retries=3,
        workflow_timeout_seconds=3600,
        escalation_enabled=True,
    )

    governor = WorkflowExecutionGovernor(
        evaluators=[
            WorkflowStateEvaluator(),
            TimeoutEvaluator(
                policy,
            ),
        ],
    )

    context = WorkflowContext(
        workflow_id="wf-chain",
        workflow_type="document-analysis",
        workflow_state=WorkflowExecutionStatus.READY,
        execution_start_time_utc=(
            datetime.now(UTC)
            - timedelta(minutes=5)
        ),
    )

    decision = governor.pre_workflow_check(
        context
    )

    print(
        "\n[Scenario 5] Full Governor Chain"
    )
    print(
        f"Decision: {decision.action.value}"
    )


def main() -> None:
    print_banner()

    scenario_ready_workflow()

    scenario_failed_workflow()

    scenario_retry_limit_exceeded()

    scenario_timeout_exceeded()

    scenario_full_governor_chain()

    print(
        "\n========================================"
    )
    print(
        "Demo Completed"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()
