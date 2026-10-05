# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for IExecutionGovernor.
#
# Responsibilities:
# - Validate interface structure.
# - Validate abstract methods.
# - Prevent accidental contract changes.
#
# Must Not:
# - Contain business logic.
# - Contain execution logic.
# - Contain workflow logic.

import unittest

from alhf.multi_agent_orchestrator.interfaces.i_execution_governor import (
    IExecutionGovernor,
)


class TestExecutionGovernorContract(
    unittest.TestCase
):
    """
    Tests for IExecutionGovernor.
    """

    def test_is_abstract(self) -> None:
        self.assertTrue(
            hasattr(
                IExecutionGovernor,
                "__abstractmethods__",
            )
        )

    def test_cannot_be_instantiated(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            IExecutionGovernor()

    def test_required_methods_exist(
        self,
    ) -> None:
        self.assertTrue(
            hasattr(
                IExecutionGovernor,
                "pre_workflow_check",
            )
        )

        self.assertTrue(
            hasattr(
                IExecutionGovernor,
                "pre_task_check",
            )
        )

        self.assertTrue(
            hasattr(
                IExecutionGovernor,
                "post_task_check",
            )
        )

    def test_expected_abstract_methods(
        self,
    ) -> None:
        self.assertEqual(
            {
                "pre_workflow_check",
                "pre_task_check",
                "post_task_check",
            },
            IExecutionGovernor.__abstractmethods__,
        )

    def test_expected_abstract_method_count(
        self,
    ) -> None:
        self.assertEqual(
            3,
            len(
                IExecutionGovernor.__abstractmethods__
            ),
        )


if __name__ == "__main__":
    unittest.main()
