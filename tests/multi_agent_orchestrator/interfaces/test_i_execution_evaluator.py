# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for IExecutionEvaluator.

import unittest

from alhf.multi_agent_orchestrator.interfaces.i_execution_evaluator import (
    IExecutionEvaluator,
)


class TestExecutionEvaluatorContract(
    unittest.TestCase
):

    def test_is_abstract(self) -> None:
        self.assertTrue(
            hasattr(
                IExecutionEvaluator,
                "__abstractmethods__",
            )
        )

    def test_cannot_be_instantiated(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            IExecutionEvaluator()

    def test_required_methods_exist(
        self,
    ) -> None:
        self.assertTrue(
            hasattr(
                IExecutionEvaluator,
                "evaluate",
            )
        )

    def test_expected_abstract_methods(
        self,
    ) -> None:
        self.assertEqual(
            {
                "evaluate",
            },
            IExecutionEvaluator.__abstractmethods__,
        )

    def test_expected_abstract_method_count(
        self,
    ) -> None:
        self.assertEqual(
            1,
            len(
                IExecutionEvaluator.__abstractmethods__
            ),
        )


if __name__ == "__main__":
    unittest.main()
