# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validate WorkflowPlanner behavior.
#
# Responsibilities:
# - Validate end-to-end planning flow.
# - Validate workflow generation.
# - Validate planning result creation.
# - Validate strategy propagation.
#
# Must Not:
# - Test execution behavior.
# - Test workflow execution.
# - Test orchestration runtime behavior.

from unittest import TestCase

from alhf.multi_agent_orchestrator.contracts.outcome_request import (
    OutcomeRequest,
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


class TestWorkflowPlanner(TestCase):

    def setUp(
        self,
    ) -> None:
        registry = DomainPackRegistry()

        self.planner = WorkflowPlanner(
            intent_detector=IntentDetector(),
            domain_detector=DomainDetector(),
            strategy_selector=StrategySelector(
                registry,
            ),
        )

    def test_build_failure_workflow(
        self,
    ) -> None:
        request = OutcomeRequest(
            request_id="req-001",
            goal="Analyze repository build failure",
        )

        result = self.planner.plan(
            request,
        )

        self.assertEqual(
            "root_cause_analysis",
            result.workflow_definition.workflow_type,
        )

    def test_release_notes_workflow(
        self,
    ) -> None:
        request = OutcomeRequest(
            request_id="req-002",
            goal="Generate release notes",
        )

        result = self.planner.plan(
            request,
        )

        self.assertEqual(
            "release_note_generation",
            result.workflow_definition.workflow_type,
        )

    def test_test_strategy_workflow(
        self,
    ) -> None:
        request = OutcomeRequest(
            request_id="req-003",
            goal="Create test strategy",
        )

        result = self.planner.plan(
            request,
        )

        self.assertEqual(
            "risk_based_test_strategy",
            result.workflow_definition.workflow_type,
        )

    def test_repository_workflow(
        self,
    ) -> None:
        request = OutcomeRequest(
            request_id="req-004",
            goal="Analyze repository",
        )

        result = self.planner.plan(
            request,
        )

        self.assertEqual(
            "root_cause_analysis",
            result.workflow_definition.workflow_type,
        )

    def test_returns_planning_result(
        self,
    ) -> None:
        request = OutcomeRequest(
            request_id="req-005",
            goal="Analyze repository",
        )

        result = self.planner.plan(
            request,
        )

        self.assertEqual(
            1.0,
            result.confidence,
        )
