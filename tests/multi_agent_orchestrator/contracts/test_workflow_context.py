# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for WorkflowContext.
#
# Responsibilities:
# - Validate WorkflowContext contract.
# - Validate default values.
# - Validate custom values.
# - Protect contract stability.

import unittest

from datetime import datetime
from datetime import UTC

from alhf.multi_agent_orchestrator.contracts.workflow_context import (
    WorkflowContext,
)
from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)


class TestWorkflowContext(
    unittest.TestCase,
):

    def test_required_fields(self) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        self.assertEqual(
            context.workflow_id,
            "wf-1",
        )

        self.assertEqual(
            context.workflow_type,
            "analysis",
        )

        self.assertEqual(
            context.workflow_state,
            WorkflowExecutionStatus.READY,
        )

    def test_default_execution_start_time(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        self.assertIsNone(
            context.execution_start_time_utc,
        )

    def test_custom_execution_start_time(
        self,
    ) -> None:
        start_time = datetime.now(
            UTC,
        )

        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
            execution_start_time_utc=start_time,
        )

        self.assertEqual(
            context.execution_start_time_utc,
            start_time,
        )

    def test_default_policy_context(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        self.assertEqual(
            context.policy_context,
            {},
        )

    def test_default_execution_context(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        self.assertEqual(
            context.execution_context,
            {},
        )

    def test_default_audit_context(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        self.assertEqual(
            context.audit_context,
            {},
        )

    def test_default_metadata(
        self,
    ) -> None:
        context = WorkflowContext(
            workflow_id="wf-1",
            workflow_type="analysis",
            workflow_state=WorkflowExecutionStatus.READY,
        )

        self.assertEqual(
            context.metadata,
            {},
        )

    def test_custom_values(
        self,
    ) -> None:
        start_time = datetime.now(
            UTC,
        )

        context = WorkflowContext(
            workflow_id="wf-99",
            workflow_type="coding",
            workflow_state=WorkflowExecutionStatus.RUNNING,
            execution_start_time_utc=start_time,
            policy_context={
                "approval": True,
            },
            execution_context={
                "executor": "agent",
            },
            audit_context={
                "trace_id": "123",
            },
            metadata={
                "priority": "high",
            },
        )

        self.assertEqual(
            context.workflow_id,
            "wf-99",
        )

        self.assertEqual(
            context.workflow_type,
            "coding",
        )

        self.assertEqual(
            context.workflow_state,
            WorkflowExecutionStatus.RUNNING,
        )

        self.assertEqual(
            context.execution_start_time_utc,
            start_time,
        )

        self.assertEqual(
            context.policy_context,
            {"approval": True},
        )

        self.assertEqual(
            context.execution_context,
            {"executor": "agent"},
        )

        self.assertEqual(
            context.audit_context,
            {"trace_id": "123"},
        )

        self.assertEqual(
            context.metadata,
            {"priority": "high"},
        )


if __name__ == "__main__":
    unittest.main()
