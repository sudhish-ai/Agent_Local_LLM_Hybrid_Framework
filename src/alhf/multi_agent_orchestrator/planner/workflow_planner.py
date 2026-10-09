# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Planner orchestration component that converts
# customer outcomes into workflow definitions.
#
# Responsibilities:
# - Detect intent.
# - Detect domain.
# - Select strategy.
# - Generate workflow definitions.
# - Produce planning results.
#
# Must Not:
# - Execute workflows.
# - Persist workflows.
# - Manage workflow state.
# - Contain execution orchestration logic.

from alhf.multi_agent_orchestrator.contracts.outcome_request import (
    OutcomeRequest,
)
from alhf.multi_agent_orchestrator.contracts.planning_result import (
    PlanningResult,
)
from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
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

from alhf.capability.capability_runtime import (
    CapabilityRuntime,
)

class WorkflowPlanner:
    """
    V1 deterministic workflow planner.
    """

    def __init__(
            self,
            intent_detector: IntentDetector,
            domain_detector: DomainDetector,
            strategy_selector: StrategySelector,
            capability_runtime: (
                    CapabilityRuntime | None
            ) = None,
    ) -> None:
        self._intent_detector = (
            intent_detector
        )

        self._domain_detector = (
            domain_detector
        )

        self._strategy_selector = (
            strategy_selector
        )

        self._capability_runtime = (
            capability_runtime
        )

    def plan(
            self,
            outcome_request: OutcomeRequest,
    ) -> PlanningResult:
        intent = self._intent_detector.detect(
            outcome_request,
        )

        domain = self._domain_detector.detect(
            intent,
        )

        strategy = self._strategy_selector.select(
            intent,
            domain,
        )

        selected_capabilities: tuple[
            str,
            ...
        ] = ()

        if (
                self._capability_runtime
                is not None
        ):
            selected_capabilities = tuple(
                capability.capability_id
                for capability in (
                    self._capability_runtime
                    .select_capabilities(
                        intent.intent,
                        domain,
                    )
                )
            )

        tasks = self._build_tasks(
            workflow_id=outcome_request.request_id,
            strategy=strategy.strategy,
        )

        workflow = WorkflowDefinition(
            workflow_id=outcome_request.request_id,
            workflow_type=strategy.strategy,
            tasks=tasks,
        )

        return PlanningResult(
            intent=intent.intent,
            domain=domain,
            strategy=strategy.strategy,
            workflow_definition=workflow,
            selected_capabilities=(
                selected_capabilities
            ),
            confidence=1.0,
        )

    def _build_tasks(
        self,
        workflow_id: str,
        strategy: str,
    ) -> list[TaskDefinition]:
        if strategy == "root_cause_analysis":
            return [
                TaskDefinition(
                    task_id="repository_inspection",
                    workflow_id=workflow_id,
                    capability="repository_inspection",
                ),
                TaskDefinition(
                    task_id="build_log_analysis",
                    workflow_id=workflow_id,
                    capability="build_log_analysis",
                    dependencies=[
                        "repository_inspection",
                    ],
                ),
                TaskDefinition(
                    task_id="root_cause_report_generation",
                    workflow_id=workflow_id,
                    capability="root_cause_report_generation",
                    dependencies=[
                        "build_log_analysis",
                    ],
                ),
            ]

        if strategy == "release_note_generation":
            return [
                TaskDefinition(
                    task_id="collect_change_summary",
                    workflow_id=workflow_id,
                    capability="collect_change_summary",
                ),
                TaskDefinition(
                    task_id="release_note_generation",
                    workflow_id=workflow_id,
                    capability="release_note_generation",
                    dependencies=[
                        "collect_change_summary",
                    ],
                ),
                TaskDefinition(
                    task_id="release_note_export",
                    workflow_id=workflow_id,
                    capability="release_note_export",
                    dependencies=[
                        "release_note_generation",
                    ],
                ),
            ]

        if strategy == "risk_based_test_strategy":
            return [
                TaskDefinition(
                    task_id="requirements_analysis",
                    workflow_id=workflow_id,
                    capability="requirements_analysis",
                ),
                TaskDefinition(
                    task_id="risk_identification",
                    workflow_id=workflow_id,
                    capability="risk_identification",
                    dependencies=[
                        "requirements_analysis",
                    ],
                ),
                TaskDefinition(
                    task_id="test_strategy_generation",
                    workflow_id=workflow_id,
                    capability="test_strategy_generation",
                    dependencies=[
                        "risk_identification",
                    ],
                ),
                TaskDefinition(
                    task_id="strategy_artifact_generation",
                    workflow_id=workflow_id,
                    capability="strategy_artifact_generation",
                    dependencies=[
                        "test_strategy_generation",
                    ],
                ),
            ]

        return [
            TaskDefinition(
                task_id="repository_scan",
                workflow_id=workflow_id,
                capability="repository_scan",
            ),
            TaskDefinition(
                task_id="repository_summary_generation",
                workflow_id=workflow_id,
                capability="repository_summary_generation",
                dependencies=[
                    "repository_scan",
                ],
            ),
        ]
