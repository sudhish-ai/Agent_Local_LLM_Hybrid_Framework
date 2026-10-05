# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for TaskContext.
#
# Responsibilities:
# - Validate TaskContext contract.
# - Validate default values.
# - Validate custom values.
# - Protect contract stability.
#
# Must Not:
# - Contain execution logic.
# - Contain scheduling logic.
# - Contain persistence logic.

import unittest

from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)


class TestTaskContext(unittest.TestCase):

    def test_required_fields(self) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
        )

        self.assertEqual(
            context.task_id,
            "task-1",
        )

        self.assertEqual(
            context.workflow_id,
            "wf-1",
        )

        self.assertEqual(
            context.capability,
            "analysis",
        )

    def test_default_attempt_number(
        self,
    ) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
        )

        self.assertEqual(
            context.attempt_number,
            1,
        )

    def test_custom_attempt_number(
        self,
    ) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
            attempt_number=3,
        )

        self.assertEqual(
            context.attempt_number,
            3,
        )

    def test_default_assigned_agent(
        self,
    ) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
        )

        self.assertIsNone(
            context.assigned_agent,
        )

    def test_default_input_context(
        self,
    ) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
        )

        self.assertEqual(
            context.input_context,
            {},
        )

    def test_default_execution_constraints(
            self,
    ) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
        )

        self.assertEqual(
            context.execution_constraints,
            {},
        )

    def test_default_metadata(
            self,
    ) -> None:
        context = TaskContext(
            task_id="task-1",
            workflow_id="wf-1",
            capability="analysis",
        )

        self.assertEqual(
            context.metadata,
            {},
        )

